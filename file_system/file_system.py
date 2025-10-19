from __future__ import annotations
from datetime import datetime

from disk import Disk
from inode import Inode
from user import User

class FileSystem:
    def __init__(self, disk: Disk, os_ref):
        self.disk = disk
        self.os_ref = os_ref
        self.root = None
        
        # Tenta pegar a raiz (inode 0) do disco
        if len(self.disk.inode_bitmap) > 0:
            self.root = list(self.disk.inode_bitmap.keys())[0]
        else:
            # Cria a raiz se não existir
            root_user = self.os_ref.current_user or User("root", "")
            self.root = Inode('/', root_user, None, self.disk, type='d')
            
        self.current_directory = self.root

    def _create_inode(self, path: list[str], creator: User, type: str) -> Inode:
        if not path:
            print("Erro: Caminho inválido.")
            return None
            
        inode_name = path[-1]
        parent_path = path[:-1]
        
        parent_dir = self._resolve_path(parent_path)
        
        if parent_dir is None:
            print(f"Erro: Caminho '{'/'.join(parent_path)}' não encontrado.")
            return None
        
        if not parent_dir.type == 'd':
            print(f"Erro: '{parent_dir}' não é um diretório.")
            return None

        if parent_dir.get_child_by_name(inode_name) is not None:
            print(f"Erro: '{inode_name}' já existe em '{parent_dir}'.")
            return None
            
        new_inode = Inode(inode_name, creator, parent_dir, self.disk, type)
        parent_dir.add_child_inode(new_inode)
        return new_inode

    def _resolve_path(self, path: list[str], start_node = None) -> Inode:        
        if not path:
            return self.current_directory

        if path[0] == '/':
            current_node = self.root
            path = path[1:]
        elif start_node:
            current_node = start_node # isso é só pra symlink
        else:
            current_node = self.current_directory # relativo
            
        # quebra o caminho e itera sobre
        for part in path:
            if part == '.':
                continue
            if part == '..':
                if current_node.parent_inode is not None:
                    current_node = current_node.parent_inode
                continue
            
            if not current_node.type == 'd':
                print(f"Erro: '{current_node.name}' não é um diretório.")
                return None
                
            child = current_node.get_child_by_name(part)
            
            if child is None:
                print(f"Erro: '{part}' não encontrado em '{current_node}'.")
                return None
            
            # Lida com Links Simbólicos
            if child.type == 'l':
                target_path_str = child.read_content()
                target_path_list = self.os_ref.parse_path(target_path_str)
                
                # Reinicia a resolução a partir do alvo do link
                if target_path_str.startswith('/'):
                    # Caminho absoluto
                    return self._resolve_path(target_path_list, start_node=self.root)
                else:
                    # Caminho relativo (a partir do *pai* do link)
                    return self._resolve_path(target_path_list, start_node=current_node)
            
            current_node = child
            
        return current_node

    def cd(self, path: list[str]):
        target_dir = self._resolve_path(path)
        if target_dir is None:
            print(f"cd: Caminho não encontrado.")
            return
        if target_dir.type != 'd':
            print(f"cd: '{target_dir.name}' não é um diretório.")
            return
        self.current_directory = target_dir
        return

    def ls(self, path: list[str] = None):
        if path is None:
            target_dir = self.current_directory # ls no diretório atual
        else:
            target_dir = self._resolve_path(path)

        if target_dir is None:
            print(f"ls: Caminho não encontrado.")
            return
        
        if target_dir.type != 'd':
            # ls em um arquivo apenas imprime o nome do arquivo
            print(target_dir.name)
            return

        for child in target_dir.list_children():
            if child.type == 'd':
                print(f"{child.name}/")
            elif child.type == 'l':
                print(f"{child.name} -> {child.read_content()}")
            else:
                print(child.name)
        return

    def mkdir(self, path: list[str]):
        new_dir = self._create_inode(path, self.os_ref.current_user, 'd')
        if new_dir:
            print(f"Diretório '{new_dir.name}' criado.")

    def rmdir(self, path: list[str]):
        target_dir = self._resolve_path(path)
        if target_dir is None:
            print(f"rmdir: Caminho não encontrado.")
            return
        if target_dir.type != 'd':
            print(f"rmdir: '{target_dir.name}' não é um diretório.")
            return
        if not target_dir.is_empty():
            print(f"rmdir: Diretório '{target_dir.name}' não está vazio.")
            return
        if target_dir == self.root:
            print(f"rmdir: Não é possível remover o diretório raiz.")
            return
            
        # Remove do pai
        target_dir.parent_inode.remove_child_inode(target_dir)
        # Libera o inode no disco
        self.disk.free_inode(target_dir)
        print(f"Diretório '{target_dir.name}' removido.")
        
    def rm(self, path: list[str]):
        target_file = self._resolve_path(path)
        if target_file is None:
            print(f"rm: Arquivo não encontrado.")
            return
        if target_file.type == 'd':
            print(f"rm: '{target_file.name}' é um diretório. Use 'rmdir'.")
            return
            
        # Remove do pai
        target_file.parent_inode.remove_child_inode(target_file)
        # Libera o inode (e seus blocos) do disco
        self.disk.free_inode(target_file)
        print(f"Arquivo '{target_file.name}' removido.")
        
    def touch(self, path: list[str]):
        target_file = self._resolve_path(path)
        if target_file:
            # atualiza data de mod
            target_file.modification_date = datetime.now()
            self.disk.inode_bitmap[target_file] = 1 # marca node como ativo
        else:
            print(f"Criando..")
            self._create_inode(path, self.os_ref.current_user, 'a')

    def write_to_file(self, path: list[str], content: str, overwrite: bool = False):
        target_file = self._resolve_path(path)
        if target_file is None:
            # arquivo n existe = cria
            target_file = self._create_inode(path, self.os_ref.current_user, 'a')
            if target_file is None:
                print(f"echo: Não foi possível criar o arquivo em '{'/'.join(path)}'.")
                return
        
        if target_file.type == 'd':
            print(f"echo: '{target_file.name}' é um diretório.")
            return
            
        try:
            target_file.write_content(content, overwrite=overwrite)
        except Exception as e:
            print(f"Erro ao escrever no arquivo: {e}")

    def read_file(self, path: list[str]):
        target_file = self._resolve_path(path)
        if target_file is None:
            print(f"cat: Arquivo não encontrado.")
            return
        if target_file.type == 'd':
            print(f"cat: '{target_file.name}' é um diretório.")
            return
            
        print(target_file.read_content())
        
    def cp(self, source_path: list[str], dest_path: list[str]):
        source_file = self._resolve_path(source_path)
        if source_file is None:
            print(f"cp: Arquivo de origem não encontrado.")
            return
        if source_file.type == 'd':
            print(f"cp: Não é possível copiar diretórios (não implementado).")
            return
            
        content = source_file.read_content()
        
        # sobscreve no dest
        self.write_to_file(dest_path, content, overwrite=True)
        print(f"Arquivo copiado para '{'/'.join(dest_path)}'.")

    def mv(self, source_path: list[str], dest_path: list[str]):
        source_node = self._resolve_path(source_path)
        if source_node is None:
            print(f"mv: Origem não encontrada.")
            return
            
        dest_name = dest_path[-1]
        dest_parent_path = dest_path[:-1]
        
        dest_parent_node = self._resolve_path(dest_parent_path)
        if dest_parent_node is None:
            print(f"mv: Diretório de destino não encontrado.")
            return
        if dest_parent_node.type != 'd':
            print(f"mv: Destino não é um diretório.")
            return

        # Verifica se um arquivo com o mesmo nome já existe
        existing_node = dest_parent_node.get_child_by_name(dest_name)
        if existing_node:
            print(f"mv: Destino '{dest_name}' já existe.")
            return
            
        source_node.move(dest_parent_node, dest_name)
        print("Movido.")

    def create_symlink(self, target_path_str: str, link_path: list[str]):
        link_inode = self._create_inode(link_path, self.os_ref.current_user, 'l')
        if link_inode:
            try:
                # conteudo do link é a string do caminho
                link_inode.write_content(target_path_str, overwrite=True)
                print(f"Link '{link_inode.name}' criado -> {target_path_str}")
            except Exception as e:
                print(f"Erro ao criar link: {e}")
                self.rm(link_path) # mata o inode
from datetime import datetime
from block import Block

class Inode:
    def __init__(self, name: str, creator, parent_inode, 
                 disk_ref, type: str = 'a', is_load=False):
        
        self.id = None
        self.name = name
        self.creator = creator
        self.owner = creator
        self.size = 0
        self.creation_date = datetime.now()
        self.modification_date = datetime.now()
        self.parent_inode = parent_inode
        self.disk_ref = disk_ref
        self.type = type # 'a' (arquivo), 'd' (diretório), 'l' (link)

        # dir
        if self.type == 'd':
            self.block_pointers = None 
            self.inode_pointers = []
            self.inode_count = 0

        # file / symlink
        elif self.type == 'a' or self.type == 'l':
            self.block_pointers = []
            self.inode_pointers = None 
            self.inode_count = None
        else:
            raise ValueError(f"Tipo de inode inválido: {type}")

        if not is_load:
            self.disk_ref.add_inode(self)
        
        # quantos blocos este inode pode apontar
        inode_size_bytes = self.disk_ref.inode_size_kb * 1024
        pointer_size_bytes = len(str(self.disk_ref.block_capacity))
        
        # tamanho aproximado ok
        metadata_size = 300 
        self.block_pointer_limit = (inode_size_bytes - metadata_size) // pointer_size_bytes

    def __str__(self) -> str:
        # Retorna o caminho absoluto do inode
        path = []
        current_inode = self
        while current_inode.parent_inode is not None:
            path.append(current_inode.name)
            current_inode = current_inode.parent_inode
        path.append(current_inode.name)
        path.reverse()
        full_path = '/'.join(path)
        if full_path.startswith('//'): # Corrige caso a raiz seja '/'
            full_path = full_path[1:]
        return full_path

    def print_metadata(self):        
        if self.type == 'd':
            type_str = "Dir"
        elif self.type == 'l':
            type_str = "Symlink"
        else:
            type_str = "File"

        print(f"--- Metadados do Inode: {self.name} ---")
        print(f"  Caminho: {str(self)}")
        print(f"  Tipo: {type_str}")
        print(f"  Criador: {self.creator.username if self.creator else 'N/A'}")
        print(f"  Dono: {self.owner.username if self.owner else 'N/A'}")
        print(f"  Tamanho (bytes): {self.size}")
        print(f"  Criado em: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Modificado em: {self.modification_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # type especific
        if self.type == 'd':
            print(f"  Contagem de Filhos: {self.inode_count}")
        elif self.type == 'l':
            print(f"  Alvo do Link: {self.read_content()}")
        else: # 'a'
            print(f"  Blocos Alocados: {len(self.block_pointers)}")

    def get_child_by_name(self, name: str):
        if self.type != 'd':
            return None
        for inode in self.inode_pointers:
            if inode.name == name:
                if inode is self: continue
                return inode
        return None

    def list_children(self):
        if self.type == 'd':
            return self.inode_pointers
        else:
            return []

    def add_child_inode(self, inode):
        if self.type != 'd':
            raise Exception(f'{self} não é um diretório.')
        self.inode_pointers.append(inode)
        self.inode_count += 1
        self.modification_date = datetime.now()

    def remove_child_inode(self, inode):
        if self.type != 'd':
            raise Exception(f'{self} não é um diretório.')
        self.inode_pointers.remove(inode)
        self.inode_count -= 1
        self.modification_date = datetime.now()

    def is_empty(self) -> bool:
        # Verifica se um diretório está vazio
        if self.type == 'd':
            return self.inode_count == 0
        raise Exception(f'{self} não é um diretório.')

    def move(self, new_parent_inode, new_name: str):
        # Move o inode (this) para um novo pai e/ou novo nome
        if self.parent_inode:
            self.parent_inode.remove_child_inode(self)
        self.parent_inode = new_parent_inode
        self.name = new_name
        self.parent_inode.add_child_inode(self)
        self.modification_date = datetime.now()

    def write_content(self, content: str, overwrite: bool = False):
        if self.type == 'd':
            raise Exception(f'{self} é um diretório.')
        
        if overwrite:
            self.clear_content() # Libera blocos antigos

        if len(self.block_pointers) == 0:
            if self.can_add_new_block():
                self.block_pointers.append(Block(self.disk_ref))
            else:
                raise Exception(f'{self} não pode adicionar novos blocos.')
        
        current_block: Block = self.block_pointers[-1]
        
        # recursivo pra lidar com conteúdo > bloco
        if current_block.can_fit(content):
            current_block.write(content)
        else:
            space_left = current_block.get_free_space()

            content_part1 = content[:space_left]
            content_part2 = content[space_left:]
            
            current_block.write(content_part1)
            
            if self.can_add_new_block():
                self.block_pointers.append(Block(self.disk_ref))
                self.write_content(content_part2, overwrite=False) 
            else:
                raise Exception(f'{self} ficou sem ponteiros de bloco.')

        self.size = len(self.read_content()) # Atualiza o tamanho
        self.modification_date = datetime.now()

    def can_add_new_block(self) -> bool:
        return len(self.block_pointers) < self.block_pointer_limit
        
    def read_content(self) -> str:
        if self.type == 'd':
            raise Exception(f'{self} é um diretório.')
        
        content = ''
        for block in self.block_pointers:
            content += block.content
        return content
        
    def clear_content(self):
        # Limpa o *conteúdo* e libera os blocos, mas não deleta o inode
        if self.type == 'd':
            self.inode_pointers = []
            self.inode_count = 0
        else:
            for block in self.block_pointers:
                self.disk_ref.free_block(block) # Libera cada bloco no disco
            self.block_pointers = []
            self.size = 0
        self.modification_date = datetime.now()

    # Serializa os metadados do inode para uma string de tamanho fixo
    def serialize(self) -> str:        
        text = ''
        
        name = str(self.name)
        name = name[name.rfind('/')+1:]
        if len(name) < self.disk_ref.inode_name_max_len:
            name += '"' # char de fim de nome
            if len(name) < self.disk_ref.inode_name_max_len:
                name = name.ljust(self.disk_ref.inode_name_max_len, '0')
        text += name
        
        
        size = str(self.size).zfill(self.disk_ref.inode_size_field_len)
        text += size
        
        text += self.creation_date.strftime('%d%m%Y%H%M')        
        text += self.modification_date.strftime('%d%m%Y%H%M')
        
        # parent
        parent_index_str = ''
        parent_index_len = len(str(self.disk_ref.inode_capacity))
        if self.parent_inode is None:
            # O pai da raiz (None) deve ser seu próprio ID (0)
            parent_index = self.id if self.id is not None else 0
        else:
            # get parent id in disk
            parent_index = self.parent_inode.id
        
        # zfill -> completa com 0 a esquerda da string
        parent_index_str = str(parent_index).zfill(parent_index_len)
        text += parent_index_str
        
        # pointers
        blocks_str = ''
        block_index_len = len(str(self.disk_ref.block_capacity))
        
        if self.block_pointers is not None:
            for block in self.block_pointers:
                try:
                    if block.id is not None:
                        blocks_str += str(block.id).zfill(block_index_len)
                except ValueError:
                    pass # bloco nao tá no bitmap?
            
        # preenche o restante dos ponteiros com '0'
        blocks_str = blocks_str.ljust(self.block_pointer_limit * block_index_len, '0')
        text += blocks_str
        
        total_inode_size = self.disk_ref.inode_size_kb * 1024
        if len(text) < total_inode_size:
            text += '"' # char de fim de dados
            text = text.ljust(total_inode_size, '0')

            # salva o tipo no nome do inode no último char
            # nota -> "metadata" é sempre em binário
            # ex. nome_diretorio"metadata"000d, nome_arquivo"metadata"000a, nome_link"metadata"000l
            text = text[:-1] + self.type
            # print("debug", text)
        return text
from collections import OrderedDict
from datetime import datetime
from block import Block
from user import User
from inode import Inode

class Disk:
    def __init__(self, max_size_mb: int, block_size_kb: int, inode_size_kb: int, 
                 os_ref, disk_filename: str, inode_name_max_len: int,
                 inode_timestamp_len: int, inode_size_field_len: int):
        
        # disk config
        self.max_size_mb = max_size_mb
        self.block_size_kb = block_size_kb
        self.inode_size_kb = inode_size_kb
        self.os_ref = os_ref 
        self.disk_filename = disk_filename
        
        # Constantes de serialização
        self.inode_name_max_len = inode_name_max_len
        self.inode_timestamp_len = inode_timestamp_len
        self.inode_size_field_len = inode_size_field_len

        
        # Bitmaps
        self.block_capacity = self.inode_capacity = self._calculate_capacity()
        self.block_bitmap = OrderedDict()
        self.inode_bitmap = OrderedDict()
        self.all_inodes = [None] * self.inode_capacity
        self.all_blocks = [None] * self.block_capacity
        
    def _calculate_capacity(self) -> int:
        # Esta função calcula o número máximo de inodes e blocos
        disk_bytes = self.max_size_mb * 1024 * 1024
        block_bytes = self.block_size_kb * 1024
        inode_bytes = self.inode_size_kb * 1024
        
        # d = (b + i + 2) * capacity
        capacity = disk_bytes // (block_bytes + inode_bytes + 2)
        print("BLOCK CAPACITY: ", capacity)
        
        return capacity
    
    def add_block(self, block) -> bool:
        # Adiciona um bloco ao bitmap (se houver espaço) - primeiro slot livre
        for i in range(self.block_capacity):
            if self.all_blocks[i] is None:
                 self.all_blocks[i] = block
                 block.id = i
                 self.block_bitmap[block] = 1
                 return True
        return False

    def add_inode(self, inode) -> bool:
        # add inode no bitmap - primeiro slot livre 
        for i in range(self.inode_capacity):
            if self.all_inodes[i] is None:
                self.all_inodes[i] = inode
                inode.id = i
                self.inode_bitmap[inode] = 1 # Adiciona ao bitmap de ativos
                return True
        return False # Disco cheio
    
    def free_block(self, block):
        if block in self.block_bitmap:
            del self.block_bitmap[block]
            if block.id is not None and self.all_blocks[block.id] == block:
                self.all_blocks[block.id] = None
            return True
        return False
    
    def free_inode(self, inode):
        # free inode
        if inode in self.inode_bitmap:
            if inode.type != 'd':
                inode.clear_content() # Libera os blocos de dados associados
            del self.inode_bitmap[inode]
            if inode.id is not None and self.all_inodes[inode.id] == inode:
                self.all_inodes[inode.id] = None
            return True
        return False
    
    def save_to_disk(self):
        # serializa todo o disco e salva no txt
        print(f"Salvando estado do disco em {self.disk_filename}...")
        
        # mapeia os bits
        block_bits = ''.join(['1' if b is not None else '0' for b in self.all_blocks])
        inode_bits = ''.join(['1' if i is not None else '0' for i in self.all_inodes])

        # itera sobre as listas all - quando fiz pelo bitmap dava corrompendo
        with open(self.disk_filename, 'w') as f:
            f.write(block_bits)
            f.write(inode_bits)

            empty_block_text = '0' * (self.block_size_kb * 1024)
            for block in self.all_blocks:
                if block:
                    f.write(block.serialize())
                else:
                    f.write(empty_block_text)

            empty_inode_text = '0' * (self.inode_size_kb * 1024)
            for inode in self.all_inodes:
                if inode:
                    f.write(inode.serialize())
                else:
                    f.write(empty_inode_text)
                    
        print("Salvo com sucesso.")

       
    def load_from_disk(self):
        # Desserializa o arquivo de texto de volta para objetos em memória
        print(f"Carregando estado do disco de {self.disk_filename}...")
        with open(self.disk_filename, 'r') as f:
            text = f.read()

        # get bits
        block_bits = [int(text[i]) for i in range(self.block_capacity)]
        inode_bits = [int(text[self.block_capacity + i]) for i in range(self.inode_capacity)]
        print("bits ok")
        
        text_offset = self.block_capacity + self.inode_capacity

        # constroi o bloco do 0
        block_size_bytes = self.block_size_kb * 1024
        for i in range(self.block_capacity):
            block_text = text[text_offset : text_offset + block_size_bytes]
            text_offset += block_size_bytes
            
            new_block = Block(self, is_load=True) 
            new_block.id = i

            # fim do bloco
            content_end_marker = block_text.rfind('"0')
            if content_end_marker != -1:
                new_block.write(block_text[:content_end_marker])

            elif block_text.endswith('"'):
                new_block.write(block_text[:-1])
            
            elif not block_text.startswith('0'):
                new_block.write(block_text)
                
            self.all_blocks[i] = new_block

        # constroi inodes
        inode_size_bytes = self.inode_size_kb * 1024
        parent_index_map = {} # (idx_inode, idx_pai)
        
        # carrega tudo com root
        loading_user = User("root", "") 

        for i in range(self.inode_capacity):
            inode_text = text[text_offset : text_offset + inode_size_bytes]
            text_offset += inode_size_bytes
            
            if not inode_bits[i]:
                self.all_inodes[i] = None
                continue

            # get metadata
            name = inode_text[:self.inode_name_max_len].split('"')[0]
            size = int(inode_text[self.inode_name_max_len : self.inode_name_max_len + self.inode_size_field_len])
            ctime_str = inode_text[270:282]
            mtime_str = inode_text[282:294]
            print(f"metadata ok for inode {i}")
            
            parent_index_len = len(str(self.inode_capacity))
            parent_index = int(inode_text[294 : 294 + parent_index_len])
            print(f"parent ok for inode {i}")
            
            type = inode_text[-1]
            if type not in ['a', 'd', 'l']: # Ignora inodes inválidos
                self.all_inodes[i] = None
                continue

            if i == 0: name = '/' # root inode
            
            new_inode = Inode(name, loading_user, None, self, type, is_load=True)
            new_inode.id = i
            new_inode.size = size
            new_inode.creation_date = datetime.strptime(ctime_str, '%d%m%Y%H%M')
            new_inode.modification_date = datetime.strptime(mtime_str, '%d%m%Y%H%M')
            
            # map block idx
            if new_inode.type != 'd':
                block_pointers_str_start = 294 + parent_index_len
                block_pointers_str_end = block_pointers_str_start + (new_inode.block_pointer_limit * len(str(self.block_capacity)))
                block_pointers_str = inode_text[block_pointers_str_start:block_pointers_str_end]
                
                block_index_len = len(str(self.block_capacity))
                for j in range(new_inode.block_pointer_limit):
                    b_idx_str = block_pointers_str[j*block_index_len : (j+1)*block_index_len]
                    b_idx = int(b_idx_str)
                    if b_idx > 0 or (b_idx == 0 and len(new_inode.block_pointers) > 0):
                        if b_idx < len(self.all_blocks):
                            new_inode.block_pointers.append(self.all_blocks[b_idx])

            self.all_inodes[i] = new_inode
            parent_index_map[i] = parent_index

        for i, inode in enumerate(self.all_inodes):
            if inode is None: continue
            
            parent_idx = parent_index_map.get(i)
            # link inode to parent
            if parent_idx is not None and parent_idx < len(self.all_inodes) and self.all_inodes[parent_idx] is not None:
                if i != parent_idx: # root aponta p root
                    parent_inode = self.all_inodes[parent_idx]
                    if parent_inode:
                        inode.parent_inode = parent_inode
                        parent_inode.add_child_inode(inode)

        # filtra só os que estão ativos
        self.block_bitmap = OrderedDict(
            (self.all_blocks[i], 1) for i, bit in enumerate(block_bits) 
            if bit == 1 and i < len(self.all_blocks) and self.all_blocks[i]
        )
        self.inode_bitmap = OrderedDict(
            (self.all_inodes[i], 1) for i, bit in enumerate(inode_bits) 
            if bit == 1 and i < len(self.all_inodes) and self.all_inodes[i]
        )

        print("Disco carregado com sucesso.")
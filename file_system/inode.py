# inode.py
from datetime import datetime
from typing import Optional, List
from block import Block

INODE_NAME_MAX_LEN = 32
INODE_SIZE_FIELD_LEN = 10
INODE_TIMESTAMP_LEN = 12
PARENT_INDEX_LEN = 6
TYPE_LEN = 1

class Inode:
    def __init__(self, name: str, creator, parent_inode, disk_ref, type: str = 'a', is_load: bool = False):
        self.id: Optional[int] = None
        self.name: str = name or ''
        self.creator = creator
        self.owner = creator
        self.size: int = 0
        self.creation_date = datetime.now()
        self.modification_date = datetime.now()
        self.parent_inode = parent_inode
        self.disk_ref = disk_ref
        self.type: str = type  # 'a', 'd', 'l'

        # pointers e estrutura de diretório
        self.block_pointers: List[Block] = []
        if self.type == 'd':
            self.inode_pointers: List[Inode] = []
            self.inode_count = 0
        else:
            self.inode_pointers = None
            self.inode_count = None

        # calcula quantos ponteiros cabem na serialização
        ptr_chars = len(str(self.disk_ref.block_capacity))
        metadata_fixed = INODE_NAME_MAX_LEN + INODE_SIZE_FIELD_LEN + INODE_TIMESTAMP_LEN*2 + PARENT_INDEX_LEN + TYPE_LEN
        self.block_pointer_limit = (self.disk_ref.inode_size_b - metadata_fixed) // ptr_chars

        if not is_load:
            # registra no disco (Disk.add_inode)
            self.disk_ref.add_inode(self)

    def __str__(self) -> str:
        parts = []
        cur = self
        while cur is not None:
            # A raiz tem nome vazio, mas seu path é '/'
            if cur.parent_inode is None:
                parts.append('')
                break
            parts.append(cur.name)
            cur = cur.parent_inode
        parts.reverse()
        # Junta as partes, garantindo que comece com '/' e não tenha barras duplas
        return '/' + '/'.join(filter(None, parts))
    
    def print_metadata(self):
        type_map = {'a': 'arquivo', 'd': 'diretório', 'l': 'link simbólico'}
        
        print(f"name: '{self.name}'")
        print(f"path: {self}")
        print(f"size: {self.size} Bytes")
        if self.type == 'l':
            print(f"link to: {self.read_content()}")

        print(f"type: {type_map.get(self.type, 'unknown')}")
        print(f"inode: {self.id}")
        
        parent_id = self.parent_inode.id if self.parent_inode else 'N/A (raiz)'
        print(f"parent inode id: {parent_id}")

        print(f"owner: {self.owner}")
        print(f"creator: {self.creator}")
        print(f"created at: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"modified at: {self.modification_date.strftime('%Y-%m-%d %H:%M:%S')}")

        block_ids = [b.id for b in self.block_pointers]
        print(f"blocks -> ({len(block_ids)}): {block_ids if block_ids else 'None'}")

    def add_child_inode(self, inode):
        if self.type != 'd':
            raise Exception("Não é diretório")
        # evita duplicata
        if inode not in self.inode_pointers:
            self.inode_pointers.append(inode)
            self.inode_count = len(self.inode_pointers)
            self.modification_date = datetime.now()

    def remove_child_inode(self, inode):
        if self.type != 'd':
            raise Exception("Não é diretório")
        if inode in self.inode_pointers:
            self.inode_pointers.remove(inode)
            self.inode_count = len(self.inode_pointers)
            self.modification_date = datetime.now()

    def get_child_by_name(self, name: str):
        if self.type != 'd':
            return None
        for c in self.inode_pointers:
            if c.name == name:
                return c
        return None

    def list_children(self):
        if self.type == 'd':
            return list(self.inode_pointers)
        return []

    def is_empty(self) -> bool:
        if self.type != 'd':
            raise Exception("Não é diretório")
        # considera vazio se não tem filhos (.) e (..) não representados aqui
        return self.inode_count == 0

    def can_add_new_block(self) -> bool:
        return len(self.block_pointers) < self.block_pointer_limit

    def write_content(self, content: str, overwrite: bool = False):
        if self.type == 'd':
            raise Exception("Não pode escrever em diretório")
        if overwrite:
            self.clear_content()
        remaining = content.encode('utf-8')
        # garante pelo menos um bloco
        if len(self.block_pointers) == 0:
            if not self.can_add_new_block():
                raise Exception("Sem ponteiros disponíveis")
            self.block_pointers.append(Block(self.disk_ref))
        while remaining:
            blk = self.block_pointers[-1]
            free = blk.get_free_space()
            part = remaining[:free]
            blk.write_bytes(part)
            remaining = remaining[len(part):]
            if remaining:
                if self.can_add_new_block():
                    self.block_pointers.append(Block(self.disk_ref))
                else:
                    raise Exception("Excedeu ponteiros do inode")
        # atualiza size e mtime
        self.size = sum(len(b.content) for b in self.block_pointers)
        self.modification_date = datetime.now()

    def read_content(self) -> str:
        if self.type == 'd':
            raise Exception("Diretório não pode ser lido como arquivo")
        data = b''.join(blk.read_bytes() for blk in self.block_pointers)
        return data.decode('utf-8', errors='ignore')

    def clear_content(self):
        if self.type == 'd':
            self.inode_pointers = []
            self.inode_count = 0
        else:
            for blk in list(self.block_pointers):
                try:
                    self.disk_ref.free_block(blk)
                except Exception:
                    pass
            self.block_pointers = []
            self.size = 0
        self.modification_date = datetime.now()

    def move(self, new_parent, new_name: str):
        if self.parent_inode:
            self.parent_inode.remove_child_inode(self)
        
        self.parent_inode = new_parent
        new_parent.add_child_inode(self)
        self.name = new_name
        self.modification_date = datetime.now()


    def serialize(self) -> bytes:
        # name
        name_b = (self.name.encode('utf-8')[:INODE_NAME_MAX_LEN]).ljust(INODE_NAME_MAX_LEN, b'\x00')
        # size
        size_b = str(int(self.size)).zfill(INODE_SIZE_FIELD_LEN).encode('ascii')
        # times
        ctime_s = self.creation_date.strftime('%d%m%Y%H%M').encode('ascii')
        mtime_s = self.modification_date.strftime('%d%m%Y%H%M').encode('ascii')
        # parent id
        # Usamos -1 para indicar 'sem pai' (raiz), para não confundir com o inode 0.
        parent_id = -1 if self.parent_inode is None else self.parent_inode.id
        parent_b = str(parent_id).zfill(PARENT_INDEX_LEN).encode('ascii')
        # pointers
        ptr_chars = len(str(self.disk_ref.block_capacity))
        ptrs = b''
        for blk in self.block_pointers:
            bid = 0 if blk is None or blk.id is None else blk.id
            ptrs += str(bid).zfill(ptr_chars).encode('ascii')
        total_ptr_len = self.block_pointer_limit * ptr_chars
        ptrs = ptrs.ljust(total_ptr_len, b'0')
        # type
        type_b = (self.type or 'a').encode('ascii')
        payload = name_b + size_b + ctime_s + mtime_s + parent_b + ptrs + type_b
        if len(payload) > self.disk_ref.inode_size_b:
            payload = payload[:self.disk_ref.inode_size_b]
        # print(f"[DEBUG-SERIALIZE] Inode '{self.name}' (ID: {self.id}) -> {payload.hex()}")
        return payload.ljust(self.disk_ref.inode_size_b, b'\x00')

    @classmethod
    def load_from_bytes(cls, data: bytes, disk_ref, is_load: bool = False):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("load_from_bytes espera bytes")
        name = data[0:INODE_NAME_MAX_LEN].split(b'\x00', 1)[0].decode('utf-8', errors='ignore').strip()
        # print(f"[DEBUG-LOAD] Carregando inode: '{name}' a partir de bytes: {data.hex()}")
        size_s = data[INODE_NAME_MAX_LEN:INODE_NAME_MAX_LEN + INODE_SIZE_FIELD_LEN].decode('ascii', errors='ignore').strip()
        try:
            size = int(size_s) if size_s else 0
        except:
            size = 0
        off = INODE_NAME_MAX_LEN + INODE_SIZE_FIELD_LEN
        ctime_s = data[off:off + INODE_TIMESTAMP_LEN].decode('ascii', errors='ignore'); off += INODE_TIMESTAMP_LEN
        mtime_s = data[off:off + INODE_TIMESTAMP_LEN].decode('ascii', errors='ignore'); off += INODE_TIMESTAMP_LEN
        parent_s = data[off:off + PARENT_INDEX_LEN].decode('ascii', errors='ignore'); off += PARENT_INDEX_LEN

        ptr_chars = len(str(disk_ref.block_capacity))
        ptrs_count = (disk_ref.inode_size_b - (INODE_NAME_MAX_LEN + INODE_SIZE_FIELD_LEN + INODE_TIMESTAMP_LEN*2 + PARENT_INDEX_LEN + TYPE_LEN)) // ptr_chars
        ptrs = []
        for i in range(ptrs_count):
            slice_s = data[off + i*ptr_chars: off + (i+1)*ptr_chars].decode('ascii', errors='ignore').strip()
            if slice_s and slice_s != '0':
                try:
                    ptrs.append(int(slice_s))
                except:
                    pass
        off += ptrs_count * ptr_chars
        type_s = data[off:off + TYPE_LEN].decode('ascii', errors='ignore') or 'a'

        inode = cls(name=name or '', creator=None, parent_inode=None, disk_ref=disk_ref, type=type_s, is_load=True)
        inode.size = size
        try:
            inode.creation_date = datetime.strptime(ctime_s, '%d%m%Y%H%M')
        except:
            inode.creation_date = datetime.now()
        try:
            inode.modification_date = datetime.strptime(mtime_s, '%d%m%Y%H%M')
        except:
            inode.modification_date = datetime.now()

        # preencher blocos com referências existentes (serão None se bloco não carregado)
        inode.block_pointers = []
        for bid in ptrs:
            if 0 <= bid < disk_ref.block_capacity and disk_ref.all_blocks[bid] is not None:
                inode.block_pointers.append(disk_ref.all_blocks[bid])

        # guarda parent temporário para resolução pós-load
        try:
            pid = int(parent_s)
            # Se o ID do pai for -1, significa que é a raiz e não tem pai.
            inode._temp_parent_id = None if pid == -1 else pid
        except:
            inode._temp_parent_id = None # Fallback

        if inode.type == 'd':
            inode.inode_pointers = []
            inode.inode_count = 0

        return inode

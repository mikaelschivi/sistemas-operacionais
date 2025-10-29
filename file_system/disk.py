# disk.py
import os
from collections import OrderedDict
from block import Block
from inode import Inode

DISK_FILENAME_DEFAULT = "disco"
DISK_SIZE_MB = 64
BLOCK_SIZE_B = 512
INODE_SIZE_B = 128

class Disk:
    def __init__(self,
                 disk_filename: str = DISK_FILENAME_DEFAULT,
                 max_size_mb: int = DISK_SIZE_MB,
                 block_size_b: int = BLOCK_SIZE_B,
                 inode_size_b: int = INODE_SIZE_B):

        self.filename = disk_filename
        print(f"[disk] filename: {self.filename}")
        self.max_size_mb = int(max_size_mb)
        print(f"[disk] disk size (MB): {self.max_size_mb}")
        self.total_bytes = self.max_size_mb * 1024 * 1024
        print(f"[disk] disk total (B): {self.total_bytes}")
        self.block_size_b = int(block_size_b)
        print(f"\n[disk] block size (B): {self.block_size_b}")
        self.inode_size_b = int(inode_size_b)
        print(f"[disk] inode size (B): {self.inode_size_b}")

        # Define o layout do disco
        metadata_size = int(self.total_bytes * 0.2)  # 20% do disco para salvar inodes - 13.421MB -> ~105000 inodes
        print(f"[disk] disk metadata table size (B): {metadata_size} - {(self.total_bytes - metadata_size) / self.total_bytes * 100:.2f}%")
        data_blocks_size = self.total_bytes - metadata_size # ~50MB para blocos
        print(f"[disk] disk data block size (B): {data_blocks_size} - {(self.total_bytes - data_blocks_size) / self.total_bytes * 100:.2f}%")

        # Calcula capacidades
        self.block_capacity = data_blocks_size // self.block_size_b
        
        # Os dois bitmaps são de 4 bytes cada.
        
        # O espaço de metadata é dividido entre tabela de inodes e os dois bitmaps
        inode_table_size = metadata_size - 64 # 64 bits = 8 bytes, são os 2 blocos de 4 bytes de Bitmap
        self.inode_capacity = inode_table_size // self.inode_size_b
        print(f"[disk] inode capacity: {self.inode_capacity}")

        # Define os offsets
        self.inode_bitmap_offset = 0 # 0 - 31 bit
        self.block_bitmap_offset = 32 # 32 - 63 bit
        self.inode_table_offset = 64
        self.block_data_offset = metadata_size
        print(f"[disk] block capacity: {self.block_capacity}")

        # Estruturas
        self.all_blocks = [None] * self.block_capacity
        self.all_inodes = [None] * self.inode_capacity
        self.block_bitmap = OrderedDict()
        self.inode_bitmap = OrderedDict()

        # Cria arquivo disco se não existir
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.truncate(self.total_bytes)
            print(f"Arquivo disco '{self.filename}' criado ({self.max_size_mb} MB).")

    def add_block(self, block: Block) -> bool:
        for i in range(self.block_capacity):
            if self.all_blocks[i] is None:
                self.all_blocks[i] = block
                block.id = i
                self.block_bitmap[block] = 1
                return True
        return False

    def add_inode(self, inode: Inode) -> bool:
        for i in range(self.inode_capacity):
            if self.all_inodes[i] is None:
                self.all_inodes[i] = inode
                inode.id = i
                self.inode_bitmap[inode] = 1
                return True
        return False

    def free_block(self, block: Block) -> bool:
        if block is None: return False
        if block in self.block_bitmap:
            del self.block_bitmap[block]
            if block.id is not None and 0 <= block.id < len(self.all_blocks):
                self.all_blocks[block.id] = None
            block.id = None
            return True
        return False

    def free_inode(self, inode: Inode) -> bool:
        if inode is None: return False
        if inode in self.inode_bitmap:
            if hasattr(inode, 'clear_content') and inode.type != 'd':
                inode.clear_content()
            del self.inode_bitmap[inode]
            if inode.id is not None and 0 <= inode.id < len(self.all_inodes):
                self.all_inodes[inode.id] = None
            inode.id = None
            return True
        return False

    def save_to_disk(self):
        print("\n[DEBUG] Iniciando salvamento no disco...")
        print("Salvando disco...", end=" ") # Mantém o original
        with open(self.filename, 'r+b') as f:
            # Bitmaps
            block_bits = bytearray(ord('0') for _ in range(self.block_capacity))
            print(f"[DEBUG] Preparando bitmap de blocos ({self.block_capacity} bits)...")
            for i, blk in enumerate(self.all_blocks):
                if blk is not None:
                    block_bits[i] = ord('1')

            inode_bits = bytearray(ord('0') for _ in range(self.inode_capacity))
            for i, inode in enumerate(self.all_inodes):
                if inode is not None:
                    inode_bits[i] = ord('1')
            
            # Escreve bitmaps nos seus offsets
            print(f"[DEBUG] Escrevendo bitmap de inodes no offset {self.inode_bitmap_offset}")
            f.seek(self.inode_bitmap_offset)
            f.write(inode_bits)
            print(f"[DEBUG] Escrevendo bitmap de blocos no offset {self.block_bitmap_offset}")
            f.seek(self.block_bitmap_offset)
            f.write(block_bits)

            # Escreve tabela de inodes
            print(f"[DEBUG] Escrevendo tabela de inodes no offset {self.inode_table_offset}")
            f.seek(self.inode_table_offset)
            for inode in self.all_inodes:
                if inode is not None:
                    print(f"[DEBUG]   -> Serializando Inode ID: {inode.id}, Nome: '{inode.name}'")
                    f.write(inode.serialize().ljust(self.inode_size_b, b'\x00'))
                else:
                    f.write(b'\x00' * self.inode_size_b)

            # Escreve blocos de dados
            print(f"[DEBUG] Escrevendo blocos de dados no offset {self.block_data_offset}")
            f.seek(self.block_data_offset)
            for blk in self.all_blocks:
                if blk is not None:
                    print(f"[DEBUG]   -> Serializando Bloco ID: {blk.id}, Tamanho: {len(blk.content)} bytes")
                    f.write(blk.serialize().ljust(self.block_size_b, b'\x00'))
                else:
                    f.write(b'\x00' * self.block_size_b)
            
            print("[DEBUG] Sincronizando dados com o arquivo físico...")
            f.flush()
            os.fsync(f.fileno())

        self.debug_summary()
        print("OK")

    def load_from_disk(self):
        print("\n[DEBUG] Iniciando carregamento do disco...")
        print("Carregando disco...", end=" ") # Mantém o original
        with open(self.filename, 'rb') as f:
            # Lê bitmaps
            print(f"[DEBUG] Lendo bitmap de inodes do offset {self.inode_bitmap_offset} ({self.inode_capacity} bytes)")
            f.seek(self.inode_bitmap_offset)
            inode_bits_raw = f.read(self.inode_capacity)
            print(f"[DEBUG] Lendo bitmap de blocos do offset {self.block_bitmap_offset} ({self.block_capacity} bytes)")
            f.seek(self.block_bitmap_offset)
            block_bits_raw = f.read(self.block_capacity)

            # Limpa estruturas
            print("[DEBUG] Limpando estruturas de dados em memória...")
            self.all_blocks = [None] * self.block_capacity
            self.all_inodes = [None] * self.inode_capacity
            self.block_bitmap = OrderedDict()
            self.inode_bitmap = OrderedDict()

            # Carrega blocos
            print(f"[DEBUG] Carregando blocos de dados do offset {self.block_data_offset}...")
            f.seek(self.block_data_offset)
            for i in range(self.block_capacity):
                blk_bytes = f.read(self.block_size_b)
                if i < len(block_bits_raw) and block_bits_raw[i] == ord('1'):
                    print(f"[DEBUG]   -> Deserializando Bloco ID: {i}")
                    blk = Block(self, is_load=True)
                    blk.id = i
                    content = blk_bytes.rstrip(b'\x00')
                    if hasattr(blk, 'write_bytes'):
                        blk.write_bytes(content)
                    else:
                        blk.content = content
                    self.all_blocks[i] = blk
                    self.block_bitmap[blk] = 1
            
            # Carrega inodes
            print(f"[DEBUG] Carregando tabela de inodes do offset {self.inode_table_offset}...")
            f.seek(self.inode_table_offset)
            temp_parent_map = {}
            for i in range(self.inode_capacity):
                inode_bytes = f.read(self.inode_size_b)
                if i < len(inode_bits_raw) and inode_bits_raw[i] == ord('1'):
                    print(f"[DEBUG]   -> Deserializando Inode ID: {i}")
                    inode = Inode.load_from_bytes(inode_bytes, disk_ref=self, is_load=True)
                    inode.id = i
                    self.all_inodes[i] = inode
                    self.inode_bitmap[inode] = 1
                    if hasattr(inode, '_temp_parent_id'):
                        pid = getattr(inode, '_temp_parent_id', None)
                        if pid is not None:
                            temp_parent_map[i] = pid

            # Resolve parents
            print("[DEBUG] Resolvendo hierarquia de diretórios (pais e filhos)...")
            for idx, inode in enumerate(self.all_inodes):
                if inode is None: continue
                pid = temp_parent_map.get(idx)
                if pid is not None and 0 <= pid < self.inode_capacity:
                    # Verificação de segurança para evitar que um inode seja seu próprio pai.
                    if idx == pid:
                        print(f"[DEBUG-WARN] Inode ID {idx} tentou se auto-referenciar como pai. Ignorando.")
                        continue
                    parent = self.all_inodes[pid]
                    if parent and parent.type == 'd':
                        print(f"[DEBUG]   -> Vinculando Inode ID: {idx} ('{inode.name}') ao Pai ID: {pid} ('{parent.name}')")
                        inode.parent_inode = parent
                        parent.add_child_inode(inode)
        print("OK")

    def debug_summary(self) -> str:
        return f"Disk: blocks={len(self.block_bitmap)}/{self.block_capacity}, inodes={len(self.inode_bitmap)}/{self.inode_capacity}"

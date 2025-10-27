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
        self.max_size_mb = int(max_size_mb)
        self.block_size_b = int(block_size_b)
        self.inode_size_b = int(inode_size_b)
        self.total_bytes = self.max_size_mb * 1024 * 1024

        # Define o layout do disco
        metadata_size = 4 * 1024 * 1024  # 4MB para metadata
        data_blocks_size = self.total_bytes - metadata_size # 60MB para blocos

        # Calcula capacidades
        self.block_capacity = data_blocks_size // self.block_size_b
        # O espaço de metadata é dividido entre tabela de inodes e os dois bitmaps
        inode_table_size = metadata_size - self.block_capacity // 8 - (metadata_size // (self.inode_size_b*8+1)) // 8
        self.inode_capacity = inode_table_size // self.inode_size_b

        # Define os offsets
        self.inode_bitmap_offset = 0
        self.block_bitmap_offset = self.inode_bitmap_offset + self.inode_capacity
        self.inode_table_offset = self.block_bitmap_offset + self.block_capacity
        self.block_data_offset = metadata_size

        print(f"[disk] filename: {self.filename}")
        print(f"[disk] size (MB): {self.max_size_mb}")
        print(f"[disk] block size (B): {self.block_size_b}")
        print(f"[disk] inode size (B): {self.inode_size_b}")
        print(f"[disk] disk total (B): {self.total_bytes}")
        print(f"[disk] block capacity: {self.block_capacity}")
        print(f"[disk] inode capacity: {self.inode_capacity}")

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
        print("Salvando disco...", end=" ")
        with open(self.filename, 'r+b') as f:
            # Bitmaps
            block_bits = bytearray(ord('0') for _ in range(self.block_capacity))
            for i, blk in enumerate(self.all_blocks):
                if blk is not None:
                    block_bits[i] = ord('1')

            inode_bits = bytearray(ord('0') for _ in range(self.inode_capacity))
            for i, inode in enumerate(self.all_inodes):
                if inode is not None:
                    inode_bits[i] = ord('1')
            
            # Escreve bitmaps nos seus offsets
            f.seek(self.inode_bitmap_offset)
            f.write(inode_bits)
            f.seek(self.block_bitmap_offset)
            f.write(block_bits)

            # Escreve tabela de inodes
            f.seek(self.inode_table_offset)
            for inode in self.all_inodes:
                if inode is not None:
                    f.write(inode.serialize().ljust(self.inode_size_b, b'\x00'))
                else:
                    f.write(b'\x00' * self.inode_size_b)

            # Escreve blocos de dados
            f.seek(self.block_data_offset)
            for blk in self.all_blocks:
                if blk is not None:
                    f.write(blk.serialize().ljust(self.block_size_b, b'\x00'))
                else:
                    f.write(b'\x00' * self.block_size_b)
            
            f.flush()
            os.fsync(f.fileno())
        print("OK")

    def load_from_disk(self):
        print("Carregando disco...", end=" ")
        with open(self.filename, 'rb') as f:
            # Lê bitmaps
            f.seek(self.inode_bitmap_offset)
            inode_bits_raw = f.read(self.inode_capacity)
            f.seek(self.block_bitmap_offset)
            block_bits_raw = f.read(self.block_capacity)

            # Limpa estruturas
            self.all_blocks = [None] * self.block_capacity
            self.all_inodes = [None] * self.inode_capacity
            self.block_bitmap = OrderedDict()
            self.inode_bitmap = OrderedDict()

            # Carrega blocos
            f.seek(self.block_data_offset)
            for i in range(self.block_capacity):
                blk_bytes = f.read(self.block_size_b)
                if i < len(block_bits_raw) and block_bits_raw[i] == ord('1'):
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
            f.seek(self.inode_table_offset)
            temp_parent_map = {}
            for i in range(self.inode_capacity):
                inode_bytes = f.read(self.inode_size_b)
                if i < len(inode_bits_raw) and inode_bits_raw[i] == ord('1'):
                    inode = Inode.load_from_bytes(inode_bytes, disk_ref=self, is_load=True)
                    inode.id = i
                    self.all_inodes[i] = inode
                    self.inode_bitmap[inode] = 1
                    if hasattr(inode, '_temp_parent_id'):
                        pid = getattr(inode, '_temp_parent_id', None)
                        if pid is not None:
                            temp_parent_map[i] = pid

            # Resolve parents
            for idx, inode in enumerate(self.all_inodes):
                if inode is None: continue
                pid = temp_parent_map.get(idx)
                if pid is not None and 0 <= pid < self.inode_capacity:
                    parent = self.all_inodes[pid]
                    if parent and parent.type == 'd':
                        inode.parent_inode = parent
                        parent.add_child_inode(inode)
        print("OK")

    def debug_summary(self) -> str:
        return f"Disk: blocks={len(self.block_bitmap)}/{self.block_capacity}, inodes={len(self.inode_bitmap)}/{self.inode_capacity}"

# block.py

class Block:
    def __init__(self, disk_ref, is_load: bool = False):
        self.id: None
        self.content: bytes = b''
        self.disk_ref = disk_ref
        self.size_limit = self.disk_ref.block_size_b

        if not is_load:
            # add self to disk -> Disk.add_block retorna id
            self.disk_ref.add_block(self)

    def __str__(self) -> str:
        try:
            return self.content.decode('utf-8', errors='ignore')
        except Exception:
            return repr(self.content)

    # bytes interface
    def write_bytes(self, data: bytes):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("write_bytes espera bytes")
        if len(data) > self.get_free_space():
            raise Exception("Conteúdo maior que espaço livre no bloco")
        self.content += data

    def read_bytes(self) -> bytes:
        return self.content

    # text interface (util)
    def write(self, text: str):
        if not isinstance(text, str):
            raise TypeError("write espera str")
        self.write_bytes(text.encode('utf-8'))

    def read(self) -> str:
        return self.read_bytes().decode('utf-8', errors='ignore')

    def get_free_space(self) -> int:
        return self.size_limit - len(self.content)

    def can_fit(self, text: str) -> bool:
        return len(text.encode('utf-8')) <= self.get_free_space()

    def clear(self):
        self.content = b''

    def serialize(self) -> bytes:
        """Retorna bytes exatamente do tamanho do bloco (padding zeros)."""
        if not isinstance(self.content, (bytes, bytearray)):
            data = str(self.content).encode('utf-8')
        else:
            data = self.content
        if len(data) > self.size_limit:
            raise ValueError("Block content maior que block size")
        return data.ljust(self.size_limit, b'\x00')

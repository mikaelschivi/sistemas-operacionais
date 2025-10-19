class Block:
    def __init__(self, disk_ref):
        self.content = ''
        self.disk_ref = disk_ref
        self.size_limit = self.disk_ref.block_size_kb * 1024
        self.disk_ref.add_block(self) # add a si mesmo ao bitmap do disco

    def __str__(self) -> str:
        return self.content

    def is_full(self) -> bool:
        return len(self.content.encode('utf-8')) == self.size_limit
    
    def write(self, content_to_write: str):
        if self.is_full():
            raise Exception('Bloco está cheio')
        if not self.can_fit(content_to_write):
            raise Exception('Tamanho do conteúdo é maior que o limite do bloco')
        self.content += content_to_write
    
    def get_free_space(self) -> int:
        # size in bytes
        return self.size_limit - len(self.content.encode('utf-8'))

    def can_fit(self, content_to_fit: str) -> bool:
        return len(content_to_fit.encode('utf-8')) <= self.get_free_space()

    def clear(self):
        self.content = ''

    def serialize(self) -> str:
        # Serializa o conteúdo do bloco para uma string de tamanho fixo
        text = ''
        text += str(self.content)
        if not self.is_full():
            # Preenche com '0's o espaço restante
            text += '"' + '0' * (self.content.ljust(self.size_limit, '0'))
        return text
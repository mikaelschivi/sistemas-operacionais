import os
from disk import Disk
from file_system import FileSystem
from user import User

class OperatingSystem:
    def __init__(self, 
                 disk_filename: str, 
                 disk_total_size_mb: int, 
                 block_size_kb: int, 
                 inode_size_kb: int,
                 inode_name_max_len: int, 
                 inode_timestamp_len: int,
                 inode_size_field_len: int
                ):
        
        self.disk = Disk(
            os_ref =                self,
            max_size_mb =           disk_total_size_mb,
            block_size_kb =         block_size_kb,
            inode_size_kb =         inode_size_kb,
            disk_filename =         disk_filename,
            inode_name_max_len =    inode_name_max_len,
            inode_timestamp_len =   inode_timestamp_len,
            inode_size_field_len =  inode_size_field_len
        )
        
        self.users = []
        self.current_user = None

        if os.path.exists(disk_filename):
            print('Arquivo de disco encontrado. Carregando...')
            print('Carregando...')
            self.disk.load_from_disk()
            
        self.file_system = FileSystem(self.disk, self)

    def create_user(self, username: str, password = None):
        for user in self.users:
            if user.username == username:
                print("Usuário já existe.")
                return False
        self.users.append(User(username, password))
        print(f"Usuário '{username}' criado.")
        return True

    def login(self, username: str) -> bool:
        for user in self.users:
            if user.username == username:
                self.current_user = user
                print(f"Bem-vindo, {username}.")
                return True
        print("Usuário ou senha inválidos.")
        return False

    def parse_path(self, path: str) -> list[str]:
        if not path:
            return []
            
        if path.startswith('/'):
            # absoluto
            parts = ['/']
            parts.extend([p for p in path.split('/') if p])
            return parts
        else:
            # relativo
            return [p for p in path.split('/') if p]
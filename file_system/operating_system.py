import os
from disk import Disk
from file_system import FileSystem
from user import User

class OperatingSystem:
    def __init__(self):
        
        self.disk = Disk()
        # Usar um dicionário para usuários melhora a performance de busca
        self.users: dict[str, User] = {}
        self.current_user = None

        if os.path.exists(self.disk.filename):
            print('Arquivo de disco encontrado. Carregando...')
            self.disk.load_from_disk()
            
        # O FileSystem espera um objeto Disk, não o nome do arquivo.
        self.file_system = FileSystem(self.disk, self)

    def create_user(self, username: str, password = None):
        if username in self.users:
            print("Usuário já existe.")
            return False
        self.users[username] = User(username, password)
        print(f"Usuário '{username}' criado.")
        return True

    def login(self, username: str) -> bool:
        user = self.users.get(username)
        if user:
            self.current_user = user
            print(f"Bem-vindo, {username}.")
            return True
        else:
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
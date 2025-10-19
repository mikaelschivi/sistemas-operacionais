class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return self.__str__()
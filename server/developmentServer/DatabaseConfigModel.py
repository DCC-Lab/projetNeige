from dataclasses import dataclass


@dataclass
class DatabaseConfigModel:
    server_host: str
    server_port: int
    database: str
    user: str
    password: str

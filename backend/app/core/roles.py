from enum import Enum


class Role(str, Enum):
    GUEST = "guest"
    CLIENT = "client"
    ADMIN = "admin"

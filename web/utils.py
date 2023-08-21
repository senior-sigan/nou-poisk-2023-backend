from passlib.context import CryptContext


context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_pwd(password: str, hashed: str):
    return context.verify(password, hashed)


def hash_pwd(password: str):
    return context.hash(password)

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password) -> str:
    return password_hash.hash(password)


def verify_password(password, stored_hash) -> bool:
    return password_hash.verify(password, stored_hash)

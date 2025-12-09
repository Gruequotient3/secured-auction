import jwt
import bcrypt
import json
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes

# Internals
from config.config import (
    RSA_KEYS_PATH,
    ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


def rsa_encrypt(message, publicKey):
    m = bytes_to_long(message.encode("utf-8"))
    if m >= publicKey["n"]:
        return None
    c = pow(m, publicKey["e"], publicKey["n"])
    return c


def rsa_decrypt(cipher, privateKey):
    m = pow(cipher, privateKey["d"], privateKey["n"])
    return long_to_bytes(m).decode("utf-8")


def public_server_key():
    json_data = open(RSA_KEYS_PATH)
    keys = json.load(json_data)

    return {
        "e": int(keys["e"]),
        "n": int(keys["n"])
    }


def private_server_key():
    json_data = open(RSA_KEYS_PATH)
    keys = json.load(json_data)

    return {
        "d": int(keys["d"]),
        "n": int(keys["n"])
    }


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


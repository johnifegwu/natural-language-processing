from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os

# Function to derive key from password
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Function to encrypt the string
def encrypt_string(payload: str, password: str) -> str:
    salt = os.urandom(16)  # Generate a random salt
    key = derive_key(password, salt)  # Derive key using password and salt
    fernet = Fernet(key)
    encrypted = fernet.encrypt(payload.encode())  # Encrypt the payload
    return base64.urlsafe_b64encode(salt + encrypted).decode()  # Combine salt and encrypted data

# Function to decrypt the string
def decrypt_string(encrypted_payload: str, password: str) -> str:
    data = base64.urlsafe_b64decode(encrypted_payload.encode())
    salt, encrypted = data[:16], data[16:]  # Extract salt and encrypted data
    key = derive_key(password, salt)  # Derive key using password and extracted salt
    fernet = Fernet(key)
    return fernet.decrypt(encrypted).decode()  # Decrypt and return the payload

# Example usage:
if __name__ == "__main__":
    payload = input("Enter the string to encrypt: ")
    password = input("Enter the password: ")

    encrypted_payload = encrypt_string(payload, password)
    print(f"Encrypted: {encrypted_payload}")

    decrypted_payload = decrypt_string(encrypted_payload, password)
    print(f"Decrypted: {decrypted_payload}")

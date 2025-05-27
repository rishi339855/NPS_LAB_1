from cryptography.fernet import Fernet
import os

def generate_key():
    """Generate a new encryption key"""
    return Fernet.generate_key()

def encrypt_file(file_path):
    """
    Encrypts a file and saves the encrypted version
    Returns the path to the encrypted file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Generate key
    key = generate_key()
    
    # Save key
    key_path = os.path.join('key', f"{os.path.basename(file_path)}.key")
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    
    # Initialize Fernet with the key
    f = Fernet(key)
    
    # Read and encrypt file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    # Save encrypted file
    encrypted_path = os.path.join('encrypted', os.path.basename(file_path))
    with open(encrypted_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)
    
    return encrypted_path 
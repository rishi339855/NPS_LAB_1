from cryptography.fernet import Fernet
import os

def decrypt_file(encrypted_file_path):
    """
    Decrypts an encrypted file using its corresponding key
    Returns the path to the decrypted file
    """
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
    
    # Get the key file path
    key_path = os.path.join('key', f"{os.path.basename(encrypted_file_path)}.key")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Key file not found: {key_path}")
    
    # Read the key
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
    
    # Initialize Fernet with the key
    f = Fernet(key)
    
    # Read and decrypt file
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    
    decrypted_data = f.decrypt(encrypted_data)
    
    # Save decrypted file
    decrypted_path = os.path.join('restored_file', os.path.basename(encrypted_file_path))
    with open(decrypted_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)
    
    return decrypted_path 
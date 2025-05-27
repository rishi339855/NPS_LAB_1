import os
import glob

def restore_file(decrypted_file_path):
    """
    Restores a file from its decrypted state
    Returns the path to the restored file
    """
    if not os.path.exists(decrypted_file_path):
        raise FileNotFoundError(f"Decrypted file not found: {decrypted_file_path}")
    
    # Get all chunks for this file
    base_name = os.path.basename(decrypted_file_path)
    chunk_pattern = os.path.join('raw_data', f'chunk_*.bin')
    chunk_files = sorted(glob.glob(chunk_pattern), 
                        key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))
    
    if not chunk_files:
        raise FileNotFoundError("No chunk files found")
    
    # Combine chunks
    restored_path = os.path.join('restored_file', base_name)
    with open(restored_path, 'wb') as restored_file:
        for chunk_file in chunk_files:
            with open(chunk_file, 'rb') as chunk:
                restored_file.write(chunk.read())
    
    # Clean up chunk files
    for chunk_file in chunk_files:
        os.remove(chunk_file)
    
    return restored_path 
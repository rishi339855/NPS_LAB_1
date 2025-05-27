import os
import math

def divide_file(file_path, chunk_size=1024*1024):  # 1MB chunks by default
    """
    Divides a file into chunks and saves them in the raw_data directory
    Returns the list of chunk file paths
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    num_chunks = math.ceil(file_size / chunk_size)
    chunk_files = []
    
    with open(file_path, 'rb') as f:
        for i in range(num_chunks):
            chunk_data = f.read(chunk_size)
            chunk_path = os.path.join('raw_data', f'chunk_{i}.bin')
            
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunk_files.append(chunk_path)
    
    return chunk_files 
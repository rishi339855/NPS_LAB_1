from flask import Flask, request, jsonify, send_file, render_template
import os
import base64
import requests
import socket
from werkzeug.utils import secure_filename
from divider import divide_file
from encrypter import encrypt_file
from decrypter import decrypt_file
from restore import restore_file
import datetime
import shutil

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
KEY_FOLDER = 'key'
FILES_FOLDER = 'files'
ENCRYPTED_FOLDER = 'encrypted'
RESTORED_FOLDER = 'restored_file'
RAW_DATA_FOLDER = 'raw_data'
RECEIVED_FILES_FOLDER = 'received_files'
METADATA_FILE = 'file_metadata.json'
ALLOWED_EXTENSIONS = {'pem', 'txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, KEY_FOLDER, FILES_FOLDER, ENCRYPTED_FOLDER, 
               RESTORED_FOLDER, RAW_DATA_FOLDER, RECEIVED_FILES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def cleanup_files(filepath, encrypted_file=None, key_path=None):
    """Clean up temporary files"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if encrypted_file and os.path.exists(encrypted_file):
            os.remove(encrypted_file)
        if key_path and os.path.exists(key_path):
            os.remove(key_path)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_metadata():
    """Load file metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Save file metadata to JSON file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-local-ip')
def local_ip():
    return jsonify({'ip': get_local_ip()})

@app.route('/test-connection', methods=['POST'])
def test_connection():
    peer_ip = request.form.get('peer_ip')
    if not peer_ip:
        return jsonify({'error': 'No peer IP provided'}), 400
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(f'http://{peer_ip}:8003/test-connection', timeout=5)
        if response.status_code == 200:
            return jsonify({'message': 'Successfully connected to peer'})
        else:
            return jsonify({'error': f'Peer responded with status code: {response.status_code}'}), 400
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Could not establish connection to peer. Make sure the peer is running and the IP address is correct.'}), 400
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Connection timed out. The peer might be offline or unreachable.'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 400

@app.route('/share-file', methods=['POST'])
def share_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    peer_ip = request.form.get('peer_ip')
    
    if not file or not peer_ip:
        return jsonify({'error': 'Missing file or peer IP'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    encrypted_file = None
    key_path = None
    
    try:
        # Save the uploaded file
        file.save(filepath)
        
        # Divide and encrypt the file
        divide_file(filepath)
        encrypted_file = encrypt_file(filepath)
        
        # Read encrypted file and key
        with open(encrypted_file, 'rb') as f:
            encrypted_data = base64.b64encode(f.read()).decode()
        
        key_path = os.path.join(KEY_FOLDER, f"{filename}.key")
        with open(key_path, 'rb') as f:
            key_data = base64.b64encode(f.read()).decode()
        
        # Send to peer
        response = requests.post(
            f'http://{peer_ip}:8003/receive-file',
            json={
                'filename': filename,
                'encrypted_data': encrypted_data,
                'key_data': key_data
            },
            timeout=30  # Increased timeout for larger files
        )
        
        if response.status_code == 200:
            return jsonify({'message': 'File shared successfully'})
        else:
            return jsonify({'error': 'Failed to share file'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup temporary files
        cleanup_files(filepath, encrypted_file, key_path)

@app.route('/receive-file', methods=['POST'])
def receive_file():
    data = request.json
    if not all(k in data for k in ['filename', 'encrypted_data', 'key_data']):
        return jsonify({'error': 'Missing required data'}), 400
    
    filename = secure_filename(data['filename'])
    encrypted_data = base64.b64decode(data['encrypted_data'])
    key_data = base64.b64decode(data['key_data'])
    timestamp = data.get('timestamp', str(datetime.datetime.now()))
    
    encrypted_path = os.path.join(ENCRYPTED_FOLDER, filename)
    key_path = os.path.join(KEY_FOLDER, f"{filename}.key")
    decrypted_file = None
    
    try:
        # Save encrypted file and key
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        with open(key_path, 'wb') as f:
            f.write(key_data)
        
        # Decrypt and restore file
        decrypted_file = decrypt_file(encrypted_path)
        restored_file = restore_file(decrypted_file)
        
        # Move to received files
        final_path = os.path.join(RECEIVED_FILES_FOLDER, filename)
        shutil.move(restored_file, final_path)
        
        return jsonify({'message': 'File received and decrypted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup temporary files
        cleanup_files(encrypted_path, decrypted_file, key_path)

@app.route('/received-files')
def list_received_files():
    files = os.listdir(RECEIVED_FILES_FOLDER)
    metadata = load_metadata()
    file_info = []
    
    for file in files:
        info = metadata.get(file, {})
        file_info.append({
            'name': file,
            'received_at': info.get('received_at', 'Unknown'),
            'size': info.get('size', 0)
        })
    
    return render_template('files.html', files=file_info)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(RECEIVED_FILES_FOLDER, secure_filename(filename))
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True) 
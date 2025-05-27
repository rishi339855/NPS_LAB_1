# Secure File Sharing Application

A peer-to-peer file sharing application with encryption capabilities built using Flask.

## Features

- Secure file sharing between peers
- File encryption before transmission
- Support for various file types (.pem, .txt, .pdf, .doc, .docx, .jpg, .jpeg, .png)
- Simple and intuitive web interface
- Real-time connection status updates

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd secure-file-sharing
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:8000
```

3. To share files between peers:
   - Start the application on both computers
   - Use the "Connect" page to establish a connection between peers
   - Use the main page to select and share files
   - Received files can be downloaded from the "Received Files" page

## Security Features

- Files are encrypted using Fernet symmetric encryption
- Files are divided into chunks for efficient transfer
- Keys are securely transmitted between peers
- All temporary files are automatically cleaned up

## Directory Structure

- `uploads/`: Temporary storage for uploaded files
- `key/`: Storage for encryption keys
- `files/`: File processing directory
- `encrypted/`: Storage for encrypted files
- `restored_file/`: Storage for decrypted files
- `raw_data/`: Intermediate data storage
- `received_files/`: Storage for downloaded files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

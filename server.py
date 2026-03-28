import os
from datetime import datetime
from flask import Flask, request, jsonify

# Try importing optional dependencies gracefully
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Optional dependency not installed

# Import PlumbingAgent for automated audit processing
try:
    from plumbing.plumbing_agent import PlumbingAgent
    PLUMBING_AGENT = None
except ImportError:
    print("Warning: PlumbingAgent not found. Automated audit disabled.")
    PLUMBING_AGENT = None

app = Flask(__name__)

# Use relative path instead of ~/Desktop for better portability
UPLOAD_DIR = 'uploads'

def create_upload_dir():
    """Create the upload directory if it doesn't exist"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR

@app.route('/upload', methods=['POST'])
def upload_file():
    # Create directory first
    create_upload_dir()
    
    # Check if file is in request
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("Empty filename")
        return jsonify({"error": "No selected file"}), 400
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save the file
    file.save(filepath)
    
    print(f"File saved to: {filepath}")
    
    # Print massive ASCII art DATA SECURED message
    ascii_art = """
   ██████╗ ██╗     ██╗██║  ██╗███████╗████████╗    ███████╗███████╗██████╗ 
  ██╔════╝ ██║     ██║██║  ██║██╔════╝╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗
  ██║  ███╗██║     ██║██║ ██╔╝█████╗      ██║       ███████╗█████╗  ██████╔╝
  ██║   ██║██║     ██║██║ ██╔╝██╔══╝      ██║       ╚════██║██╔══╝  ██╔══██╗
  ╚██████╔╝██║     ██║██║ ██╔╝███████╗    ██║       ███████║███████╗██║  ██║
   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝       ╚══════╝╚══════╝╚═╝  ╚═
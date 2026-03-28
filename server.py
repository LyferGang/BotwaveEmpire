import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_DIR = os.path.expanduser("~/Desktop/Plumbing_Audit")

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
   ██████╗ ██╗     ██╗██╗  ██╗███████╗████████╗    ███████╗███████╗██████╗ 
  ██╔════╝ ██║     ██║██║  ██║██╔════╝╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗
  ██║  ███╗██║     ██║██║ ██╔╝█████╗      ██║       ███████╗█████╗  ██████╔╝
  ██║   ██║██║     ██║██║ ██╔╝██╔══╝      ██║       ╚════██║██╔══╝  ██╔══██╗
  ╚██████╔╝██║     ██║██║ ██╔╝███████╗    ██║       ███████║███████╗██║  ██║
   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝       ╚══════╝╚══════╝╚═╝  ╚═╝

         ██████╗ ███████╗███████╗███████╗
        ██╔════╝ ██╔════╝██╔════╝██╔════╝
        ██║  ███╗█████╗  ███████╗███████╗
        ██║   ██║██╔══╝  ╚════██║██╔════╝
        ╚██████╔╝███████╗███████║███████╗
         ╚═════╝ ╚══════╝╚══════╝╚══════╝

              DATA SECURED
    """
    
    print(ascii_art)
    
    return jsonify({
        "status": "success",
        "filename": safe_filename,
        "path": filepath,
        "size": file.content_length or 0
    }), 200

if __name__ == '__main__':
    create_upload_dir()
    print("Flask server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

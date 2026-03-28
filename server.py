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
    
    # Check if it's a zip file and extract for auto-audit
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall('./projects/incoming/')
        
        # Initialize agent for auto-audit
        from plumbing.plumbing_agent import PlumbingAgent
        agent = PlumbingAgent()
        
        # Find all .txt files in extracted directory
        txt_files = glob.glob('./projects/incoming/*.txt')
        
        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                content = f.read().strip()
            
            result = agent.handle_message(phone="system", message=content)
            
            print(f"\n=== Auto-Audit Result ===")
            print(f"File: {txt_file}")
            print(f"Issue Type: {result.get('issue_type', 'N/A')}")
            print(f"Price Range: ${result.get('price_low', 0)} - ${result.get('price_high', 0)}")

    # Print massive ASCII art DATA SECURED message
    ascii_art = """
   ██████╗ ██╗     ██╗██║  ██╗███████╗████████╗    ███████╗███████╗██████╗ 
  ██╔════╝ ██║     ██║██║  ██║██╔════╝╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗
  ██║  ███╗██║     ██║██║ ██╔╝█████╗      ██║       ███████╗█████╗  ██████╔╝
  ██║   ██║██║     ██║██║ ██╔╝██╔══╝      ██║       ╚════██║██╔══╝  ██╔══██╗
  ╚██████╔╝██║     ██║██║ ██╔╝███████╗    ██║       ███████║███████╗██║  ██║
   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝       ╚══════╝╚══════╝╚═╝  ╚═"""

print(ascii_art)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='100.81.36.31', port=5000, debug=True)

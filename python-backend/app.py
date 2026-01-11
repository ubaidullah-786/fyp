from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import zipfile
import logging
import os
from smell_detector import traverse_zip

# Configure logging for production
FLASK_ENV = os.getenv("FLASK_ENV", "development")
log_level = logging.WARNING if FLASK_ENV == "production" else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/upload", methods=["POST"])
def upload_project():
    logger.debug("Received upload request")
    
    if "file" not in request.files:
        logger.error("No file uploaded in request")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename:
        logger.error("Empty filename received")
        return jsonify({"error": "Invalid filename"}), 400
        
    if not file.filename.endswith(".zip"):
        logger.error("Uploaded file is not a ZIP file: %s", file.filename)
        return jsonify({"error": "File must be a ZIP file"}), 400

    try:
        # Read ZIP file in memory
        logger.debug("Reading ZIP file: %s", file.filename)
        zip_data = io.BytesIO(file.read())
        
        # Verify ZIP file integrity
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            if zip_ref.testzip() is not None:
                logger.error("ZIP file is corrupted")
                return jsonify({"error": "ZIP file is corrupted"}), 400
            logger.debug("ZIP file is valid, starting smell detection")
        
        # Analyze smells in the ZIP file
        detected_smells = traverse_zip(zip_data)
        
        # Format results to match requested structure
        results = []
        for filepath, smells in detected_smells.items():
            filename = filepath.split("/")[-1]
            for smell in smells:
                results.append({
                    "fileName": filename,
                    "filePath": filepath,
                    "startLine": smell["startline"],
                    "endLine": smell["endline"],
                    "smellType": smell["codeSmellType"],
                    "code": smell["code"],
                    "category": smell["category"],
                    "weight": smell["weight"]
                })
        
        logger.debug("Smell detection completed, returning %d smells", len(results))
        return jsonify({"total_smells": len(results), "codeSmells": results}), 200
    
    except zipfile.BadZipFile as e:
        logger.error("Invalid ZIP file: %s", str(e))
        return jsonify({"error": "Invalid or corrupted ZIP file"}), 400
    except Exception as e:
        logger.error("Error during smell detection: %s", str(e), exc_info=True)
        if FLASK_ENV == "production":
            return jsonify({"error": "Internal server error"}), 500
        else:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error("Server error: %s", str(error))
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    debug_mode = FLASK_ENV != "production"
    logger.info(f"Starting Flask application (debug={debug_mode})")
    app.run(debug=debug_mode, port=5000, host="127.0.0.1")
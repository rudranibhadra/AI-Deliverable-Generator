from azure.storage.blob import BlobServiceClient
from flask import Flask, request, jsonify
from flask_cors import CORS
from generator import DeliverableGenerator
from prompt import build_detailed_prompt
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
import requests
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv
load_dotenv()


# Initialize the generator
generator = DeliverableGenerator()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpeg", "jpg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


# Azure Blob Storage configuration (set your connection string and container name)
AZURE_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING", "<your-connection-string>")
AZURE_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME", "<your-container-name>")

def upload_to_blob_storage(file_path, blob_name=None):
    """Uploads a file to Azure Blob Storage and returns the blob URL."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    if not blob_name:
        blob_name = os.path.basename(file_path)
    with open(file_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)
    blob_url = f"{container_client.url}/{blob_name}"
    return blob_url

@app.route("/extract", methods=["POST"])
def extract():
    """Extract text from uploaded file (PDF, DOCX, JPEG, PNG)."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in request"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)
        file.save(file_path)
        ext = filename.rsplit(".", 1)[1].lower()
        try:
            if ext == "pdf":
                text = extract_text_from_pdf(file_path)
            elif ext == "docx":
                text = extract_text_from_docx(file_path)
            elif ext in ("jpeg", "jpg", "png"):
                text = extract_text_from_image(file_path)
            else:
                return jsonify({"success": False, "error": "Unsupported file type"}), 400
            # Upload file to Azure Blob Storage
            blob_url = upload_to_blob_storage(file_path, filename)
        except Exception as e:
            return jsonify({"success": False, "error": f"Extraction failed: {e}"}), 500

    return jsonify({"success": True, "text": text, "blob_url": blob_url}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/deliverable", methods=["GET"])
def deliverable():
    """
    Returns a sample deliverable JSON based on the 'type' query parameter.
    Supported types: summary, roadmap, architecture, data-schema
    """
    deliverable_type = request.args.get("type", "").strip().lower()
    business_problem = request.args.get("business_problem", "")
    tech_stack = request.args.get("tech_stack", "")
    time_constraint = request.args.get("time_constraint", "")
    resource_constraints = request.args.get("resource_constraints", "")

    PROMPT_FILES = {
        "summary": "prompts/summary_prompt.txt",
        "roadmap": "prompts/roadmap_prompt.txt",
        "architecture": "prompts/architecture_prompt.txt",
        "data-schema": "prompts/data_schema_prompt.txt"
    }

    if deliverable_type not in PROMPT_FILES:
        return jsonify({"error": "Invalid or missing 'type' parameter"}), 400

    # Load the prompt template
    prompt_path = PROMPT_FILES[deliverable_type]
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Fill in the template with user/context values
    prompt = prompt_template.format(
        business_problem=business_problem,
        tech_stack=tech_stack,
        time_constraint=time_constraint,
        resource_constraints=resource_constraints
    )

    # Generate text deliverable
    content = generator.generate_deliverable(prompt)

    # Generate image (using DALL·E 3)
    image_prompt = (
    f"Draw a clear and minimal architecture diagram for the following business problem: {business_problem}. "
    f"Show only the main components: {tech_stack}. Use simple shapes, clear labels, and avoid extra details or decorations."
)
    image_url = generator.generate_image(image_prompt)

    return jsonify({
        "success": True,
        "content": content,
        "image_url": image_url
    }), 200
    
if __name__ == "__main__":
    app.run(debug=False, port=5000)

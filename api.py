from flask import Flask, request, jsonify
from flask_cors import CORS
from generator import DeliverableGenerator
import logging

app = Flask(__name__)
CORS(app)

# Initialize the generator
generator = DeliverableGenerator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/generate", methods=["POST"])
def generate():
    """Generate AI content from user request.
    
    Expected JSON payload:
    {
        "prompt": "Your request here"
    }
    
    Returns:
    {
        "success": true/false,
        "content": "Generated content...",
        "error": "Error message if failed"
    }
    """
    try:
        data = request.get_json()
        
        if not data or "prompt" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'prompt' field in request"
            }), 400
        
        user_prompt = data.get("prompt", "").strip()
        
        if not user_prompt:
            return jsonify({
                "success": False,
                "error": "Prompt cannot be empty"
            }), 400
        
        # Generate content
        content = generator.generate_deliverable(user_prompt)
        
        return jsonify({
            "success": True,
            "content": content
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

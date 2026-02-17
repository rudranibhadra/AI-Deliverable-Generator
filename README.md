# AI Deliverable Generator

## Overview

This project provides a Flask-based API for generating business deliverables (such as summaries, roadmaps, architecture diagrams, data schemas, and business proposals) using Azure OpenAI models (GPT-4 for text, DALL·E 3 for images). The backend supports file extraction, prompt templating, and dynamic content generation. The frontend can be built with React or any other framework.

---

## Key Features

- **/deliverable** endpoint: Generates JSON deliverables and (optionally) diagrams based on user input and deliverable type.
- **Prompt templates**: Each deliverable type uses a dedicated prompt template for consistent, high-quality outputs.
- **Image generation**: Integrates with Azure OpenAI DALL·E 3 to generate architecture diagrams or other visuals.
- **File extraction**: Supports extracting text from uploaded documents and images (if enabled).
- **Centralized configuration**: All environment variables and Azure resource info are managed in `config.py` and `.env`.

---

### .env file parameters:

AZURE_OPENAI_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_BLOB_CONNECTION_STRING=
AZURE_BLOB_CONTAINER_NAME=
AZURE_DALL_E_DEPLOYMENT=dall-e-3

---

## How It Works

1. **Configuration Loading**
   - On startup, `config.py` loads environment variables from `.env` (using `python-dotenv`).
   - Azure OpenAI client and deployment names are initialized and imported into `api.py`.

2. **API Initialization**
   - `api.py` sets up the Flask app and imports the `DeliverableGenerator` class from `generator.py`.
   - The generator is instantiated with the Azure OpenAI client and deployment names.

3. **Handling a Request**
   - A user (or frontend) sends a request to the `/deliverable` endpoint with query parameters specifying:
     - `type` (e.g., summary, roadmap, architecture, data-schema, business-proposal)
     - Context fields (e.g., `business_problem`, `tech_stack`, etc.)

4. **Prompt Construction**
   - The endpoint selects the appropriate prompt template file from the `prompts/` directory based on the `type` parameter.
   - The template is loaded and placeholders are filled with the provided context.

5. **Text Generation**
   - The filled prompt is passed to `DeliverableGenerator.generate_text()`, which calls the Azure OpenAI GPT-4 deployment via the SDK.
   - The model returns the generated JSON deliverable.

6. **Image Generation (if applicable)**
   - For deliverable types that require a diagram (e.g., architecture), an image prompt is constructed using the business problem and tech stack.
   - This prompt is passed to `DeliverableGenerator.generate_image()`, which calls the DALL·E 3 deployment.
   - The model returns a URL to the generated image.

7. **Response Construction**
   - The API combines the generated text (JSON) and image URL (if any) into a single JSON response.
   - The response is returned to the user or frontend.

8. **Frontend/Tester**
   - The frontend or tester receives the JSON, displays the deliverable, and (if present) renders the image from the URL.

**Summary Diagram:**

```
User/Frontend
     │
     ▼
[Flask API: /deliverable]
     │
     ├─► Load prompt template & fill context
     │
     ├─► Generate text with GPT-4 (DeliverableGenerator.generate_text)
     │
     ├─► (Optional) Generate image with DALL·E 3 (DeliverableGenerator.generate_image)
     │
     ▼
Return JSON response (deliverable + image_url)
```

## Example Usage

**Request:**
```bash
curl -X GET "http://localhost:5000/deliverable?type=architecture&business_problem=E-commerce%20platform&tech_stack=Azure%20Web%20Apps%20and%20MongoDB"
```

**Response:**
```json
{
  "success": true,
  "content": {
    "summary": "...",
    "tech": [...],
    "api design": [...]
  },
  "image_url": "https://..."
}
```

---

## Setup & Testing

1. **Clone the repo and install dependencies**
2. **Set up your `.env` file** with Azure OpenAI credentials and deployment names.
3. **Run the Flask app**
   ```bash
   python api.py
   ```
4. **Test endpoints** using curl, Postman, or your frontend.

---

## Notes

- Make sure your Azure OpenAI deployments (GPT-4 and DALL·E 3) are active and the deployment names match your `.env` and `config.py`.
- If image generation fails, check API version, deployment name, and Azure resource status.
- Prompt templates must use double curly braces (`{{ }}`) for JSON blocks and single braces for placeholders.

---

## File Structure

```
.
├── api.py
├── config.py
├── generator.py
├── prompts/
│   ├── summary_prompt.txt
│   ├── roadmap_prompt.txt
│   ├── architecture_prompt.txt
│   ├── data_schema_prompt.txt
│   └── business_proposal_prompt.txt
├── .env
└── ...
```

---

## Contact

For issues or questions, contact the project maintainer or open an issue in the repository.
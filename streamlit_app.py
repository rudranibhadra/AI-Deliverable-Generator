import pytesseract
import streamlit as st
from azure.storage.blob import BlobServiceClient
import tempfile
import os
import pandas as pd
import json
from fpdf import FPDF
import requests
from PIL import Image
import io

from PyPDF2 import PdfReader
from docx import Document
from config import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
from generator import DeliverableGenerator
from features import display_deliverable, export_to_pdf, format_content_as_text, render_validation_results, validate_inputs,validate_inputs_with_model,render_validation_results,generate_slide_deck_from_text,render_slide_deck,export_to_pdf

# Allowed extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpeg", "jpg", "png"}

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def upload_to_blob_storage(file_path, blob_name=None):
    print('file_path:', file_path)
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    if not blob_name:
        blob_name = os.path.basename(file_path)
    with open(file_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)
    blob_url = f"{container_client.url}/{blob_name}"
    return blob_url



st.title("Deliverable Generator (Streamlit)")

uploaded_file = st.file_uploader("Upload a file (optional)", type=list(ALLOWED_EXTENSIONS))

deliverable_type = st.selectbox("Type", ["summary", "roadmap", "architecture", "data-schema"])
business_problem = st.text_input("Business Problem Description")
tech_stack = st.text_input("Tech Stack (comma separated)")
time_constraint = st.text_input("Time Constraint")
resource_constraints = st.text_input("Resource Constraints")

prompt_files = {
    "summary": "prompts/summary_prompt.txt",
    "roadmap": "prompts/roadmap_prompt.txt",
    "architecture": "prompts/architecture_prompt.txt",
    "data-schema": "prompts/data_schema_prompt.txt"
}
prompt_path = prompt_files.get(deliverable_type)

extracted_text = ""
# if uploaded_file is not None:
#     filename = uploaded_file.name
#     ext = filename.rsplit(".", 1)[1].lower()
#     with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
#         file_bytes = uploaded_file.read()
#         tmp.write(file_bytes)
#         tmp.flush()  # Ensure all data is written
#         tmp_path = tmp.name

#     if os.path.getsize(tmp_path) == 0:
#         st.error("Uploaded file is empty.")
#         os.unlink(tmp_path)
#         st.stop()

#     try:
#         if ext == "pdf":
#             with open(tmp_path, "rb") as f:
#                 extracted_text = extract_text_from_pdf(f)
#         elif ext == "docx":
#             with open(tmp_path, "rb") as f:
#                 extracted_text = extract_text_from_docx(f)
#         elif ext in ("jpeg", "jpg", "png"):
#             with open(tmp_path, "rb") as f:
#                 extracted_text = extract_text_from_image(f)
#         else:
#             st.error("Unsupported file type.")
#             # os.unlink(tmp_path)
#             st.stop()

#         # Upload after extraction for all file types
#         blob_url = upload_to_blob_storage(tmp_path, filename)
#         st.success(f"File uploaded to blob: {blob_url}")
#         st.write("Extracted Text:")
#         st.write(extracted_text)
    # except Exception as e:
        # st.error(f"Extraction or upload failed: {e}")
    # finally:
        # os.unlink(tmp_path)

# Always show prompt preview with current values
if prompt_path and os.path.exists(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_message = f.read()
#     prompt = prompt_template.format(
#         business_problem=business_problem,
#         extracted_text=extracted_text,
#         tech_stack=tech_stack,
#         time_constraint=time_constraint,
#         resource_constraints=resource_constraints
#     )
#     st.write("Prompt Preview:")
#     st.code(prompt)
# else:
#     st.warning("Prompt template not found.")
if st.button("Generate Deliverable"):

    with st.spinner("🔍 Validating inputs..."):
        validation = validate_inputs_with_model(
            deliverable_type,
            business_problem,
            tech_stack,
            time_constraint,
            resource_constraints
        )

    st.write("Validation result:", validation)  # Debugging output
    st.subheader("📋 Validation Results")
    render_validation_results(validation)

    if not validation.get("is_valid", False):
        st.error("Validation failed. Fix the issues above to continue.")
        st.stop()


    # if not validation.get("is_valid", False):
    #     st.error("Fix the following errors:")
    #     for e in validation.get("errors", []):
    #         st.markdown(f"- {e}")
    #     if validation.get("warnings"):
    #         st.warning("Warnings:")
    #         for w in validation["warnings"]:
    #             st.markdown(f"- {w}")
    #     st.stop()

    # if validation.get("warnings"):
    #     st.warning("Warnings:")
    #     for w in validation["warnings"]:
    #         st.markdown(f"- {w}")


    # validation = validate_inputs(
    #     deliverable_type,
    #     business_problem,
    #     tech_stack,
    #     time_constraint,
    #     resource_constraints
    # )
    # print("Validation result:", validation)
    # if not validation["is_valid"]:
    #     st.error("Please fix the following errors before generating:")
    #     for e in validation["errors"]:
    #         st.markdown(f"- {e}")

    #     if validation["warnings"]:
    #         st.warning("Warnings:")
    #         for w in validation["warnings"]:
    #             st.markdown(f"- {w}")
    #     st.stop()

    # if validation["warnings"]:
    #     st.warning("Warnings:")
    #     for w in validation["warnings"]:
    #         st.markdown(f"- {w}")

    blob_url = None

    if uploaded_file is not None:
        filename = uploaded_file.name
        ext = filename.rsplit(".", 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(uploaded_file.read())
            tmp.flush()  # Ensure all data is written
            tmp_path = tmp.name

        try:
            if ext == "pdf":
                with open(tmp_path, "rb") as f:
                    extracted_text = extract_text_from_pdf(f)
            elif ext == "docx":
                with open(tmp_path, "rb") as f:
                    extracted_text = extract_text_from_docx(f)
            elif ext in ("jpeg", "jpg", "png"):
                with open(tmp_path, "rb") as f:
                    extracted_text = extract_text_from_image(f)
            else:
                st.error("Unsupported file type.")
                os.unlink(tmp_path)
                st.stop()

            # Upload after extraction for all file types
            blob_url = upload_to_blob_storage(tmp_path, filename)
            st.success(f"File uploaded to blob: {blob_url}")
            # st.write("Extracted Text:")
            # st.write(extracted_text)
        except Exception as e:
            st.error(f"Extraction or upload failed: {e}")
        finally:
            os.unlink(tmp_path)
    else:
        st.info("No file uploaded. Using only the business problem description.")

    # final_prompt = prompt_template.format(
    #     business_problem=business_problem,
    #     extracted_text=extracted_text,
    #     tech_stack=tech_stack,
    #     time_constraint=time_constraint,
    #     resource_constraints=resource_constraints
    # )

    user_message = f"""
    Business Problem: {business_problem}
    Extracted Text: {extracted_text}
    Tech Stack: {tech_stack}
    Time Constraint: {time_constraint}
    Resource Constraints: {resource_constraints}
    """


    with st.spinner("📝 Generating deliverable and diagram..."):
        generator = DeliverableGenerator(system_message=system_message)
        content = generator.generate_deliverable(user_message)
        image_prompt = (
            f"Draw a clear and minimal architecture diagram for the following business problem: {business_problem}. "
            f"Extracted file text: {extracted_text}. "
            f"Show only the main components: {tech_stack}. "
            "Use simple shapes and clear labels. "
            "Do NOT use any random or made-up words. "
            "ONLY use labels that are present in the tech stack or extracted text. "
            "If no tech stack is provided, use only keywords from the business problem and extracted text. "
            "If you cannot label a component with an allowed word, leave it unlabeled. "
            "Do not use any other text or letters in the diagram."
        )
        image_url = generator.generate_image(image_prompt)

    st.subheader("Generated Deliverable")
    display_deliverable(content)

    st.subheader("Generated Architecture Diagram")
    if image_url:
        st.image(image_url)
    else:
        st.info("No image was generated.")

    st.markdown("---")
    st.subheader("🎯 Slide Deck Structure")
    with st.spinner("📊 Generating slide deck..."):
        content_text = format_content_as_text(content)
        slides_data = generate_slide_deck_from_text(content_text, generator)
    render_slide_deck(slides_data)

    # st.write("Content for PDF:", content)
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:
            pass

    if content:
        pdf_bytes = export_to_pdf(content, image_url)
        st.download_button(
            label="Download as PDF",
            data=pdf_bytes,
            file_name="deliverable.pdf",
            mime="application/pdf"
        )

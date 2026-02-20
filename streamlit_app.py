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

def export_to_pdf(content, image_url=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def add_section(title, text):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=1)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, str(text))
        pdf.ln(5)

    # Loop through all top-level keys
    if isinstance(content, dict):
        for key, value in content.items():
            # Skip the image key if present
            if key in ["image_url", "diagram", "image"]:
                continue
            # For lists (like functional-requirements), format nicely
            if isinstance(value, list):
                section_text = ""
                for idx, item in enumerate(value, 1):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            section_text += f"{k.capitalize()}: {v}\n"
                        section_text += "\n"
                    else:
                        section_text += f"{idx}. {item}\n"
                add_section(key.replace("-", " ").title(), section_text)
            else:
                add_section(key.replace("-", " ").title(), value)

    # Add the image if present
    if image_url:
        try:
            response = requests.get(image_url)
            img = Image.open(io.BytesIO(response.content))
            img_path = "temp_img.png"
            img.save(img_path)
            pdf.image(img_path, w=pdf.w - 20)
        except Exception as e:
            pdf.cell(0, 10, f"Could not load image: {e}", ln=1)

    return pdf.output(dest="S").encode("latin-1")

def display_deliverable(content):
    import pandas as pd
    import streamlit as st
    import json

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:
            st.write(content)
            return

    if not isinstance(content, dict):
        st.write(content)
        return

    # Executive summary and problem definition
    if "executive-summary" in content:
        st.markdown(f"### Executive Summary\n{content.get('executive-summary', '')}")
    if "problem-definition" in content:
        st.markdown(f"### Problem Definition\n{content.get('problem-definition', '')}")

    # Functional requirements
    func_reqs = content.get("functional-requirements")
    if isinstance(func_reqs, list) and func_reqs:
        st.markdown("### Functional Requirements")
        for idx, req in enumerate(func_reqs, 1):
            if isinstance(req, dict):
                st.markdown(f"**{idx}. User Story:** {req.get('user-story', '')}")
                st.markdown(f"- **Description:** {req.get('description', '')}")
                st.markdown(f"- **Acceptance Criteria:** {req.get('acceptance-criteria', '')}")
            else:
                st.markdown(f"- {req}")
            st.markdown("---")

    # Roadmap-specific keys
    if "summary" in content:
        st.markdown(f"### Summary\n{content.get('summary', '')}")
    if "dependencies" in content:
        st.markdown("### Dependencies")
        for dep in content["dependencies"]:
            if isinstance(dep, dict):
                st.markdown(f"- {dep.get('dependency', str(dep))}")
            else:
                st.markdown(f"- {dep}")
    if "risks-mitigation" in content:
        st.markdown("### Risks and Mitigation")
        for rm in content["risks-mitigation"]:
            if isinstance(rm, dict):
                st.markdown(f"**Risk:** {rm.get('risk', '')}")
                st.markdown(f"**Mitigation:** {rm.get('mitigation', '')}")
            else:
                st.markdown(f"- {rm}")
            st.markdown("---")

    # Data schema-specific keys
    data_schema = content.get("data-schema")
    if isinstance(data_schema, list) and data_schema:
        st.markdown("### Data Schema")
        for table in data_schema:
            if isinstance(table, dict):
                st.markdown(f"**Database:** {table.get('db-name', '')}")
                st.markdown(f"**Table:** {table.get('table-name', '')}")
                st.markdown(f"**Description:** {table.get('table-description', '')}")
                columns = table.get("columns", [])
                if columns:
                    # Ensure columns is a list of dicts
                    columns = [col if isinstance(col, dict) else {"col": str(col)} for col in columns]
                    df = pd.DataFrame(columns)
                    st.markdown("**Columns:**")
                    st.table(df)
            else:
                st.markdown(f"- {table}")
            st.markdown("---")

    # Architecture-specific keys
    tech = content.get("tech")
    if isinstance(tech, list) and tech:
        st.markdown("### Technology Stack")
        # Ensure tech is a list of dicts
        tech = [t if isinstance(t, dict) else {"tech": str(t)} for t in tech]
        df = pd.DataFrame(tech)
        st.table(df)

    api_design = content.get("api design")
    if isinstance(api_design, list) and api_design:
        st.markdown("### API Design")
        # Ensure api_design is a list of dicts
        api_design = [api if isinstance(api, dict) else {"api": str(api)} for api in api_design]
        df = pd.DataFrame(api_design)
        st.table(df)

    # Fallback: show as JSON if nothing else matches
    if not any(k in content for k in [
        "executive-summary", "problem-definition", "functional-requirements",
        "summary", "dependencies", "risks-mitigation", "data-schema", "tech", "api design"
    ]):
        st.json(content)

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


    with st.spinner("Generating deliverable and diagram..."):
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

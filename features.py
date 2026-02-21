import tempfile
import os
import pandas as pd
import json
from fpdf import FPDF
import requests
from PIL import Image
import io


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
import tempfile
import os
import pandas as pd
import json
from fpdf import FPDF
import requests
from PIL import Image
import io
import re
from generator import DeliverableGenerator
import generator
import streamlit as st


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

def export_to_pdf(content, image_url=None, slides_data=None):
    """Export deliverable to PDF including slides"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "AI-Generated Deliverable", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # Clean text to remove unicode characters that latin-1 can't handle
    def clean_text(text):
        """Replace unicode characters with ASCII equivalents"""
        replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Ellipsis
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Remove any remaining non-latin-1 characters
        return text.encode('latin-1', errors='ignore').decode('latin-1')
    
    # Deliverable content
    if isinstance(content, dict):
        for key, value in content.items():
            pdf.set_font("Arial", "B", 14)
            clean_key = clean_text(str(key).replace("-", " ").title())
            pdf.cell(200, 10, clean_key, ln=True)
            pdf.set_font("Arial", size=12)
            
            if isinstance(value, list):
                for item in value:
                    clean_item = clean_text(str(item))
                    pdf.multi_cell(0, 10, f"- {clean_item}")
            else:
                clean_value = clean_text(str(value))
                pdf.multi_cell(0, 10, clean_value)
            pdf.ln(5)
    else:
        clean_content = clean_text(str(content))
        pdf.multi_cell(0, 10, clean_content)
    
    # Add image if available
    if image_url:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Generated Diagram", ln=True, align="C")
        # Image handling remains the same
    
    # Add slide deck information
    if slides_data and not slides_data.get("error"):
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Slide Deck Structure", ln=True, align="C")
        pdf.ln(10)
        
        # Total slides
        pdf.set_font("Arial", "B", 14)
        total_slides = slides_data.get("total-slides", 0)
        pdf.cell(200, 10, f"Total Slides: {total_slides}", ln=True)
        pdf.ln(5)
        
        # Storyline
        storyline = slides_data.get("storyline", "")
        if storyline:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Storyline:", ln=True)
            pdf.set_font("Arial", size=12)
            clean_storyline = clean_text(storyline)
            pdf.multi_cell(0, 10, clean_storyline)
            pdf.ln(5)
        
        # Slides breakdown
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Slide Breakdown:", ln=True)
        pdf.ln(5)
        
        for slide in slides_data.get("slides", []):
            num = slide.get("slide-number", "?")
            title = clean_text(slide.get("title", "Untitled"))
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, f"Slide {num}: {title}", ln=True)
            
            pdf.set_font("Arial", size=10)
            section = clean_text(slide.get("section", ""))
            content_type = clean_text(slide.get("content-type", ""))
            pdf.cell(200, 8, f"Section: {section} | Type: {content_type}", ln=True)
            
            suggested_content = clean_text(slide.get("suggested-content", ""))
            if suggested_content:
                pdf.multi_cell(0, 8, f"Content: {suggested_content}")
            
            visual_elements = slide.get("visual-elements", [])
            if visual_elements:
                pdf.cell(200, 8, f"Visual Elements: {', '.join(visual_elements)}", ln=True)
            
            pdf.ln(3)
        
        # Design recommendations
        design_recs = slides_data.get("design-recommendations", [])
        if design_recs:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Design Recommendations:", ln=True)
            pdf.set_font("Arial", size=12)
            for idx, rec in enumerate(design_recs, 1):
                clean_rec = clean_text(rec)
                pdf.multi_cell(0, 10, f"{idx}. {clean_rec}")
            pdf.ln(5)
    
    return pdf.output(dest="S").encode("latin-1")

# def validate_inputs(
#     deliverable_type,
#     business_problem,
#     tech_stack,
#     time_constraint,
#     resource_constraints,
#     allowed_types=None
# ):
#     """Validate all inputs and detect incompatible assumptions."""
#     allowed_types = allowed_types or ["summary", "roadmap", "architecture", "data-schema"]

#     errors = []
#     warnings = []
#     normalized = {}

#     # Deliverable type
#     if deliverable_type not in allowed_types:
#         errors.append("Invalid deliverable type selected.")
#     normalized["deliverable_type"] = deliverable_type

#     # Business problem
#     if not business_problem or len(business_problem.strip()) < 20:
#         errors.append("Business Problem must be at least 20 characters.")
#     normalized["business_problem"] = business_problem.strip()

#     # Tech stack
#     if not tech_stack or len(tech_stack.strip()) < 3:
#         errors.append("Tech Stack is required (comma separated).")
#         normalized["tech_stack_list"] = []
#     else:
#         # Split and normalize
#         stack_list = [t.strip() for t in tech_stack.split(",") if t.strip()]
#         if len(stack_list) < 1:
#             errors.append("Tech Stack must have at least 1 item.")
#         if any(len(t) < 2 for t in stack_list):
#             warnings.append("Some tech stack items look too short.")
#         normalized["tech_stack_list"] = stack_list

#         # Incompatible assumptions (simple rules)
#         stack_lower = [t.lower() for t in stack_list]
#         if "mongodb" in stack_lower and "mysql" in stack_lower:
#             warnings.append("Mixing MongoDB and MySQL may require justification.")
#         if "serverless" in stack_lower and "on-prem" in stack_lower:
#             warnings.append("Serverless + On‑prem may be conflicting assumptions.")

#     # Time constraint
#     if time_constraint:
#         time_match = re.search(r"(\d+)\s*(day|days|week|weeks|month|months)", time_constraint.lower())
#         if not time_match:
#             errors.append("Time Constraint must include a number and unit (e.g., '3 months').")
#         normalized["time_constraint"] = time_constraint.strip()
#     else:
#         warnings.append("Time Constraint not provided.")
#         normalized["time_constraint"] = ""

#     # Resource constraints
#     if resource_constraints:
#         res_match = re.search(r"(\d+)", resource_constraints)
#         if not res_match:
#             errors.append("Resource Constraints should include a number (e.g., '3 team members').")
#         normalized["resource_constraints"] = resource_constraints.strip()
#     else:
#         warnings.append("Resource Constraints not provided.")
#         normalized["resource_constraints"] = ""

#     # Incompatible assumptions (timeline vs resources)
#     if time_constraint and resource_constraints:
#         time_match = re.search(r"(\d+)\s*(day|days|week|weeks|month|months)", time_constraint.lower())
#         res_match = re.search(r"(\d+)", resource_constraints)
#         if time_match and res_match:
#             time_val = int(time_match.group(1))
#             unit = time_match.group(2)
#             team_size = int(res_match.group(1))

#             # Convert to days for rough comparison
#             if "month" in unit:
#                 days = time_val * 30
#             elif "week" in unit:
#                 days = time_val * 7
#             else:
#                 days = time_val

#             if days <= 14 and team_size <= 2:
#                 warnings.append("Very short timeline with very small team may be unrealistic.")

#     return {
#         "is_valid": len(errors) == 0,
#         "errors": errors,
#         "warnings": warnings,
#         "normalized": normalized
#     }

def validate_inputs_with_model(
    deliverable_type,
    business_problem,
    tech_stack,
    time_constraint,
    resource_constraints,
    prompt_path="prompts/validation_prompt.txt"
):
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_message = f.read()

    user_message = f"""
Deliverable Type: {deliverable_type}
Business Problem: {business_problem}
Tech Stack: {tech_stack}
Time Constraint: {time_constraint}
Resource Constraints: {resource_constraints}
"""

    try:
        generator = DeliverableGenerator(system_message=system_message)
        result = generator.generate_deliverable(system_message, user_message)
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        return {"is_valid": False, "errors": [str(e)], "warnings": [], "incompatible_assumptions": []}

def render_validation_results(validation_data):
    """Nicely render validation results."""
    if not validation_data or validation_data.get("error"):
        st.error(f"Validation failed: {validation_data.get('error', 'Unknown error')}")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        status = "✅ Passed" if validation_data.get("is_valid") or validation_data.get("validation-passed") else "❌ Failed"
        st.metric("Validation Status", status)
    with col2:
        score = validation_data.get("quality_score", "N/A")
        st.metric("Quality Score", score if score != "N/A" else "N/A")
    with col3:
        issues_count = len(validation_data.get("errors", []))
        st.metric("Errors Found", issues_count)

    st.markdown("---")

    def render_list(title, items, level="warning"):
        if items:
            if level == "error":
                st.error(title)
            elif level == "warning":
                st.warning(title)
            else:
                st.info(title)
            for item in items:
                st.markdown(f"- {item}")

    render_list("❌ Errors", validation_data.get("errors", []), "error")
    render_list("⚠️ Warnings", validation_data.get("warnings", []), "warning")
    render_list("⚠️ Incompatible Assumptions", validation_data.get("incompatible_assumptions", []), "warning")
    render_list("⚠️ Commercial Risks", validation_data.get("commercial_risks", []), "warning")
    render_list("⚠️ Legal Risks", validation_data.get("legal_risks", []), "warning")
    render_list("⚠️ Scope vs Deliverables", validation_data.get("scope_vs_deliverables", []), "warning")

def format_content_as_text(content):
    """Convert deliverable JSON/dict into readable text for slide generation."""
    if isinstance(content, str):
        return content

    if not isinstance(content, dict):
        return str(content)

    lines = []
    for key, value in content.items():
        lines.append(f"{key.replace('-', ' ').title()}:")
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        lines.append(f"  - {k}: {v}")
                else:
                    lines.append(f"  - {item}")
        elif isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"  - {k}: {v}")
        else:
            lines.append(str(value))
        lines.append("")

    return "\n".join(lines)


def generate_slide_deck_from_text(content_text, generator, prompt_path="prompts/slides_prompt.txt"):
    """Generate slide deck from existing deliverable text."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_message = f.read()

    user_message = f"Deliverable Text:\n{content_text}"

    try:
        slides_data = generator.generate_deliverable(system_message, user_message)
        if isinstance(slides_data, str):
            slides_data = json.loads(slides_data)
        return slides_data
    except Exception as e:
        return {"error": str(e)}


def render_slide_deck(slides_data):
    """Nicely render slide deck structure."""
    if not slides_data or slides_data.get("error"):
        st.error(f"Slide generation failed: {slides_data.get('error', 'Unknown error')}")
        return

    col1, col2 = st.columns([3, 1])
    with col2:
        st.metric("Total Slides", slides_data.get("total-slides", 0))

    storyline = slides_data.get("storyline", "")
    if storyline:
        st.markdown("### Storyline")
        st.markdown(storyline)

    st.markdown("---")
    st.markdown("### Slide-by-Slide Breakdown")

    for slide in slides_data.get("slides", []):
        title = slide.get("title", "Untitled")
        num = slide.get("slide-number", "?")
        with st.expander(f"Slide {num}: {title}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Section:** {slide.get('section','')}")
                st.markdown(f"**Content Type:** {slide.get('content-type','')}")
                st.markdown("**Suggested Content:**")
                st.markdown(slide.get("suggested-content", ""))
            with col2:
                st.markdown("**Visual Elements:**")
                for v in slide.get("visual-elements", []):
                    st.markdown(f"- {v}")

            notes = slide.get("speaker-notes", "")
            if notes:
                st.markdown("**Speaker Notes:**")
                st.markdown(notes)

    design_recs = slides_data.get("design-recommendations", [])
    if design_recs:
        st.markdown("---")
        st.markdown("### Design Recommendations")
        for idx, rec in enumerate(design_recs, 1):
            st.markdown(f"{idx}. {rec}")


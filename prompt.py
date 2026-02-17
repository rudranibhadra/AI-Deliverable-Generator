SYSTEM_INSTRUCTION = (
    "You are an expert proposal generator for consulting and advisory services. "
    "Your task is to create a full, structured, high-quality, and validated commercial proposal draft based on the following inputs. "
    "Ensure the output includes: Executive Summary, Scope, Methodology, Schedule, Risks, Recommendations, and any other relevant sections. "
    "Make the proposal clear, concise, and follow best practices for business proposals. "
    "Validate for technical, commercial, legal, and operational coherence. "
    "Reuse relevant previous content if provided. "
    "Highlight any risks or inconsistencies. "
    "If style or length instructions are given, adapt accordingly. "
    "Expand each section with sufficient detail for client review. "
)

def build_detailed_prompt(
    business_problem: str = "",
    tech_stack: str = "",
    time_constraint: str = "",
    resource_constraints: str = "",
    user_prompt: str = "",
    extracted_text: str = "",
    deliverable_type: str = ""
) -> str:
    """Builds a detailed prompt for the AI model from all user inputs."""
    prompt = "You are an AI assistant helping to generate project deliverables.\n"
    if deliverable_type:
        prompt += f"Generate a {deliverable_type} in JSON format as per the following requirements.\n"
    if business_problem:
        prompt += f"Business Problem: {business_problem}\n"
    if tech_stack:
        prompt += f"Tech Stack: {tech_stack}\n"
    if time_constraint:
        prompt += f"Time Constraint: {time_constraint}\n"
    if resource_constraints:
        prompt += f"Resource Constraints: {resource_constraints}\n"
    if user_prompt:
        prompt += f"User Prompt: {user_prompt}\n"
    if extracted_text:
        prompt += f"Extracted Text: {extracted_text}\n"
    prompt += "Respond only with the required JSON structure."
    return prompt

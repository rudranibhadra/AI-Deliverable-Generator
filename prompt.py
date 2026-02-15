
SYSTEM_INSTRUCTION = (
    "You are an expert proposal generator for consulting and advisory services. "
    "Your task is to create a structured, high-quality, and validated commercial proposal draft based on the following inputs. "
    "Ensure the output is clear, concise, and follows best practices for business proposals. "
    "Validate for technical, commercial, legal, and operational coherence. "
    "Reuse relevant previous content if provided. "
    "Highlight any risks or inconsistencies. "
    "If style or length instructions are given, adapt accordingly. "
)

def build_detailed_prompt(
    business_problem: str = "",
    tech_stack: str = "",
    time_constraint: str = "",
    resource_constraints: str = "",
    user_prompt: str = "",
    extracted_text: str = ""
) -> str:
    """Builds a detailed prompt for the AI model from all user inputs."""
    prompt_lines = [SYSTEM_INSTRUCTION, "\n---\n"]
    if business_problem:
        prompt_lines.append(f"Business Problem/Requirement:\n{business_problem}\n")
    if tech_stack:
        prompt_lines.append(f"Tech Stack:\n{tech_stack}\n")
    if time_constraint:
        prompt_lines.append(f"Time Constraint:\n{time_constraint}\n")
    if resource_constraints:
        prompt_lines.append(f"Resource Constraints:\n{resource_constraints}\n")
    if user_prompt:
        prompt_lines.append(f"Additional Instructions or Prompts:\n{user_prompt}\n")
    if extracted_text:
        prompt_lines.append(f"Extracted File Content:\n{extracted_text}\n")
    return "".join(prompt_lines)

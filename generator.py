
from config import client, DEPLOYMENT_NAME



class ContentGenerator:
    """Generates content using the AI API."""
    def __init__(self, client_instance=None, deployment_name: str = DEPLOYMENT_NAME, temperature: float = 0.7, max_tokens: int = 4096, top_p: float = 0.95, system_message: str = None):
        self.client = client_instance or client
        self.deployment_name = deployment_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.system_message = system_message

    def generate(self, prompt: str, system_message: str = None) -> str:
        """Generate content from a prompt and system message."""
        sys_msg = system_message or self.system_message
        if not sys_msg:
            sys_msg = "You are an expert proposal generator for consulting and advisory services."
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating content: {e}")


class DeliverableGenerator:
    """Simplified orchestrator for the AI Deliverable Generator."""
    def __init__(self, content_generator: ContentGenerator = None, system_message: str = None):
        from prompt import SYSTEM_INSTRUCTION
        self.system_message = system_message or SYSTEM_INSTRUCTION
        self.content_generator = content_generator or ContentGenerator(system_message=self.system_message)

    def generate_deliverable(self, prompt: str) -> str:
        """Generate deliverable from a single prompt string."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        return self.content_generator.generate(prompt, self.system_message)

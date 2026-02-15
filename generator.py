
from config import client, DEPLOYMENT_NAME



class ContentGenerator:
    """Generates content using the AI API."""
    def __init__(self, client_instance=None, deployment_name: str = DEPLOYMENT_NAME, temperature: float = 0.4):
        self.client = client_instance or client
        self.deployment_name = deployment_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate content from a single prompt string."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating content: {e}")


class DeliverableGenerator:
    """Simplified orchestrator for the AI Deliverable Generator."""
    def __init__(self, content_generator: ContentGenerator = None):
        self.content_generator = content_generator or ContentGenerator()

    def generate_deliverable(self, prompt: str) -> str:
        """Generate deliverable from a single prompt string."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        return self.content_generator.generate(prompt)

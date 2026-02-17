import requests
import os
from config import client, DEPLOYMENT_NAME, DALLE_DEPLOYMENT_NAME


class DeliverableGenerator:
    """Simplified orchestrator for the AI Deliverable Generator."""
    def __init__(self, client_instance=None, deployment_name=None, dalle_deployment_name=None,temperature: float = 0.7, max_tokens: int = 4096, top_p: float = 0.95, system_message: str = None):
        self.client = client or client
        self.deployment_name = deployment_name or DEPLOYMENT_NAME
        self.dalle_deployment_name = dalle_deployment_name or DALLE_DEPLOYMENT_NAME
        self.client = client_instance or client
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.system_message = system_message

    def generate_deliverable(self, prompt: str, system_message: str = None) -> str:
        """Generate deliverable from a single prompt string."""
        sys_msg = system_message or self.system_message
        if not sys_msg:
            sys_msg = "You are an expert proposal generator for consulting and advisory services."
        try:
            print("Using deployment name:", self.deployment_name)
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

    def generate_image(self, prompt):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        deployment = os.getenv("AZURE_DALL_E_DEPLOYMENT")

        url = f"{endpoint}openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
        
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "deployment": deployment,
            "n": 1
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("data", [{}])[0].get("url", "")
        except Exception as e:
            print(f"Image generation failed: {e}")
            return ""

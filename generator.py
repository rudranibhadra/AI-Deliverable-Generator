import json
from config import client, DEPLOYMENT_NAME
from prompt import SYSTEM_MESSAGE, build_user_prompt


class DataLoader:
    """Loads project data from JSON file."""
    
    def __init__(self, data_path: str = "data/project_data.json"):
        self.data_path = data_path
    
    def load_data(self) -> list:
        """Load project data from file."""
        try:
            with open(self.data_path) as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {self.data_path}")


class PromptProcessor:
    """Processes user input and builds prompts for the API."""
    
    def __init__(self, system_message: str = SYSTEM_MESSAGE):
        self.system_message = system_message
    
    def format_internal_updates(self, data: list) -> str:
        """Format project data into internal updates string."""
        return "\n".join(
            f"- {item['title']} ({item['status']})" for item in data
        )
    
    def build_messages(self, user_request: str, internal_updates: str) -> list:
        """Build message list for API call."""
        user_prompt = build_user_prompt(user_request, internal_updates)
        return [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_prompt}
        ]


class ContentGenerator:
    """Generates content using the AI API."""
    
    def __init__(self, client=None, deployment_name: str = DEPLOYMENT_NAME, temperature: float = 0.4):
        self.client = client or client
        self.deployment_name = deployment_name
        self.temperature = temperature
    
    def generate(self, messages: list) -> str:
        """Generate content from messages."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating content: {e}")


class DeliverableGenerator:
    """Main orchestrator for the AI Deliverable Generator."""
    
    def __init__(
        self,
        data_loader: DataLoader = None,
        prompt_processor: PromptProcessor = None,
        content_generator: ContentGenerator = None
    ):
        self.data_loader = data_loader or DataLoader()
        self.prompt_processor = prompt_processor or PromptProcessor()
        self.content_generator = content_generator or ContentGenerator()
    
    def generate_deliverable(self, user_request: str) -> str:
        """Generate deliverable from user request."""
        if not user_request.strip():
            raise ValueError("User request cannot be empty")
        
        # Load project data
        data = self.data_loader.load_data()
        
        # Process prompt
        internal_updates = self.prompt_processor.format_internal_updates(data)
        messages = self.prompt_processor.build_messages(user_request, internal_updates)
        
        # Generate content
        output = self.content_generator.generate(messages)
        
        return output

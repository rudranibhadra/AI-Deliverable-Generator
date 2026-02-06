import json
from config import client, DEPLOYMENT_NAME
from prompt import SYSTEM_MESSAGE, build_user_prompt

# Load input data
with open("data/project_data.json") as f:
    data = json.load(f)

internal_updates = "\n".join(
    f"- {item['title']} ({item['status']})" for item in data
)

# Let user enter what they want
user_request = input(
    "\nWhat would you like to generate? "
    "(e.g., 'Executive summary for client'):\n"
)

user_prompt = build_user_prompt(user_request, internal_updates)

messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user", "content": user_prompt}
]


response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,
    messages=messages,
    temperature=0.4
)

print("\nGenerated client-ready content:\n")
print(response.choices[0].message.content)
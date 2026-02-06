import json
import streamlit as st
from config import client, DEPLOYMENT_NAME
from prompt import SYSTEM_MESSAGE, build_user_prompt

st.set_page_config(page_title="AI Deliverable Generator", layout="centered")

st.title("AI Deliverable Generator")

with open("data/project_data.json") as f:
    data = json.load(f)

internal_updates = "\n".join(
    f"- {item['title']} ({item['status']})" for item in data
)

user_request = st.text_area("Enter your prompt", height=150)

if st.button("Generate"):
    if not user_request.strip():
        st.warning("Please enter a prompt before generating.")
    else:
        user_prompt = build_user_prompt(user_request, internal_updates)

        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt}
        ]

        with st.spinner("Generating..."):
            try:
                response = client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=messages,
                    temperature=0.4
                )

                output = response.choices[0].message.content
                st.subheader("Generated content")
                st.write(output)
            except Exception as e:
                st.error(f"Error generating content: {e}")

from openai import OpenAI
import os
import re

def generate(prompt, is_subtopic=False):
    client = OpenAI(api_key="super-secret-token")
    BASE_URL = "https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1"
    client.base_url = BASE_URL

    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": prompt}
        ]
    )

    content = completion.choices[0].message.content

    if not is_subtopic:
        # Extract subtopics and highlight key terms
        subtopics, highlighted_content = process_content(content)
        return {
            "main_content": highlighted_content,
            "subtopics": subtopics
        }

    return {"main_content": content}

def process_content(content):
    # Extract subtopics (assuming they're marked with '##')
    subtopics = re.findall(r'##\s*(.*)', content)
    
    # Highlight key terms (assuming they're marked with '**')
    highlighted_content = re.sub(r'\*\*(.*?)\*\*', r'<a href="#" class="key-term">\1</a>', content)
    
    return subtopics, highlighted_content
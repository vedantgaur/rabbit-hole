from openai import OpenAI
import os
import re

def generate(prompt, is_subtopic=False):
    client = OpenAI(api_key="super-secret-token")
    BASE_URL = "https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1"
    client.base_url = BASE_URL

    # Modify the prompt to encourage MathJax-friendly output
    prompt = f"{prompt}\n\nPlease provide any mathematical content in a format that is ONLY compatible with MathJax, ensuring that all equations are properly formatted without mentioning LaTeX explicitly (unless relevant to the topic/query explicitly)."

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

    # For subtopic generation, ensure subtopics are hyperlinked
    subtopics = re.findall(r'##\s*(.*)', content)  # Extract subtopics
    highlighted_content = process_subtopic_content(content)  # Process content for subtopics
    return {
        "main_content": highlighted_content,
        "subtopics": subtopics
    }

def process_subtopic_content(content):
    # Highlight key terms (assuming they're marked with '**')
    highlighted_content = re.sub(r'\*\*(.*?)\*\*', r'<a href="#" class="key-term">\1</a>', content)
    
    # Format mathematical content for MathJax
    highlighted_content = re.sub(r'\$(.*?)\$', r'\\(\1\\)', highlighted_content)  # Inline math
    highlighted_content = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', highlighted_content)  # Block math

    # Ensure subtopics are hyperlinked
    subtopics = re.findall(r'##\s*(.*)', content)
    for subtopic in subtopics:
        highlighted_content = highlighted_content.replace(subtopic, f'<a href="#" class="subtopic">{subtopic}</a>')

    return highlighted_content

def process_content(content):
    # Extract subtopics (assuming they're marked with '##')
    subtopics = re.findall(r'##\s*(.*)', content)
    
    # Highlight key terms (assuming they're marked with '**')
    highlighted_content = re.sub(r'\*\*(.*?)\*\*', r'<a href="#" class="key-term">\1</a>', content)
    
    # Format mathematical content for MathJax
    highlighted_content = re.sub(r'\$(.*?)\$', r'\\(\1\\)', highlighted_content)  # Inline math
    highlighted_content = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', highlighted_content)  # Block math
    
    # Ensure subtopics are hyperlinked
    for subtopic in subtopics:
        highlighted_content = highlighted_content.replace(subtopic, f'<a href="#" class="subtopic">{subtopic}</a>')
    
    return subtopics, highlighted_content
from modal import App, Image, Secret
import requests
import re

app = App("huggingface-inference")

@app.function(
    image=Image.debian_slim().pip_install("requests"),
    secrets=[Secret.from_name("huggingface-secret")]
)
def llm_inference(prompt, is_subtopic=False):
    import os

    API_URL = "https://api-inference.huggingface.co/models/gpt2-large"
    headers = {"Authorization": f"Bearer {os.environ['HUGGINGFACE_API_KEY']}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": prompt,
        "parameters": {"max_length": 500}
    })

    content = output[0]['generated_text']

    if not is_subtopic:
        # Extract subtopics and highlight key terms
        subtopics, highlighted_content = process_content(content)
        return {
            "main_content": highlighted_content,
            "subtopics": subtopics
        }
    else:
        return {"main_content": content}

def process_content(content):
    # Extract subtopics (assuming they're marked with '##')
    subtopics = re.findall(r'##\s*(.*)', content)
    
    # Highlight key terms (assuming they're marked with '**')
    highlighted_content = re.sub(r'\*\*(.*?)\*\*', r'<a href="#" class="key-term">\1</a>', content)
    
    return subtopics, highlighted_content

if __name__ == "__main__":
    app.serve()
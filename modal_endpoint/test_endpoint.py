from openai import OpenAI

API_KEY = "super-secret-token"
BASE_URL = "https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1"

client = OpenAI(api_key=API_KEY)
client.base_url = BASE_URL

completion = client.chat.completions.create(
  model="meta-llama/Meta-Llama-3-8B-Instruct",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion)

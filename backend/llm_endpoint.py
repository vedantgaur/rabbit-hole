import modal

stub = modal.Stub("llm-endpoint")

# Define the image with the required dependencies
image = modal.Image.debian_slim().pip_install("vllm")

# Define the model to be used
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

@stub.function(
    image=image,
    gpu="A10G",
    timeout=600,
)
@modal.web_endpoint(method="POST")
def generate(prompt: str):
    from vllm import LLM, SamplingParams

    llm = LLM(model=MODEL_NAME)
    sampling_params = SamplingParams(temperature=0.7, max_tokens=256)
    
    outputs = llm.generate([prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text
    
    return {"generated_text": generated_text}

if __name__ == "__main__":
    stub.serve()
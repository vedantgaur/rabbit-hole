from modal import App, Image

app = App("manim-renderer")
inference_app = App("huggingface-inference")

manim_image = (
    Image.debian_slim()
    .apt_install(
        "libcairo2-dev", 
        "pkg-config", 
        "python3-dev", 
        "ffmpeg", 
        "texlive", 
        "texlive-latex-extra",
        "libpango1.0-dev"
    )
    .env({"PKG_CONFIG_PATH": "/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/share/pkgconfig"})
    .pip_install("manim")
)

@app.function(gpu="any")
def generate_manim_animation(content):
    manim_code = text_to_manim_llm(content)
    animation = render_manim(manim_code)
    return save_animation(animation)

@app.function()
def text_to_manim_llm(content):
    prompt = f"""
    Generate Manim code for the following content. Here's the template to use:

    ```python
    from manim import *

    class ExplanationScene(Scene):
        def construct(self):
            # Put your animation logic here
            pass
    ```

    Now, generate Manim code for the following content:
    {content}
    """
    
    # Use your LLM to generate the Manim code based on this prompt
    manim_code = inference_app.llm_inference.remote(prompt)
    return manim_code

@app.function(image=manim_image)
def render_manim(code: str):
    from manim import config, tempconfig
    from manim.scene.scene import Scene
    import importlib.util
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    spec = importlib.util.spec_from_file_location("manim_scene", temp_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    scene_class = next(obj for name, obj in module.__dict__.items() if isinstance(obj, type) and issubclass(obj, Scene))

    with tempconfig({"quality": "medium_quality", "format": "gif"}):
        scene = scene_class()
        scene.render()

    output_file = f"{scene.__class__.__name__}.gif"
    with open(output_file, "rb") as f:
        rendered_content = f.read()

    os.remove(temp_file_path)
    os.remove(output_file)

    return rendered_content

@app.function()
def save_animation(animation):
    import uuid
    filename = f"animation_{uuid.uuid4()}.gif"
    path = f"/tmp/{filename}"
    with open(path, "wb") as f:
        f.write(animation)
    return path

if __name__ == "__main__":
    app.serve()
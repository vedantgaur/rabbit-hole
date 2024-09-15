from modal import App, Image
from modal_inference import generate
import base64
import os
import tempfile
import re

app = App("manim-renderer")

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
    .pip_install("manim", "flask", "openai")
)

@app.function(gpu="any", image=manim_image)
def generate_manim_animation(content):
    manim_code = text_to_manim_llm(content)
    if not manim_code:
        return None
    animation = render_manim(manim_code)
    return base64.b64encode(animation).decode('utf-8') if animation else None

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
    response = generate(prompt)["main_content"]
    code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
    
    manim_code = manim_code = code_match.group(1).strip() if code_match else None

    return manim_code

def render_manim(code: str):
    from manim import config, tempconfig
    from manim.scene.scene import Scene
    import importlib.util
    import sys
    import glob
    from PIL import Image as PILImage

    output_dir = None
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            temp_file_path = os.path.join(temp_dir, "manim_scene.py")
            with open(temp_file_path, "w") as temp_file:
                temp_file.write(code)

            sys.path.insert(0, temp_dir)
            spec = importlib.util.spec_from_file_location("manim_scene", temp_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            scene_class = next((obj for name, obj in module.__dict__.items() 
                                if isinstance(obj, type) and issubclass(obj, Scene)), None)
            
            if not scene_class:
                raise ValueError("No valid Scene class found in the generated code.")

            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            with tempconfig({
                "quality": "medium_quality",
                "format": "png",
                "output_file": os.path.join(output_dir, "scene"),
                "verbosity": "DEBUG",
                "write_to_movie": True,
                "disable_caching": True
            }):
                scene = scene_class()
                scene.render()

            output_files = glob.glob(os.path.join(output_dir, "*.png"))
            if not output_files:
                raise FileNotFoundError(f"No output PNG file found in {output_dir}")

            png_path = output_files[0]
            gif_path = os.path.join(output_dir, "scene.gif")
            
            with PILImage.open(png_path) as img:
                img.save(gif_path, format='GIF', save_all=True, append_images=[img]*10, duration=100, loop=0)

            with open(gif_path, "rb") as f:
                return f.read()

        except Exception as e:
            print(f"Error rendering Manim animation: {str(e)}")
            if output_dir and os.path.exists(output_dir):
                print(f"Contents of output directory: {os.listdir(output_dir)}")
            else:
                print("Output directory was not created.")
            return None
        finally:
            if sys.path and sys.path[0] == temp_dir:
                sys.path.pop(0)

if __name__ == "__main__":
    app.serve()
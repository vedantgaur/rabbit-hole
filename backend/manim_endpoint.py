import modal

stub = modal.Stub("manim-renderer")

image = modal.Image.debian_slim().pip_install("manim")

@stub.function(image=image, gpu="any")
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

if __name__ == "__main__":
    stub.serve()
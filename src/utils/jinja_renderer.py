import os
from jinja2 import Environment, FileSystemLoader

def render_template_folder(template_name: str, context: dict) -> str:
    """
    Renders all .j2 files in a template folder and returns a multi-file string 
    compatible with the current renderer's parsing logic (>>> filename).
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_path, "templates", template_name)
    
    if not os.path.exists(template_dir):
        raise ValueError(f"Template directory {template_dir} does not exist.")

    env = Environment(loader=FileSystemLoader(template_dir))
    
    rendered_files = []
    
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith(".j2"):
                # Get relative path for the template
                rel_dir = os.path.relpath(root, template_dir)
                if rel_dir == ".":
                    rel_path = file
                else:
                    rel_path = os.path.join(rel_dir, file)
                
                # Render the template
                template = env.get_template(rel_path.replace("\\", "/"))
                content = template.render(context)
                
                # Determine final filename (remove .j2)
                final_filename = rel_path[:-3].replace("\\", "/")
                
                # Format as >>> filename
                rendered_files.append(f">>> {final_filename}\n{content}")
                
    return "\n\n".join(rendered_files)

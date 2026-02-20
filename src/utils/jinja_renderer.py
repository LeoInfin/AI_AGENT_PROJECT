import os
import re
from jinja2 import Environment, FileSystemLoader
from typing import Dict

def render_template_folder(template_name: str, context: dict) -> Dict[str, str]:
    """
    Renders all .j2 files in a template folder and returns a dictionary 
    mapping filenames to their rendered content.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_path, "templates", template_name)
    
    if not os.path.exists(template_dir):
        raise ValueError(f"Template directory {template_dir} does not exist.")

    env = Environment(
        loader=FileSystemLoader(template_dir),
        comment_start_string='{##',
        comment_end_string='##}'
    )
    
    rendered_files = {}
    
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
                
                # If the template already uses multi-file delimiters (>>>), 
                # split them into multiple entries in the dictionary.
                if ">>>" in content:
                    # Split while keeping the delimiter to find filenames
                    blocks = re.split(r'^>>>\s*', content, flags=re.MULTILINE)
                    for block in blocks:
                        block = block.strip()
                        if not block: continue
                        lines = block.split('\n')
                        fname = lines[0].strip()
                        fcontent = "\n".join(lines[1:]).strip()
                        rendered_files[fname] = fcontent
                else:
                    rendered_files[final_filename] = content.strip()
                
    return rendered_files

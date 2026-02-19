import os
import re
from src.state import AgentState
from src.utils.jinja_renderer import render_template_folder
from src.config import PROJECTS_FOLDER

def parse_and_write_files(raw_code: str, target_folder: str):
    """
    Parses the multi-file string format (>>> filename) and writes content to disk.
    """
    file_blocks = re.split(r'^>>>\s*', raw_code, flags=re.MULTILINE)

    for block in file_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        filename = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        # Clean up markdown tags
        content = re.sub(r'```[a-z]*', '', content).replace('```', '').strip()

        file_path = os.path.join(target_folder, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"  📄 Written: {filename}")

def save_project_to_disk(state: AgentState, base_folder: str = "generated_app"):
    """
    1. Finds a unique folder name.
    2. Renders the base Jinja2 template.
    3. Overwrites/adds AI-generated code from the agent state.
    """
    # 1. Define a parent folder for all generated projects
    projects_parent = PROJECTS_FOLDER
    os.makedirs(projects_parent, exist_ok=True)

    project_name = base_folder
    final_folder = os.path.join(projects_parent, project_name)
    counter = 1

    while os.path.exists(final_folder):
        project_name = f"{base_folder}_{counter}"
        final_folder = os.path.join(projects_parent, project_name)
        counter += 1

    # Create the unique directory
    os.makedirs(final_folder)
    print(f"📁 Created unique project folder: {final_folder}")

    # 2. Render Template First
    # This provides the base structure (Vite, TS, Tailwind config, etc.)
    template_name = state.get("template_name", "react_ts_tailwind")
    context = state.get("template_context", {
        "project_name": "My AI Project",
        "primary_color": "#3b82f6",
        "secondary_color": "#10b981"
    })

    print(f"🎨 Rendering base template: {template_name}")
    try:
        template_code = render_template_folder(template_name, context)
        parse_and_write_files(template_code, final_folder)
    except Exception as e:
        print(f"⚠️ Template rendering failed or skipped: {e}")

    # 3. Write AI-Generated Code
    # This will overwrite template files (like App.tsx) or add new ones (components)
    raw_code = state.get("code", "")
    if raw_code:
        print("🧠 Applying AI generated logic and components...")
        parse_and_write_files(raw_code, final_folder)
    else:
        print("ℹ️ No AI code found in state to apply.")

    print(f"\n✅ Project successfully generated in ./{final_folder}")

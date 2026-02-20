import os
import re
import subprocess
from src.state import AgentState
from src.utils.jinja_renderer import render_template_folder
from src.config import PROJECTS_FOLDER, PROTECTED_FILES

def parse_and_write_files(files_dict: dict | str, target_folder: str, is_template: bool = False):
    """
    Writes content to disk. Supports both the new Dict[fname, content] format 
    and the legacy multi-file string format (>>> filename).
    """
    if isinstance(files_dict, str):
        # Legacy support for multi-file string format
        file_blocks = re.split(r'^>>>\s*', files_dict, flags=re.MULTILINE)
        files_dict = {}
        for block in file_blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split('\n')
            filename = lines[0].strip()
            content = "\n".join(lines[1:]).strip()
            files_dict[filename] = content

    for filename, content in files_dict.items():
        # Clean up markdown tags
        content = re.sub(r'```[a-z]*', '', content).replace('```', '').strip()

        if not is_template and filename in PROTECTED_FILES:
            print(f"  🛡️  Blocked attempt to overwrite protected file: {filename}")
            continue

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
        template_files = render_template_folder(template_name, context)
        parse_and_write_files(template_files, final_folder, is_template=True)
    except Exception as e:
        print(f"⚠️ Template rendering failed or skipped: {e}")

    # 3. Write AI-Generated Code
    # This will overwrite template files (like App.tsx) or add new ones (components)
    code_dict = state.get("code", {})
    if code_dict:
        print("🧠 Applying AI generated logic and components...")
        parse_and_write_files(code_dict, final_folder, is_template=False)
    else:
        print("ℹ️ No AI code found in state to apply.")

    print(f"\n✅ Project successfully generated in ./{final_folder}")
    return final_folder

def run_npm_build_check(project_path: str) -> str | None:
    """
    Runs 'npm install' and 'npm run build' in the specified folder.
    Returns stderr/stdout as error message if it fails, otherwise None.
    """
    print(f"🛠️ Starting build validation in: {project_path}")
    
    try:
        # Run npm install
        print("📦 Running npm install...")
        install_res = subprocess.run(
            ["npm", "install"], 
            cwd=project_path, 
            capture_output=True, 
            text=True, 
            shell=True
        )
        if install_res.returncode != 0:
            error_msg = f"NPM Install Failed:\n{install_res.stderr}\n{install_res.stdout}"
            print(f"❌ Build validation failed at install step.")
            return error_msg

        # Run npm run build
        print("🏗️ Running npm run build...")
        build_res = subprocess.run(
            ["npm", "run", "build"], 
            cwd=project_path, 
            capture_output=True, 
            text=True, 
            shell=True
        )
        if build_res.returncode != 0:
            error_msg = f"NPM Build Failed:\n{build_res.stderr}\n{build_res.stdout}"
            print(f"❌ Build validation failed at build step.")
            return error_msg

        print("✨ Build successful!")
        return None

    except Exception as e:
        print(f"⚠️ Build check exception: {e}")
        return str(e)

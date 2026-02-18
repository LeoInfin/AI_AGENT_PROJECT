import os
import re
from src.state import AgentState

def save_project_to_disk(state: AgentState, base_folder: str = "generated_app"):
    """
    Parses the multi-file string and writes it to a unique local folder.
    If the folder exists, it appends _1, _2, etc.
    """
    # 1. Logic to find a unique folder name
    final_folder = base_folder
    counter = 1

    while os.path.exists(final_folder):
        final_folder = f"{base_folder}_{counter}"
        counter += 1

    # 2. Create the unique directory
    os.makedirs(final_folder)
    print(f"📁 Created unique project folder: {final_folder}")

    raw_code = state.get("code", "")
    if not raw_code:
        print("❌ No code found in state.")
        return

    # 3. Split and Save logic
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

        file_path = os.path.join(final_folder, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"  📄 Written: {filename}")

    print(f"\n✅ Project successfully generated in ./{final_folder}")

import os
from jinja2 import Environment, FileSystemLoader


def get_agent_prompt(project_type, agent_role, context_data):
    # 1. Point Jinja to your templates folder
    template_path = os.path.join("templates", project_type)
    env = Environment(loader=FileSystemLoader(template_path))

    # 2. Load the specific agent file (e.g., architect.jinja2)
    template = env.get_template(f"{agent_role}.jinja2")

    # 3. Render it with your specific task data
    return template.render(context_data)

# Example usage:
# task_prompt = get_agent_prompt("react_ts", "architect", {"task": "Crypto Dashboard"})
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import llm
from src.state import AgentState

def implementor_agent(state: AgentState):
    print("--- NODE: IMPLEMENTOR ---")

    files_to_implement = state["architecture"].get("files", [])
    code_dict = {}

    system_prompt = (
        "You are a Senior Lead Developer. Your task is to implement the specified file "
        "as part of a larger React and TypeScript project.\n\n"
        
        "CONTEXT:\n"
        "A base 'react_ts_tailwind' template is already in place. Below are the rendered skeleton files "
        "that provide the project structure. You MUST ensure your code is compatible with these files.\n\n"
        
        "SKELETON FILES:\n"
        "{rendered_skeletons}\n\n"

        "FULL ARCHITECTURE DECISIONS:\n"
        "{arch_summary}\n\n"

        "CRITICAL INSTRUCTIONS:\n"
        "1. Write the FULL code for the file: {target_file}\n"
        "2. Do NOT provide any explanations, markdown code blocks, or delimiters. Just the raw code.\n"
        "3. MARKER ADHERENCE: You MUST use the provided skeleton as your base. Replace markers like `{{# AI_IMPORTS #}}`, `{{# AI_INTERFACE #}}`, `{{# AI_STATE #}}`, etc., with your actual code. DO NOT delete the existing code in the skeleton (like the main component signature or existing interface properties).\n"
        "4. NO DUPLICATION: Do NOT redefine the `Props` interface or the main component function if they already exist in the skeleton. Just add properties to the interface via the `{{# AI_INTERFACE #}}` marker and logic to the body via `{{# AI_STATE #}}`.\n"
        "5. DEPENDENCY HYGIENE: Only use imports from: 'react', 'lucide-react', or other files explicitly mentioned in the architecture. Do NOT use 'framer-motion' or other libraries NOT in the base template unless you are SURE they are available.\n"
        "6. NO LOCAL HOAXES: Do NOT import files that don't exist (e.g., `./CTAProps`). All types and props for this component should be defined within this file.\n"
        "7. Ensure all imports are correct and Tailwind classes are used appropriately."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Please implement the following file: {target_file}")
    ])

    chain = prompt | llm | StrOutputParser()

    # Pre-format rendered templates for context
    skeletons_context = "\n".join([f">>> {fname}\n{content}" for fname, content in state.get("rendered_templates", {}).items()])

    for filename in files_to_implement:
        print(f"  🛠️ Implementing: {filename}")
        
        file_code = chain.invoke({
            "target_file": filename,
            "arch_summary": state["architecture"].get("logic_summary", ""),
            "rendered_skeletons": skeletons_context
        })
        
        code_dict[filename] = file_code.strip()
    
    return {"code": code_dict}
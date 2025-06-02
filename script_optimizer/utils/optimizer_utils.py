import subprocess
import os
from openai import OpenAI
import ollama
from dotenv import load_dotenv
import httpx
from IPython.display import Markdown, display

def run_python_script(script_path: str):
    """
    Executes a Python script given its path.

    Args:
        script_path (str): Path to the .py file to be executed.
    """
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        if "An error occurred" in result.stdout:
            print("⚠️ The script finished with internal errors:")
            print(result.stdout)
        else:
            print("✅ Script executed successfully.")
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("❌ Error while executing the script:")
        print(e.stderr)


def find_first_file(directory: str, extension: str) -> str:
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            return os.path.join(directory, filename)
    raise FileNotFoundError(f"No .py files found in directory: {directory}")

def call_llama3_ollama(prompt: str, model: str, system_prompt: str) -> str:
    import ollama
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    llm_response = response["message"]["content"]
    return llm_response

def call_chatgpt_openai(prompt: str, model_name: str, system_prompt: str) -> str:
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    openai = OpenAI(http_client=httpx.Client(verify=False))
    
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def optimize_script(input_path: str, extension: str, output_dir: str, model_source: str, system_prompt: str, execution_mode, output_file_name="optimized_script.py", create_unitary_tests=True):

        
    if not os.path.isdir(input_path):
        raise NotADirectoryError(f"{input_path} is not a directory")

    file_path = find_first_file(input_path, extension)
    print(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()
        
    if create_unitary_tests:
        unit_test_string = "12. write unit tests for EVERY SINGLE FUNCTION on the code"
    else:
        unit_test_string = "12. DO NOT write unit tests"
        
    prompt = f"""
    
You are a Python expert. Refactor the following Python script with these goals:

1. Add concise comments explaining the purpose of each function, its parameters, return values, and any complex logic.
2. Use proper Python docstrings (PEP 257) for every function.
3. Remove unused imports and dead code.
4. Replace redundant or repeated logic with reusable functions if appropriate.
5. Use meaningful and descriptive names for all variables and functions.
6. Add error handling with try/except blocks where needed.
7. Ensure that all pandas and numpy operations are optimized and vectorized.
8. Organize the logic into separate functions or classes as needed.
9. Ensure PEP 8 style compliance.
10. Ensure the script is fully self-contained, with all necessary imports and definitions.
11. Include a block:

    if __name__ == "__main__":
        # run a simple example or test to demonstrate the main functionality
        
{unit_test_string}

12. The refactored script MUST be executable without any errors by running:

    subprocess.run(["python", script_path], capture_output=True, text=True, check=True)

IMPORTANT:
- Return ONLY the full Python script.
- Then a section titled "NOTE:" (in plain text) explaining what was done and any assumptions.
- Do NOT include explanations before the script or extra formatting.

ORIGINAL CODE:

    {original_code}
    """.strip()

    if execution_mode.lower() == "offline":
        print(f"▶️ Using {model_source} via Ollama...")
        full_response = call_llama3_ollama(prompt, model_source, system_prompt)
    
    elif execution_mode.lower() == "online":
        print(f"▶️ Using {model_source} via OpenAI API...")
        full_response = call_chatgpt_openai(prompt, model_source, system_prompt)
    
    else:
        raise ValueError("Invalid execution_mode. Use 'offline' or 'online'.")
    

    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, output_file_name)

    # clean markdown delimiter
    full_response = full_response.replace("```python", "").strip()
    parts = parts = full_response.split("```")

    # 🔸 here is the optimized clean code
    optimized_code = parts[0].replace("```", "").strip()
    
    # 🔸 here is the NOTE section
    if len(parts) > 1:
        notes = parts[1].replace("```", "").strip()
        display(Markdown(f"📝 **Notes from LLM:**\n\n{notes}"))
    else:
        notes = None
        display(Markdown("⚠️ No notes section found."))

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(optimized_code)

    print(f"✅ Optimized script saved to: {output_file_path}")

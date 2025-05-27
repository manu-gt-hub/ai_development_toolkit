import subprocess
import os
from openai import OpenAI
import ollama
from dotenv import load_dotenv
import httpx

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

def optimize_script(input_path: str, extension: str, output_dir: str, model_source: str, system_prompt: str, output_file_name="optimized_script.py", create_unitary_tests=True):
    if not os.path.isdir(input_path):
        raise NotADirectoryError(f"{input_path} is not a directory")

    file_path = find_first_file(input_path, extension)
    print(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    if create_unitary_tests:
        unit_test_string = "12. write unit tests"
    else:
        unit_test_string = "12. DO NOT write unit tests"
        
    
    prompt = f"""
    
    Refactor the following Python code with the following goals:
    
    1. Add clear and concise comments explaining each function, its parameters, return values, and complex logic.
    2. Document all functions using standard Python docstrings (PEP 257).
    3. Remove unused imports and dependencies.
    4. Simplify repetitive or redundant code by creating reusable functions.
    5. Use descriptive variable, function, and class names.
    6. Eliminate dead or unused code.
    7. Add try/except blocks for error handling where appropriate.
    8. Optimize loops and pandas/numpy operations (prefer vectorized solutions).
    9. Separate logic into functions or classes.
    10. Write basic unit tests for each function.
    11. Ensure PEP 8 compliance.
    {unit_test_string}
    
    IMPORTANT: Return ONLY the improved Python script and a section NOTE: with the explanation about what you have done IN PLAIN TEXT
    
    ```python
    {original_code}
    ```
    """.strip()
    
    if "llama" in model_source.lower():
        print(f"▶️ Using {model_source} via Ollama...")
        full_response = call_llama3_ollama(prompt, model_source, system_prompt)
    
    elif "gpt" in model_source.lower():
        print(f"▶️ Using {model_source} via OpenAI API...")
        full_response = call_chatgpt_openai(prompt, model_source, system_prompt)
    
    else:
        raise ValueError("Invalid model_source. Use 'llama3' or 'chatgpt'.")

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
        print("📝 Notes from LLM:\n", notes)
    else:
        notes = None
        print("⚠️ No notes section found.")

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(optimized_code)

    print(f"✅ Optimized script saved to: {output_file_path}")

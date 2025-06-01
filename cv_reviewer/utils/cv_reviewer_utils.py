import ollama
from openai import OpenAI
import httpx
import pdfplumber
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
import os
import json

def evaluate_all_candidates(model, job_description, mandatory_keywords, landing_path, language, execution_mode):
    """
    Process all CVs in the given directory and evaluate them against a job description.

    Args:
        model (str): Model name to be used for evaluation.
        job_description (str): The job description to compare candidates against.
        mandatory_keywords (list): List of keywords to highlight in evaluation.
        landing_path (str): Path to the folder containing CV files.

    Returns:
        list: A list of JSON strings representing the evaluation results.
    """
    matches = []

    for filename in os.listdir(landing_path):
        path = os.path.join(landing_path, filename)
        
        if os.path.isfile(path):
            cv_text = extract_text_from_cv(path)
            if cv_text is not None:
                
                words = cv_text.split()    
                num_of_words = len(words)

                if num_of_words > 5:    
                    anonymized_desc = anonymize_resume(cv_text)

                    keywords_string = "Additional note: " + evaluate_mandatory_keywords(anonymized_desc, mandatory_keywords)

                    llm_answer = evaluate_candidate(model, anonymized_desc, job_description, language, keywords_string, execution_mode)
                    llm_answer['name'] = filename

                    updated_json_str = json.dumps(llm_answer, indent=2)
                    matches.append(updated_json_str)

    return matches

def render_candidate_evaluations(matches):
    """
    Parse, sort and display candidate evaluations in Markdown format.

    Args:
        matches (list): List of candidate evaluation results (as JSON strings or dicts).
    """
    # Ensure all elements are dictionaries
    parsed_matches = [json.loads(m) if isinstance(m, str) else m for m in matches]
    sorted_matches = sorted(parsed_matches, key=lambda x: x.get("match_percentage", 0), reverse=True)

    markdown_text = "### 📊 Candidate Evaluations\n\n"

    for i, match in enumerate(sorted_matches, start=1):
        questions = match.get("recommended_questions", "")

        # Handle both list and string formats
        if isinstance(questions, list):
            question_lines = [q.strip("-• ").strip() for q in questions if q.strip()]
        else:
            question_lines = [q.strip("-• ").strip() for q in questions.split("\n") if q.strip()]

        question_md = "\n".join([f"- {q}" for q in question_lines])

        markdown_text += f"""
**🧑‍💼 Candidate #{i}: {match['name']} – {match['match_percentage']}%**

{match.get('summary', 'No summary provided.')}

**📝 Recommended Questions**
{question_md}

---
"""

    return markdown_text

def analyze_candidates(model, job_description, mandatory_keywords, landing_path, language, execution_mode = "online"):
    
    matches = evaluate_all_candidates(model, job_description, mandatory_keywords, landing_path, language, execution_mode)
    evaluation_text = render_candidate_evaluations(matches)
    
    return evaluation_text
    
def extract_json(text):
    try:
        # Intenta encontrar el primer bloque de texto que parezca JSON
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No valid JSON block found")
    except Exception as e:
        raise ValueError(f"Error parsing JSON: {e}\nRaw text:\n{text}")

def anonymize_resume(text):

    prompt = f"""
    I want you to anonymize this CV text content and return it without sensible data (name, surname, email, location, telephone number...), DON'T provide notes
    
    {text}
    """
    
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "you are a CV anonymizer"},
            {"role": "user", "content": prompt}
        ]
    )
    llm_response = response["message"]["content"]
    return llm_response
    
def call_llama3_ollama(prompt: str, model: str, system_prompt: str) -> str:
    
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
        ],
        temperature = 0.1
    )
    
    return response.choices[0].message.content

# Función para leer el contenido de un archivo .docx
def read_docx(cv_path):
    try:
        # Cargar el documento
        doc = Document(cv_path)
        
        # Leer el contenido del documento
        contenido = []
        for parrafo in doc.paragraphs:
            contenido.append(parrafo.text)
        
        return '\n'.join(contenido)
    except:
        return None

def read_doc(cv_path):
    try:
        # Inicializar la aplicación de Word
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Abrir el documento
        doc = word.Documents.Open(cv_path)
        
        # Leer el contenido del documento
        contenido = doc.Content.Text
        
        # Cerrar el documento y la aplicación de Word
        doc.Close(False)
        word.Quit()
        
        return contenido
    except:
        return None

def read_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except:
        return None

def extract_text_from_cv(cv_path):
    cv_text = read_pdf(cv_path)
    if cv_text is None:
        cv_text = read_docx(cv_path)
        if cv_text is None:
            cv_text =read_doc(cv_path)

    return cv_text


def get_job_description(url):
    class_name = 'wiki-content'
    # Hacer la solicitud HTTP
    response = requests.get(url, verify = False)
    
    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        # Analizar el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar todos los elementos con la clase especificada
        elements = soup.find_all(class_=class_name)
        
        # Extraer el texto de esos elementos
        text = '\n'.join([element.get_text(separator='\n').strip() for element in elements])
        return text
    else:
        return f"Error: Unable to fetch the page. Status code: {response.status_code}"

def evaluate_candidate(model_source, candidate_desc, job_description, language, execution_mode, keywords_string = ""):

    system_prompt = "you are a CV reviewer."
       
    prompt = f"""
    Review the following CV description:

    {candidate_desc}
    
    Evaluate how well this candidate matches the following job description:
    
    {job_description}
    
    You MUST pay attention mostly to the ROLE and the SENIORITY match between what we are looking for and the candidate's seniority, and answer ONLY with a JSON object in the following structure:
    
    {{
      "name": "Candidate Name",
      "match_percentage": number between 0 and 100 based on seniority and technologies fit with the job description ,
      "summary": "A  summary explaining the match, including relevant skills, technologies, and gaps",
      "recommended_questions" : list about recommended questions, focused on mandatory keywords (if provided)
    }}
    
    ❗️Output STRICTLY as valid JSON with {language} language content. Do NOT include any explanations, extra text, markdown formatting, or comments.
    
    Example:
    
    {{
      "name": "John Marston",
      "match_percentage": 78,
      "summary": "he has strong knowledge on AWS, he has developed using Spark, Python and knows a few database systems.",
      "recommended_questions" : [
          "What is your current role's focus on data analytics and reporting?",
          "Can you walk me through your experience with data modeling concepts?"
        ]
    }}

    {keywords_string}
    """
    
    if "offline" in execution_mode.lower():
        print(f"▶️ Using {model_source} via Ollama...")
        full_response = call_llama3_ollama(prompt, model_source, system_prompt)
    
    else:
        print(f"▶️ Using {model_source} via OpenAI API...")
        full_response = call_chatgpt_openai(prompt, model_source, system_prompt)

    #print(prompt)

    # clean markdown delimiter
    clean_response = full_response.replace("```python", "").replace("```", "").strip()
    
    #print(full_response)
    
    result = extract_json(clean_response)
    return result

def evaluate_mandatory_keywords(cv_text, mandatory_keywords):
    """
    Evaluates the percentage of mandatory keywords present in the candidate's CV text.
    
    :param cv_text: str, the candidate's CV text
    :param mandatory_keywords: list of str, mandatory keywords
    :return: str, summary of the match percentage and details of found/not found keywords
    """

    found = []
    not_found = []
    
    text = cv_text.lower()

    for kw in mandatory_keywords:
        pattern = re.escape(kw.lower())
        if re.search(rf"\b{pattern}\b", text):
            found.append(kw)
        else:
            not_found.append(kw)

    total = len(mandatory_keywords)
    matched = len(found)
    percentage = round((matched / total) * 100) if total > 0 else 0

    found_str = ", ".join(found) if found else "none"
    not_found_str = ", ".join(not_found) if not_found else "none"

    return (
        f"The candidate accomplishes {percentage}% of the mandatory keywords required: "
        f"{found_str} were found but {not_found_str} {'was' if len(not_found)==1 else 'were'} not found."
    )

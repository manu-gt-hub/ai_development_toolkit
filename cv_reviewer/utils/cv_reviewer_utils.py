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

def evaluate_candidate(model_source, candidate_desc, job_description, keywrods_string = ""):

    system_prompt = "you are a CV reviewer."
       
    prompt = f"""
    Review the following CV description:

    {candidate_desc}
    
    Evaluate how well this candidate matches the following job description:
    
    {job_description}
    
    You MUST pay attention mostly to the ROLE and the SENIORITY match between what we are looking for and the candidate's seniority, and answer ONLY with a JSON object in the following structure:
    
    {{
      "name": "Candidate Name",
      "match_percentage": number between 0 and 100,
      "summary": "A  summary explaining the match, including relevant skills, technologies, and gaps"
    }}
    
    ❗️Output STRICTLY as valid JSON. Do NOT include any explanations, extra text, markdown formatting, or comments.
    
    Example:
    
    {{
      "name": "John Marston",
      "match_percentage": 78,
      "summary": "ihe has strong knowledge on AWS, he has developed using Spark, Python and knows a few database systems."
    }}

    {keywrods_string}
    """
    
    if "llama" in model_source.lower():
        print(f"▶️ Using {model_source} via Ollama...")
        full_response = call_llama3_ollama(prompt, model_source, system_prompt)
    
    elif "gpt" in model_source.lower():
        print(f"▶️ Using {model_source} via OpenAI API...")
        full_response = call_chatgpt_openai(prompt, model_source, system_prompt)
    
    else:
        raise ValueError("Invalid model_source. Use 'llama3' or 'chatgpt'.")

    #print(prompt)

    # clean markdown delimiter
    clean_response = full_response.replace("```python", "").replace("```", "").strip()
    
    #print(full_response)
    
    result = json.loads(clean_response)
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

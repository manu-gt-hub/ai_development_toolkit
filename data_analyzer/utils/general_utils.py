import os
import time
import hashlib
import pandas as pd
import glob
from openai import OpenAI
from dotenv import load_dotenv
import warnings
import httpx
from IPython.display import display, Markdown

def hash_value(value):
    if pd.isna(value):
        return value
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

def anonymize_and_process(
    model_name,
    temperature,
    columns_to_anonymize,
    input_csv_dir,
    output_csv_dir,  
    output_file_name,
    report_file_name,
    prompt,
    show_sample=False
):
    report_lines = []
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    
    openai = OpenAI(http_client=httpx.Client(verify=False))
    openai.api_type = "openai"  # 👈 Required to resolve ambiguity

    try:
        # Find the first CSV file in the input directory
        csv_files = glob.glob(os.path.join(input_csv_dir, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in {input_csv_dir}")
        
        csv_file_path = csv_files[0]
        df = pd.read_csv(csv_file_path)
        
        if show_sample:
            display(Markdown("## Original data:\n"))
            display(df.head(1))
            
        report_lines.append(f"✅ CSV read from: {input_csv_dir}")
        report_lines.append(f"➡️ Rows: {len(df)}, Columns: {len(df.columns)}")

        # 2. Anonymize sensitive columns
        for col in columns_to_anonymize:
            if col in df.columns:
                df[col] = df[col].apply(hash_value)
                report_lines.append(f"🔒 Anonymized column: {col}")
            else:
                report_lines.append(f"⚠️ Column not found for anonymization: {col}")

        # 3. Save the anonymized CSV temporarily
        anon_csv_path = os.path.join(output_csv_dir, output_file_name)
        
        if show_sample:
            display(Markdown("## Anonymized data:\n"))
            display(df.head(1))
            
        df.to_csv(anon_csv_path, index=False)
        report_lines.append(f"📁 Anonymized CSV saved at: {anon_csv_path}")

        # 4. Upload file to OpenAI
        file_upload = openai.files.create(file=open(anon_csv_path, "rb"), purpose="assistants")
        report_lines.append(f"☁️ File uploaded to OpenAI with file_id: {file_upload.id}")

        # 5. Create a temporary assistant (if you don’t have a permanent one)
        assistant = openai.beta.assistants.create(
            name="CSV Cleaner",
            temperature=temperature,
            instructions="You are an expert in data cleansing and analysis. Use code to process CSV files.",
            tools=[{"type": "code_interpreter"}],
            model=model_name
        )

        # 6. Create thread
        thread = openai.beta.threads.create()

        # 7. Send message with prompt and attached file
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
            attachments=[{
                "file_id": file_upload.id,
                "tools": [{"type": "code_interpreter"}]
            }]
        )

        # 8. Run assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # 9. Wait for completion
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                raise Exception("❌ Assistant execution failed.")
            time.sleep(2)

        # 10. Get assistant response
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        last_response = messages.data[0].content[0].text.value
        report_lines.append("🤖 Assistant response:")
        report_lines.append(last_response)

        # 11. Save report
        report_path = os.path.join(output_csv_dir, report_file_name)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print(f"✅ Process completed. Report saved at: {report_path}")
        return report_lines

    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        print(error_message)
        report_path = os.path.join(output_csv_dir, report_file_name)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines) + "\n" + error_message)

def print_report(report):
    display(Markdown("\n===== Processing Report =====\n"))

    for line in report:
        if line.startswith('🤖 Assistant response:'):
            display(Markdown(line))
            display(Markdown("\n--- Begin Assistant Response ---\n"))
        elif line.startswith("The DataFrame contains"):
            display(Markdown(line))
            display(Markdown("\n--- End Assistant Response ---\n"))
        else:
            display(Markdown(line))
    
    display(Markdown("\n================================="))

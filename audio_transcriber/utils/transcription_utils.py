import os
import glob
import whisper
import ollama

def llm_summarization(transcription):
    # Generate meeting minutes from transcription
    system_message = "You are an assistant that produces minutes of meetings from transcripts, with summary, key discussion points, in markdown."
    user_prompt = f"Below is an extract transcript from a conversation. Please write minutes in markdown, including a summary with any relevant discussion points;\n{transcription}"
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
    )
    summary = response["message"]["content"]
    return summary

def transcribe_audio(audio_dir: str, output_dir: str, model_size: str = "medium") -> None:
    """
    Transcribe the first MP3 file found in `audio_dir` using Whisper model of size `model_size`.
    Saves transcription and summary to `output_dir`.

    Parameters:
    - audio_dir (str): Path to the directory containing MP3 files.
    - output_dir (str): Path to save transcription and summary outputs.
    - model_size (str): Whisper model size to use (default: "medium").
    """

    # 2. Create the output folder if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # 3. Find the first MP3 file
    mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
    if not mp3_files:
        raise FileNotFoundError(f"No MP3 file found in {audio_dir}")
    audio_path = mp3_files[0]
    print(f"🎧 Using audio file: {audio_path}")

    # 4. Load the Whisper model and transcribe
    print(f"🧠 Transcribing with Whisper ({model_size})... please wait, this can take several minutes...")
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)

    transcription = result["text"]
    print("✅ Transcription completed.")

    # 5. Save transcription
    transcription_path = os.path.join(output_dir, "transcription.txt")
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"📝 Transcription saved at {transcription_path}")

    # 6. Optional: summarize the text with a local or Hugging Face model
    print("🧾 Generating text summary using LLaMa 3...")
    summary = llm_summarization(transcription)

    # 7. Save summary
    summary_path = os.path.join(output_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"📄 Summary saved at {summary_path}")
    display(summary)

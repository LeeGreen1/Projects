import os
from openai import OpenAI
import requests

# Configuration for the local Ollama model
OLLAMA_BASE_URL = "http://localhost:11434"
LOCAL_MODEL_NAME = "phi3" # The model you downloaded with 'ollama pull'

def is_ollama_running():
    """Checks if the Ollama server is running."""
    try:
        response = requests.get(OLLAMA_BASE_URL)
        response.raise_for_status()
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return False

def get_ai_breakdown(brief: str, examples: list[dict]) -> str:
    """
    Sends the assignment brief to a local AI model via Ollama and gets a breakdown.

    Args:
        brief: The new assignment brief to be analyzed.
        examples: A list of past briefs and their breakdowns to use as context.

    Returns:
        A string containing the AI-generated reasoning and breakdown.
    """
    if not is_ollama_running():
        return (
            "Error: Ollama server is not running.\n"
            "Please make sure the Ollama application is running on your computer."
        )

    client = OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key='ollama',
    )

    # --- ENHANCED SYSTEM PROMPT ---
    system_prompt = (
        "You are an expert academic assistant. Your primary function is to deconstruct a university assignment brief and identify all explicit and implicit tasks. "
        "Your response MUST be in two parts, with the specified headings.\n\n"
        "1.  **Reasoning Section**: Start with the heading '### Reasoning'. In this section, explain your interpretation of the brief. Identify key academic keywords (e.g., 'analyze', 'compare', 'contrast', 'deliverable', 'submit', 'report', 'presentation'). State what you believe the core requirements are.\n\n"
        "2.  **Task Breakdown Section**: Start with the heading '### Task Breakdown'. Based on your reasoning, provide a clear, numbered list of all the tasks the student needs to complete. You must assume there are tasks to be found; do not state that no tasks were specified."
    )

    messages = [{"role": "system", "content": system_prompt}]

    for example in examples:
        structured_example_output = f"### Task Breakdown\n{example['breakdown_text']}"
        messages.append({"role": "user", "content": f"Assignment Brief:\n{example['brief_text']}"})
        messages.append({"role": "assistant", "content": structured_example_output})
    
    messages.append({"role": "user", "content": f"Please analyze this new assignment brief:\n{brief}"})

    try:
        response = client.chat.completions.create(
            model=LOCAL_MODEL_NAME,
            messages=messages,
            temperature=0.2, # Lowered temperature for more focused and deterministic output
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while contacting the local AI model: {e}"
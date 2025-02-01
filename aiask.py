import sys
import os
import re
import litellm
from litellm import completion, aspeech
from pathlib import Path
import asyncio
import itertools
import threading
import time
import shutil
import argparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import Terminal256Formatter
from pygments.util import ClassNotFound
from colorama import init as init_colorama
from colorama import Fore, Style, Back
from pydub import AudioSegment
from pydub.playback import play
import PyPDF2


init_colorama()

def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Assistant with multiple provider options")
    parser.add_argument("prompt", nargs="+", help="Your question or prompt for the AI")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI provider")
    parser.add_argument("--anthropic", action="store_true", help="Use Anthropic provider")
    parser.add_argument("--gemini", action="store_true", help="Use Gemini provider")
    parser.add_argument("--openrouter", action="store_true", help="Use OpenRouter provider")
    parser.add_argument("--sambanova", action="store_true", help="Use SambaNova provider")
    parser.add_argument("--mistral", action="store_true", help="Use Mistral provider")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama as a local provider")
    parser.add_argument("--model", help="Model to use")
    parser.add_argument("--audio", action="store_true", help="Generate audio response") 
    parser.add_argument("--play", action="store_true", help="Play audio response")
    parser.add_argument("--file", help="Input text file (to ask queries about)")
    parser.add_argument("--max-tokens", type=int, default=500, help="Maximum number of tokens in the response")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature for response generation (0.0 to 1.0)")
    parser.add_argument("--save-code", action="store_true", help="Prompt to save code blocks to a file")
    parser.add_argument('--wd', metavar='directory', default=".", type=str, help='Specify the working directory')
    return parser.parse_args()

def select_provider(args):
    """
    Determines the provider to use based on command-line arguments.
    A provider is selected if its corresponding argument is True.
    If no provider is specified, the function defaults to OpenAI.
    A model is also selected based on the provider and command-line arguments.
    A model can be explicitly specified using the --model argument.
    """
    (model, api_key) =  get_model_and_api_key(args)
    if args.model:
        model = args.model
    return model, api_key


def get_model_and_api_key(args):
    """
    Determines the model and API key to use based on command-line arguments and environment variables.

    Args:
        args: Namespace object containing command-line arguments (e.g., args.openai, args.anthropic, etc.).  Assumed to have attributes corresponding to API keys (e.g., args.openai_api_key).

    Returns:
        A tuple containing the model name and API key.

    Raises:
        ValueError: If no valid API key is found.
    """

    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")

    # Define a dictionary mapping providers to good default model names and API keys
    api_key_options = {
        "openai": ("gpt-4", openai_api_key),
        "anthropic": ("anthropic/claude-3-5-sonnet-20240620", anthropic_api_key),
        "gemini": ("gemini/gemini-1.5-flash", gemini_api_key),
        "openrouter": ("openrouter/anthropic/claude-3.5-sonnet", openrouter_api_key),
        "sambanova": ("sambanova/Meta-Llama-3.1-70B-Instruct", sambanova_api_key),
        "mistral": ("mistral/mistral-large-latest", mistral_api_key),
    }

    for provider, (model, api_key) in api_key_options.items():
        if getattr(args, provider):  # Check if the provider flag was set
            if api_key:
                return model, api_key

    # Check for API keys without provider flags being explicitly set
    for provider, (model, api_key) in api_key_options.items():
        if api_key:
            return model, api_key

    raise ValueError("No valid API key found. Please set an environment variable for one of the supported providers.")


# ANSI color codes
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"
GREY_BACKGROUND = "\033[48;5;236m"

class Spinner:
    def __init__(self, message='Loading...'):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.thread = threading.Thread(target=self.spin)
        self.running = False
        self.message = message

    def start(self):
        self.running = True
        self.thread.start()

    def spin(self):
        while self.running:
            print(next(self.spinner), end='\r')
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.thread.join()

def format_code_blocks(text):
    """Format code blocks in the text with syntax highlighting and grey background."""
    def replace_code_block(match):
        language = match.group(1) or ''
        code = match.group(2).strip()

        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = guess_lexer(code)
        except ClassNotFound:
            # Fallback to no highlighting if language is not recognized
            lexer = get_lexer_by_name('text')

        formatter = Terminal256Formatter(style='monokai')
        highlighted_code = highlight(code, lexer, formatter)

        # Remove any trailing newline and add grey background
        highlighted_code = highlighted_code.strip()

        # Get terminal width
        terminal_width, _ = shutil.get_terminal_size()

        # Pad each line to terminal width
        highlighted_lines = []
        for line in highlighted_code.split('\n'):
            # Strip ANSI escape codes for length calculation
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            padding = ' ' * (terminal_width - len(clean_line.rstrip()))
            highlighted_lines.append(f"{GREY_BACKGROUND}{line.rstrip()}{padding}{RESET}")

        highlighted_code_with_background = '\n'.join(highlighted_lines)

        return f"{Back.LIGHTBLACK_EX}{highlighted_code_with_background}{Style.RESET_ALL}"

    # Replace code blocks
    text = re.sub(r'```(\w+)?\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
    return text

def format_response(response):
    # Extract and format the response
    try:
        ai_response = response.choices[0].message.content.strip()
    except AttributeError:
        ai_response = "No response was returned."
    except Exception as e: #catch other unexpected errors
        ai_response = f"An error occurred: {e}"

    # Extract code blocks
    code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', ai_response, re.DOTALL)
    text_paragraphs = re.findall(r'(?s)(?!```)(.*?)(?=\n```|\Z)', ai_response) 

    return code_blocks, text_paragraphs, format_code_blocks(ai_response)

def get_ai_response(prompt, model, api_key, max_tokens, temperature, conversation_history, context):
    """Gets a response from the AI based on the given prompt."""
    try:

        # Start the spinner
        spinner = Spinner()
        spinner.start()
        conversation_history.append({"role": "user", "content": prompt})
        if model.startswith("ollama/"):
            response = completion(
                model=model,
                messages=conversation_history,
                api_base="http://localhost:11434",
                max_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            # Set the API key
            litellm.api_key = api_key
            # Get the AI response
            response = completion(
                model=model,
                messages=conversation_history,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        # Stop the spinner
        spinner.stop()

        code_blocks, text_paragraphs, formatted_response = format_response(response)

        # Extract cost information
        cost = response._hidden_params.get("response_cost", 0.0)
        if cost is None:
            cost = 0.0

        # Clear the spinner line
        print('\r' + ' ' * 80 + '\r', end='', flush=True)

        # Append AI response to conversation history
        conversation_history.append({"role": "assistant", "content": formatted_response})

        return formatted_response, cost, code_blocks, text_paragraphs

    except Exception as e:
        print(f"Error getting AI response: {e}")
        return None, 0, []

def save_code_to_file(code_blocks, working_directory="."):
    """Prompts the user for a filename and saves the code blocks to that file."""
    if not code_blocks:
        print("No code blocks found to save.")
        return

    filename = input(f"{Style.BRIGHT}{Fore.YELLOW}{Back.RED}Enter a filename to save the code:{Style.RESET_ALL} ").strip() 
    if not filename:
        print("No filename provided. Code will not be saved.")
        return

    full_filename = os.path.join(working_directory, filename)
    with open(full_filename, 'w') as f:
        for language, code in code_blocks:
            if language:
                f.write(f"# Language: {language}\n")
            f.write(f"{code.strip()}\n\n")

    print(f"Code has been saved to {full_filename}")


async def async_speech(input, audio_output_file):
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("Please set the OPENAI_API_KEY environment variable.")
        return

    try:
        speech_response = await aspeech(
            model="openai/tts-1",
            voice="onyx",
            input=input,
            api_key=openai_api_key,
        )
        with open(audio_output_file, "wb") as f:
            f.write(speech_response.content)
    except Exception as e:
        print(f"Error generating speech: {e}")

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


if __name__ == "__main__":
    args = parse_arguments()

    if len(sys.argv) == 1:
        print("Usage: aiask [--openai|--anthropic|--gemini|--openrouter|--sambanova|--mistral|--ollama] [--model] [--max-tokens MAX_TOKENS] [--temperature TEMPERATURE] [--save-code] 'Your question here'")
        print("If no provider is specified, the script will use the first available API key in the order: OpenAI, Anthropic, Gemini, OpenRouter, Sambanova, Mistral")
        sys.exit(1)

    # Check that the given working directory exists
    if not os.path.exists(args.wd):
        print(f"Error: The specified working directory '{args.wd}' does not exist.")
        sys.exit(1)

    try:
        if args.ollama:
            context = ""
            # If we have an input file to be usead as context, read it!
            if args.file:
                # If the path is absolute (starts with /), use it directly
                # Otherwise, join it with the working directory
                input_path = args.file if args.file.startswith('/') else os.path.join(args.wd, args.file)
                if os.path.isfile(input_path):
                    if input_path.endswith(".pdf"):
                        context = extract_text_from_pdf(input_path)
                        print(f"Extracted text from PDF: {context}...")
                    else:
                        with open(input_path, 'r') as f:
                            context = f.read().strip()
            # Setup the rest of the input to Ollama
            user_prompt = " ".join(args.prompt)
            model = args.model or "ollama/phi4:latest"
            api_key = None
            conversation_history = [{"role": "system", "content": f"""You are a helpful AI assistant. You may use the following context to extend your knowledge in order to aid you to answer the question at the end. Use a Chain of Thought process to generate a response. If you don't know the answer, just say you don't know. Don't try to make up an answer. When providing code examples, always use markdown code block syntax with language specification.\n\nContext: {context}\n"""}]
        else:
            user_prompt = " ".join(args.prompt)
            model, api_key = select_provider(args)
            context = ""
            conversation_history = [{"role": "system", "content": "You are a helpful AI assistant. When providing code examples, always use markdown code block syntax with language specification."}]
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    while True:
        response, cost, code_blocks, text_paragraphs = get_ai_response(user_prompt, model, api_key, args.max_tokens, args.temperature, conversation_history, context)

        if response:
            print(f"\nAI Response (model: {model} , cost: ${cost:.6f}):")
            print(f"\n{response}\n")

            if args.save_code and code_blocks:
                save_code_to_file(code_blocks, args.wd)
        else:
            print("No response could be generated.")

        if args.audio:
            audio_output_file = Path(__file__).parent / "aiask_speech.mp3"
            # Safely handle existing audio file
            if audio_output_file.exists():
                backup_filename = f"{audio_output_file}.bak"
                if Path(backup_filename).exists():
                    # Remove old backup if it exists
                    Path(backup_filename).unlink()
                audio_output_file.rename(backup_filename)
                print(f"Created backup file: {backup_filename}")

            print("Processing audio...")
            asyncio.run(async_speech(" ".join(text_paragraphs), str(audio_output_file))) 
            print("Audio processed!")
            if args.play:
                try:
                    sound = AudioSegment.from_file(str(audio_output_file))
                    play(sound)
                except Exception as e:
                    print(f"An unexpected error occurred while playing audio: {e}")

        if args.ollama:
            user_prompt = input("Enter another question (or 'quit' to exit): ")
            if user_prompt.lower().strip() == 'quit':
                sys.exit(0)
            else:
                continue

        sys.exit(0)

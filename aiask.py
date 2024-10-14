import sys
import os
import re
import litellm
from litellm import completion
import itertools
import threading
import time
import shutil
import argparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import Terminal256Formatter
from pygments.util import ClassNotFound

def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Assistant with multiple provider options")
    parser.add_argument("prompt", nargs="+", help="Your question or prompt for the AI")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI provider")
    parser.add_argument("--anthropic", action="store_true", help="Use Anthropic provider")
    parser.add_argument("--gemini", action="store_true", help="Use Gemini provider")
    parser.add_argument("--openrouter", action="store_true", help="Use OpenRouter provider")
    parser.add_argument("--sambanova", action="store_true", help="Use SambaNova provider")
    parser.add_argument("--max-tokens", type=int, default=500, help="Maximum number of tokens in the response")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature for response generation (0.0 to 1.0)")
    return parser.parse_args()

def select_provider(args):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")

    if args.openai and openai_api_key:
        return "gpt-4", openai_api_key
    elif args.anthropic and anthropic_api_key:
        return "anthropic/claude-3-5-sonnet-20240620", anthropic_api_key
    elif args.gemini and gemini_api_key:
        return "gemini/gemini-1.5-flash", gemini_api_key
    elif args.openrouter and openrouter_api_key:
        return "openrouter/anthropic/claude-3.5-sonnet", openrouter_api_key
    elif args.sambanova and sambanova_api_key:
        return "sambanova/Meta-Llama-3.1-70B-Instruct", sambanova_api_key
    elif openai_api_key:
        return "gpt-4", openai_api_key
    elif anthropic_api_key:
        return "anthropic/claude-3-5-sonnet-20240620", anthropic_api_key
    elif gemini_api_key:
        return "gemini/gemini-1.5-flash", gemini_api_key
    elif openrouter_api_key:
        return "openrouter/anthropic/claude-3.5-sonnet", openrouter_api_key
    elif sambanova_api_key:
        return "sambanova/Meta-Llama-3.1-70B-Instruct", sambanova_api_key
    else:
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

        return f"{GREY_BACKGROUND}{highlighted_code_with_background}{RESET}"

    # Replace code blocks
    text = re.sub(r'```(\w+)?\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
    return text

def get_ai_response(prompt, model, api_key, max_tokens, temperature):
    """Gets a response from the AI based on the given prompt."""
    try:
        # Start the spinner
        spinner = Spinner()
        spinner.start()

        # Set the API key
        litellm.api_key = api_key

        # Get the AI response
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. When providing code examples, always use markdown code block syntax with language specification."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract and format the response
        ai_response = response.choices[0].message.content.strip()
        formatted_response = format_code_blocks(ai_response)

        # Extract cost information
        cost = response._hidden_params.get("response_cost", 0.0)
        if cost is None:
            cost = 0.0

        # Stop the spinner
        spinner.stop()

        # Clear the spinner line
        print('\r' + ' ' * 80 + '\r', end='', flush=True)

        return formatted_response, cost

    except Exception as e:
        print(f"Error getting AI response: {e}")
        return None, 0

if __name__ == "__main__":
    args = parse_arguments()

    if len(sys.argv) == 1:
        print("Usage: aiask [--openai|--anthropic|--gemini|--openrouter] [--max-tokens MAX_TOKENS] [--temperature TEMPERATURE] 'Your question here'")
        print("If no provider is specified, the script will use the first available API key in the order: OpenAI, Anthropic, Gemini, OpenRouter")
        sys.exit(1)

    try:
        model, api_key = select_provider(args)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    user_prompt = " ".join(args.prompt)
    response, cost = get_ai_response(user_prompt, model, api_key, args.max_tokens, args.temperature)

    if response:
        print(f"\nAI Response (model: {model} , cost: ${cost:.6f}):")
        print(f"\n{response}\n")
    else:
        print("No response could be generated.")

    sys.exit(0)

import sys
import os
import re
import litellm
from litellm import completion
import itertools
import threading
import time
import shutil
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import Terminal256Formatter
from pygments.util import ClassNotFound

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Set your OpenAI API key
litellm.api_key = openai_api_key

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

def get_ai_response(prompt):
    """Gets a response from the AI based on the given prompt."""
    try:
        # Start the spinner
        spinner = Spinner()
        spinner.start()

        # Get the AI response
        response = completion(
            model="gpt-4",  # Using GPT-4 for better responses
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. When providing code examples, always use markdown code block syntax with language specification."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,  # Increased for more detailed responses
            temperature=0.7,  # Adjust for creativity vs. accuracy
        )

        # Extract and format the response
        ai_response = response.choices[0].message.content.strip()
        formatted_response = format_code_blocks(ai_response)

        # Stop the spinner
        spinner.stop()

        # Clear the spinner line
        print('\r' + ' ' * 80 + '\r', end='', flush=True)

        return formatted_response

    except Exception as e:
        print(f"Error getting AI response: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: aiask 'Your question here'")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    response = get_ai_response(user_prompt)

    if response:
        print("\nAI Response:")
        print(f"\n{response}\n")
    else:
        print("No response could be generated.")

    sys.exit(0)

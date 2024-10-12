import sys
import os
import re
import litellm
from litellm import completion
import itertools
import threading
import time

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
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

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
    """Format code blocks in the text."""
    def replace_code_block(match):
        code = match.group(1).strip()
        lines = code.split('\n')
        max_length = max(len(line) for line in lines)


        formatted = f"{CYAN}{'=' * (max_length + 4)}{RESET}\n"
        for line in lines:
            formatted += f"{BLUE}{line.ljust(max_length)}{RESET}\n"
        formatted += f"{CYAN}{'=' * (max_length + 4)}{RESET}"

        return f"\n{formatted}\n"

    # Replace code blocks
    text = re.sub(r'```(?:\w+)?\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
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
        print("\nAI Response:\n")
        print(response)
    else:
        print("No response could be generated.")

    sys.exit(0)

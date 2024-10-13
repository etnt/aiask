# aiask.py: Your Multi-Provider AI-Powered Copilot

`aiask.py` is a simple, yet powerful command-line tool that leverages multiple AI providers to mimic the GitHub Copilot command-line tool. It now supports OpenAI, Anthropic, Google's Gemini, and OpenRouter.

## Features

* Generates answers to your coding prompts and questions using various AI language models.
* Supports multiple AI providers: OpenAI, Anthropic, Google's Gemini, and OpenRouter.
* Simple to use, with no bells and whistles.
* Uses `litellm` for easy interaction with different AI APIs.

## Requirements

* Python 3.7 or higher
* API keys for the AI providers you want to use

## Setup

1. **Install Libraries:** Install the required libraries by running:
   ```bash
   make
   ```

2. **Obtain API Keys:** Create accounts and obtain API keys for the providers you want to use:
   - OpenAI: https://platform.openai.com/
   - Anthropic: https://www.anthropic.com/
   - Google (for Gemini): https://aistudio.google.com//
   - OpenRouter: https://openrouter.ai/

3. **Set API Keys:** Add the following lines to your `~/.bashrc` (or similar) for each provider you want to use:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   export GEMINI_API_KEY=your_gemini_api_key
   export OPENROUTER_API_KEY=your_openrouter_api_key
   ```

4. **Use the aiask script:** Modify the paths in the `aiask` script to match your setup. Move the script to a directory in your PATH. Make the script executable (`chmod +x aiask`).

## Usage

You can now specify which AI provider to use with command-line options:

```bash
aiask [--openai|--anthropic|--gemini|--openrouter] 'Your question here'
```

If no provider is specified, the script will use the first available API key in the order: OpenAI, Anthropic, Gemini, OpenRouter.

## Examples

1. Using the default provider:
   ```bash
   ❯ aiask 'What is the capital of Cameroon?'

   AI Response (gpt-4):

   The capital of Cameroon is Yaoundé.
   ```

2. Specifying a provider:
   ```bash
   ❯ aiask --gemini "List the five deepest lakes in the world." 

   AI Response (gemini/gemini-1.5-flash):

   Here are the five deepest lakes in the world, along with their approximate depths: 

   1. **Lake Baikal (Russia):** 1,642 meters (5,387 feet) 
   2. **Lake Tanganyika (Tanzania, Burundi, Democratic Republic of Congo, Zambia):** 1,470 meters (4,823 feet) 
   3. **Lake Vostok (Antarctica):** 900-1,200 meters (2,953-3,937 feet) - Note: Lake Vostok is a subglacial lake, meaning it is buried under a thick ice sheet.
   4. **Lake O'Higgins/San Martín (Chile/Argentina):** 836 meters (2,743 feet)
   5. **Lake Malawi (Malawi, Mozambique, Tanzania):** 706 meters (2,316 feet)
   ```

   This function does the following:
   1. It handles edge cases for n <= 0, n == 1, and n == 2.
   2. For n > 2, it initializes the sequence with [0, 1] and then calculates each subsequent number by adding the two preceding ones.
   3. It returns the full Fibonacci sequence up to the nth number.

   You can call this function with any positive integer to get the Fibonacci sequence up to that number of elements.
   ```

Syntax highlighting is supported for code blocks in the responses.

<img src="fibionacci.png" alt="Compute Fibionacci numbers" width="800" />

<img src="lsockets.png" alt="Listening Sockets" width="800" />

<img src="ssmac.png" alt="ss install on Mac" width="800" />

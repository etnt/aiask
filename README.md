# aiask.py: Your Multi-Provider AI-Powered Copilot

`aiask.py` is a simple, yet powerful command-line tool that leverages multiple AI providers to mimic the GitHub Copilot command-line tool. It now supports OpenAI, Anthropic, Google's Gemini, OpenRouter, Sambanova, Mistral as well as Ollama running locally.

## Features

* Generates answers to your coding prompts and questions using various AI language models.
* Supports multiple AI providers: OpenAI, Anthropic, Google's Gemini, OpenRouter and Sambanova
* Simple to use, with no bells and whistles.
* Uses `litellm` for easy interaction with different AI APIs.
* Allows customization of response length and creativity through command-line options.
* Displays the cost of each API request, helping you track usage and expenses.
* Generates and plays audio responses using OpenAI's text-to-speech API.

## Requirements

* Python 3.7 or higher
* API keys for the AI providers you want to use
* `pydub` might require `ffmpeg` to be installed

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
   - Sambanova: https://cloud.sambanova.ai/
   - Mistral: https://mistral.ai/

3. **Set API Keys:** Add the following lines to your `~/.bashrc` (or similar) for each provider you want to use:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   export GEMINI_API_KEY=your_gemini_api_key
   export OPENROUTER_API_KEY=your_openrouter_api_key
   export SAMBANOVAS_API_KEY=your_sambanova_api_key
   export MISTRAL_API_KEY=your_mistral_api_key
   ```

4. **Use the aiask script:** Modify the paths in the `aiask` script to match your setup. Move the script to a directory in your PATH. Make the script executable (`chmod +x aiask`).

## Usage

You can now specify which AI provider to use with command-line options, as well as customize the response:

```bash
aiask [--openai|--anthropic|--gemini|--openrouter|--sambanova|--mistral|--ollama] [--model MODEL] [--save-code] [--max-tokens MAX_TOKENS] [--temperature TEMPERATURE] [--wd WORKING_DIRECTORY] [--audio] [--play] 'Your question here'
```

- If no provider is specified, the script will use the first available API key in the order: OpenAI, Anthropic, Gemini, OpenRouter, Sambanova.
- `--model`: Will override the default model used for the choosen provider.
- `--save-code`: In case program code is returned, prompt for a filename where to save the code.
- `--max-tokens`: Set the maximum number of tokens in the response (default: 500).
- `--temperature`: Set the temperature for response generation, controlling creativity (default: 0.2, range: 0.0 to 1.0).
- `--wd`: Set the working directory for the command. i.e where files will be stored (default: current directory).
- `--audio`: Generates an audio file of the AI's response using OpenAI's text-to-speech API.  Requires an OpenAI API key. The audio file will be saved as `aiask_speech.mp3` in the same directory as `aiask.py`.
- `--play`: Plays the generated audio file.  Uses `pydub`.

## Examples

1. Using the default provider:
   ```bash
   ❯ aiask 'What is the capital of Cameroon?'

   AI Response (model: gpt-4 , cost: $0.001740):

   The capital of Cameroon is Yaoundé.

   ```

2. Specifying a provider:
   ```bash
   ❯ aiask --gemini "List the five deepest lakes in the world." 

   AI Response (model: gemini/gemini-1.5-flash , cost: $0.000054):

   Here are the five deepest lakes in the world, along with their approximate depths: 

   1. **Lake Baikal (Russia):** 1,642 meters (5,387 feet) 
   2. **Lake Tanganyika (Tanzania, Burundi, Democratic Republic of Congo, Zambia):** 1,470 meters (4,823 feet) 
   3. **Lake Vostok (Antarctica):** 900-1,200 meters (2,953-3,937 feet) - Note: Lake Vostok is a subglacial lake, meaning it is buried under a thick ice sheet.
   4. **Lake O'Higgins/San Martín (Chile/Argentina):** 836 meters (2,743 feet)
   5. **Lake Malawi (Malawi, Mozambique, Tanzania):** 706 meters (2,316 feet)

   ```

3. Using custom max tokens and temperature:
   ```bash
   ❯ aiask --openai --max-tokens 100 --temperature 0.8 "Write a short poem about coding"

   AI Response (model: gpt-4 , cost: $0.007170):

   In realms of logic, we create,
   Lines of code, we orchestrate.
   Bugs and errors, we navigate,
   With each compile, we elevate.
   Syntax dances, algorithms flow,
   In this digital world we grow.
   From simple scripts to complex schemes,
   Coding brings life to our dreams.

   ```

4. Generating and playing audio:
   ```bash
   ❯ aiask --openai --audio --play "What is the meaning of life?"
   ```

Syntax highlighting is supported for code blocks in the responses as well as the possibility to save the code to file.

<img src="save-code.png" alt="Compute Fibionacci numbers" width="800" />

<img src="lsockets.png" alt="Listening Sockets" width="800" />

<img src="ssmac.png" alt="ss install on Mac" width="800" />

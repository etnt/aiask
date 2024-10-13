# aiask.py: Your AI-Powered Copilot

`aiask.py` is a simple command-line tool that leverages OpenAI's API to mimic the
githubs `gh copilot` command line tool. 

## Features

*   Generates answers to your coding prompts and questions using OpenAI's language models.
*   Simple , with no bells and whistles.
*   Uses `litellm` for easy interaction with the OpenAI API.

## Requirements

*   Python 3.7 or higher
*   An OpenAI API key (obtain one at [https://platform.openai.com/](https://platform.openai.com/))


## Setup

1.  **Install Libraries:** Install the required libraries by running:
    ```bash
    make
    ```
2.  **Obtain an OpenAI API Key:** Create an account at [https://platform.openai.com/](https://platform.openai.com/) and obtain your API key.

3.  **Set API Key:**  Add: `export OPENAI_API_KEY=xxxx` to your ~/.bashrc (or similar).

4.  **Use the aiask script:** Modify the paths in the `aiask` script to match your setup. Move the script to a directory in your PATH. Make the script executable (`chmod +x aiask`)

## Example

Just ask any question:

```bash
❯ aiask what is the capital of Kamerun?

AI Response: 

The capital of Cameroon is Yaoundé. 
```

Syntax highlighting is supported:

<img src="fibionacci.png" alt="Compute Fibionacci numbers" width="800" /> 

More examples:

<img src="lsockets.png" alt="Listening Sockets" width="800" /> 
<img src="ssmac.png" alt="ss install on Mac" width="800" /> 


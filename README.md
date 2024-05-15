
# py-cli-chat

## Description
The purpose of this project is to provide a quick and simple CLI for evaluating different LLM (Large Language Model) APIs and models, as well as exploring how various experts and users may interact in an LLM dialog.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/py-cli-expert-chat.git
    cd py-cli-expert-chat
    ```
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
The behavior of the chatbot is controlled by several JSON configuration files. These configurations are combined to create the prompt for the chat:

1. `config.json`: This file contains the main configuration for the chatbot. It specifies which LLM API, instruction set, user, expert, and context to use. It also controls the history length and whether to use text-to-speech.
2. `instruction_sets.json`,`experts.json`, `users.json`, `contexts.json`: These files contain the data for the different instruction sets, experts, users, and contexts that can be used..
3. `llm_apis.json`: This file contains the configuration for the different LLM APIs and models that can be used.

## API Keys
Create a file named `api_keys.json` in the root directory of the project. This file should contain your API keys. Below is an example structure for `api_keys.json`:

```json
    [
        {
        "name": "API Name",
        "key": "Your API Key"
        }
    ]
```

## Usage
To start the application, run:
```sh
python app.py
```

To quit the application, simply enter `quit` for the chat prompt.

## License
This project is licensed under the MIT License.

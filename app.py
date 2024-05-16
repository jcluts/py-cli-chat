import json
import re
import requests
from pydub import AudioSegment
from pydub.playback import play
import io

message_history = []
system_message = ""

def load_json_config(file_path):
    """Loads JSON configuration file."""
    with open(file_path, "r") as file:
        return json.load(file)

def build_system_message(instruction_set, expert, user, context_description):
    """Constructs and returns a system message based on expert and user details."""
    instructions = " ".join(instruction_set["instructions"])
    expert_description = " ".join(expert["description"])

    system_message_content = instructions.format(
        expertName=expert["name"],
        expertDescription=expert_description,
        context=context_description,
        userName=user["name"],
        userDescription=" ".join(user["description"])
    )
    return system_message_content

def text_to_speech_elevenlabs(text, elevenlabs_api_key, voice_id):
    """Converts text to speech using ElevenLabs API and plays it."""
    api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {"Accept": "audio/mpeg", "xi-api-key": elevenlabs_api_key}
    clean_text = re.sub(r"\*[^*]+\*", "", text).strip()
    data = {
        "text": clean_text,
        "model_id": "eleven_multilingual_v2",
        "voice_contexts": {"stability": 0.5, "similarity_boost": 0.75, "use_speaker_boost": True},
        "output_format": "mp3_44100_128", 
        "optimize_streaming_latency": 0
    }

    # print(f"Sending to ElevenLabs API: {data}")

    response = requests.post(api_url, json=data, headers=headers)
    # response.raise_for_status()
   

    if response.status_code == 200:
        play_audio(response.content)
    else:
        raise ValueError(f"An error occurred: {response.json()}")

def play_audio(audio_bytes):
    """Plays audio from bytes."""
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    play(audio)

def send_to_llm_api(messages, llm_config, api_key):
    """Sends messages to the LLM API and returns the processed response."""
    api_endpoint = llm_config['llm_endpoint']
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    selected_model_index = llm_config["llm_selected_model"]
    data = json.dumps({
        "model": llm_config["llm_models"][selected_model_index],
        "messages": messages,
        "max_tokens": llm_config["llm_max_tokens"],
        "temperature": llm_config["llm_temperature"]
    })

    # print(f"Sending to LLM API: {data}")

    response = requests.post(api_endpoint, headers=headers, data=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise ValueError(f"An error occurred: {response.json()['error']['message']}")

def main():
    """Main function to run the chatbot."""
    config = load_json_config("config.json")
    llm_apis = load_json_config("llm_apis.json")
    instruction_sets = load_json_config("instruction_sets.json")
    experts = load_json_config("experts.json")
    users = load_json_config("users.json")
    contexts = load_json_config("contexts.json")
    api_keys = load_json_config("api_keys.json")

    llm_config = llm_apis[config["llm_api"]]
    instruction_set = instruction_sets[config["instruction_set"]]
    expert = experts[config["expert"]]
    user = users[config["user"]]
    context = contexts[config["context"]]

    elevenlabs_voice_id = config["tts_voices"][expert["tts_voice"]]["id"]

    context_description = " ".join(context["description"])
    context_description = context_description.format(userName=user["name"], expertName=expert["name"])

    system_message_content = build_system_message(instruction_set, expert, user, context_description)
    system_message = {"role": "system", "content": system_message_content}

    llm_api_key = api_keys[llm_config["llm_api_key"]]["key"]
    elevenlabs_api_key = api_keys[config["tts_api_key"]]["key"]

    print(f"\n{context_description}\n")

    message_history = []

    while True:
        user_input = input(f"{user['name']}: ").strip()
        if user_input.lower() == "quit":
            print("Exiting chatbot.")
            break
        elif user_input.lower() == "rb":
            if len(message_history) >= 2:
                message_history.pop()
                message_history.pop()
                print("\nThe last two messages have been removed.\n")
                continue
        elif user_input.lower() == "reset":
            message_history.clear()
            print("\nChat history has been reset.\n")
            continue
        
        history_length = config["history_length"]

        messages_to_send = []
        messages_to_send.append(system_message)
        messages_to_send.extend(message_history[-history_length:])
        messages_to_send.append({"role": "user", "content": user_input})
        
        response = send_to_llm_api(messages_to_send, llm_config, llm_api_key)

        print(f"\n{expert['name']}: {response}\n")

        if config.get("use_tts"):
            text_to_speech_elevenlabs(response, elevenlabs_api_key, elevenlabs_voice_id)

        message_history.extend([{"role": "user", "content": user_input}, {"role": "assistant", "content": response}])


if __name__ == "__main__":
    main()

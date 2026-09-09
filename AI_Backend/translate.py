import riva.client
from config import NVIDIA_API_KEY , NVIDIA_RIVA_SERVER , NVIDIA_RIVA_FUNCTION_ID

def _get_riva_auth():
    metadata = [
        [
            "function-id", NVIDIA_RIVA_FUNCTION_ID
        ],
        [
            "authorization", f"Bearer {NVIDIA_API_KEY}"
        ]
    ]

    return riva.client.Auth(uri = NVIDIA_RIVA_SERVER , use_ssl = True , metadata_args = metadata)

def translate_text(text: str, source_language: str="hi", target_language: str="en") -> str:
    auth = _get_riva_auth()
    nmt_client = riva.client.NeuralMachineTranslationClient(auth)

    response = nmt_client.translate(
        texts=[text] ,
        model = "",
        source_language = source_language ,
        target_language = target_language
    )

    translated_text = response.translations[0].text
    return translated_text.strip()


def list_supported_languages():
    auth = _get_riva_auth()
    nmt_client = riva.client.NeuralMachineTranslationClient(auth)
    config_response = nmt_client.get_config("")
    return config_response

if __name__ == "__main__":
    # Example usage
    text_to_translate = "नमस्ते, आप कैसे हैं?"
    try:
        translated = translate_text(text_to_translate, source_language="hi", target_language="en")
        print(f"Original Text: {text_to_translate}")
        print(f"Translated Text: {translated}")
    except Exception as e:
        print(f"Error occurred: {e}")

    supported_languages = list_supported_languages()
    print("Supported Languages:", supported_languages)

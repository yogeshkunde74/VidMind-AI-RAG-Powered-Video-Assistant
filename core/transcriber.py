# import whisper
# import os
# import requests

# WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

# SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
# SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
# SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

# _model = None



# def load_model():

#     global _model

#     if _model is None:
#         print(f"loading Whhisper model ...")
#         _model = whisper.load_model(WHISPER_MODEL)
#         print("whisper model loaded successfully")
#     return _model

# def transcribe_chunk_whisper(chunk_path : str) -> str:

#     model = load_model()

#     result = model.transcribe(chunk_path, task="transcribe")
#     return result["text"]

#     # task = "translate" if translate else "transcribe"
#     # result = model.transcribe(chunk_path, task = task)
#     # return result['text']

# def transcribe_chunk_sarvam(chunk_path: str) -> str:
#     if not SARVAM_API_KEY:
#         raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

#     headers = {"api-subscription-key": SARVAM_API_KEY}

#     with open(chunk_path, "rb") as f:
#         files = {"file": (os.path.basename(chunk_path), f, "audio/wav")}
#         data = {"model": SARVAM_MODEL, "with_diarization": "false"}
#         response = requests.post(
#             SARVAM_STT_TRANSLATE_URL,
#             headers = headers,
#             files = files,
#             data = data,
#             timeout = 300,
#         )
#     response.raise_for_status()

#     return response.json().get("transcript", "")

# def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
#     """
#     Rout one chunk to whisper or Sarvam depending on language chooice.
#     - english - whisper (local model)
#     - hinglish - sarvam (translates to engliah while transcribing)
#     """

#     if language.lower() == "hinglish":
#         return transcribe_chunk_sarvam(chunk_path)
#     return transcribe_chunk_whisper(chunk_path)

# def transcribe_all(chunks : list, language: str = "english") -> str:
#     full_transcript = ""

#     engine = "Sarvam AI" if language.lower() == "hinglish" else "whisper"
#     print(f"Using {engine} for transcription.")

#     for i, chunk in enumerate(chunks):
#         print(f"Transcribing chunk {i+1}/{len(chunks)}...")
#         text = transcribe_chunk(chunk, language=language)

#         full_transcript += text + " "

#     print("Transcription completed")

#     return full_transcript.strip()   

# 2ND VERSION

import whisper
import os
import requests
# -----------------------------
# Whisper Configuration
# -----------------------------
WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "small"
)
# -----------------------------
# Sarvam AI Configuration
# -----------------------------
SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

SARVAM_STT_TRANSLATE_URL = (
    "https://api.sarvam.ai/speech-to-text-translate"
)

SARVAM_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v2.5"
)


# Whisper model cache
_model = None


# -----------------------------
# Load Whisper Model
# -----------------------------

def load_model():

    global _model

    if _model is None:

        print(
            f"Loading Whisper model: {WHISPER_MODEL}..."
        )

        _model = whisper.load_model(
            WHISPER_MODEL
        )

        print(
            "Whisper model loaded successfully"
        )

    return _model


# -----------------------------
# Whisper Transcription
# -----------------------------

def transcribe_chunk_whisper(
    chunk_path: str
) -> str:

    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=False
    )

    return result["text"]


# -----------------------------
# Sarvam AI Transcription
# -----------------------------

def transcribe_chunk_sarvam(
    chunk_path: str
) -> str:

    # Check API key
    if not SARVAM_API_KEY:

        raise RuntimeError(
            "SARVAM_API_KEY is not set "
            "in environment / .env"
        )


    # Sarvam expects headers as a dictionary
    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }


    print(
        f"Sending to Sarvam: "
        f"{os.path.basename(chunk_path)}"
    )


    # Open audio file
    with open(chunk_path, "rb") as f:

        files = {
            "file": (
                os.path.basename(chunk_path),
                f,
                "audio/wav"
            )
        }


        # Request parameters
        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }


        # Send request
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=300
        )


    # ---------------------------------
    # Debug API errors
    # ---------------------------------

    if not response.ok:

        print(
            "\n========== SARVAM ERROR =========="
        )

        print(
            "Status code:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        print(
            "==================================\n"
        )


    # Raise HTTP error if request failed
    response.raise_for_status()


    # Convert JSON response
    result = response.json()


    print("Sarvam response received successfully.")


    return result.get(
        "transcript",
        ""
    )


# -----------------------------
# Select Transcription Engine
# -----------------------------

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    """
    Route one chunk to Whisper or Sarvam.

    english:
        Whisper local model

    hinglish:
        Sarvam AI
    """

    if language.lower() == "hinglish":

        return transcribe_chunk_sarvam(
            chunk_path
        )

    return transcribe_chunk_whisper(
        chunk_path
    )


# -----------------------------
# Transcribe All Chunks
# -----------------------------

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = ""


    # Select engine
    if language.lower() == "hinglish":

        engine = "Sarvam AI"

    else:

        engine = "Whisper"


    print(
        f"Using {engine} for transcription."
    )


    # Process every chunk
    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk "
            f"{i + 1}/{len(chunks)}..."
        )


        text = transcribe_chunk(
            chunk,
            language=language
        )


        # Add transcript
        full_transcript += text + " "


    print(
        "Transcription completed"
    )


    return full_transcript.strip()

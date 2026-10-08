import yt_dlp
from pydub import AudioSegment
import os


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

        # Change extension to wav
        filename = os.path.splitext(filename)[0] + ".wav"

    return filename


def convert_to_wav(input_path: str) -> str:

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(input_path)

    # Convert to mono and 16 kHz
    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
        .set_sample_width(2)
    )

    audio.export(
        output_path,
        format="wav"
    )

    return output_path


def chunk_audio(
    wav_path: str,
    chunk_seconds: int = 30
) -> list:

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_seconds * 1000

    chunks = []

    for i, start in enumerate(
        range(0, len(audio), chunk_ms)
    ):

        chunk = audio[start:start + chunk_ms]

        chunk = (
            chunk
            .set_channels(1)
            .set_frame_rate(16000)
            .set_sample_width(2)
        )

        chunk_path = (
            f"{os.path.splitext(wav_path)[0]}"
            f"_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:

    if (
        source.startswith("http://")
        or source.startswith("https://")
    ):

        print(
            "Detected YouTube URL. "
            "Downloading audio..."
        )

        wav_path = download_youtube_audio(source)
        wav_path = convert_to_wav(wav_path)

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(
        wav_path,
        chunk_seconds=29
    )

    print(
        f"Audio ready - {len(chunks)} chunk(s) created."
    )

    return chunks
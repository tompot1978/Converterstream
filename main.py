import streamlit as st
from pytube import YouTube
import os
import tempfile
import whisper

# Custom CSS to create a box around the app interface
st.markdown("""
    <style>
    .reportview-container .main .block-container {
        padding-top: 5rem;
        padding-right: 5rem;
        padding-left: 5rem;
        padding-bottom: 5rem;
        border: 2px solid #79aea3;
        border-radius: 20px;
        background-color: white;
    }
    .reportview-container {
        background: #f0f0f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: 2px solid #79aea3;
        color: white;
        background-color: #79aea3;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: white;
        color: #79aea3;
    }
    </style>
""", unsafe_allow_html=True)

def download_youtube_video(url, file_name, format_choice, save_path):
    try:
        yt = YouTube(url)
        if format_choice in ['.mp3', '.mp4']:
            video = yt.streams.filter(only_audio=(format_choice == '.mp3')).first()
            if video is None:
                return None, "Requested format not available for this video."
            output_file = video.download(output_path=save_path)
            final_path = os.path.join(save_path, file_name + format_choice)
            os.rename(output_file, final_path)
            return final_path, "Download successful! Click below to download the file."

        elif format_choice == '.txt':
            video = yt.streams.filter(only_audio=True).first()
            if video is None:
                return None, "Audio format not available for this video."
            temp_dir = tempfile.mkdtemp()
            output_file = video.download(output_path=temp_dir)
            audio_path = os.path.join(temp_dir, 'temp_audio.mp3')
            if os.path.exists(audio_path):
                os.remove(audio_path)
            os.rename(output_file, audio_path)

            # Extract audio and convert to text
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            final_text = result["text"]

            final_path = os.path.join(save_path, file_name + '.txt')
            with open(final_path, 'w') as file:
                file.write(final_text)

            # Clean up temporary audio file and directory
            os.remove(audio_path)
            os.rmdir(temp_dir)

            return final_path, "Transcription successful! Click below to download the file."

    except Exception as e:
        return None, f'Error: {e}'

# Streamlit UI
st.title("YouTube Video Downloader & Converter")

url = st.text_input("YouTube URL:")
file_name = st.text_input("Save File As:")
format_choice = st.selectbox("Choose Format:", ['.mp3', '.mp4', '.txt'])
start_button = st.button("Download & Convert")

if start_button:
    if url and file_name and format_choice:
        save_path = tempfile.mkdtemp()
        file_path, result = download_youtube_video(url, file_name, format_choice, save_path)
        if file_path:
            with open(file_path, "rb") as file:
                btn = st.download_button(
                    label="Download File",
                    data=file,
                    file_name=file_name + format_choice,
                    mime="audio/mpeg" if format_choice == '.mp3' else "video/mp4" if format_choice == '.mp4' else "text/plain"
                )
            st.success(result)
        else:
            st.error(result or "An error occurred.")
    else:
        st.error("Please provide a URL, file name, and select a format.")

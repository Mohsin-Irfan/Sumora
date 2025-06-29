import streamlit as st
from video_utils import extract_video_id, get_transcript, extract_metadata, download_thumbnail
from summarize_text import summarize_text
import os
import base64
import whisper
from gtts import gTTS


model = whisper.load_model("base")


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("summary_audio.mp3")


def get_binary_file_download_link(file_path, file_label='Download File'):
    with open(file_path, "rb") as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'
    return href


def transcribe_local_video(video_file_path):
    result = model.transcribe(video_file_path)
    return result["text"]


def main():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;700&display=swap');


            html, body, .stApp {
                background-color: #0e1a2b;
                color: #f5f5f5 !important;
                font-family: 'Ubuntu', sans-serif;
            }


            .title-style {
                text-align: center;
                font-size: 46px;
                font-weight: 700;
                margin-top: 20px;
                margin-bottom: 10px;
                background: linear-gradient(to right, #5bc0eb, #00ffff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }


            .tagline {
                text-align: center;
                font-size: 18px;
                color: #5bc0eb;
                margin-bottom: 30px;
            }


            .gold-card {
                background: #1c2c45;
                border: 1px solid #5bc0eb;
                padding: 25px;
                border-radius: 16px;
                color: #f5f5f5 !important;
                box-shadow: 0 4px 16px rgba(91, 192, 235, 0.3);
                margin-bottom: 25px;
            }


            .stButton>button {
                background: linear-gradient(to right, #00ffff, #5bc0eb);
                color: #0e1a2b;
                font-weight: bold;
                border-radius: 12px;
                border: none;
                padding: 0.65em 1.5em;
                font-size: 16px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }


            .stButton>button:hover {
                background: linear-gradient(to right, #5bc0eb, #00ffff);
                transform: scale(1.03);
            }


            .stTextInput>div>div>input,
            .stTextArea>div>textarea {
                background-color: #2e3d56 !important;
                color: #f5f5f5 !important;
                border: 1px solid #5bc0eb !important;
            }


            input::placeholder {
                color: #999 !important;
            }


            label, .stRadio div, .stTextInput, .stFileUploader, .stRadio label span, .stRadio label {
                color: #f5f5f5 !important;
            }


            .stRadio [role="radiogroup"] > label > div,
            .stCheckbox > div {
                border: 1px solid #5bc0eb !important;
                background-color: #1c2c45 !important;
            }


            .stRadio [role="radiogroup"] > label > div:has(input:checked),
            .stCheckbox > div:has(input:checked) {
                background-color: #5bc0eb !important;
                border: 1px solid #00ffff !important;
            }
        </style>


        <div class='title-style'>✨ Sumora</div>
        <div class='tagline'>Smarter Summaries. Sharper Focus.</div>
    """, unsafe_allow_html=True)


    st.markdown("---")


    source = st.radio("📤 Choose Input Method:", ["YouTube URL", "Upload Video File"])
    transcript = ""
    title = ""
    channel = ""


    if source == "YouTube URL":
        url = st.text_input("📺 Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=example")
        if url:
            video_id = extract_video_id(url)
            title, channel = extract_metadata(url)
            download_thumbnail(video_id)
            transcript = get_transcript(video_id)
    else:
        uploaded_video = st.file_uploader("🎥 Upload a video file", type=["mp4", "mov", "avi"])
        if uploaded_video:
            with open("uploaded_video.mp4", "wb") as f:
                f.write(uploaded_video.read())
            transcript = transcribe_local_video("uploaded_video.mp4")
            title = "Uploaded Video"
            channel = "Local Upload"
            st.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=200)


    if transcript:
        tts_enabled = st.checkbox("🔊 Enable Text-to-Speech")
        show_transcript = st.checkbox("📜 Show Full Transcript")
        show_metadata = st.checkbox("ℹ️ Show Metadata (Title & Channel)", value=True)
        show_raw_text = st.checkbox("🧾 Show Raw Extracted Text")
        show_word_count = st.checkbox("🔢 Show Word Count")


        if st.button("🚀 Generate Summary"):
            with st.spinner('⏳ Processing... Please wait.'):
                summary = summarize_text(transcript)


                if show_metadata:
                    st.markdown(f"""
                        <div class='gold-card'>
                            <strong>📌 Title:</strong> {title}<br>
                            <strong>🎙️ Channel:</strong> {channel}
                        </div>
                    """, unsafe_allow_html=True)


                if show_word_count:
                    st.markdown(f"<p style='color:#5bc0eb;'>🧮 Word Count: {len(transcript.split())}</p>", unsafe_allow_html=True)


                st.markdown("<h3 style='color:#5bc0eb;'>🧠 Summary</h3>", unsafe_allow_html=True)
                st.markdown(f"<div class='gold-card'>{summary.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)


                with open("summary.txt", "w", encoding='utf-8') as f:
                    f.write(summary)
                st.markdown(get_binary_file_download_link("summary.txt", "💾 Download Summary (.txt)"), unsafe_allow_html=True)


                if tts_enabled:
                    text_to_speech(summary)
                    st.audio("summary_audio.mp3")


                if show_transcript:
                    st.markdown("<h4 style='color:#5bc0eb;'>📜 Full Transcript</h4>", unsafe_allow_html=True)
                    st.text_area("Transcript", value=transcript, height=300)


                if show_raw_text:
                    st.markdown("<h4 style='color:#5bc0eb;'>🧾 Raw Extracted Transcript</h4>", unsafe_allow_html=True)
                    st.code(transcript, language='text')


if __name__ == "__main__":
    main()
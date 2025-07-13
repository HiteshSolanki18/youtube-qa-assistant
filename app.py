__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from services.transcript_service import get_transcript, extract_video_id
from services.vector_store_service import split_text, setup_vector_store
from chains.query_chain import build_chain
import sqlite3

print("sqlite_version",sqlite3.sqlite_version)

st.set_page_config(page_title="YouTube Q&A", layout="wide")
st.title("YouTube Video Q&A with AI")

# Initialize session state
if "chain" not in st.session_state:
    st.session_state.chain = None
if "video_url" not in st.session_state:
    st.session_state.video_url = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None

# ========== LEFT SIDEBAR: YouTube Input & Q&A ========== #
with st.sidebar:
    st.header("Video Input + Q&A")

    # YouTube URL form
    with st.form("video_form"):
        youtube_url = st.text_input("Enter YouTube video URL")
        submitted = st.form_submit_button("Submit Video")
        if submitted:
            video_id = extract_video_id(youtube_url)
            print("Video Id: ", extract_video_id(youtube_url))
            if not video_id:
                st.error("Invalid YouTube URL")
            else:
                with st.spinner("Fetching and processing transcript..."):
                    try:
                        transcript = get_transcript(video_id)
                        texts = split_text(transcript)
                        retriever = setup_vector_store(video_id, texts)
                        chain = build_chain(retriever)

                        st.session_state.video_url = youtube_url
                        st.session_state.video_id = video_id
                        st.session_state.chain = chain

                        st.success("Video processed! Ask your questions below.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Q&A Section (shown only if video is processed)
    if st.session_state.chain and st.session_state.video_url:
        st.markdown("#### Ask a Question About the Video")
        with st.form("question_form"):
            question = st.text_input("Your question")
            asked = st.form_submit_button("Ask")
            if asked and question:
                with st.spinner("Thinking..."):
                    try:
                        answer = st.session_state.chain.invoke(question)
                        st.success(answer)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# ========== RIGHT SIDE: Embedded YouTube Video ========== #
if st.session_state.video_url and st.session_state.video_id:
    st.markdown("#### Video Preview")
    st.components.v1.html(
        f"""
        <iframe width="640" height="360" 
                src="https://www.youtube.com/embed/{st.session_state.video_id}" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen></iframe>
        """,
        height=370,
    )

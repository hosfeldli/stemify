import streamlit as st
import os
import subprocess

def page_config():
    st.set_page_config(
        page_title="Stemify",
        page_icon="🎶",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def save_uploaded_file(uploaded_file):
    try:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def separate_audio(file_path):
    try:
        # Ensure the separated output directory exists
        output_dir = os.path.join("uploads", "separated")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Run the demucs command with a progress bar
        progress_bar = st.progress(0)
        with st.spinner("Generating stems..."):
            process = subprocess.Popen(["python3", "-m", "demucs.separate", "-o", output_dir, file_path], 
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            for line in process.stdout:
                line = line.strip()
                if "%" in line:
                    progress = int(line.split("%")[0])
                    progress_bar.progress(progress)
        process.wait()

        # The output will be in a directory named after the model used (default is htdemucs)
        model_name = "htdemucs"
        output_dir = os.path.join(output_dir, model_name, os.path.basename(file_path).rsplit('.', 1)[0])

        return output_dir
    except Exception as e:
        st.error(f"Error separating audio: {e}")
        return None

def main():
    page_config()
    st.title("Stemify")
    st.subheader("Generate the root stems of songs")
    mp3_file = st.file_uploader("Upload an mp3 file", type=["mp3"])

    if mp3_file:
        st.write("MP3 file uploaded successfully.")
        
        file_path = save_uploaded_file(mp3_file)
        
        if file_path:
            output_dir = separate_audio(file_path)
            
            if output_dir:
                st.write("Separation successful.")
                
                # Display and provide download options for all stem files
                stem_files = ["drums.wav", "bass.wav", "other.wav", "vocals.wav"]
                for stem in stem_files:
                    stem_path = os.path.join(output_dir, stem)
                    if os.path.exists(stem_path):
                        with st.container(border=True):
                            st.audio(stem_path, format="audio/wav", start_time=0)
                            st.download_button(label=f"Download {stem[:-4].capitalize()}", 
                                            data=open(stem_path, "rb"), 
                                            file_name=stem)

if __name__ == "__main__":
    main()

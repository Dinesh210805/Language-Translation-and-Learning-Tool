import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import tempfile
import time
from deep_translator import GoogleTranslator
from streamlit_lottie import st_lottie
import requests
import json
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LANGUAGES = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese': 'zh',
    'Tamil': 'ta'  # Added Tamil support
}

def voice_translation_interface():
    try:
        # Enhanced styling
        st.markdown("""
            <style>
            .voice-container {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
                border-radius: 20px;
                padding: 2.5rem;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin: 1.5rem 0;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            
            .pulse-button {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(145deg, #6C63FF, #4A90E2);
                position: relative;
                animation: pulse 2s infinite;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                border: none;
                box-shadow: 0 0 25px rgba(108, 99, 255, 0.4);
            }
            
            @keyframes pulse {
                0% { transform: scale(1); box-shadow: 0 0 25px rgba(108, 99, 255, 0.4); }
                50% { transform: scale(1.05); box-shadow: 0 0 35px rgba(108, 99, 255, 0.6); }
                100% { transform: scale(1); box-shadow: 0 0 25px rgba(108, 99, 255, 0.4); }
            }
            
            .status-indicator {
                padding: 0.8rem 1.5rem;
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.1);
                margin: 1.2rem 0;
                text-align: center;
                transition: all 0.3s ease;
                border-left: 4px solid #6C63FF;
            }
            
            .translation-result {
                background: linear-gradient(135deg, rgba(108, 99, 255, 0.1), rgba(74, 144, 226, 0.05));
                border-radius: 15px;
                padding: 2rem;
                margin: 1.5rem 0;
                border-left: 4px solid #6C63FF;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }

            .stSelectbox {
                background: rgba(255, 255, 255, 0.05) !important;
                border-radius: 10px !important;
                border: 1px solid rgba(108, 99, 255, 0.2) !important;
                padding: 5px !important;
            }

            .stSelectbox:hover {
                border: 1px solid rgba(108, 99, 255, 0.5) !important;
                box-shadow: 0 0 15px rgba(108, 99, 255, 0.2) !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <h1 style='text-align: center; color: #6C63FF; margin-bottom: 2rem;'>
                🎙️ Real-Time Voice Translation
            </h1>
        """, unsafe_allow_html=True)

        # Initialize audio system if not already done
        if 'audio_system_initialized' not in st.session_state:
            try:
                pygame.mixer.init()
                st.session_state.audio_system_initialized = True
            except Exception as e:
                st.error(f"Failed to initialize audio system: {str(e)}")
                return

        # Language selection with improved layout and error handling
        try:
            # Enhanced language selection with icons
            def get_language_icon(lang):
                icons = {
                    'English': '🇬🇧', 'Spanish': '🇪🇸', 'French': '🇫🇷',
                    'German': '🇩🇪', 'Italian': '🇮🇹', 'Portuguese': '🇵🇹',
                    'Russian': '🇷🇺', 'Japanese': '🇯🇵', 'Korean': '🇰🇷',
                    'Chinese': '🇨🇳', 'Tamil': '🇮🇳'
                }
                return icons.get(lang, '🌐')

            col1, col2 = st.columns(2)
            with col1:
                source_lang = st.selectbox(
                    "Speak in:",
                    list(LANGUAGES.keys()) if 'LANGUAGES' in globals() else ['English'],
                    key="voice_source_lang",
                    format_func=lambda x: f"{get_language_icon(x)} {x}"
                )
            with col2:
                available_targets = [lang for lang in (LANGUAGES.keys() if 'LANGUAGES' in globals() else ['Spanish']) 
                                  if lang != source_lang]
                target_lang = st.selectbox(
                    "Translate to:",
                    available_targets,
                    key="voice_target_lang",
                    format_func=lambda x: f"{get_language_icon(x)} {x}"
                )

            # Voice recording interface with animation
            st.markdown('<div class="voice-container">', unsafe_allow_html=True)
            
            # Center the recording button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Load animation with fallback
                def load_lottie_url(url: str) -> Optional[Dict]:
                    try:
                        r = requests.get(url)
                        if r.status_code != 200:
                            return None
                        return r.json()
                    except Exception as e:
                        logger.error(f"Failed to load animation: {str(e)}")
                        return None

                # Try primary animation URL first, then fallback
                recording_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_eq9hnyqv.json")
                if recording_animation is None:
                    # Fallback animation URL
                    recording_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_GofK09.json")
                
                # If both fail, use a simple default animation JSON
                if recording_animation is None:
                    recording_animation = {
                        "v": "5.5.7",
                        "fr": 60,
                        "ip": 0,
                        "op": 60,
                        "w": 100,
                        "h": 100,
                        "layers": [{
                            "ddd": 0,
                            "ind": 1,
                            "ty": 4,
                            "nm": "circle",
                            "ks": {
                                "o": {"a": 1, "k": [{"t": 0, "s": [100]}, {"t": 30, "s": [50]}, {"t": 60, "s": [100]}]},
                                "r": {"a": 0, "k": 0},
                                "p": {"a": 0, "k": [50, 50, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 0, "k": [100, 100, 100]}
                            }
                        }]
                    }

                if st.button("🎙️ Start Recording", key="voice_record_btn", use_container_width=True):
                    if not st.session_state.get('translator'):
                        st.error("Translator not initialized. Please refresh the page.")
                        return

                    with st.spinner("Recording... Speak now"):
                        try:
                            # Record audio
                            text = record_audio(source_lang)
                            if text:
                                # Show recording animation
                                with st.container():
                                    st_lottie(recording_animation, height=120, key="recording")
                                
                                st.success("Recording complete!")
                                st.write("Recognized text:", text)
                                
                                # Translate with visual feedback
                                with st.spinner("✨ Translating..."):
                                    translation = st.session_state.translator.translate_with_context(
                                        text, source_lang, target_lang
                                    )
                                    
                                    if translation:
                                        # Display translation result
                                        st.markdown(f"""
                                            <div class="translation-result">
                                                <h3>Translation</h3>
                                                <p>{translation.get('translation', 'Translation failed')}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Generate and play audio
                                        with st.spinner("🔊 Generating audio..."):
                                            play_translation_audio(translation['translation'], target_lang)
                                        
                                        # Show additional information
                                        with st.expander("🔍 Translation Details"):
                                            st.write("Grammar notes:", translation.get('grammar', 'No grammar notes available'))
                                            st.write("Cultural context:", translation.get('cultural_context', 'No cultural context available'))
                                            if 'examples' in translation:
                                                st.write("Examples:", "\n".join(translation['examples']))
                                    else:
                                        st.error("Translation failed. Please try again.")
                        except Exception as e:
                            st.error(f"Error during recording: {str(e)}")
                            logger.error(f"Recording error: {str(e)}", exc_info=True)

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error in voice interface: {str(e)}")
            logger.error(f"Voice interface error: {str(e)}", exc_info=True)

    except Exception as e:
        st.error(f"Voice translation interface error: {str(e)}")
        logger.error(f"Voice translation interface error: {str(e)}", exc_info=True)

def record_audio(source_lang: str) -> Optional[str]:
    """Enhanced audio recording with noise reduction and timeout"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Improve noise handling
        r.dynamic_energy_threshold = True
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(
                audio, 
                language=LANGUAGES[source_lang]
            )
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
        except sr.RequestError as e:
            st.error(f"Could not request results: {str(e)}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        return None

def play_translation_audio(text: str, target_lang: str) -> None:
    """Play translated audio with improved error handling"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(
                text=text,
                lang=LANGUAGES[target_lang],
                slow=False
            )
            tts.save(fp.name)
            
            # Display audio player
            st.audio(fp.name)
            
            # Cleanup
            os.unlink(fp.name)
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")   
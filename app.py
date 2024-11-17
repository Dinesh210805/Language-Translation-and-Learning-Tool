import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import io
import os
import json
import requests
from datetime import datetime, date
import time
from typing import Dict, List
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq API key
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    st.error("Please set your GROQ_API_KEY in the environment variables.")
    st.stop()

# Supported languages
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru"
}

class GroqTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def translate_with_context(self, text: str, source_lang: str, target_lang: str) -> Dict:
        try:
            prompt = f"""
            Act as an expert language translator and teacher.
            
            Translate the following text from {source_lang} to {target_lang}.
            
            Text: {text}
            
            Provide the following in a structured format:
            1. Direct translation
            2. Literal word-by-word translation (if applicable)
            3. Cultural context and usage notes
            4. Grammar explanation
            5. Three example sentences using key phrases
            6. Common idioms or expressions related to this content (if any)
            
            Format the response as JSON with the following keys:
            "translation", "literal", "cultural_context", "grammar", "examples", "idioms"
            """

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "llama3-groq-70b-8192-tool-use-preview",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse the JSON response from the message content
            content = result['choices'][0]['message']['content']
            try:
                translation_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if the response isn't proper JSON
                translation_data = {
                    "translation": content,
                    "literal": "Not available",
                    "cultural_context": "Not available",
                    "grammar": "Not available",
                    "examples": [],
                    "idioms": []
                }
            
            return translation_data

        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Error: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")
        except Exception as e:
            logger.error(f"General Error: {str(e)}")
            raise

class UserProgressTracker:
    def __init__(self):
        self.points = 0
        self.streak = 0
        self.last_active = None
        self.translations_count = 0
        self.practice_sessions = 0
        self.quiz_scores = []

    def add_points(self, points: int):
        self.points += points
        self.update_streak()

    def update_streak(self):
        today = date.today()
        if self.last_active:
            days_diff = (today - self.last_active).days
            if days_diff == 1:
                self.streak += 1
            elif days_diff > 1:
                self.streak = 1
            # If same day, streak stays the same
        else:
            self.streak = 1
        self.last_active = today

    def record_translation(self):
        self.translations_count += 1
        self.add_points(5)  # Points for each translation

    def record_practice(self):
        self.practice_sessions += 1
        self.add_points(10)  # Points for completing practice

    def record_quiz_score(self, score: float):
        self.quiz_scores.append(score)
        self.add_points(int(score * 10))  # Points based on quiz score

def initialize_session_state():
    if 'translator' not in st.session_state:
        st.session_state.translator = GroqTranslator(GROQ_API_KEY)
    if 'progress' not in st.session_state:
        st.session_state.progress = UserProgressTracker()
    if 'translation_history' not in st.session_state:
        st.session_state.translation_history = []
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None

def create_stylish_ui():
    st.set_page_config(
        page_title="LinguaLearn Pro",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            height: 3em;
            background: linear-gradient(135deg, #1e9638 0%, #1e5c9b 100%);
            color: white;
            border: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            background: linear-gradient(135deg, #1e5c9b 0%, #1e9638 100%);
        }
        .status-card {
            padding: 1.5rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .translation-result {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
        .custom-metric {
            text-align: center;
            padding: 1rem;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .custom-metric h3 {
            margin: 0;
            color: #1e5c9b;
        }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar_metrics():
    with st.sidebar:
        st.title("🌍 LinguaLearn Pro")
        st.markdown("---")
        
        # User Progress Section
        st.subheader("📊 Your Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="custom-metric">
                    <h3>{st.session_state.progress.points}</h3>
                    <p>Points</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="custom-metric">
                    <h3>🔥 {st.session_state.progress.streak}</h3>
                    <p>Day Streak</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Activity Statistics
        st.markdown("### 📈 Activity Stats")
        stats_data = {
            'Translations': st.session_state.progress.translations_count,
            'Practice Sessions': st.session_state.progress.practice_sessions,
            'Avg Quiz Score': f"{np.mean(st.session_state.progress.quiz_scores)*100:.1f}%" if st.session_state.progress.quiz_scores else "No quizzes taken"
        }
        
        for metric, value in stats_data.items():
            st.metric(metric, value)

def translation_interface():
    st.header("🔤 Smart Translation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        source_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), key="source_lang")
        target_lang = st.selectbox("Target Language", 
                                 [lang for lang in LANGUAGES.keys() if lang != source_lang],
                                 key="target_lang")
        
        text_to_translate = st.text_area(
            "Enter text to translate",
            height=150,
            placeholder="Type or paste your text here..."
        )
        
        if st.button("Translate", use_container_width=True):
            if text_to_translate:
                try:
                    with st.spinner("Translating..."):
                        translation_result = st.session_state.translator.translate_with_context(
                            text_to_translate,
                            source_lang,
                            target_lang
                        )
                        
                        # Record the translation
                        st.session_state.progress.record_translation()
                        st.session_state.translation_history.append({
                            "timestamp": datetime.now(),
                            "source_text": text_to_translate,
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                            "result": translation_result
                        })
                        
                        # Display results in the second column
                        with col2:
                            st.markdown("### Translation Results")
                            
                            # Main translation
                            st.markdown(
                                f"""
                                <div class="translation-result">
                                    <h4>Translation</h4>
                                    <p>{translation_result['translation']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Expandable sections for additional information
                            with st.expander("📚 Grammar Notes"):
                                st.write(translation_result['grammar'])
                            
                            with st.expander("🎭 Cultural Context"):
                                st.write(translation_result['cultural_context'])
                            
                            with st.expander("💡 Example Usage"):
                                for example in translation_result['examples']:
                                    st.write(f"• {example}")
                            
                            if translation_result['idioms']:
                                with st.expander("🗣️ Related Idioms"):
                                    for idiom in translation_result['idioms']:
                                        st.write(f"• {idiom}")
                            
                            # Save translation button
                            if st.button("Save Translation"):
                                st.success("Translation saved to your history!")
                                
                except Exception as e:
                    st.error(f"Translation error: {str(e)}")
            else:
                st.warning("Please enter text to translate.")

def practice_interface():
    st.header("🎯 Language Practice")
    
    practice_type = st.selectbox(
        "Choose Practice Type",
        ["Grammar Quiz", "Vocabulary Builder", "Sentence Construction"]
    )
    
    if practice_type == "Grammar Quiz":
        grammar_quiz()
    elif practice_type == "Vocabulary Builder":
        vocabulary_builder()
    elif practice_type == "Sentence Construction":
        sentence_construction()

def grammar_quiz():
    if 'current_quiz' not in st.session_state or not st.session_state.current_quiz:
        # Generate a new quiz
        quiz_questions = [
            {
                "question": "Select the correct form of the verb:",
                "context": "She ___ to the store yesterday.",
                "options": ["go", "goes", "went", "going"],
                "correct": "went"
            },
            {
                "question": "Choose the appropriate article:",
                "context": "I saw ___ elephant at the zoo.",
                "options": ["a", "an", "the", "no article"],
                "correct": "an"
            },
            # Add more questions as needed
        ]
        st.session_state.current_quiz = quiz_questions
        st.session_state.quiz_score = 0
        st.session_state.questions_answered = 0
    
    # Display current question
    current_q = st.session_state.current_quiz[st.session_state.questions_answered]
    
    st.markdown(f"### Question {st.session_state.questions_answered + 1}")
    st.write(current_q["question"])
    st.write(f"*{current_q['context']}*")
    
    answer = st.radio("Select your answer:", current_q["options"], key=f"q_{st.session_state.questions_answered}")
    
    if st.button("Submit Answer"):
        if answer == current_q["correct"]:
            st.success("Correct! +10 points")
            st.session_state.quiz_score += 1
            st.session_state.progress.add_points(10)
        else:
            st.error(f"Incorrect. The correct answer was: {current_q['correct']}")
        
        st.session_state.questions_answered += 1
        
        if st.session_state.questions_answered >= len(st.session_state.current_quiz):
            final_score = (st.session_state.quiz_score / len(st.session_state.current_quiz)) * 100
            st.session_state.progress.record_quiz_score(final_score / 100)
            st.success(f"Quiz completed! Final score: {final_score:.1f}%")
            if st.button("Start New Quiz"):
                st.session_state.current_quiz = None
                st.experimental_rerun()

def vocabulary_builder():
    st.subheader("📚 Vocabulary Builder")
    
    # Sample vocabulary sets (in practice, this would come from a database)
    vocab_sets = {
        "Beginner Basics": [
            {"word": "hello", "translation": "hola", "example": "Hello, how are you?"},
            {"word": "goodbye", "translation": "adiós", "example": "Goodbye, see you tomorrow!"},
            # Add more words
        ],
        "Travel Essentials": [
            {"word": "airport", "translation": "aeropuerto", "example": "The airport is very busy today."},
            {"word": "ticket", "translation": "boleto", "example": "I need to buy a ticket."},
            # Add more words
        ]
    }
    
    selected_set = st.selectbox("Choose Vocabulary Set:", list(vocab_sets.keys()))
    
    # Display vocabulary cards
# Continuing from vocabulary_builder function...
    for word_data in vocab_sets[selected_set]:
        with st.expander(f"📝 {word_data['word']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Translation:** {word_data['translation']}")
            with col2:
                st.markdown(f"**Example:** {word_data['example']}")
            
            if st.button(f"Practice '{word_data['word']}'", key=f"practice_{word_data['word']}"):
                st.session_state.progress.add_points(5)
                st.success("Great job practicing! +5 points")

def sentence_construction():
    st.subheader("🔨 Sentence Construction Practice")
    
    # Sample sentence patterns
    patterns = [
        {
            "pattern": "Subject + Verb + Object",
            "example": "I eat apples",
            "elements": {
                "subjects": ["I", "You", "He", "She", "They"],
                "verbs": ["eat", "read", "write", "watch"],
                "objects": ["apples", "books", "letters", "movies"]
            }
        },
        {
            "pattern": "Subject + Verb + Preposition + Object",
            "example": "She listens to music",
            "elements": {
                "subjects": ["He", "She", "They", "We"],
                "verbs": ["listens", "looks", "talks"],
                "prepositions": ["to", "at", "about"],
                "objects": ["music", "pictures", "friends"]
            }
        }
    ]
    
    selected_pattern = st.selectbox("Choose Pattern:", [p["pattern"] for p in patterns])
    pattern_data = next(p for p in patterns if p["pattern"] == selected_pattern)
    
    st.markdown(f"**Example:** {pattern_data['example']}")
    
    # Let user construct sentence
    constructed_sentence = {}
    for element, options in pattern_data["elements"].items():
        constructed_sentence[element] = st.selectbox(
            f"Choose {element}:",
            options,
            key=f"select_{element}"
        )
    
    # Display constructed sentence
    if st.button("Check Sentence"):
        sentence = " ".join(constructed_sentence.values())
        st.write(f"Your sentence: **{sentence}**")
        st.session_state.progress.add_points(5)
        st.success("Sentence constructed! +5 points")

def history_interface():
    st.header("📚 Translation History")
    
    if not st.session_state.translation_history:
        st.info("No translations yet. Start translating to build your history!")
        return
    
    for idx, entry in enumerate(reversed(st.session_state.translation_history)):
        with st.expander(f"Translation {len(st.session_state.translation_history) - idx}", expanded=(idx == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Original Text")
                st.write(entry["source_text"])
                st.caption(f"From {entry['source_lang']} to {entry['target_lang']}")
            
            with col2:
                st.markdown("### Translation")
                st.write(entry["result"]["translation"])
            
            st.markdown("### Additional Information")
            tab1, tab2, tab3 = st.tabs(["Grammar", "Cultural Notes", "Examples"])
            
            with tab1:
                st.write(entry["result"]["grammar"])
            with tab2:
                st.write(entry["result"]["cultural_context"])
            with tab3:
                for example in entry["result"]["examples"]:
                    st.write(f"• {example}")

def main():
    create_stylish_ui()
    initialize_session_state()
    display_sidebar_metrics()
    
    # Main navigation
    selected = option_menu(
        menu_title=None,
        options=["Translate", "Practice", "History"],
        icons=["translate", "book", "clock-history"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "20px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#1e9638"},
        }
    )
    
    if selected == "Translate":
        translation_interface()
    elif selected == "Practice":
        practice_interface()
    elif selected == "History":
        history_interface()

if __name__ == "__main__":
    main()

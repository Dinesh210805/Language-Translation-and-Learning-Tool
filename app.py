import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import io
import os
import json
import requests
from datetime import datetime, date, timedelta
import time
from typing import Dict, List
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import logging
from dotenv import load_dotenv
from streamlit_card import card
from streamlit_extras.switch_page_button import switch_page
import random
from streamlit_lottie import st_lottie
import requests
from gtts import gTTS
import base64
import streamlit_authenticator as stauth
import speech_recognition as sr
from io import BytesIO
import pyperclip
import keyboard

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
    "Russian": "ru",
    "Tamil": "ta"  # Add Tamil language
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
            Act as an expert language tutor. Help me translate and learn {target_lang}.
            
            Text to translate: {text}
            From: {source_lang}
            To: {target_lang}

            Respond in a conversational way, but ensure the response can be parsed as JSON with these fields:
            {{
                "translation": "direct translation",
                "literal": "word-by-word translation if applicable",
                "cultural_context": "explain cultural context and usage",
                "grammar": "explain grammar points",
                "examples": ["3 example sentences"],
                "idioms": ["related expressions or idioms"],
                "conversation": "a natural response as a language tutor"
            }}
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
            content = result['choices'][0]['message']['content']
            
            # Clean up JSON string
            content = content.replace('\n', ' ').strip()
            if not content.startswith('{'): 
                content = content[content.find('{'):content.rfind('}')+1]
            
            try:
                translation_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "translation": content,
                    "literal": "Not available",
                    "cultural_context": "Not available",
                    "grammar": "Not available",
                    "examples": [],
                    "idioms": [],
                    "conversation": "I apologize, but I couldn't process that properly. Could you try rephrasing?"
                }
            
            return translation_data

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
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
    defaults = {
        'translator': GroqTranslator(GROQ_API_KEY),
        'progress': UserProgressTracker(),
        'translation_history': [],
        'current_quiz': None,
        'source_lang': "English",
        'target_lang': "Spanish",
        'chat_messages': [],
        'chat_language': "English",
        'questions_answered': 0,
        'quiz_score': 0,
        'keyboard_shortcuts_enabled': True,  # Now using regular checkbox
        'translation_result': None,
        'text_to_translate': "",
        'audio_cache': {},
        'chat_context': [],
        'current_conversation': [],
        'current_page': 'Translate',  # Add current page tracking
        'nav_history': [],  # Add navigation history
        'audio_settings': {
            'enabled': True,
            'voice_type': 'default',
            'rate': 1.0,
            'pitch': 1.0
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Add new modern CSS styles
def create_stylish_ui():
    st.set_page_config(
        page_title="LinguaLearn Pro",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Enhanced CSS with dark theme
    st.markdown("""
        <style>
        /* Base styles */
        .main {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            color: #ffffff;
            padding: 0rem 1rem;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            height: 3em;
            background: linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%);
            color: white;
            border: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(74, 144, 226, 0.3);
            background: linear-gradient(135deg, #1E5C9B 0%, #4A90E2 100%);
        }
        
        /* Cards and containers */
        .status-card, .translation-result, .custom-metric, .flashcard {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            color: #ffffff;
            border: 1px solid #4A90E2;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        /* Navigation menu */
        .stHorizontalBlock {
            background: #1a1a1a !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
        }
        
        .nav-link {
            background: transparent !important;
            color: #ffffff !important;
            border-radius: 10px;
            margin: 5px;
        }
        
        .nav-link:hover {
            background: rgba(74, 144, 226, 0.2) !important;
        }
        
        .nav-link.active {
            background: linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%) !important;
        }
        
        /* Text elements */
        h1, h2, h3, h4, p {
            color: #ffffff !important;
        }
        
        .stMarkdown {
            color: #ffffff;
        }
        
        /* Input fields */
        .stTextInput>div>div, .stTextArea>div>div {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #4A90E2;
        }
        
        /* Expander */
        .streamlit-expanderContent {
            background: #2d2d2d;
            color: #ffffff;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: #1a1a1a;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #ffffff;
        }
        
        /* Select boxes */
        .stSelectbox>div>div {
            background: #2d2d2d;
            color: #ffffff;
        }
        
        /* Achievement badges */
        .achievement-badge {
            background: linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%);
            color: #ffffff;
        }
        
        /* Chat messages */
        .chat-message {
            background: #2d2d2d;
            color: #ffffff;
        }
        
        .user-message {
            background: linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%);
        }
        
        .bot-message {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        }
        
        /* Fix for option menu */
        .stOptionMenu {
            position: sticky;
            top: 0;
            z-index: 999;
            background: #1a1a1a;
            padding: 10px 0;
        }
        /* Modern Gradient Background */
        .main {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            color: #ffffff;
        }
        
        /* Glassmorphism Cards */
        .translation-result, .custom-metric, .flashcard {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        /* Neon Accents */
        .stButton>button {
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            border: none;
            padding: 10px 20px;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(74, 144, 226, 0.5);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            box-shadow: 0 0 25px rgba(74, 144, 226, 0.8);
            transform: translateY(-2px);
        }
        
        /* Floating Animation for Cards */
        .custom-metric {
            animation: float 6s ease-in-out infinite;
        }
        
        /* Professional Navigation */
        .stOptionMenu {
            background: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            z-index: 999;
        }
        
        /* Success Messages */
        .stSuccess {
            background: linear-gradient(45deg, #67B26F, #4ca2cd);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 10px;
            animation: slideIn 0.5s ease-out;
        }
        
        /* Loading Spinner */
        .stSpinner {
            border-color: #4A90E2;
        }
        
        /* Keyboard Shortcuts Tooltip */
        .keyboard-shortcut {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            margin: 0 4px;
        }
        
        /* New Feature Badge */
        .new-feature {
            background: linear-gradient(45deg, #FF6B6B, #FFE66D);
            color: black;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }
        
        /* Progress Indicators */
        .progress-ring {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: conic-gradient(#4A90E2 var(--progress), #2d2d2d 0deg);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        /* Voice Input Button */
        .voice-input {
            background: linear-gradient(45deg, #FF416C, #FF4B2B);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .voice-input:hover {
            transform: scale(1.1);
        }
        
        /* Quick Action Buttons */
        .quick-action {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .quick-action:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            border-radius: 4px;
        }
        
        /* Animations */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .custom-metric {
                margin-bottom: 1rem;
            }
            
            .stOptionMenu {
                overflow-x: auto;
            }
        }
        /* Voice Input Button */
        .voice-input-button {
            background: linear-gradient(45deg, #FF416C, #FF4B2B);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        /* Copy Button */
        .copy-button {
            background: rgba(74, 144, 226, 0.1);
            border: 1px solid rgba(74, 144, 226, 0.2);
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .copy-button:hover {
            background: rgba(74, 144, 226, 0.2);
        }
        
        /* Speech Button */
        .speech-button {
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .speech-button:hover {
            transform: scale(1.05);
        }
        /* Glassmorphism Enhancement */
        .glassmorphism {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Floating Feedback Button */
        .floating-feedback {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            padding: 10px 20px;
            border-radius: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            animation: float 6s ease-in-out infinite;
            cursor: pointer;
        }
        
        /* Grammar Notes Enhancement */
        .grammar-notes {
            border-left: 3px solid #4A90E2;
            padding-left: 15px;
            margin: 10px 0;
        }
        
        /* Quick Action Buttons Enhancement */
        .quick-action-button {
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        /* Chat Interface Styling */
        .chat-bubble {
            margin: 1rem 0;
            padding: 1rem;
            border-radius: 15px;
            position: relative;
            max-width: 80%;
            animation: fadeIn 0.3s ease-in;
        }
        
        .chat-bubble.user {
            background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        
        .chat-bubble.bot {
            background: linear-gradient(135deg, #2D2D2D 0%, #1A1A1A 100%);
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        
        .chat-content {
            color: white;
            line-height: 1.5;
        }
        
        .chat-actions {
            position: absolute;
            bottom: -20px;
            right: 0;
            display: flex;
            gap: 5px;
        }
        
        .chat-btn {
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .chat-btn:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.1);
        }
        
        /* Audio Player Styling */
        .audio-player {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .audio-player button {
            background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .audio-player button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(74,144,226,0.3);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Enhanced Translation Card */
        .translation-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid rgba(74, 144, 226, 0.2);
        }
        
        .translation-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .action-btn {
            background: rgba(74, 144, 226, 0.1);
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        /* Chat Improvements */
        .chat-input-area {
            position: sticky;
            bottom: 0;
            background: #1a1a1a;
            padding: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Voice Button */
        .voice-btn {
            width: 40px !important;
            height: 40px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        /* Idiom Card Styling */
        .idiom-card {
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05);
        }
        
        .idiom-text {
            font-style: italic;
            margin-bottom: 10px;
        }
        
        .idiom-actions {
            display: flex;
            gap: 10px;
        }
        /* Card Styles */
        .card-container {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(74, 144, 226, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
        }
        
        /* Button Styles */
        .action-button {
            background: linear-gradient(135deg, #4A90E2, #357ABD);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .action-button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(74, 144, 226, 0.3);
        }
        
        /* Content Styles */
        .content-text {
            color: white;
            font-size: 1.1em;
            line-height: 1.5;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    additional_styles = """
    <style>
    /* Enhanced Cards */
    .info-card, .example-card, .idiom-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(74, 144, 226, 0.2);
    }
    
    .card-actions {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    
    .action-btn {
        background: rgba(74, 144, 226, 0.1);
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: white;
    }
    
    .action-btn:hover {
        background: rgba(74, 144, 226, 0.2);
        transform: scale(1.05);
    }
    
    /* Translation Content */
    .translation-content {
        margin: 15px 0;
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Tab Content */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 15px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 0 0 10px 10px;
    }
    </style>
    """
    
    st.markdown(additional_styles, unsafe_allow_html=True)

    # Add JavaScript for copy and speak functionality
    st.markdown("""
    <script>
    function copy(text) {
        navigator.clipboard.writeText(text)
            .then(() => {
                // Show success message
                const msg = document.createElement('div');
                msg.textContent = '✓ Copied';
                msg.style.position = 'fixed';
                msg.style.bottom = '20px';
                msg.style.right = '20px';
                msg.style.background = '#4CAF50';
                msg.style.color = 'white';
                msg.style.padding = '10px 20px';
                msg.style.borderRadius = '5px';
                msg.style.animation = 'fadeInOut 2s ease-in-out';
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 2000);
            })
            .catch(err => console.error('Failed to copy:', err));
    }

    function speak(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    }
    </script>
    """, unsafe_allow_html=True)

    # Update JavaScript for text-to-speech
    st.markdown("""
    <script>
    function speak(text, lang) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || 'en-US';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }

    // Expose speak function to Streamlit
    window.speakText = speak;
    </script>
    """, unsafe_allow_html=True)

class SpacedRepetitionSystem:
    def __init__(self):
        self.items = {}  # {item_id: {'next_review': datetime, 'interval': int, 'ease': float}}
    
    def add_item(self, item_id):
        self.items[item_id] = {
            'next_review': datetime.now(),
            'interval': 1,
            'ease': 2.5
        }
    
    def update_item(self, item_id, quality):
        if item_id not in self.items:
            self.add_item(item_id)
            
        item = self.items[item_id]
        item['ease'] = max(1.3, item['ease'] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if quality < 3:
            item['interval'] = 1
        else:
            if item['interval'] == 1:
                item['interval'] = 6
            else:
                item['interval'] = int(item['interval'] * item['ease'])
                
        item['next_review'] = datetime.now() + timedelta(days=item['interval'])

class AchievementSystem:
    def __init__(self):
        self.achievements = {
            'first_translation': {'name': 'First Steps', 'desc': 'Complete your first translation', 'icon': '🎯'},
            'translation_master': {'name': 'Translation Master', 'desc': 'Complete 100 translations', 'icon': '🏆'},
            'streak_warrior': {'name': 'Streak Warrior', 'desc': 'Maintain a 7-day streak', 'icon': '⚔️'},
            'vocabulary_hero': {'name': 'Vocabulary Hero', 'desc': 'Learn 500 words', 'icon': '📚'},
            'perfect_quiz': {'name': 'Perfect Score', 'desc': 'Get 100% on a quiz', 'icon': '🌟'}
        }
        self.earned_achievements = set()

    def check_achievements(self, progress):
        earned = set()
        if progress.translations_count >= 1:
            earned.add('first_translation')
        if progress.translations_count >= 100:
            earned.add('translation_master')
        if progress.streak >= 7:
            earned.add('streak_warrior')
        if len(progress.quiz_scores) > 0 and max(progress.quiz_scores) == 1.0:
            earned.add('perfect_quiz')
        
        new_achievements = earned - self.earned_achievements
        self.earned_achievements.update(earned)
        return new_achievements

def add_pronunciation_feature(text, lang_code):
    """Enhanced pronunciation feature with better error handling"""
    try:
        audio_key = f"audio_{hash(text)}"
        if audio_key not in st.session_state:
            tts = gTTS(text=text, lang=lang_code)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_bytes = audio_file.getvalue()
            st.session_state[audio_key] = base64.b64encode(audio_bytes).decode()
        
        st.markdown(f"""
            <div class="audio-player">
                <audio id="audio_{audio_key}" style="width:100%">
                    <source src="data:audio/mp3;base64,{st.session_state[audio_key]}" type="audio/mp3">
                </audio>
                <button onclick="document.getElementById('audio_{audio_key}').play()">
                    🔊 Listen
                </button>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not generate audio: {str(e)}")

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

# Update example sentences for all languages
def get_example_sentences(lang_code):
    examples = {
        "en": ["How are you?", "What's the weather like?", "Where is the restaurant?", "I love learning languages!"],
        "es": ["¿Cómo estás?", "¿Qué tiempo hace?", "¿Dónde está el restaurante?", "¡Me encanta aprender idiomas!"],
        "fr": ["Comment allez-vous?", "Quel temps fait-il?", "Où est le restaurant?", "J'adore apprendre les langues!"],
        "de": ["Wie geht es dir?", "Wie ist das Wetter?", "Wo ist das Restaurant?", "Ich liebe es, Sprachen zu lernen!"],
        "it": ["Come stai?", "Che tempo fa?", "Dov'è il ristorante?", "Amo imparare le lingue!"],
        "pt": ["Como está você?", "Como está o tempo?", "Onde é o restaurante?", "Eu amo aprender idiomas!"],
        "zh": ["你好吗？", "天气怎么样？", "餐厅在哪里？", "我喜欢学习语言！"],
        "ja": ["お元気ですか？", "お天気はどうですか？", "レストランはどこですか？", "言語を学ぶのが大好きです！"],
        "ko": ["안녕하세요?", "날씨가 어떻습니까?", "레스토랑이 어디에 있습니까?", "언어 배우는 것을 좋아합니다!"],
        "ru": ["Как дела?", "Какая погода?", "Где ресторан?", "Я люблю изучать языки!"],
        "ta": ["நீங்கள் எப்படி இருக்கிறீர்கள்?", "வானிலை எப்படி உள்ளது?", "உணவகம் எங்கே உள்ளது?", "மொழிகளைக் கற்க எனக்கு மிகவும் பிடிக்கும்!"]
    }
    return examples.get(LANGUAGES[lang_code], ["No examples available"])

# Fix voice input function
def voice_to_text(source_lang):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... (Speak now)")
        try:
            audio = r.listen(source, timeout=5)
            # Get language code correctly
            lang_code = LANGUAGES.get(source_lang, 'en')  # Default to English if not found
            text = r.recognize_google(audio, language=lang_code)
            return text
        except sr.UnknownValueError:
            st.error("🔇 Could not understand audio")
            return None
        except sr.RequestError:
            st.error("🚫 Could not process audio. Check your internet connection.")
            return None
        except Exception as e:
            st.error(f"🚫 Error: {str(e)}")
            return None

# Enhanced copy functionality
def create_copy_button(text, button_text="📋", key_suffix=""):
    button_key = f"copy_{hash(text)}_{key_suffix}"
    if st.button(button_text, key=button_key, help="Click to copy"):
        try:
            pyperclip.copy(text)
            st.success("✅ Copied to clipboard!", icon="✂️")
            return True
        except Exception as e:
            st.error(f"❌ Failed to copy: {str(e)}")
            return False

# Add floating feedback button
def add_feedback_button():
    st.sidebar.markdown("""
        <div class='floating-feedback'>
            <a href="mailto:support@lingualean.com" target="_blank" 
               style="text-decoration:none; color:white;">
                💭 Feedback
            </a>
        </div>
    """, unsafe_allow_html=True)

# Enhance translation interface with voice and copy features
def translation_interface():
    st.header("🔤 Smart Translation")
    
    # Layout improvements
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        # Language selection and input area
        lang_col1, lang_col2, voice_col = st.columns([2, 2, 1])
        with lang_col1:
            source_lang = st.selectbox("From:", list(LANGUAGES.keys()), key="source_lang")
        with lang_col2:
            target_lang = st.selectbox("To:", [lang for lang in LANGUAGES.keys() if lang != source_lang])
        with voice_col:
            voice_placeholder = st.empty()
            with voice_placeholder:
                voice_button = st.button("🎤", key="voice_input", help="Click to speak")
                if voice_button:
                    with st.spinner("🎤 Listening..."):
                        text = voice_to_text(source_lang)
                        if text:
                            st.session_state.text_to_translate = text
                            st.rerun()  # Changed from experimental_rerun

        # Text input area
        text_to_translate = st.text_area(
            "Enter text",
            height=150,
            value=st.session_state.text_to_translate,
            placeholder="Type or paste text here..."
        )

        # Example sentences with better layout
        with st.expander("📝 Example Sentences"):
            examples = get_example_sentences(source_lang)
            for i, example in enumerate(examples):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"{example}", key=f"ex_{i}"):
                        st.session_state.text_to_translate = example
                        st.rerun()  # Changed from experimental_rerun

    # Enhanced translation display
    if text_to_translate:
        try:
            with st.spinner("Translating..."):
                result = process_translation(text_to_translate, source_lang, target_lang)
                display_translation_results(result, right_col)
        except Exception as e:
            st.error(f"Translation error: {str(e)}")

def process_translation(text, source_lang, target_lang):
    # Add enhanced translation processing
    translation = st.session_state.translator.translate_with_context(text, source_lang, target_lang)
    st.session_state.progress.record_translation()
    
    # Add to history
    st.session_state.translation_history.append({
        "timestamp": datetime.now(),
        "source_text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "result": translation
    })
    
    return translation

def display_translation_results(result, container):
    with container:
        # Clean and escape the text for JavaScript
        def clean_text(text):
            if isinstance(text, str):
                return text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
            return text

        # Main translation card
        translation = clean_text(result['translation'])
        main_translation = f"""
        <div class="translation-card glassmorphism">
            <h3 style="color: white;">Translation</h3>
            <div class="translation-content">
                <p style="color: white; font-size: 1.2em;">{translation}</p>
            </div>
            <div class="translation-actions">
                <button class="action-btn" onclick="navigator.clipboard.writeText('{translation}')">📋</button>
                <button class="action-btn" onclick="window.audioSystem.speak('{translation}', '{LANGUAGES[st.session_state.target_lang]}')">🔊</button>
            </div>
        </div>
        """
        st.markdown(main_translation, unsafe_allow_html=True)

        # Display additional information in tabs
        tab_grammar, tab_context, tab_examples, tab_idioms = st.tabs([
            "📚 Grammar", "🌍 Context", "💡 Examples", "🗣️ Idioms"
        ])
        
        with tab_grammar:
            grammar_content = f"""
            <div class="info-card glassmorphism">
                <h4 style="color: white;">Grammar Explanation</h4>
                <p style="color: white;">{result['grammar']}</p>
                <button class="copy-button" onclick="copy('{result['grammar']}')">📋 Copy</button>
            </div>
            """
            st.markdown(grammar_content, unsafe_allow_html=True)
            
        with tab_context:
            context_content = f"""
            <div class="info-card glassmorphism">
                <h4 style="color: white;">Cultural Context</h4>
                <p style="color: white;">{result['cultural_context']}</p>
                <button class="copy-button" onclick="copy('{result['cultural_context']}')">📋 Copy</button>
            </div>
            """
            st.markdown(context_content, unsafe_allow_html=True)
            
        with tab_examples:
            if result['examples']:
                for example in result['examples']:
                    example_content = f"""
                    <div class="example-card glassmorphism">
                        <p style="color: white;">• {example}</p>
                        <div class="card-actions">
                            <button class="action-btn" onclick="copy('{example}')">📋</button>
                            <button class="action-btn" onclick="speak('{example}')">🔊</button>
                        </div>
                    </div>
                    """
                    st.markdown(example_content, unsafe_allow_html=True)
            else:
                st.info("No examples available")
                
        with tab_idioms:
            if result.get('idioms'):
                if isinstance(result['idioms'], list):
                    for idiom in result['idioms']:
                        idiom_content = f"""
                        <div class="idiom-card glassmorphism">
                            <p class="idiom-text" style="color: white;">"{idiom}"</p>
                            <div class="idiom-actions">
                                <button class="action-btn" onclick="copy('{idiom}')">📋</button>
                                <button class="action-btn" onclick="speak('{idiom}')">🔊</button>
                            </div>
                        </div>
                        """
                        st.markdown(idiom_content, unsafe_allow_html=True)
                else:
                    idiom_content = f"""
                    <div class="idiom-card glassmorphism">
                        <p class="idiom-text" style="color: white;">"{result['idioms']}"</p>
                        <div class="idiom-actions">
                            <button class="action-btn" onclick="copy('{result['idioms']}')">📋</button>
                            <button class="action-btn" onclick="speak('{result['idioms']}')">🔊</button>
                        </div>
                    </div>
                    """
                    st.markdown(idiom_content, unsafe_allow_html=True)
            else:
                st.info("No idioms available")

        # Add JavaScript for better functionality
        st.markdown("""
            <script>
            function handleCopy(text) {
                navigator.clipboard.writeText(text).then(function() {
                    showToast('Copied to clipboard!');
                }).catch(function(err) {
                    showToast('Failed to copy');
                });
            }
            
            function handleSpeak(text) {
                const utterance = new SpeechSynthesisUtterance(text);
                window.speechSynthesis.speak(utterance);
            }
            
            function showToast(message) {
                const toast = document.createElement('div');
                toast.textContent = message;
                toast.style.position = 'fixed';
                toast.style.bottom = '20px';
                toast.style.right = '20px';
                toast.style.background = '#4A90E2';
                toast.style.color = 'white';
                toast.style.padding = '10px 20px';
                toast.style.borderRadius = '5px';
                toast.style.animation = 'fadeIn 0.5s, fadeOut 0.5s 1.5s';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 2000);
            }
            </script>
        """, unsafe_allow_html=True)

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
            {
                "question": "Choose the correct tense:",
                "context": "By next month, she ___ in Paris for five years.",
                "options": ["will be living", "will have been living", "has been living", "lives"],
                "correct": "will have been living",
                "explanation": "Use future perfect continuous for actions that will continue up to a specific point in the future."
            },
            {
                "question": "Select the correct conditional form:",
                "context": "If I ___ rich, I would travel the world.",
                "options": ["am", "were", "will be", "had been"],
                "correct": "were",
                "explanation": "Use 'were' in second conditional sentences for hypothetical present/future situations."
            }
        ]
        st.session_state.current_quiz = quiz_questions
        st.session_state.quiz_score = 0
        st.session_state.questions_answered = 0
    
    # Check if all questions have been answered
    if st.session_state.questions_answered >= len(st.session_state.current_quiz):
        final_score = (st.session_state.quiz_score / len(st.session_state.current_quiz)) * 100
        st.session_state.progress.record_quiz_score(final_score / 100)
        st.success(f"Quiz completed! Final score: {final_score:.1f}%")
        if st.button("Start New Quiz"):
            st.session_state.current_quiz = None
            st.rerun()
        return

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
                st.rerun()  # Changed from experimental_rerun

def vocabulary_builder():
    st.subheader("📚 Vocabulary Builder")
    
    vocab_sets = {
        "Beginner Basics": [
            {"word": "hello", "translation": "hola", "example": "Hello, how are you?", "category": "Greetings"},
            {"word": "goodbye", "translation": "adiós", "example": "Goodbye, see you tomorrow!", "category": "Greetings"},
            {"word": "please", "translation": "por favor", "example": "Please help me.", "category": "Courtesy"},
            {"word": "thank you", "translation": "gracias", "example": "Thank you for your help.", "category": "Courtesy"}
        ],
        "Travel Essentials": [
            {"word": "airport", "translation": "aeropuerto", "example": "The airport is very busy today.", "category": "Transport"},
            {"word": "ticket", "translation": "boleto", "example": "I need to buy a ticket.", "category": "Transport"},
            {"word": "hotel", "translation": "hotel", "example": "The hotel is near the beach.", "category": "Accommodation"},
            {"word": "passport", "translation": "pasaporte", "example": "Don't forget your passport!", "category": "Documents"}
        ],
        "Food and Dining": [
            {"word": "restaurant", "translation": "restaurante", "example": "Let's go to a restaurant.", "category": "Places"},
            {"word": "menu", "translation": "menú", "example": "Can I see the menu?", "category": "Dining"},
            {"word": "water", "translation": "agua", "example": "I would like some water.", "category": "Drinks"},
            {"word": "bill", "translation": "cuenta", "example": "Could I have the bill, please?", "category": "Dining"}
        ]
    }
    
    # Initialize spaced repetition system if not exists
    if 'srs' not in st.session_state:
        st.session_state.srs = SpacedRepetitionSystem()
    
    selected_set = st.selectbox("Choose Vocabulary Set:", list(vocab_sets.keys()))
    
    # Display vocabulary as flashcards
    for word_data in vocab_sets[selected_set]:
        word_id = f"{selected_set}_{word_data['word']}"
        
        with st.container():
            clicked = card(
                title=word_data['word'],
                text=word_data['translation'],
                key=f"card_{word_id}",
                image="https://via.placeholder.com/150"
            )
            
            if clicked:
                with st.expander("Details", expanded=True):
                    st.markdown(f"**Category:** {word_data['category']}")
                    st.markdown(f"**Example:** {word_data['example']}")
                    
                    # Confidence rating
                    confidence = st.slider(
                        "Rate your confidence (1-5):",
                         1, 5, 3,
                        key=f"confidence_{word_id}"
                    )
                    
                    if st.button("Save Progress", key=f"save_{word_id}"):
                        st.session_state.srs.update_item(word_id, confidence)
                        st.session_state.progress.add_points(confidence * 2)
                        st.success(f"Progress saved! +{confidence * 2} points")

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

def display_chat_messages():
    """Display chat messages with enhanced styling"""
    if not st.session_state.chat_messages:
        st.write("No messages yet.")
    else:
        for msg in st.session_state.chat_messages:
            message_class = "user" if msg['type'] == 'user' else "bot"
            
            st.markdown(f"""
                <div class="chat-bubble {message_class}">
                    <div class="chat-content">
                        {msg['text']}
                    </div>
                    <div class="chat-actions">
                        <button class="chat-btn" onclick="copy('{msg['text']}')">📋</button>
                        <button class="chat-btn" onclick="speak('{msg['text']}')">🔊</button>
                    </div>
                    <small style="color: rgba(255,255,255,0.6);">
                        {msg['timestamp'].strftime('%H:%M')}
                    </small>
                </div>
            """, unsafe_allow_html=True)

            # Show translation context for bot messages
            if msg['type'] == 'bot' and 'context' in msg:
                with st.expander("Show context"):
                    st.write("Grammar notes:", msg['context'].get('grammar', 'No grammar notes available'))
                    st.write("Cultural context:", msg['context'].get('cultural_context', 'No cultural context available'))
                    if 'examples' in msg['context']:
                        st.write("Examples:")
                        for example in msg['context']['examples']:
                            st.write(f"• {example}")

def process_chat_message(user_input: str, chat_lang: str):
    """Process and handle chat messages"""
    try:
        # Add user message
        st.session_state.chat_messages.append({
            'type': 'user',
            'text': user_input,
            'timestamp': datetime.now()
        })
        
        # Get AI response
        translation = st.session_state.translator.translate_with_context(
            user_input,
            "English",  # Source language
            chat_lang   # Target language
        )
        
        # Add AI response
        conversation_response = translation.get('conversation', translation['translation'])
        st.session_state.chat_messages.append({
            'type': 'bot',
            'text': conversation_response,
            'context': translation,  # Store full context for later use
            'timestamp': datetime.now()
        })
        
        # Add follow-up question or practice suggestion
        if random.random() < 0.7:  # 70% chance of follow-up
            follow_ups = [
                "Can you try using this in a different sentence?",
                "How would you say this in a formal situation?",
                "Do you understand why we use this grammar structure?",
                "Can you identify the key vocabulary here?",
                "Would you like to practice similar phrases?"
            ]
            st.session_state.chat_messages.append({
                'type': 'bot',
                'text': random.choice(follow_ups),
                'timestamp': datetime.now()
            })
        
        # Record activity
        st.session_state.progress.record_translation()
        
    except Exception as e:
        st.error(f"Chat Error: {str(e)}")

def chat_interface():
    st.header("🗣️ Language Practice Chat")
    
    # Chat settings
    chat_col1, chat_col2 = st.columns([3, 1])
    with chat_col1:
        chat_lang = st.selectbox(
            "Chat Language",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.chat_language)
        )
    with chat_col2:
        clear_chat = st.button("🗑️ Clear Chat")
        if clear_chat:
            st.session_state.chat_messages = []
            st.rerun()

    # Chat display
    chat_container = st.container()
    with chat_container:
        display_chat_messages()

    # Input area with message handling
    def handle_submit():
        if st.session_state.chat_input:
            process_chat_message(st.session_state.chat_input.strip(), chat_lang)
            # Instead of directly modifying session state, we'll rerun the app
            st.rerun()

    input_col1, input_col2, input_col3 = st.columns([4, 1, 1])
    with input_col1:
        # Create text input with on_change callback
        st.text_input(
            "Message:", 
            key="chat_input",
            on_change=handle_submit
        )

    with input_col2:
        if st.button("🎤"):
            with st.spinner("🎤 Listening..."):
                text = voice_to_text(LANGUAGES[chat_lang])
                if text:
                    process_chat_message(text, chat_lang)
                    st.rerun()

    with input_col3:
        if st.button("Send 📤"):
            handle_submit()

def display_achievements():
    st.header("🏆 Achievements")
    
    cols = st.columns(3)
    for i, (achievement_id, achievement) in enumerate(st.session_state.achievement_system.achievements.items()):
        with cols[i % 3]:
            earned = achievement_id in st.session_state.achievement_system.earned_achievements
            st.markdown(f"""
                <div class="achievement-badge" style="opacity: {'1' if earned else '0.5'}">
                    <h3>{achievement['icon']}</h3>
                    <h4>{achievement['name']}</h4>
                    <p>{achievement['desc']}</p>
                </div>
            """, unsafe_allow_html=True)

# Add keyboard shortcuts helper
def show_keyboard_shortcuts():
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <h4>⌨️ Keyboard Shortcuts</h4>
            <p><span class="keyboard-shortcut">Ctrl + Enter</span> Translate</p>
            <p><span class="keyboard-shortcut">Ctrl + S</span> Save Translation</p>
            <p><span class="keyboard-shortcut">Ctrl + Space</span> Voice Input</p>
            <p><span class="keyboard-shortcut">Ctrl + /</span> Show/Hide Shortcuts</p>
        </div>
    """, unsafe_allow_html=True)

# Add quick action buttons
def show_quick_actions():
    st.markdown("""
        <div style="display: flex; gap: 10px; margin: 1rem 0;">
            <div class="quick-action">🎯 Daily Goal</div>
            <div class="quick-action">📊 Progress Report</div>
            <div class="quick-action">🎮 Language Games</div>
            <div class="quick-action">👥 Community</div>
        </div>
    """, unsafe_allow_html=True)

# Add keyboard shortcuts
def initialize_keyboard_shortcuts():
    """Initialize keyboard shortcuts in a way that's compatible with Streamlit's threading model"""
    if not hasattr(st.session_state, 'keyboard_initialized'):
        try:
            keyboard.unhook_all()  # Clear any existing hooks
            
            def safe_update(key):
                # Use a thread-safe way to update session state
                if st.session_state.keyboard_shortcuts_enabled:
                    st.session_state[key] = True
            
            keyboard.add_hotkey('ctrl+enter', lambda: safe_update("translate_triggered"))
            keyboard.add_hotkey('ctrl+s', lambda: safe_update("save_triggered"))
            keyboard.add_hotkey('ctrl+space', lambda: safe_update("voice_triggered"))
            
            st.session_state.keyboard_initialized = True
        except Exception as e:
            logger.warning(f"Could not initialize keyboard shortcuts: {str(e)}")

# Update navigation style
def create_nav_menu():
    setup_page_navigation()
    selected = option_menu(
        menu_title=None,
        options=["Translate", "Practice", "Chat", "History", "Achievements"],
        icons=["translate", "book", "chat-dots", "clock-history", "trophy"],
        menu_icon="cast",
        default_index=list(["Translate", "Practice", "Chat", "History", "Achievements"]).index(st.session_state.current_page),
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#1a1a1a!important",  # Added !important
                "position": "sticky",
                "top": "0",
                "z-index": "9999"  # Increased z-index
            },
            "icon": {
                "color": "#4A90E2",
                "font-size": "25px"
            },
            "nav-link": {
                "font-size": "20px",
                "text-align": "center",
                "margin": "0px",
                "color": "#ffffff",
                "--hover-color": "#2d2d2d",
                "padding": "15px 20px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%)",
                "color": "#ffffff",
                "font-weight": "bold",
            },
        }
    )
    
    # Update navigation history
    if selected != st.session_state.current_page:
        st.session_state.nav_stack.append(st.session_state.current_page)
        st.session_state.current_page = selected
        st.rerun()
    
    return selected

def setup_audio_features():
    """Initialize and configure audio features"""
    if 'audio_initialized' not in st.session_state:
        st.session_state.audio_initialized = True
        st.session_state.audio_queue = []
        
    # Add to your JavaScript
    js_code = """
    <script>
    const speakText = (text, lang) => {
        try {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = window.sessionStorage.getItem('speech_rate') || 1.0;
            utterance.pitch = window.sessionStorage.getItem('speech_pitch') || 1.0;
            
            // Get available voices
            let voices = speechSynthesis.getVoices();
            if (voices.length > 0) {
                // Try to find a voice for the specific language
                let voice = voices.find(v => v.lang.startsWith(lang)) || voices[0];
                utterance.voice = voice;
            }
            
            window.speechSynthesis.speak(utterance);
            return true;
        } catch (e) {
            console.error('Speech synthesis error:', e);
            return false;
        }
    };
    
    window.speakText = speakText;
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

def setup_page_navigation():
    """Setup persistent navigation"""
    if 'nav_stack' not in st.session_state:
        st.session_state.nav_stack = []
        st.session_state.current_page = 'Translate'
        
def setup_audio_system():
    """Setup audio system with proper initialization"""
    if 'audio_system' not in st.session_state:
        st.session_state.audio_system = {
            'initialized': False,
            'last_played': None,
            'voice_settings': {
                'rate': 1.0,
                'pitch': 1.0,
                'volume': 1.0
            }
        }
        
        js = """
        <script>
        if (typeof window.audioSystem === 'undefined') {
            window.audioSystem = {
                speak: function(text, lang) {
                    return new Promise((resolve, reject) => {
                        if (!window.speechSynthesis) {
                            reject('Speech synthesis not supported');
                            return;
                        }
                        
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.lang = lang || 'en-US';
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        
                        utterance.onend = () => resolve(true);
                        utterance.onerror = (err) => reject(err);
                        
                        window.speechSynthesis.speak(utterance);
                    });
                }
            };
        }
        </script>
        """
        st.components.v1.html(js, height=0)
        st.session_state.audio_system['initialized'] = True

def main():
    try:
        create_stylish_ui()
        initialize_session_state()
        setup_audio_system()
        
        if st.session_state.keyboard_shortcuts_enabled:
            initialize_keyboard_shortcuts()
        
        if 'achievement_system' not in st.session_state:
            st.session_state.achievement_system = AchievementSystem()
        
        # Move navigation menu before achievements check
        selected = create_nav_menu()
        
        # Check for new achievements
        new_achievements = st.session_state.achievement_system.check_achievements(st.session_state.progress)
        if new_achievements:
            # Create a container for achievements that doesn't interfere with navbar
            with st.container():
                for achievement_id in new_achievements:
                    achievement = st.session_state.achievement_system.achievements[achievement_id]
                    st.markdown("""
                        <div style="position: fixed; 
                                bottom: 20px; 
                                right: 20px; 
                                background: linear-gradient(135deg, #4A90E2 0%, #1E5C9B 100%);
                                padding: 1rem;
                                border-radius: 10px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                z-index: 1000;
                                animation: slideIn 0.5s ease-out;">
                            <h4 style="margin:0">🎉 Achievement Unlocked!</h4>
                            <p style="margin:0">{} - {}</p>
                        </div>
                    """.format(achievement['name'], achievement['desc']), unsafe_allow_html=True)
                    st.balloons()
        
        display_sidebar_metrics()
        
        # Handle page selection
        if selected == "Translate":
            translation_interface()
        elif selected == "Practice":
            practice_interface()
        elif selected == "Chat":
            chat_interface()
        elif selected == "History":
            history_interface()
        elif selected == "Achievements":
            display_achievements()

        # Handle keyboard shortcuts
        if st.session_state.get("translate_triggered"):
            st.session_state.translate_triggered = False
            # Trigger translation
        
        if st.session_state.get("save_triggered"):
            st.session_state.save_triggered = False
            # Trigger save
        
        if st.session_state.get("voice_triggered"):
            st.session_state.voice_triggered = False
            # Trigger voice input

    except Exception as e:
        st.error("Application Error: Please refresh the page")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

def display_idioms(idioms):
    """Display idioms with better formatting"""
    if isinstance(idioms, list):
        for idiom in idioms:
            st.markdown(
                f"""
                <div class="idiom-card glassmorphism">
                    <p class="idiom-text">"{idiom}"</p>
                    <div class="idiom-actions">
                        <button onclick="copyText('{idiom}')" class="action-btn">📋</button>
                        <button onclick="speak('{idiom}')" class="action-btn">🔊</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"""
            <div class="idiom-card glassmorphism">
                <p class="idiom-text">"{idioms}"</p>
                <div class="idiom-actions">
                    <button onclick="copyText('{idioms}')" class="action-btn">📋</button>
                    <button onclick="speak('{idioms}')" class="action-btn">🔊</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_chat_messages():
    """Display chat messages with enhanced styling"""
    if not st.session_state.chat_messages:
        st.write("No messages yet.")
    else:
        for msg in st.session_state.chat_messages:
            message_class = "user" if msg['type'] == 'user' else "bot"
            
            st.markdown(f"""
                <div class="chat-bubble {message_class}">
                    <div class="chat-content">
                        {msg['text']}
                    </div>
                    <div class="chat-actions">
                        <button class="chat-btn" onclick="copy('{msg['text']}')">📋</button>
                        <button class="chat-btn" onclick="speak('{msg['text']}')">🔊</button>
                    </div>
                    <small style="color: rgba(255,255,255,0.6);">
                        {msg['timestamp'].strftime('%H:%M')}
                    </small>
                </div>
            """, unsafe_allow_html=True)

            # Show translation context for bot messages
            if msg['type'] == 'bot' and 'context' in msg:
                with st.expander("Show context"):
                    st.write("Grammar notes:", msg['context'].get('grammar', 'No grammar notes available'))
                    st.write("Cultural context:", msg['context'].get('cultural_context', 'No cultural context available'))
                    if 'examples' in msg['context']:
                        st.write("Examples:")
                        for example in msg['context']['examples']:
                            st.write(f"• {example}")

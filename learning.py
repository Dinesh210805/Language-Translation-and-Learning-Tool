import streamlit as st
from datetime import datetime
import json
import pandas as pd
from typing import Dict, List, Optional
import logging
import requests
import os

# Configure logging for learning module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Add this at the top level after imports
GROQ_API_KEY = "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"

# Expand LANGUAGE_COURSES dictionary
LANGUAGE_COURSES = {
    "Spanish": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of Spanish",
                "lessons": [
                    # Updated video_id for Basic Greetings with multiple options
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1", "description": "Essential Spanish greetings", 
                     "video_options": [
                         {"id": "TZ0bPXFHiiY", "title": "Spanish Lesson 1: Greetings"},
                         {"id": "j91m55N7e9I", "title": "Learn Spanish 1.1 - Greetings and Introductions"},
                         {"id": "R865tE-jkcM", "title": "Basic Spanish Greetings - Part 1"},
                         {"id": "zYEzw29zNms", "title": "Lesson 1 - Basic Greeting in Spanish"},
                         {"id": "hq_ci0u45_k", "title": "Learn Spanish Greetings for Beginners"}
                     ],
                     "video_id": "TZ0bPXFHiiY"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "VIDEO_ID_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "VIDEO_ID_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "VIDEO_ID_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "VIDEO_ID_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "VIDEO_ID_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "VIDEO_ID_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "VIDEO_ID_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "VIDEO_ID_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    },
    "French": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of French",
                "lessons": [
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1",
                     "description": "Essential French greetings",
                     "video_options": [
                         {"id": "car6SARpDDc", "title": "French Greetings for Beginners (With Pronunciations)"},
                         {"id": "VE2m0OGPoQE", "title": "Basic French Greetings for Beginners"},
                         {"id": "m8xTQus9Y24", "title": "French Greetings for Beginners"},
                         {"id": "FyYeL_OEC2U", "title": "Learn French Greetings and Basic Phrases"}
                     ],
                     "video_id": "car6SARpDDc"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "French_VIDEO_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "French_VIDEO_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "French_VIDEO_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "French_VIDEO_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "French_VIDEO_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "French_VIDEO_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "French_VIDEO_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "French_VIDEO_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    },
    "German": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of German",
                "lessons": [
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1",
                     "description": "Essential German greetings",
                     "video_options": [
                         {"id": "e784UaFETQg", "title": "Basic German Greetings, Introductions, and Phrases"},
                         {"id": "_WHzlca3r3c", "title": "Lesson 1: Greetings in German"},
                         {"id": "n0eA7ERpsF8", "title": "Deutsch A1 - Guten Tag: Begrüßungen"},
                         {"id": "noal4Uk9luA", "title": "A1 - Lesson 1 Begrüßungen"}
                     ],
                     "video_id": "e784UaFETQg"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "German_VIDEO_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "German_VIDEO_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "German_VIDEO_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "German_VIDEO_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "German_VIDEO_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "German_VIDEO_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "German_VIDEO_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "German_VIDEO_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    },
    "Italian": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of Italian",
                "lessons": [
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1",
                     "description": "Essential Italian greetings",
                     "video_options": [
                         {"id": "3d7SSE6fJvo", "title": "Simple Italian Greetings for Beginners"},
                         {"id": "w89QV6akOeY", "title": "Complete Guide to Italian Greetings"},
                         {"id": "i5t51Byl4Sw", "title": "Italian Greetings and Basic Expressions"}
                     ],
                     "video_id": "3d7SSE6fJvo"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "Italian_VIDEO_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "Italian_VIDEO_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "Italian_VIDEO_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "Italian_VIDEO_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "Italian_VIDEO_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "Italian_VIDEO_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "Italian_VIDEO_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "Italian_VIDEO_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    },
    "Japanese": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of Japanese",
                "lessons": [
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1",
                     "description": "Essential Japanese greetings",
                     "video_options": [
                         {"id": "CqwE1F0XEL4", "title": "Basic Japanese Greetings for Beginners"},
                         {"id": "qtJea9Bnc4g", "title": "Learn Basic Japanese Greetings"},
                         {"id": "4qa6SnRP-zc", "title": "Learn 10 Basic Japanese Greetings"},
                         {"id": "y53Y1QFAWX4", "title": "Master MORE Basic Greetings in Japanese"}
                     ],
                     "video_id": "CqwE1F0XEL4"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "Japanese_VIDEO_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "Japanese_VIDEO_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "Japanese_VIDEO_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "Japanese_VIDEO_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "Japanese_VIDEO_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "Japanese_VIDEO_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "Japanese_VIDEO_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "Japanese_VIDEO_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    },
    "Tamil": {
        "chapters": {
            "1": {
                "title": "Fundamentals",
                "description": "Master the basics of Tamil",
                "lessons": [
                    {"id": "1.1", "title": "Basic Greetings", "level": "A1",
                     "description": "Essential Tamil greetings",
                     "video_options": [
                         {"id": "GJtg74yxhcg", "title": "Basic Tamil Greetings"},
                         {"id": "BH0D7TI45gM", "title": "Learn Common Tamil Greetings"},
                         {"id": "3embo9gU1po", "title": "Greetings and Introduction in Tamil"}
                     ],
                     "video_id": "GJtg74yxhcg"  # Default video
                    },
                    {"id": "1.2", "title": "Numbers & Counting", "level": "A1", "description": "Numbers 1-100", "video_id": "Tamil_VIDEO_2"},
                    {"id": "1.3", "title": "Calendar & Time", "level": "A1", "description": "Days, months, and time", "video_id": "Tamil_VIDEO_3"}
                ]
            },
            "2": {
                "title": "Daily Communication",
                "description": "Essential everyday conversations",
                "lessons": [
                    {"id": "2.1", "title": "Self Introduction", "level": "A1", "description": "Introduce yourself confidently", "video_id": "Tamil_VIDEO_4"},
                    {"id": "2.2", "title": "Family & Relations", "level": "A1", "description": "Talk about your family", "video_id": "Tamil_VIDEO_5"},
                    {"id": "2.3", "title": "Daily Activities", "level": "A2", "description": "Describe your routine", "video_id": "Tamil_VIDEO_6"}
                ]
            },
            "3": {
                "title": "Practical Skills",
                "description": "Real-world language applications",
                "lessons": [
                    {"id": "3.1", "title": "Shopping & Money", "level": "A2", "description": "Shopping conversations", "video_id": "Tamil_VIDEO_7"},
                    {"id": "3.2", "title": "Directions & Travel", "level": "A2", "description": "Navigate with confidence", "video_id": "Tamil_VIDEO_8"},
                    {"id": "3.3", "title": "Food & Dining", "level": "A2", "description": "Restaurant vocabulary", "video_id": "Tamil_VIDEO_9"}
                ]
            }
        },
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    }
}

# Complete LESSON_CONTENT dictionary
LESSON_CONTENT = {
    "Spanish": {
        "1.1": {
            "title": "Basic Greetings",
            "sections": [
                {
                    "title": "Common Greetings",
                    "content": """
                    - Hola = Hello
                    - Buenos días = Good morning
                    - Buenas tardes = Good afternoon
                    - Buenas noches = Good night
                    - ¿Cómo estás? = How are you?
                    - Bien, gracias = Fine, thank you
                    """
                },
                {
                    "title": "Practice Dialogue",
                    "content": """
                    A: ¡Hola! ¿Cómo estás?
                    B: ¡Hola! Bien, gracias. ¿Y tú?
                    A: Muy bien, gracias.
                    """
                }
            ],
            "summary": "In this lesson, we learned basic Spanish greetings and how to have a simple conversation.",
            "quiz": [
                {
                    "question": "How do you say 'Hello' in Spanish?",
                    "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                    "answer": "Hola"
                },
                {
                    "question": "What does 'Buenos días' mean?",
                    "options": ["Good night", "Good morning", "Good afternoon", "Goodbye"],
                    "answer": "Good morning"
                }
            ]
        },
        "1.3": {
            "title": "Days and Months",
            "sections": [
                {
                    "title": "Days of the Week",
                    "content": """
                    - Lunes = Monday
                    - Martes = Tuesday
                    - Miércoles = Wednesday
                    - Jueves = Thursday
                    - Viernes = Friday
                    - Sábado = Saturday
                    - Domingo = Sunday
                    """
                },
                {
                    "title": "Months",
                    "content": """
                    - Enero = January
                    - Febrero = February
                    ...and so on
                    """
                }
            ],
            "quiz": [
                {
                    "question": "What is 'Monday' in Spanish?",
                    "options": ["Lunes", "Martes", "Miércoles", "Domingo"],
                    "answer": "Lunes"
                }
            ]
        }
    },
    "French": {
        "1.1": {
            "title": "French Greetings",
            "sections": [
                {
                    "title": "Basic Greetings",
                    "content": """
                    - Bonjour = Hello/Good day
                    - Bonsoir = Good evening
                    - Au revoir = Goodbye
                    - Comment allez-vous? = How are you?
                    - Très bien, merci = Very well, thank you
                    """
                }
            ],
            "summary": "This lesson covered essential French greetings and basic conversation starters.",
            "quiz": [
                {
                    "question": "What does 'Bonjour' mean?",
                    "options": ["Goodbye", "Hello", "Good night", "Please"],
                    "answer": "Hello"
                }
            ]
        }
    }
}

class LanguageLearningSystem:
    def __init__(self):
        self.selected_language = None
        self.selected_chapter = None
        self.selected_lesson = None
        self.selected_lesson_id = None
        self.progress = {}
        self.lesson_generator = DynamicLessonGenerator()
        self.current_lesson = None
        self.load_progress()
        self.initialize_progress()

    def initialize_progress(self):
        """Initialize the progress tracking system"""
        if 'learning_progress' not in st.session_state:
            st.session_state.learning_progress = {}
        self.progress = st.session_state.learning_progress
        if 'progress' in st.session_state:
            self.main_progress = st.session_state.progress
        else:
            st.session_state.progress = {}
            self.main_progress = st.session_state.progress

    def select_language(self):
        languages = list(LANGUAGE_COURSES.keys())
        self.selected_language = st.sidebar.selectbox("Select Language", languages)

    def select_chapter(self):
        chapters = LANGUAGE_COURSES[self.selected_language]["chapters"]
        chapter_titles = [chapters[chap]["title"] for chap in chapters]
        self.selected_chapter = st.sidebar.selectbox("Select Chapter", chapter_titles)

    def get_lesson_id(self, title):
        """Get lesson ID from lesson title"""
        for lang in LANGUAGE_COURSES:
            for chapter in LANGUAGE_COURSES[lang]["chapters"].values():
                for lesson in chapter["lessons"]:
                    if lesson["title"] == title:
                        return lesson["id"]
        return None

    def select_lesson(self):
        chapters = LANGUAGE_COURSES[self.selected_language]["chapters"]
        for chap_id, chap_data in chapters.items():
            if chap_data["title"] == self.selected_chapter:
                lessons = chap_data["lessons"]
                lesson_titles = [lesson["title"] for lesson in lessons]
                self.selected_lesson = st.sidebar.selectbox("Select Lesson", lesson_titles)
                # Get the lesson ID for the selected title
                for lesson in lessons:
                    if lesson["title"] == self.selected_lesson:
                        self.selected_lesson_id = lesson["id"]
                break

    def update_progress(self):
        """Update progress for current lesson"""
        if self.selected_language and self.selected_lesson:
            lesson_key = f"{self.selected_language}-{self.selected_lesson_id}"
            self.progress[lesson_key] = True
            st.session_state.learning_progress = self.progress
            
            # Update main progress tracker
            if hasattr(self.main_progress, 'add_points'):
                self.main_progress.add_points(10)
            if hasattr(self.main_progress, 'record_practice'):
                self.main_progress.record_practice()

    def load_progress(self):
        # Load user progress from session state or initialize it
        if 'progress' not in st.session_state:
            st.session_state['progress'] = {}
        self.progress = st.session_state['progress']

    def save_progress(self):
        # Save user progress to session state
        st.session_state['progress'] = self.progress

    def get_progress_for_language(self, language):
        """Get progress percentage for a specific language"""
        if not language or not LANGUAGE_COURSES.get(language):
            return 0.0
        
        total_lessons = sum(
            len(chapter["lessons"]) 
            for chapter in LANGUAGE_COURSES[language]["chapters"].values()
        )
        
        if total_lessons == 0:
            return 0.0
            
        # Use self.progress dictionary instead of UserProgressTracker
        completed_lessons = sum(
            1 for key in self.progress.keys() 
            if key.startswith(f"{language}-") and self.progress[key]
        )
        
        return completed_lessons / total_lessons

    def show_lesson(self, lesson_id):
        """Load and display a specific lesson"""
        try:
            if not self.selected_language:
                raise ValueError("No language selected")
            
            # First try static content
            if self.selected_language in LESSON_CONTENT and lesson_id in LESSON_CONTENT[self.selected_language]:
                return LESSON_CONTENT[self.selected_language][lesson_id]
            
            # If not found, try dynamic generation
            lesson_title = None
            for chapter in LANGUAGE_COURSES[self.selected_language]["chapters"].values():
                for lesson in chapter["lessons"]:
                    if lesson["id"] == lesson_id:
                        lesson_title = lesson["title"]
                        break
                if lesson_title:
                    break
            
            if lesson_title:
                return self.lesson_generator.get_lesson_content(lesson_title, self.selected_language)
            
            raise ValueError(f"No content found for lesson {lesson_id}")
                
        except Exception as e:
            logger.error(f"Error loading lesson {lesson_id}: {str(e)}")
            return None

def embed_youtube_video(video_id, width=None):
    video_url = f"https://www.youtube.com/embed/{video_id}"
    st.video(video_url, format="video/mp4", start_time=0)

def show_lesson_catalog(system):
    """Display a catalog-style view of available lessons"""
    st.sidebar.markdown("### 📚 Course Navigation")
    
    # Language selection with flags
    languages = {
        "Spanish": "🇪🇸",
        "French": "🇫🇷",
        "German": "🇩🇪",
        "Italian": "🇮🇹",
        "Japanese": "🇯🇵",
        "Tamil": "🇮🇳"  # Using Indian flag for Tamil
    }
    
    selected_lang = st.sidebar.selectbox(
        "Choose Language",
        list(languages.keys()),
        format_func=lambda x: f"{languages[x]} {x}"
    )
    
    # Level filter
    levels = LANGUAGE_COURSES[selected_lang]["levels"]
    selected_level = st.sidebar.multiselect(
        "Filter by Level",
        levels,
        default=levels[0]
    )
    
    # Main content area
    st.markdown(f"## {languages[selected_lang]} {selected_lang} Learning Path")
    
    # Progress tracking
    progress = system.get_progress_for_language(selected_lang)
    st.progress(progress)
    st.markdown(f"**Course Progress:** {progress*100:.1f}%")
    
    # Display chapters in tabs
    chapter_tabs = st.tabs([
        f"Chapter {chap_num}: {chap_data['title']}" 
        for chap_num, chap_data in LANGUAGE_COURSES[selected_lang]["chapters"].items()
    ])
    
    for tab_idx, (chap_num, chap_data) in enumerate(LANGUAGE_COURSES[selected_lang]["chapters"].items()):
        with chapter_tabs[tab_idx]:
            st.markdown(f"### {chap_data['description']}")
            
            # Create columns for lesson cards
            cols = st.columns(2)
            for idx, lesson in enumerate(chap_data["lessons"]):
                if lesson["level"] in selected_level:
                    with cols[idx % 2]:
                        # Lesson card with glassmorphism
                        st.markdown(f"""
                        <div class="lesson-card glassmorphism">
                            <h4>{lesson["title"]} <span class="level-badge">{lesson["level"]}</span></h4>
                            <p>{lesson["description"]}</p>
                            <div class="lesson-actions">
                                <button onclick="startLesson('{lesson['id']}')">Start Lesson</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Make the card clickable
                        if st.button(f"Start {lesson['title']}", key=f"btn_{lesson['id']}"):
                            st.session_state.selected_lesson = lesson
                            st.rerun()

def show_lesson_interface(system):
    """Display lesson interface with proper error handling"""
    try:
        if 'selected_lesson' not in st.session_state:
            show_lesson_catalog(system)
            return

        lesson = st.session_state.selected_lesson
        
        # Set the selected language if not already set
        if not system.selected_language:
            for lang in LANGUAGE_COURSES:
                for chapter in LANGUAGE_COURSES[lang]["chapters"].values():
                    for l in chapter["lessons"]:
                        if l["id"] == lesson["id"]:
                            system.selected_language = lang
                            break
        
        lesson_content = system.show_lesson(lesson["id"])
        
        if not lesson_content:
            st.error("Could not load lesson content")
            if st.button("Return to Catalog"):
                del st.session_state.selected_lesson
                st.rerun()
            return

        # Display lesson content
        st.title(lesson_content["title"])
        
        # Show video selector if multiple options are available
        if "video_options" in lesson:
            video_titles = [v["title"] for v in lesson["video_options"]]
            selected_video = st.selectbox("Choose video lesson:", video_titles)
            video_id = next(v["id"] for v in lesson["video_options"] if v["title"] == selected_video)
            embed_youtube_video(video_id)
        elif "video_id" in lesson:
            embed_youtube_video(lesson["video_id"])

        # Display sections
        for section in lesson_content["sections"]:
            st.subheader(section["title"])
            st.markdown(section["content"])
        
        # Show quiz and navigation
        col1, col2 = st.columns(2)
        with col1:
            if "quiz" in lesson_content:
                show_quiz(lesson_content["quiz"])
        
        with col2:
            if "summary" in lesson_content:
                st.markdown("### Summary")
                st.write(lesson_content["summary"])
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Catalog"):
                del st.session_state.selected_lesson
                st.rerun()
        
        with col2:
            if st.button("Complete Lesson ✓"):
                system.update_progress()
                st.success("¡Muy bien! Lesson completed! +10 points")
                next_lesson = get_next_lesson(system.selected_language, lesson["id"])
                if next_lesson:
                    st.session_state.selected_lesson = next_lesson
                else:
                    del st.session_state.selected_lesson
                st.rerun()

    except Exception as e:
        logger.error(f"Error in lesson interface: {str(e)}", exc_info=True)
        st.error("Failed to display lesson. Please try again.")
        if st.button("Return to Catalog"):
            if 'selected_lesson' in st.session_state:
                del st.session_state.selected_lesson
            st.rerun()

def generate_lesson_summary(lesson_content):
    st.subheader("Lesson Summary")
    summary = lesson_content.get("summary")
    if summary:
        st.write(summary)
    else:
        st.write("No summary available for this lesson.")

def show_quiz(quiz_questions):
    st.subheader("Quiz")
    if not quiz_questions:
        st.write("No quiz available for this lesson.")
        return
    score = 0
    total = len(quiz_questions)
    for idx, question in enumerate(quiz_questions):
        st.write(f"Question {idx + 1}: {question['question']}")
        options = question['options']
        user_answer = st.radio("Choose your answer:", options, key=f"quiz_{idx}")
        if st.button("Submit Answer", key=f"submit_{idx}"):
            if user_answer == question['answer']:
                st.success("Correct!")
                score += 1
            else:
                st.error(f"Incorrect. The correct answer is: {question['answer']}.")
    st.write(f"You scored {score} out of {total}.")

    if score == total:
        st.balloons()  # Celebrate perfect score

def learning_interface():
    try:
        st.markdown("""
        <style>
        .lesson-card {
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
        }
        .level-badge {
            background: linear-gradient(45deg, #4A90E2, #67B26F);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
        }
        .breadcrumb {
            padding: 10px;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize system
        if 'learning_system' not in st.session_state:
            st.session_state.learning_system = LanguageLearningSystem()
        
        system = st.session_state.learning_system
        show_lesson_interface(system)
        
    except Exception as e:
        st.error(f"Error in learning interface: {str(e)}")
        logger.error(f"Learning interface error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    learning_interface()

class DynamicLessonGenerator:
    def __init__(self):
        self.lesson_cache = {}
        
    def get_lesson_content(self, lesson_name, language):
        try:
            # Try to get from cache first
            cache_key = f"{language}_{lesson_name}"
            if cache_key in self.lesson_cache:
                return self.lesson_cache[cache_key]
            
            # Generate dynamic content if not in cache
            content = self._generate_lesson_content(lesson_name, language)
            if not content:
                return self.get_fallback_content(lesson_name)
                
            # Cache the content
            self.lesson_cache[cache_key] = content
            return content
        except Exception as e:
            logger.error(f"Error generating lesson content: {str(e)}")
            return self.get_fallback_content(lesson_name)

    def get_fallback_content(self, lesson_name):
        """Provide fallback content when dynamic generation fails"""
        fallback_content = {
            "Basic Greetings": {
                "title": "Basic Greetings",
                "introduction": "Learn essential greetings to start conversations.",
                "sections": [
                    {
                        "title": "Common Greetings",
                        "content": ["Hello - The most basic greeting",
                                  "Hi - Informal greeting",
                                  "Good morning - Morning greeting",
                                  "Good afternoon - Afternoon greeting",
                                  "Good evening - Evening greeting"]
                    },
                    {
                        "title": "Practice",
                        "content": ["Practice these greetings with a partner",
                                  "Try using different greetings at different times of day"]
                    }
                ],
                "exercises": [
                    {
                        "question": "What greeting would you use at 9 AM?",
                        "options": ["Good morning", "Good evening", "Good afternoon"],
                        "correct": "Good morning"
                    }
                ],
                "summary": "You've learned basic greetings for different times of day."
            }
        }
        
        return fallback_content.get(lesson_name, {
            "title": "Lesson Not Found",
            "introduction": "We're sorry, this lesson is not available at the moment.",
            "sections": [],
            "exercises": [],
            "summary": "Please try another lesson."
        })

    def _generate_lesson_content(self, lesson_name, language):
        """Generate dynamic lesson content based on lesson name and language"""
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"Generate a structured lesson about {lesson_name} in {language}"
            
            response = requests.post(
                GROQ_API_ENDPOINT,
                headers=headers,
                json={
                    "prompt": prompt,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return None

def get_next_lesson(language, current_id):
    """Helper function to find the next lesson"""
    current_chapter, current_lesson = current_id.split('.')
    current_chapter = int(current_chapter)
    current_lesson = int(current_lesson)
    
    chapters = LANGUAGE_COURSES[language]["chapters"]
    
    # Try next lesson in current chapter
    if f"{current_chapter}.{current_lesson + 1}" in LESSON_CONTENT[language]:
        for lesson in chapters[str(current_chapter)]["lessons"]:
            if lesson["id"] == f"{current_chapter}.{current_lesson + 1}":
                return lesson
    
    # Try first lesson of next chapter
    if str(current_chapter + 1) in chapters:
        next_chapter_lessons = chapters[str(current_chapter + 1)]["lessons"]
        if next_chapter_lessons:
            return next_chapter_lessons[0]
    
    return None

# Move GROQ configuration to proper location
GROQ_API_ENDPOINT = "https://api.groq.com/v1/completions"
GROQ_API_KEY = "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"

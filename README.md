

# LinguaLearn Pro 🌍

A sophisticated language learning and translation platform built with Python and Streamlit, featuring AI-powered translations, interactive learning, and real-time practice.

## Features

### Core Features
- 🔤 Smart Translation with context and cultural insights
- 🗣️ Interactive Language Practice Chat
- 📚 Vocabulary Builder with spaced repetition
- 🎯 Grammar Quizzes and Exercises
- 🎮 Sentence Construction Practice
- 📊 Progress Tracking and Achievements
- 🌟 Multiple Language Support (11+ languages)

### Technical Features
- Voice Input/Output Capabilities
- Real-time Text-to-Speech
- Keyboard Shortcuts
- Session Management
- Progress Tracking System
- Spaced Repetition Algorithm
- Achievement System
- Responsive UI with Dark Theme

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd lingualearn-pro
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a 

.env

 file and add:
```
GROQ_API_KEY=your_api_key_here
```

## Dependencies

```txt
numpy>=1.23.0
pandas>=1.5.0
Pillow>=9.0.0
plotly>=5.13.0
python-dateutil>=2.8.2
python-dotenv>=0.21.0
pytesseract>=0.3.10
pyperclip>=1.8.2
requests>=2.28.0
SpeechRecognition>=3.10.0
streamlit>=1.24.0
streamlit-authenticator>=0.2.2
streamlit-card>=0.0.4
streamlit-extras>=0.2.7
streamlit-lottie>=0.0.3
streamlit-option-menu>=0.3.2
streamlit-toggle-switch>=1.0.0  # Updated version specification
keyboard>=0.13.5
gTTS>=2.3.1
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Navigate to `http://localhost:8501` in your web browser

## Features in Detail

### Translation
- Context-aware translations
- Cultural notes and explanations
- Grammar insights
- Example sentences
- Related idioms and expressions

### Practice Modes
- Grammar quizzes
- Vocabulary flashcards
- Sentence construction exercises
- Interactive chat practice

### Progress Tracking
- Points system
- Daily streaks
- Achievement badges
- Learning statistics

### User Interface
- Modern dark theme
- Responsive design
- Keyboard shortcuts
- Voice input/output
- Copy/paste functionality

## Architecture

The application is built with:
- Frontend: Streamlit
- Translation API: Groq
- Text-to-Speech: gTTS
- Speech Recognition: Google Speech Recognition
- Session Management: Streamlit State Management
- Data Persistence: Local Storage

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License

## Acknowledgments

- Streamlit for the amazing framework
- Groq for the translation API
- All contributors and maintainers

## Support

For support, email dinesh210805@gmail.com or create an issue in the repository.

---
Built with ❤️ by LinguaLearn Pro Team


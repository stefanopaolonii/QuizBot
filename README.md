![GitHub Repo stars](https://img.shields.io/github/stars/stefanopaolonii/quizbot?style=flat-square&logo=github&labelColor=0d1117&color=FFD700)
![Discord](https://img.shields.io/discord/1336983930015846400?style=flat-square&logo=discord&logoColor=ffffff&labelColor=0d1117&link=https%3A%2F%2Fdiscord.gg%2FWJDjPHANV7)



# Quiz-Bot: A Telegram Bot for Interactive Quizzes

`quiz-bot` is a **Telegram bot** designed to create, manage, and take interactive quizzes. It allows users to start a quiz and review existing questions. The bot supports **multiple languages** and allows questions to be categorized by topics.

- **Start Quiz**: Users can initiate a quiz and answer a series of questions.
- **Review Question**: Users can review and explore existing quiz questions.
- **Automated Testing**: Ensures that updates do not break functionality by testing the bot automatically.
- **Module Update Automation**: Automatically manages and updates the bot’s dependencies.

<!--
Keywords for Enhanced Visibility:
Telegram bot, Quiz bot, Interactive quizzes, Telegram quiz bot, Python Telegram bot, Python quiz bot, Multiple language support, Quiz management system, Quiz question database, Quiz questions, Automated testing, Data-driven quizzes, Open source quiz bot, Dockerized Telegram bot, Telegram API, Online quiz system, Quiz questions categorization
-->

## Requirements

- **Python Version**: 3.7 or higher.
- **Required Libraries**: All required libraries are listed in the `requirements.txt` file.
  - `python-telegram-bot` for Telegram API integration.
  - `python-dotenv` for managing environment variables.
- **Optional**: Docker for containerized deployment.

## Installation Guide

### Install Quiz-Bot Using Python

1. **Fork and Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/quiz-bot.git
    cd quiz-bot
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Install Quiz-Bot Using Docker

1. **Fork and Clone the Repository**:
    ```bash
    git clone https://github.com/stefanopaolonii/quizbot.git
    cd quiz-bot
    ```

2. **Build the Docker Image**:
    ```bash
    docker build -t quiz-bot .
    ```

3. **Run the Docker Container**:
    ```bash
    docker run -d --name quiz-bot -v $(pwd)/config.py:/app/config.py -v $(pwd)/questions.json:/app/questions.json quiz-bot
    ```

## Configuration of Quiz-Bot ⚙️
1.  **Set up Environment Variables**:
    Create a `.env` file in the root of your project. This file will store your bot's token securely.
    ```
    TOKEN="YOUR_BOT_TOKEN_HERE"
    ```
    > **Important**: Add the `.env` file to your `.gitignore` to prevent your token from being committed to version control.

2.  **Configure Paths (`config.py`)**:
    Ensure the `config.py` file points to your questions data file.
     ```python
     QUESTIONS_JSON_PATH = "data/questions.json"
     ```

2. **Setup Questions File (`questions.json`)**:  
   Ensure you have a `data/questions.json` file containing an array of questions in the specified format:
    ```json
    [
        {
            "id": -1,
            "language": "en",
            "text": "What is the capital of France?",
            "options": [
                "Berlin",
                "Madrid",
                "Paris",
                "Rome"
            ],
            "correct_index": 2,
            "verified": true,
            "explanation": "Paris is the capital city of France.",
            "topic": "Geography"
        }
    ]
    ```

## Running the Quiz-Bot
Once you've completed the installation and configuration steps, you can start the bot with the following command:

```bash
python main.py


<div align="left">
  <img src="https://visitor-badge.laobi.icu/badge?page_id=stefanopaolonii.quizbot&left_text=Visitors" />
</div>

# Quiz-Bot: A Telegram Bot for Interactive Quizzes 🤖🎮

`quiz-bot` is a **Telegram bot** designed to create, manage, and take interactive quizzes. It allows users to start a quiz, add and modify questions, and review existing questions. The bot supports **multiple languages** and allows questions to be categorized by topics. 🌍📚

While all users can participate in quizzes, only authorized users (staff) can add, edit, and manage quiz questions, providing a flexible and secure environment for quiz management. 🔐

## Features of Quiz-Bot ✨

- **Start Quiz**: Users can initiate a quiz and answer a series of questions. 🎯
- **Add Question**: Authorized users (staff members) can add new questions to the quiz database. 📝
- **Review Question**: Users can review and explore existing quiz questions. 🔍
- **Modify Question**: Only staff members can modify or update existing questions. 🛠️
- **Staff Management**: An advanced system for managing staff with different roles, such as Owner, Admin, and Moderator. 👨‍💻👩‍💻
- **Report System**: Users can submit, review, and manage quiz-related reports. 📊
- **Privacy Enhancements**: User IDs are masked for added privacy and anonymity. 🕵️‍♂️
- **Automated Testing**: Ensures that updates do not break functionality by testing the bot automatically. 🧪
- **Module Update Automation**: Automatically manages and updates the bot’s dependencies. 🔄

## Requirements 📋

- **Python Version**: 3.7 or higher 🐍
- **Required Libraries**: 
  - `python-telegram-bot` (for Telegram API integration) 📲
  - `asyncio` (for asynchronous functionality) ⏳
- **Optional**: Docker for containerized deployment 🚢

## Installation Guide 🛠️

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
    git clone https://github.com/your-username/quiz-bot.git
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

1. **Create a `config.py` File**:  
   Create a `config.py` file in the main project directory with the following content:
    ```python
    TOKEN = "YOUR_BOT_TOKEN"
    QUESTIONS_JSON_PATH = "data/questions.json"
    STAFF_JSON_PATH = "data/staff.json"
    REPORT_JSON_PATH = "data/reports.json"
    ```

2. **Setup Questions File (`questions.json`)**:  
   Ensure you have a `data/questions.json` file containing an array of questions in the following format:
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

3. **Setup Staff File (`staff.json`)**:  
   Define the staff members and their roles in the `staff.json` file:
    ```json
    [
        {
            "id": "YOUR_USER_ID",
            "role": "Owner"  # Possible roles: Owner, Admin, Mod
        }
    ]
    ```

## Running the Quiz-Bot 🚀

Once you've completed the installation and configuration steps, you can start the bot with the following command:

```bash
python main.py

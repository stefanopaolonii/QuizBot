# quiz-bot

## Description
`quiz-bot` is a simple Telegram bot designed to manage interactive quizzes. Users can start a quiz, add new questions, review existing questions, and modify questions. The bot supports selecting topics and languages for quiz questions. The bot can be used by all users, but only allowed users can add and modify questions.

This bot is ideal for educational purposes or for creating a fun, interactive quiz game for your Telegram group!

## Features
- **Start Quiz**: Users can start a quiz and answer a series of questions.
- **Add Question**: Allowed users can add new questions to the quiz database.
- **Review Question**: Users can review existing questions.
- **Change Question**: Allowed users can modify existing questions.
- **Multilingual Support**: The bot supports multiple languages for quiz questions, allowing for greater accessibility.
- **Topic Selection**: Users can choose a quiz topic from a predefined list when starting a quiz.

## Requirements
- Python 3.7+
- Python libraries:
  - `python-telegram-bot`
  - `asyncio`
  - (Other dependencies listed in `requirements.txt`)
- Docker (optional for containerized setup)

## Installation

### Using Python

1. **Fork the repository and clone your fork:**
    ```sh
    git clone https://github.com/your-username/quiz-bot.git
    cd quiz-bot
    ```

2. **Create a virtual environment and activate it:**
    - On macOS/Linux:
      ```sh
      python3 -m venv venv
      source venv/bin/activate
      ```
    - On Windows:
      ```sh
      python -m venv venv
      venv\Scripts\activate
      ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

### Using Docker (optional)

1. **Fork the repository and clone your fork:**
    ```sh
    git clone https://github.com/your-username/quiz-bot.git
    cd quiz-bot
    ```

2. **Build the Docker image:**
    ```sh
    docker build -t quiz-bot .
    ```

3. **Run the Docker container:**
    ```sh
    docker run -d --name quiz-bot -v $(pwd)/config.py:/app/config.py -v $(pwd)/questions.json:/app/questions.json quiz-bot
    ```

## Configuration

### 1. Update the `config.py` File

In the main project directory, you'll find the `config.py` file. You need to modify it with your own bot's API token and other necessary information. Update the file as follows:

```python
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Your bot's API token from BotFather
QUESTIONS_JSON_PATH = "questions.json"  # Path to the questions JSON file
ALLOWED_USER_IDS = [ ]  # List of user IDs that are allowed to add, modify, or delete questions
```

### 2. Ensure `questions.json` is configured properly

The `questions.json` file is already present in the main project directory. Ensure that it contains valid quiz questions in the following format:

## JSON Format for Questions

```json
[
    {
        "id": -1,
        "language": "en",
        "text": "Question text here",
        "options": [
            "Option 1",
            "Option 2",
            "Option 3",
            "Option 4"
        ],
        "correct_index": 0,
        "verified": true,
        "explanation": "Explanation text here",
        "topic": "Topic here"
    }
]
```

## Running the Bot
To start the bot, run the following command:
```sh
python main.py
```

This will launch the bot, and it will be ready to interact with users. Ensure the bot token and configuration files are set up correctly before running it.

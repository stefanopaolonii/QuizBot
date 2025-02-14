# quiz-bot

## Description
`quiz-bot` is a simple Telegram bot designed to manage interactive quizzes. Users can start a quiz, add new questions, review existing questions, and modify questions. The bot supports selecting topics and languages for quiz questions. The bot can be used by all users, but only allowed users can add and modify questions.

## Features
- **Start Quiz**: Users can start a quiz and answer a series of questions.
- **Add Question**: Allowed users can add new questions to the quiz database.
- **Review Question**: Users can review existing questions.
- **Change Question**: Allowed users can modify existing questions.

## Requirements
- Python 3.7+
- Python libraries: `python-telegram-bot`, `asyncio`
- Docker (optional)

## Installation

### Using Python
1. Fork the repository and clone your fork:
    ```sh
    git clone https://github.com/your-username/quiz-bot.git
    cd quiz-bot
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Using Docker
1. Fork the repository and clone your fork:
    ```sh
    git clone https://github.com/your-username/quiz-bot.git
    cd quiz-bot
    ```

2. Build the Docker image:
    ```sh
    docker build -t quiz-bot .
    ```

3. Run the Docker container:
    ```sh
    docker run -d --name quiz-bot -v $(pwd)/config.py:/app/config.py -v $(pwd)/questions.json:/app/questions.json quiz-bot
    ```

## Configuration
1. Create a [config.py](http://_vscodecontentref_/1) file in the main project directory with the following content:
    ```python
    TOKEN = "YOUR_TELEGRAM_TOKEN"
    QUESTIONS_JSON_PATH = "questions.json"
    ALLOWED_USER_IDS = [ ]  # Replace with the IDs of authorized users
    ```

2. Ensure you have a [questions.json](http://_vscodecontentref_/2) file in the main project directory. This file should contain an array of questions in JSON format.
## JSON Format for Questions
Each question in the [questions.json](http://_vscodecontentref_/3) file should follow this format:
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
    },
]
```


## Running the Bot
To start the bot, run the following command:
```sh
python main.py
```
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.bot_runner import QuizBot
from telegram import Update, Bot
from telegram.ext import CallbackContext
from app.handlers import _escape_markdown, State
from app import main_menu_text

# Mock Telegram dependencies
@pytest.fixture
def mock_bot():
    # Mock a bot application
    bot = MagicMock(spec=Bot)
    quiz_bot = QuizBot("dummy_token", "data/questions.json", MagicMock())
    quiz_bot.application.bot = bot
    # Mock a coroutine method
    quiz_bot.conv_quiz_start = AsyncMock()
    quiz_bot.conv_review_question_start = AsyncMock()
    return quiz_bot

@pytest.fixture
def mock_update():
    # Create a mock Update
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user.id = 12345  # A dummy ID
    mock_update.effective_chat.id = 12345  # A dummy chat ID
    return mock_update

@pytest.fixture
def mock_context():
    # Create a mock CallbackContext
    context = MagicMock(spec=CallbackContext)
    context.user_data = {}
    return context

# Test for the /start command
@pytest.mark.asyncio
async def test_command_start(mock_bot, mock_update, mock_context):
    # Mock the bot's response for sending a message
    await mock_bot.command_start(mock_update, mock_context)
    
    # Verify that the send_message method is called with the correct parameters
    mock_bot.application.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY  # Verify that a reply_markup is passed
    )
    assert mock_context.user_data["state"] == State.SELECTING_ACTION

# Test for the /quiz command
@pytest.mark.asyncio
async def test_command_quiz(mock_bot, mock_update, mock_context):
    # Simulate the behavior of the /quiz command
    await mock_bot.command_quiz(mock_update, mock_context)
    
    # Verify that the conv_quiz_start method is called
    mock_bot.conv_quiz_start.assert_called_once_with(mock_update, mock_context)

# Test for the /review command
@pytest.mark.asyncio
async def test_command_review(mock_bot, mock_update, mock_context):
    # Simulate the behavior of the /review command
    await mock_bot.command_review(mock_update, mock_context)
    
    # Verify that the conv_review_question_start method is called
    mock_bot.conv_review_question_start.assert_called_once_with(mock_update, mock_context)

# Test for the /cancel command (reset user state)
@pytest.mark.asyncio
async def test_command_restart(mock_bot, mock_update, mock_context):
    # Simulate the use of the /cancel command
    await mock_bot.command_restart(mock_update, mock_context)
    
    # Verify that the restart message is sent and the state logic has been reset
    mock_bot.application.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY
    )
    assert mock_context.user_data["state"] == State.SELECTING_ACTION
import pytest
from unittest.mock import MagicMock
from app.bot_runner import QuizBot
from telegram import Update, Bot
from telegram.ext import CallbackContext
from app.handlers import _escape_markdown
from app import main_menu_text

# Mock delle dipendenze di Telegram
@pytest.fixture
def mock_bot():
    # Mock di una bot application
    bot = MagicMock(spec=Bot)
    quiz_bot = QuizBot("dummy_token", "data/questions.json", "data/staff.json", "data/reports.json", MagicMock())
    quiz_bot.application.bot = bot
    return quiz_bot

@pytest.fixture
def mock_update():
    # Crea un mock di Update
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user.id = 12345  # Un ID fittizio
    mock_update.effective_chat.id = 12345  # Un ID fittizio per il chat
    return mock_update

@pytest.fixture
def mock_context():
    # Crea un mock di CallbackContext
    return MagicMock(spec=CallbackContext)

# Test per il comando /start
@pytest.mark.asyncio
async def test_command_start(mock_bot, mock_update, mock_context):
    # Mock della risposta del bot per l'invio di un messaggio
    await mock_bot.command_start(mock_update, mock_context)
    
    # Verifica che il metodo send_message venga chiamato con i corretti parametri
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY  # Verifica che venga passato un reply_markup
    )

# Test per il comando /quiz
@pytest.mark.asyncio
async def test_command_quiz(mock_bot, mock_update, mock_context):
    # Simula il comportamento del comando /quiz
    await mock_bot.command_quiz(mock_update, mock_context)
    
    # Verifica che il metodo conv_quiz_start venga chiamato
    mock_bot.conv_quiz_start.assert_called_once_with(mock_update, mock_context)

# Test per il comando /addq
@pytest.mark.asyncio
async def test_command_add_question(mock_bot, mock_update, mock_context):
    # Simula il comportamento del comando /addq
    await mock_bot.command_add_question(mock_update, mock_context)
    
    # Verifica che il metodo conv_add_question_start venga chiamato
    mock_bot.conv_add_question_start.assert_called_once_with(mock_update, mock_context)

# Test per il comando /cancel (reset dello stato dell'utente)
@pytest.mark.asyncio
async def test_command_restart(mock_bot, mock_update, mock_context):
    # Simula l'uso del comando /cancel
    await mock_bot.command_restart(mock_update, mock_context)
    
    # Verifica che venga inviato il messaggio di restart e la logica di stato sia stata reset
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY
    )
    assert mock_context.user_data["state"] == "SELECTING_ACTION"
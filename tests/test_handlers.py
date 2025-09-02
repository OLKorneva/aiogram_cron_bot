import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from app.handlers.start_dialogue import cmd_start
from app.utils.form import UserForm


@pytest.mark.asyncio
async def test_cmd_start_new_user():
    mock_from_user = MagicMock()
    mock_from_user.id = 123
    mock_from_user.first_name = "TestUser"

    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = mock_from_user
    mock_message.answer = AsyncMock()

    mock_state = AsyncMock(spec=FSMContext)
    mock_state.get_state = AsyncMock(return_value=None)
    mock_state.clear = AsyncMock()
    mock_state.set_state = AsyncMock()

    mock_bot = AsyncMock(spec=Bot)
    mock_bot.forward_message = AsyncMock()

    with patch("app.handlers.start_dialogue.dialogue_messages", {"start": {"forward_key": 15}}), \
         patch("app.handlers.start_dialogue.questions", {"name": "What is your name?"}), \
         patch("app.handlers.start_dialogue.CHANNEL_ID", -1003069055963):

        await cmd_start(mock_message, mock_bot, mock_state)

    mock_state.clear.assert_awaited_once()
    mock_bot.forward_message.assert_awaited_once_with(
        chat_id=123,
        from_chat_id=-1003069055963,
        message_id=15
    )
    mock_message.answer.assert_awaited_once_with(text="What is your name?")
    mock_state.set_state.assert_awaited_once_with(UserForm.waiting_for_question_name)

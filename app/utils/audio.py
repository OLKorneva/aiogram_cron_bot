import os
import logging
from aiogram.types import FSInputFile, Message, Audio, Document
from app.cash.cash import save_cache, messages_meta

async def send_audio_challenge(bot, user_id: int, key: str):
    meta = messages_meta.get(key)
    if not meta:
        logging.info(f'метаданные по ключу {key} в messages_meta не найдены')
        return

    name = meta['name']
    title = meta['title']
    file_id = meta.get('file_id')

    if file_id:
        try:
            await bot.send_audio(chat_id=user_id, audio=file_id, protect_content=True)
            logging.info(f"Аудио {name} отправлено пользователю {user_id} через file_id")
            return
        except Exception as e:
            logging.warning(f"file_id для {name} не сработал: {e}, пробуем загрузить файл")

    # Загружаем локальный файл
    audio_path = os.path.join("app/audio", name)
    if os.path.exists(audio_path):
        audio = FSInputFile(audio_path)
        msg: Message = await bot.send_audio(chat_id=user_id, audio=audio, title=title)

        new_file_id = None
        if isinstance(msg.audio, Audio):
            new_file_id = msg.audio.file_id
        elif isinstance(msg.document, Document):
            new_file_id = msg.document.file_id

        if new_file_id:
            messages_meta[key]['file_id'] = new_file_id
            save_cache()  # сохраняем кеш
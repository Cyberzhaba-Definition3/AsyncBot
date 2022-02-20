from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import config
import generator
import messages
import os
import states

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
generator = generator.Generator(bot)


# Commands /help, /start
@dp.message_handler(commands=["help", "start"])
async def send_guide(message: types.Message):
    await message.answer(messages.guide)


# Command /new
@dp.message_handler(commands=["new"])
async def create_collection(message: types.Message):
    await message.answer(messages.send_archive)
    await states.CollectionCreation.waiting_for_archive.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT,
                    state=states.CollectionCreation.waiting_for_archive)
async def upload_archive(message: types.File, state: FSMContext):
    e_file_id = message.document.file_id
    e_file = await bot.get_file(e_file_id)
    e_file_path = e_file.file_path

    user_id = message["from"]["id"]
    i_file_name = e_file_id + "." + e_file_path.split(".")[-1]

    await bot.download_file(e_file_path, f"temp/{message.document.file_id}.zip")
    
    generator.queue.append({
        "file": f"data/{user_id}/{i_file_name}",
        "user_id": user_id,
        'msg': message
    })
    print(generator.queue)
    await message.answer(messages.archive_added_to_queue)


# ___
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

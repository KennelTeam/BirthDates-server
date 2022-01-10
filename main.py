from aiogram.utils import executor

from bot import dp, shutdown

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)

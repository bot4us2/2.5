# apoio_apple_25.py
from aiogram import types, Dispatcher
from config_25 import user_data

def register_handlers_apoio_apple(dp: Dispatcher):
    @dp.callback_query(lambda c: c.data == "apoio_apple")
    async def apoio_apple(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user or not user.get("username"):
            await callback_query.message.answer("⚠️ Faz login primeiro para ver os teus dados.")
            return

        await callback_query.message.answer(
            "🍏 <b>App recomendada para iPhone/Mac</b>:\n"
            "🔸 MYTVOnline+ IPTV Player 4+\n"
            "🔗 https://apps.apple.com/us/app/mytvonline-iptv-player/id6714452886"
        )

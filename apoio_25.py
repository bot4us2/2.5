# apoio_25.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config_25 import user_data
from apoio_apple_25 import register_handlers_apoio_apple
from apoio_android_25 import register_handlers_apoio_android
from apoio_windows_25 import register_handlers_apoio_windows
from apoio_tv_25 import register_handlers_apoio_tv

def register_handlers_apoio(dp):

    def teclado_apoio():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Android", callback_data="apoio_android")],
            [InlineKeyboardButton(text="💻 Windows", callback_data="apoio_windows")],
            [InlineKeyboardButton(text="🍏 iPhone/Mac", callback_data="apoio_apple")],
            [InlineKeyboardButton(text="📺 Smart TV", callback_data="apoio_tv")],
            [InlineKeyboardButton(text="💬 Apoio via Chat", url="https://t.me/hhcihs")]
        ])

    @dp.callback_query(lambda c: c.data == "apoio")
    async def apoio_tecnico_callback(callback_query: types.CallbackQuery):
        dados = user_data.get(callback_query.from_user.id)
        if not dados or not dados.get("username"):
            await callback_query.message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
            return
        await callback_query.message.answer("🛠 Qual destes dispositivos usas?", reply_markup=teclado_apoio())

    @dp.message(lambda msg: msg.text and "apoio" in msg.text.lower())
    async def menu_apoio_handler(message: Message):
        dados = user_data.get(message.from_user.id)
        if not dados or not dados.get("username"):
            await message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
            return
        await message.answer("🛠 Qual destes dispositivos usas?", reply_markup=teclado_apoio())

    # Registar handlers dos outros ficheiros
    register_handlers_apoio_android(dp)
    register_handlers_apoio_windows(dp)
    register_handlers_apoio_tv(dp)
    register_handlers_apoio_apple(dp)

# 🔧 Esta função está fora do register_handlers_apoio para ser usada externamente (ex: em login_25.py)
async def mostrar_menu_apoio(message, user):
    username = user.get("username", "")
    password = user.get("password", "")

    texto = (
        f"🔧 <b>Apoio Técnico</b>\n\n"
        f"Estás com o acesso:\n"
        f"👤 <b>Username:</b> {username}\n"
        f"🔑 <b>Password:</b> {password}\n\n"
        f"Escolhe a tua plataforma para receber instruções:"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📱 Android", callback_data="apoio_android")],
        [InlineKeyboardButton("💻 Windows", callback_data="apoio_windows")],
        [InlineKeyboardButton("🍏 iPhone/Mac", callback_data="apoio_apple")],
        [InlineKeyboardButton("📺 Smart TV", callback_data="apoio_tv")],
        [InlineKeyboardButton("💬 Apoio via Chat", url="https://t.me/hhcihs")]
    ])

    await message.answer(texto, reply_markup=kb, parse_mode="HTML")

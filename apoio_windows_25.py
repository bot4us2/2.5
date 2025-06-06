from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_25 import user_data

def register_handlers_apoio_windows(dp: Dispatcher):

    @dp.callback_query(lambda c: c.data == "apoio_windows")
    async def apoio_windows(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user or not user.get("username"):
            await callback_query.message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
            return

        await callback_query.message.answer(
            "💻 <b>Seleciona uma das opções abaixo:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📲 IPTV Smarters – Instalação com os meus dados", callback_data="instalar_smarters_windows")],
                [InlineKeyboardButton(text="🔐 VPN Guardian – Instalação com os meus dados", callback_data="instalar_vpn_windows")]
            ])
        )

    @dp.callback_query(lambda c: c.data == "instalar_smarters_windows")
    async def tutorial_smarters_windows(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Faz Log In primeiro.")
            return

        username = user.get("username", "SEU_USERNAME")
        password = user.get("password", "SUA_PASSWORD")

        await callback_query.message.answer("💻 <b>Instalação do IPTV Smarters Pro (Windows)</b>")

        await callback_query.message.answer(
            "1️⃣ <b>Instala a aplicação:</b>\n"
            "👉 <a href=\"https://drive.google.com/uc?export=download&id=1_UVQde1U38srRZhL9Gydkb4U20Pv6KDw\">Clique aqui para baixar</a>\n"
            "Depois de instalar, abre a aplicação no teu PC."
        )

        await callback_query.message.answer_photo(
            photo="https://drive.google.com/uc?export=view&id=1HJ2pESFnV6bGmfZiSrbPgY7pChDRYJmK",
            caption="2️⃣ Preenche os campos deste quadro:\n"
                    f"📝 Nome da Playlist: <i>O que quiseres</i>\n"
                    f"👤 Username: <code>{username}</code>\n"
                    f"🔐 Password: <code>{password}</code>\n"
                    f"🌐 URL: <code>http://v6666.live:8080</code>"
        )

        await callback_query.message.answer_photo(
            photo="https://drive.google.com/uc?export=view&id=1sTfBXyWx_AuSpdcN57GdBwqKC8nCYLKq",
            caption="3️⃣ Após guardar, abre as definições (Settings)"
        )

        await callback_query.message.answer_photo(
            photo="https://drive.google.com/uc?export=view&id=15FpL5MGoIQI1hRJK5Op6XaYQ2w7TAxH8",
            caption="4️⃣ Dentro de <b>Settings</b> clica em <b>Stream Format</b>"
        )

        await callback_query.message.answer_photo(
            photo="https://drive.google.com/uc?export=view&id=1z77HOK3LGu_l__8EsjToPZYg0mKX52_J",
            caption="5️⃣ Dentro de <b>Stream Format</b>, escolhe <b>MPEGTS</b> (obrigatório)"
        )

        await callback_query.message.answer(
            "✅ Agora volta ao Menu Principal e começa a desfrutar do conteúdo!\n\n"
            "<i>Se precisares de ajuda, fala connosco via chat: @hhcihs</i>"
        )

    @dp.callback_query(lambda c: c.data == "instalar_vpn_windows")
    async def tutorial_vpn_windows(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Faz Log In primeiro.")
            return

        email = user.get("email", "SEU_EMAIL")
        password = user.get("password", "SUA_PASSWORD")

        await callback_query.message.answer("🔐 <b>Instalação da VPN Guardian (Windows)</b>")

        await callback_query.message.answer(
            "1️⃣ <b>Instala a aplicação VPN Guardian:</b>\n"
            "👉 <a href=\"https://platinum-apk.com/platinumvpn.exe\">Clique aqui para baixar</a>\n"
            "Depois de instalado, abre a aplicação no teu PC."
        )

        await callback_query.message.answer_photo(
            photo="https://drive.google.com/uc?export=view&id=1Yi2VruRKK2m_QlnBp9PRsERyQwvqKM0U",
            caption="2️⃣ Ao abrir a aplicação, deverás ver este ecrã inicial da VPN Guardian."
        )

        await callback_query.message.answer(
            f"3️⃣ Preenche com os teus dados:\n\n"
            f"📧 Email: <code>{email}</code>\n"
            f"🔐 Password: <code>{password}</code>"
        )

        await callback_query.message.answer(
            "4️⃣ Clica em <b>AUTO SELECT</b> para a VPN escolher o melhor servidor.\n"
            "5️⃣ A VPN ficará ativa e pronta para proteger a tua ligação.\n\n"
            "✅ <b>Agora estás protegido e otimizado para streaming!</b>\n"
            "<i>Se precisares de ajuda, fala connosco via chat: @hhcihs</i>"
        )

from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_25 import user_data

def botao_instalacao(nome, callback):
    return [InlineKeyboardButton(text=f"📲 {nome} – Instalação com os meus dados", callback_data=callback)]

def register_handlers_apoio_android(dp: Dispatcher):

    @dp.callback_query(lambda c: c.data == "apoio_android")
    async def apoio_android(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📲 <b>Apps compatíveis com Android</b>:\n\n"
            "🔸 https://platinum-apk.com/PlatinumTeam-7.0-v1001-1006-vpn.apk\n"
            "🔑 Password: <code>PLATINUM2030</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                botao_instalacao("V7", "instalar_v7")
            ])
        )

        await callback_query.message.answer(
            "🔸 https://platinum-apk.com/PlatinumTeam-6.0-v801.apk\n"
            "🔑 Password: <code>PLATINUM2030</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                botao_instalacao("V6", "instalar_v6")
            ])
        )

        await callback_query.message.answer(
            "🔸 https://platinum-apk.com/PlatinumTeamV2.apk\n"
            "🔑 Password: <code>PLATINUM2030</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                botao_instalacao("V2", "instalar_v2")
            ])
        )

        await callback_query.message.answer(
            "🔸 https://platinum-apk.com/PurplePLATINUMTEAM.apk\n"
            "🔑 Password: <code>PLATINUM2030</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                botao_instalacao("Purple", "instalar_purple")
            ])
        )

        await callback_query.message.answer(
            "🔸 https://platinum-apk.com/PlatinumGuardianVPN(3.0).apk\n"
            "🔑 Password: <code>PLATINUM2030</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                botao_instalacao("VPN", "instalar_vpn")
            ])
        )

        await callback_query.message.answer(
            "🔸 https://platinum-apk.com/smarters4-0.apk\n"
            "🔸 https://platinum-apk.com/mytvonline+.apk\n"
            "🔑 Password: <code>PLATINUM2030</code>"
        )

    # Handlers para cada botão de instalação
    async def enviar_instrucao(callback_query, app_nome, url):
        user = user_data.get(callback_query.from_user.id)
        if not user or not user.get("username"):
            await callback_query.message.answer("⚠️ Faz login primeiro para veres os teus dados.")
            return

        username = user.get("username", "SEU_USERNAME")
        password = user.get("password", "SUA_PASSWORD")

        await callback_query.message.answer(f"📲 <b>Instalação da app {app_nome} (Android)</b>")
        await callback_query.message.answer(
            f"🔗 Link para instalar: {url}\n"
            f"🔑 Password: <code>PLATINUM2030</code>\n\n"
            f"🧾 Dados para configuração:\n"
            f"👤 Username: <code>{username}</code>\n"
            f"🔐 Password: <code>{password}</code>\n"
            f"🌐 URL: <code>http://v6666.live:8080</code>",
            parse_mode="HTML"
        )

    @dp.callback_query(lambda c: c.data == "instalar_v7")
    async def instalar_v7(callback_query: types.CallbackQuery):
        await enviar_instrucao(callback_query, "Platinum V7", "https://platinum-apk.com/PlatinumTeam-7.0-v1001-1006-vpn.apk")

    @dp.callback_query(lambda c: c.data == "instalar_v6")
    async def instalar_v6(callback_query: types.CallbackQuery):
        await enviar_instrucao(callback_query, "Platinum V6", "https://platinum-apk.com/PlatinumTeam-6.0-v801.apk")

    @dp.callback_query(lambda c: c.data == "instalar_v2")
    async def instalar_v2(callback_query: types.CallbackQuery):
        await enviar_instrucao(callback_query, "Platinum V2", "https://platinum-apk.com/PlatinumTeamV2.apk")

    @dp.callback_query(lambda c: c.data == "instalar_purple")
    async def instalar_purple(callback_query: types.CallbackQuery):
        await enviar_instrucao(callback_query, "Purple", "https://platinum-apk.com/PurplePLATINUMTEAM.apk")

    @dp.callback_query(lambda c: c.data == "instalar_vpn")
    async def instalar_vpn(callback_query: types.CallbackQuery):
        await enviar_instrucao(callback_query, "VPN Guardian", "https://platinum-apk.com/PlatinumGuardianVPN(3.0).apk")

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

    # Handlers de instalação com passo a passo
    async def procedimento_instalacao(callback_query, app_nome, imagem_id, instrucoes, user_data_extra=None):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
            return

        username = user.get("username", "SEU_USERNAME")
        password = user.get("password", "SUA_PASSWORD")
        email = user.get("email", "SEU_EMAIL")

        # Extra substituições no texto (como {username})
        user_info = {"username": username, "password": password, "email": email}
        if user_data_extra:
            user_info.update(user_data_extra)

        await callback_query.message.answer_photo(
            photo=f"https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
            caption=f"1️⃣ Instala a app 'Downloader' da Play Store"
        )

        for instrucao in instrucoes:
            texto = instrucao["texto"].format(**user_info)
            if "img_id" in instrucao:
                await callback_query.message.answer_photo(
                    photo=f"https://drive.google.com/uc?export=view&id={instrucao['img_id']}",
                    caption=texto,
                    parse_mode="HTML"
                )
            else:
                await callback_query.message.answer(texto, parse_mode="HTML")

    @dp.callback_query(lambda c: c.data == "instalar_v7")
    async def instalar_v7(callback_query: types.CallbackQuery):
        await procedimento_instalacao(
            callback_query,
            "Platinum V7",
            "1ZIjc6nPq9cAcTQvnEPc0mz5L_z_NH2hW",
            [
                {"texto": "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\nVai a ‘Definições’ > ‘Opções de Programador’\nAtiva fontes desconhecidas para a app Downloader."},
                {"texto": "<b>3️⃣ Abre a app Downloader</b> e escreve:\n<code>https://platinum-apk.com</code>"},
                {"texto": "4️⃣ Seleciona a app 'PLATINUM V7 XCIPTV'", "img_id": "1ZIjc6nPq9cAcTQvnEPc0mz5L_z_NH2hW"},
                {"texto": "5️⃣ Escreve a password: <code>PLATINUM2030</code>"},
                {"texto": "6️⃣ Ao abrir, escolhe o painel <b>PLATINUM OLD</b>.\n7️⃣ Preenche:\n👤 <code>{username}</code>\n🔐 <code>{password}</code>\n🌐 URL: <code>http://v6666.live:8080</code>\n✅ <b>Bom proveito!</b>"}
            ]
        )

    @dp.callback_query(lambda c: c.data == "instalar_v6")
    async def instalar_v6(callback_query: types.CallbackQuery):
        await procedimento_instalacao(
            callback_query,
            "Platinum V6",
            "1ivI08loZf6JqywY8DxVM5Zctt7mM9b-B",
            [
                {"texto": "<b>2️⃣ Permite instalações de fontes desconhecidas</b>"},
                {"texto": "<b>3️⃣ Abre a app Downloader</b> e escreve:\n<code>https://platinum-apk.com</code>"},
                {"texto": "4️⃣ Seleciona a app 'PLATINUM V6 XCIPTV'", "img_id": "1ivI08loZf6JqywY8DxVM5Zctt7mM9b-B"},
                {"texto": "5️⃣ Password: <code>PLATINUM2030</code>"},
                {"texto": "6️⃣ Escolhe painel <b>PLATINUM OLD</b>\n👤 <code>{username}</code> | 🔐 <code>{password}</code>\n🌐 <code>http://v6666.live:8080</code>"}
            ]
        )

    @dp.callback_query(lambda c: c.data == "instalar_v2")
    async def instalar_v2(callback_query: types.CallbackQuery):
        await procedimento_instalacao(
            callback_query,
            "Platinum V2",
            "1eTYXhfpzw74lQg22XTkXbV7OzB19MO1q",
            [
                {"texto": "Mesmas instruções acima. Seleciona agora a app V2:"},
                {"texto": "4️⃣ App 'PLATINUM V2 XCIPTV'", "img_id": "1eTYXhfpzw74lQg22XTkXbV7OzB19MO1q"},
                {"texto": "Painel: <b>PLATINUM OLD</b>\n👤 <code>{username}</code>\n🔐 <code>{password}</code>"}
            ]
        )

    @dp.callback_query(lambda c: c.data == "instalar_purple")
    async def instalar_purple(callback_query: types.CallbackQuery):
        await procedimento_instalacao(
            callback_query,
            "Purple",
            "1DcLU55kb3JNAc6czmtmnlx4oV0yir_qP",
            [
                {"texto": "4️⃣ Seleciona a app 'Purple PLATINUM TEAM'", "img_id": "1DcLU55kb3JNAc6czmtmnlx4oV0yir_qP"},
                {"texto": "Escolhe dispositivo (TV/Móvel), depois insere:\n👤 <code>{username}</code>\n🔐 <code>{password}</code>"}
            ]
        )

    @dp.callback_query(lambda c: c.data == "instalar_vpn")
    async def instalar_vpn(callback_query: types.CallbackQuery):
        await procedimento_instalacao(
            callback_query,
            "VPN",
            "1Yi2VruRKK2m_QlnBp9PRsERyQwvqKM0U",
            [
                {"texto": "4️⃣ Seleciona a app 'Platinum Guardian VPN'", "img_id": "1Yi2VruRKK2m_QlnBp9PRsERyQwvqKM0U"},
                {"texto": "Insere os dados:\n📧 <code>{email}</code>\n🔐 <code>{password}</code>\n✅ Clica em AUTO SELECT."}
            ]
        )

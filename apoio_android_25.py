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

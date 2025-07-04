# carregamentos_25.py
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import os, tempfile
from googleapiclient.http import MediaFileUpload

from config_25 import bot, user_data, sheet_service, drive_service, SPREADSHEET_ID, PASTA_COMPROVATIVOS_ID
from email_utils_25 import enviar_email
from notificacao_upload_25 import enviar_notificacao
from utils_carregamentos_25 import atualizar_registro_revendedor, registar_historico_carregamento

ENTIDADE = os.getenv("ENTIDADE")
REFERENCIA = os.getenv("REFERENCIA")

def register_handlers_carregamentos(dp: Dispatcher):
    @dp.callback_query(lambda c: c.data == "menu_carregamentos")
    async def menu_carregamentos(callback_query: types.CallbackQuery):
        opcoes = [
            ("75€ – 25 créditos", "carregar_75"),
            ("100€ – 34 créditos", "carregar_100"),
            ("150€ – 51 créditos", "carregar_150"),
            ("200€ – 75 créditos", "carregar_200"),
            ("300€ – 115 créditos", "carregar_300"),
            ("400€ – 155 créditos", "carregar_400"),
            ("500€ – 200 créditos", "carregar_500"),
            ("600€ – 250 créditos", "carregar_600")
        ]

        botoes = [
            [
                InlineKeyboardButton(text=f"💵 {texto}", callback_data=code),
                InlineKeyboardButton(text="📊 + Info", callback_data=f"info_{code.split('_')[1]}")
            ] for texto, code in opcoes
        ]

        await callback_query.message.answer("💰 Escolhe o valor de carregamento:", reply_markup=InlineKeyboardMarkup(inline_keyboard=botoes))

    @dp.callback_query(lambda c: c.data.startswith("info_"))
    async def mais_info_carregamento(callback_query: types.CallbackQuery):
        cod = callback_query.data.split("_")[1]
        tabela_info = {
        "75": ("3.00", ["2.94", "2.94", "8.82", "8.82", "17.65", "14.71", "35.29", "29.41"]),
        "100": ("2.94", ["2.94", "2.94", "8.82", "8.82", "17.65", "14.71", "35.29", "29.41"]),
        "150": ("2.94", ["2.94", "2.94", "8.82", "8.82", "17.65", "14.71", "35.29", "29.41"]),
        "200": ("2.67", ["2.67", "2.67", "8.00", "8.00", "16.00", "13.33", "32.00", "26.67"]),
        "300": ("2.61", ["2.61", "2.61", "7.83", "7.83", "15.65", "13.04", "31.30", "26.09"]),
        "370": ("2.62", ["2.62", "2.62", "7.87", "7.87", "15.74", "13.12", "31.49", "26.24"]),
        "400": ("2.58", ["2.58", "2.58", "7.74", "7.74", "15.48", "12.90", "30.97", "25.81"]),
        "500": ("2.50", ["2.50", "2.50", "7.50", "7.50", "15.00", "12.50", "30.00", "25.00"]),
        "600": ("2.40", ["2.40", "2.40", "7.20", "7.20", "14.40", "12.00", "28.80", "24.00"])
    }
        preco_unit, planos = tabela_info.get(cod, ("N/A", []))
        texto = (
            f"📊 <b>Detalhes – {cod} créditos</b>\n\n"
            f"• Valor por unidade: <b>{preco_unit}€</b>\n\n"
            f"💡 Preços por plano:\n"
            f"- 1M PT: {planos[0]}€   | 1M Full: {planos[1]}€\n"
            f"- 3M PT: {planos[2]}€   | 3M Full: {planos[3]}€\n"
            f"- 6M PT: {planos[4]}€   | 6M Full: {planos[5]}€\n"
            f"- 12M PT: {planos[6]}€ | 12M Full: {planos[7]}€"
        )
        await callback_query.message.answer(texto, parse_mode="HTML")

    @dp.callback_query(lambda c: c.data.startswith("carregar_"))
    async def iniciar_carregamento(callback_query: types.CallbackQuery):
        valor = callback_query.data.split("_")[1]
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Sessão expirada. Faz login novamente.")
            return
        user["valor_total"] = valor
        user["data_hora"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        user["etapa"] = "comprovativo_carregamento"

        await callback_query.message.answer(
            f"<b>📌 Dados para pagamento:</b>\n"
            f"🏦 Entidade: {ENTIDADE}\n"
            f"🔢 Referência: {REFERENCIA}\n"
            f"💰 Valor: {valor}€\n\n"
            f"📎 Envia agora o comprovativo (imagem ou PDF).",
            parse_mode="HTML"
        )

    @dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "comprovativo_carregamento" and (msg.document or msg.photo))
    async def receber_comprovativo_carregamento(message: types.Message):
        user = user_data[message.from_user.id]
        nome = user.get("username", "sem_nome").replace(" ", "_")
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")

        if message.document:
            file_id = message.document.file_id
            nome_ficheiro = f"carregamento_{nome}_{agora}.{message.document.file_name.split('.')[-1]}"
        elif message.photo:
            file_id = message.photo[-1].file_id
            nome_ficheiro = f"carregamento_{nome}_{agora}.jpg"
        else:
            await message.answer("❌ Ficheiro inválido.")
            return

        file = await bot.get_file(file_id)
        temp_path = os.path.join(tempfile.gettempdir(), nome_ficheiro)
        await bot.download_file(file.file_path, destination=temp_path)

        try:
            media = MediaFileUpload(temp_path, resumable=True)
            uploaded = drive_service.files().create(
                media_body=media,
                body={"name": nome_ficheiro, "parents": [PASTA_COMPROVATIVOS_ID]},
                fields="id"
            ).execute()
            link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"
        except Exception as e:
            print(f"❌ Erro ao subir para o Drive: {e}")
            await message.answer("⚠️ Erro ao guardar o comprovativo. Tenta novamente.")
            return
        finally:
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"⚠️ Aviso: erro ao apagar ficheiro temporário: {e}")

        username = user.get("username")
        valor = user.get("valor_total")
        telegram_id = message.from_user.id

        atualizar_registro_revendedor(username, valor, link, telegram_id)
        registar_historico_carregamento(username, valor, link, telegram_id)

        nova_linha = [[
            datetime.now().strftime("%d/%m/%Y"),
            "Receita Rev",
            username,
            valor,
            "MB",
            f"Carregamento {valor}€"
        ]]
        sheet_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Contabilidade!A1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": nova_linha}
        ).execute()

        await enviar_notificacao("Carregamento", user, link)
        await message.answer(
            f"✅ Carregamento registado com sucesso!\n\n"
            f"📎 O comprovativo foi guardado e será processado em breve.\n"
            f"Aguarda confirmação automática no teu Telegram ou email."
        )

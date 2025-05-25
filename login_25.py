# login_25.py
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import os
import tempfile
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload
from config_25 import bot, user_data, sheet_service, SPREADSHEET_ID, SHEET_CLIENTES, drive_service, PASTA_COMPROVATIVOS_ID, mapa_colunas
from email_utils_25 import enviar_email
from notificacao_upload_25 import enviar_notificacao
from apoio_25 import mostrar_menu_apoio  # (garante que existe esta função no ficheiro)
load_dotenv()
ENTIDADE = os.getenv("ENTIDADE")
REFERENCIA = os.getenv("REFERENCIA")

def register_handlers_login(dp: Dispatcher):

    # IMPORTANTE: toda a lógica de login, renovacao e comprovativo
    # foi migrada integralmente aqui. Tudo foi encapsulado em "register_handlers_login"

    @dp.message(lambda msg: msg.text == "🔐 Log In")
    async def login_handler(message: types.Message):
        user_data[message.from_user.id] = {}
        await message.answer("Indica o teu <b>username</b> ou <b>email</b>:", parse_mode="HTML")

    @dp.message(lambda msg: msg.text == "👥 Rev")
    async def revendedor_handler(message: types.Message):
        user_data[message.from_user.id] = {"via_rev": True}
        await message.answer("Indica o teu <b>username</b> (Revendedor):", parse_mode="HTML")
    
    @dp.message(lambda msg: msg.text and not user_data.get(msg.from_user.id, {}).get("etapa") and msg.text not in ["➕ Adesão", "🔐 Log In", "👥 Rev", "/start", "Menu"])
    async def tratar_login(message: types.Message):
        user_input = message.text.strip().lower()
        via_rev = user_data.get(message.from_user.id, {}).get("via_rev")
        aba = "Revendedores" if via_rev else SHEET_CLIENTES

        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=aba).execute()
        valores = result.get("values", [])
        if not valores:
            await message.answer("⚠️ Base de dados vazia.")
            return

        headers = valores[0]
        rows = valores[1:]

        correspondencias = []
        row_index = None

        for i, row in enumerate(rows):
            dados = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            if via_rev:
                username = dados.get("Nome de utilizador", "").strip().lower()
                if user_input == username:
                    correspondencias = [dados]
                    row_index = i + 2
                    break
            else:
                username = dados.get("username", "").strip().lower()
                email = dados.get("email", "").strip().lower()
                if user_input == email:
                    correspondencias.append(dados)
                elif user_input == username:
                    correspondencias = [dados]
                    row_index = i + 2
                    break

        if not correspondencias:
            await message.answer("❌ Utilizador não encontrado.")
            return

        # Se for revendedor
        if via_rev:
            dados = correspondencias[0]
            user_data[message.from_user.id] = dados
            user_data[message.from_user.id]["telegram_id"] = str(message.from_user.id)
            user_data[message.from_user.id]["username"] = dados.get("Nome de utilizador", "")

            if "Telegram ID" in headers and row_index:
                col_idx = headers.index("Telegram ID")
                col_letra = chr(65 + col_idx)
                cell = f"{col_letra}{row_index}"
                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"Revendedores!{cell}",
                    valueInputOption="RAW",
                    body={"values": [[str(message.from_user.id)]]}
                ).execute()

            texto = (
                f"👥 <b>Revendedor</b>\n"
                f"👤 Nome: {dados.get('Nome de utilizador')}\n"
                f"📧 Email: {dados.get('email', 'sem email')}\n"
                f"🌐 DNS: {dados.get('DNS')}\n\n"
                f"🔻 Escolhe uma opção:"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 Carregar Saldo", callback_data="menu_carregamentos")]
            ])
            await message.answer(texto, reply_markup=kb, parse_mode="HTML")
            return

        # Se houver várias correspondências (pelo email)
        if len(correspondencias) > 1:
            user_data[message.from_user.id] = {"email_para_login": user_input}
            botoes = []
            for i, dados in enumerate(correspondencias):
                username = dados.get("username", "")
                ref = dados.get("ref_extra", "") or "sem referência"
                texto = f"{username} — {ref}"
                botoes.append([InlineKeyboardButton(text=texto, callback_data=f"escolher_username:{i}")])
            user_data[message.from_user.id]["opcoes_login"] = correspondencias  # Guardar todas as opções

            await message.answer(
                "📧 Foram encontrados vários acessos com este email. Escolhe qual desejas consultar:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=botoes)
            )
            return

        # Caso seja apenas uma correspondência (login normal cliente)
        dados = correspondencias[0]
        user_data[message.from_user.id] = dados
        user_data[message.from_user.id]["telegram_id"] = str(message.from_user.id)
        user_data[message.from_user.id]["username"] = dados.get("username", "")

        texto = (
            f"👤 Username: {dados.get('username')}\n"
            f"🔐 Password: {dados.get('password')}\n"
            f"📧 Email: {dados.get('email')}\n"
            f"📌 Referência extra: {dados.get('ref_extra')}\n"
            f"📦 Plano: {dados.get('plano')}\n"
            f"🔑 VPN: {dados.get('conta_vpn')}\n"
            f"🕓 Criada em: {dados.get('vpn_criada_em')}\n"
            f"📡 Estado da linha: {dados.get('estado_da_linha')}\n"
            f"📅 Expira em: {dados.get('expira_em')}\n"
            f"📆 Dias restantes: {dados.get('dias_para_terminar')}\n\n"
            f"🔻 Escolhe uma opção:"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧾 Renovar", callback_data="renovar")],
            [InlineKeyboardButton(text="🛠 Apoio Técnico", callback_data="apoio")]
        ])

        await message.answer(texto, reply_markup=kb)

    @dp.callback_query(lambda c: c.data.startswith("escolher_username:"))
    async def escolher_username_callback(callback_query: types.CallbackQuery):
        index = int(callback_query.data.split(":")[1])
        user_id = callback_query.from_user.id
        opcoes = user_data.get(user_id, {}).get("opcoes_login", [])

        if index >= len(opcoes):
            await callback_query.message.answer("❌ Opção inválida.")
            return

        # Carregar os dados da linha escolhida
        dados = opcoes[index]
        user_data[user_id] = dados
        user_data[user_id]["telegram_id"] = str(user_id)
        user_data[user_id]["username"] = dados.get("username", "")

        # Mostrar os dados tal como no login normal
        texto = (
            f"👤 Username: {dados.get('username')}\n"
            f"🔐 Password: {dados.get('password')}\n"
            f"📧 Email: {dados.get('email')}\n"
            f"📌 Referência extra: {dados.get('ref_extra')}\n"
            f"📦 Plano: {dados.get('plano')}\n"
            f"🔑 VPN: {dados.get('conta_vpn')}\n"
            f"🕓 Criada em: {dados.get('vpn_criada_em')}\n"
            f"📡 Estado da linha: {dados.get('estado_da_linha')}\n"
            f"📅 Expira em: {dados.get('expira_em')}\n"
            f"📆 Dias restantes: {dados.get('dias_para_terminar')}\n\n"
            f"🔻 Escolhe uma opção:"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧾 Renovar", callback_data="renovar")],
            [InlineKeyboardButton(text="🛠 Apoio Técnico", callback_data="apoio")]
        ])

        await callback_query.message.answer(texto, reply_markup=kb)

           
    @dp.callback_query(lambda c: c.data == "renovar")
    async def iniciar_renovacao(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Não foi possível obter os teus dados. Faz login novamente.")
            return

        user["etapa"] = "renovacao_plano"

        planos = [
            ("Plano PT 6 Meses - 28.10€", "plano_pt_6_r"),
            ("Plano PT 12 Meses - 51.25€", "plano_pt_12_r"),
            ("Plano Full 6 Meses - 33.10€", "plano_full_6_r"),
            ("Plano Full 12 Meses - 61.25€", "plano_full_12_r")
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texto, callback_data=code)] for texto, code in planos
        ])
        await callback_query.message.answer("📦 Escolhe o novo plano:", reply_markup=kb)

    @dp.callback_query(lambda c: c.data.startswith("plano_") and c.data.endswith("_r"))
    async def escolher_vpn_renovacao(callback_query: types.CallbackQuery):
        planos = {
            "plano_pt_6_r": ("Plano PT 6 Meses", 28.10),
            "plano_pt_12_r": ("Plano PT 12 Meses", 51.25),
            "plano_full_6_r": ("Plano Full 6 Meses", 33.10),
            "plano_full_12_r": ("Plano Full 12 Meses", 61.25)
        }
        plano_nome, plano_valor = planos.get(callback_query.data, (None, None))

        if not plano_nome:
            await callback_query.message.answer("❌ Plano inválido. Tenta novamente.")
            return

        user = user_data[callback_query.from_user.id]
        user["plano_novo"] = plano_nome
        user["plano_valor"] = plano_valor

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="VPN 6M - 6€", callback_data="vpn6_r")],
            [InlineKeyboardButton(text="VPN 12M - 10€", callback_data="vpn12_r")],
            [InlineKeyboardButton(text="Sem VPN", callback_data="vpn0_r")]
        ])
        await callback_query.message.answer("🔒 Desejas adicionar VPN?", reply_markup=kb)

    @dp.callback_query(lambda c: c.data in ["vpn6_r", "vpn12_r", "vpn0_r"])
    async def mostrar_total_renovacao(callback_query: types.CallbackQuery):
        vpn_opcoes = {
            "vpn6_r": ("VPN 6 Meses", 6.0),
            "vpn12_r": ("VPN 12 Meses", 10.0),
            "vpn0_r": ("Sem VPN", 0.0)
        }
        vpn_nome, vpn_valor = vpn_opcoes[callback_query.data]
        user = user_data[callback_query.from_user.id]
        total = round((user["plano_valor"] + vpn_valor) * 1.025, 2)

        user["vpn"] = vpn_nome
        user["vpn_valor"] = vpn_valor
        user["total"] = f"{total:.2f}€"

        resumo = (
            f"📦 Plano escolhido: {user['plano_novo']}\n"
            f"🔒 VPN: {vpn_nome}\n"
            f"💰 Total com taxa: {user['total']}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📌 Confirmar e gerar referência", callback_data="confirmar_renovacao")]
        ])
        await callback_query.message.answer(resumo, reply_markup=kb)

    @dp.callback_query(lambda c: c.data == "confirmar_renovacao")
    async def gerar_referencia_renovacao(callback_query: types.CallbackQuery):
        user = user_data[callback_query.from_user.id]
        user["data_hora"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        user["estado_do_pedido"] = "AGUARDA_COMPROVATIVO"
        user["conta_vpn"] = "platinum" if user.get("vpn_valor", 0) > 0 else ""
        user["etapa"] = "comprovativo_renovacao"

        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        idx_username = headers.index("username")
        for i, row in enumerate(rows, start=2):
            if len(row) > idx_username and row[idx_username].strip().lower() == user["username"].strip().lower():
                for campo in [
                    "estado_do_pedido",
                    "comprovativo",
                    "renovada_no_painel_e_tabela_de_clientes",
                    "telegram_id"
                ]:
                    col = mapa_colunas.get(campo)
                    if col:
                        sheet_service.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"{SHEET_CLIENTES}!{col}{i}",
                            valueInputOption="RAW",
                            body={"values": [[""]]}
                        ).execute()

                for campo, chave in {
                    "vpn": "vpn",
                    "conta_vpn": "conta_vpn",
                    "plano_novo": "plano_novo",
                    "total": "total",
                    "data_hora": "data/hora",
                    "estado_do_pedido": "estado_do_pedido",
                    "telegram_id": str(callback_query.from_user.id)
                }.items():
                    col = mapa_colunas[campo]
                    valor = user.get(chave, chave)
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{SHEET_CLIENTES}!{col}{i}",
                        valueInputOption="RAW",
                        body={"values": [[valor]]}
                    ).execute()
                break

        texto_pagamento = (
            f"<b>📌 Dados para pagamento:</b>\n"
            f"🏦 Entidade: <b>{ENTIDADE}</b>\n"
            f"🔢 Referência: <b>{REFERENCIA}</b>\n"
            f"💰 Valor: <b>{user['total']}</b>\n\n"
            f"⏳ <b>Tens até 10 minutos</b> para carregar o comprovativo.\n"
            f"Se não o enviares dentro deste tempo, terás de repetir o processo desde o início."
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Carregar comprovativo", callback_data="comprovativo_renovacao")]
        ])

        await callback_query.message.answer(texto_pagamento, reply_markup=kb, parse_mode="HTML")

    @dp.callback_query(lambda c: c.data == "comprovativo_renovacao")
    async def pedir_comprovativo_renovacao(callback_query: types.CallbackQuery):
        user_data[callback_query.from_user.id]["etapa"] = "comprovativo_renovacao"
        await callback_query.message.answer(
    "📎 Envia agora o comprovativo (imagem ou PDF).\n\n"
    "⏳ <b>Tens até 10 minutos</b> para o fazer. Se não o enviares dentro deste tempo, "
    "terás de repetir o processo desde o início.",
    parse_mode="HTML"
)

    @dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "comprovativo_renovacao" and (msg.document or msg.photo))
    async def receber_comprovativo_renovacao(message: types.Message):
        user = user_data[message.from_user.id]
        nome_ref = user.get("username", "renovacao").replace(" ", "_")
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")

        if message.document:
            file_id = message.document.file_id
            nome_ficheiro = f"comprovativo_{nome_ref}_{agora}.{message.document.file_name.split('.')[-1]}"
        elif message.photo:
            file_id = message.photo[-1].file_id
            nome_ficheiro = f"comprovativo_{nome_ref}_{agora}.jpg"
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
        except Exception as e:
            await message.answer("❌ Erro ao guardar o comprovativo. Tenta novamente.")
            print(f"❌ Erro ao subir ficheiro para o Drive: {e}")
            return

        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível apagar o ficheiro temporário: {e}")

        link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"

        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        idx_username = headers.index("username")

        for i, row in enumerate(rows, start=2):
            username_sheet = row[idx_username].strip().lower() if len(row) > idx_username else ""
            username_user = user["username"].strip().lower()

            if username_sheet == username_user:
                # Atualizar estado e comprovativo na sheet
                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{mapa_colunas['estado_do_pedido']}{i}",
                    valueInputOption="RAW",
                    body={"values": [["PAGO"]]}
                ).execute()

                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{mapa_colunas['comprovativo']}{i}",
                    valueInputOption="RAW",
                    body={"values": [[link]]}
                ).execute()

                # Atualizar a data/hora (coluna M)
                idx_data_hora = headers.index("data_hora")
                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{chr(65+idx_data_hora)}{i}",
                    valueInputOption="RAW",
                    body={"values": [[user["data_hora"]]]}
                ).execute()


                # Tentar enviar notificação ao grupo
                print("telegram_id:", user.get("telegram_id"))

                try:
                    await enviar_notificacao("Renovacao", user, link)
                except Exception as e:
                    print(f"❌ Erro ao enviar notificação de renovação: {e}")

                # Mensagem final ao cliente
                await message.answer(
                    f"✅ Comprovativo recebido com sucesso!\n\n"
                    f"A tua renovação será processada em breve.\n"
                    f"Irás receber email com os dados atualizados."
                )

                print("✅ Mensagem final de renovação enviada ao cliente.")
                break
        else:
            print("⚠️ Nenhuma linha coincidente com o username foi encontrada na Sheet.")

        corpo = f"""
Olá {user.get('ref_extra')},

Recebemos o teu comprovativo de pagamento com sucesso.

Resumo da renovação:
• Username: {user.get('username')}
• Email: {user.get('email')}
• Plano: {user.get('plano_novo')}
• VPN: {user.get('vpn')}
• Total pago: {user.get('total')}
• Data/Hora: {datetime.now().strftime('%d-%m-%Y %H:%M')}

A tua linha será atualizada em breve.

---

Para renovar no futuro:
1. Inicia o bot: https://t.me/fourus_help_bot
2. Clica em "Log In"
3. Introduz o teu username
4. Seleciona "Renovar"
5. Escolhe plano e VPN
6. Efetua o pagamento e envia o comprovativo

Com os melhores cumprimentos,
A equipa 4US
"""


        enviar_email(
            destinatario="notificacoes.4us@gmail.com",
            assunto="[BOT] Renovação – Comprovativo Recebido (MODELO ENVIADO)",
            corpo=corpo,
            username=user.get("username"),
            motivo="Renovação – comprovativo"
        )

    @dp.callback_query(lambda c: c.data == "apoio_instalacao")
    async def apoio_instalacao_callback(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Sessão expirada. Volta ao início com /start.")
            return

        await mostrar_menu_apoio(callback_query.message, user)

    @dp.callback_query(lambda c: c.data == "outros_assuntos")
    async def outros_assuntos_callback(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📩 Para outros assuntos ou ajuda personalizada, contacta:\n\n"
            "📧 <b>luis.phoenix@tutanota.com</b>\n"
            "📨 Ou envia mensagem direta no Telegram: @hhcihs",
            parse_mode="HTML"
        )

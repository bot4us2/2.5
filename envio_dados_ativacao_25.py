import asyncio
import os
import requests
import json
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email_utils_25 import enviar_email  # ✅ Importa a nova versão modularizada

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_CLIENTES")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
BOT_TOKEN = os.getenv("API_TOKEN")

# --- Função auxiliar para obter índice de coluna ---
def idx(headers, col):
    return headers.index(col)

# --- Envio de mensagem via Telegram ---
def enviar_telegram(chat_id, texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"📨 Mensagem enviada para {chat_id}")
        else:
            print(f"❌ Erro Telegram ({response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem Telegram: {e}")
        return False

# --- Loop principal de monitorização ---
async def monitor_ativacoes():
    print("🚀 Monitor de ativações iniciado (loop a cada 30 segundos)...")

    json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if json_credentials:
        creds_dict = json.loads(json_credentials)
        creds = Credentials.from_service_account_info(creds_dict)
    else:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

    sheet = build('sheets', 'v4', credentials=creds)

    while True:
        try:
            result = sheet.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
            valores = result.get('values', [])
            headers = valores[0]
            rows = valores[1:]

            for row_idx, row in enumerate(rows, start=2):
                if len(row) <= idx(headers, "renovada_no_painel_e_tabela_de_clientes"):
                    continue

                status = row[idx(headers, "renovada_no_painel_e_tabela_de_clientes")].strip().upper()
                if status != "SIM":
                    continue

                try:
                    chat_id = row[idx(headers, "telegram_id")]
                    if not chat_id.strip():
                        continue
                except:
                    continue

                username = row[idx(headers, "username")]
                password = row[idx(headers, "password")]
                email = row[idx(headers, "email")]
                ref_extra = row[idx(headers, "ref_extra")]
                plano = row[idx(headers, "plano_novo")]
                vpn = row[idx(headers, "vpn")]
                conta_vpn = row[idx(headers, "conta_vpn")]
                expira_em = row[idx(headers, "expira_em")]
                dias_para_terminar = row[idx(headers, "dias_para_terminar")]

                corpo = f"""
Olá {ref_extra},

A tua linha foi ativada com sucesso.

Aqui estão os teus dados de acesso:
• Username: {username}
• Password: {password}
• Plano: {plano}
• VPN: {vpn}
• Expira em: {expira_em}

Para instalar, podes seguir os tutoriais disponíveis ou contactar o nosso assistente:
https://t.me/fourus_help_bot

Com os melhores cumprimentos,  
A equipa 4US
"""
                enviar_email(
                    destinatario=email,
                    assunto="✅ Serviço Ativado – Dados de Acesso",
                    corpo=corpo,
                    username=username,
                    motivo="Ativação Manual (coluna P)"
                )

                telegram_msg = (
                    f"✅ <b>Serviço Ativado</b>\n\n"
                    f"<b>👤 Username:</b> {username}\n"
                    f"<b>🔐 Password:</b> {password}\n"
                    f"<b>📧 Email:</b> {email}\n"
                    f"<b>📌 Referência:</b> {ref_extra}\n"
                    f"<b>📦 Plano:</b> {plano}\n"
                    f"<b>🔒 VPN:</b> {vpn}\n"
                    f"<b>🔑 Conta VPN:</b> {conta_vpn}\n"
                    f"<b>🗓 Expira em:</b> {expira_em}\n"
                    f"<b>📆 Dias restantes:</b> {dias_para_terminar}"
                )
                enviar_telegram(chat_id, telegram_msg)

                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!P{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Dados Enviados"]]}
                ).execute()

                # --- Registo na aba Contabilidade (adesão ou renovação) ---
                try:
                    mes_atual = datetime.now().strftime("%B")
                    try:
                        plano_original = row[idx(headers, "plano")].strip().lower()
                    except:
                        plano_original = ""

                    tipo_operacao = "adesão confirmada" if plano_original == "" else "renovação confirmada"
                    receita = float(row[idx(headers, "total")].replace("€", "").replace(",", ".").strip())

                    nova_linha = [[
                        mes_atual, "receita_total", "Receita", f"{receita:.2f}", tipo_operacao
                    ]]

                    sheet.spreadsheets().values().append(
                        spreadsheetId=SPREADSHEET_ID,
                        range="Contabilidade!A1",
                        valueInputOption="RAW",
                        insertDataOption="INSERT_ROWS",
                        body={"values": nova_linha}
                    ).execute()

                    print(f"💰 Receita registada na Contabilidade: {receita:.2f}€ – {tipo_operacao}")
                except Exception as e:
                    print(f"❌ Erro ao registar receita na Contabilidade: {e}")

                print(f"✅ Linha {row_idx} atualizada com 'Dados Enviados'")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Erro geral: {e}")

        await asyncio.sleep(30)
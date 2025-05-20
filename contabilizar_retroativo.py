import os
import json
from datetime import datetime
from collections import defaultdict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- Carregar variáveis de ambiente ---
load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
SHEET_NAME = "Tabela de Clientes 2"

# --- Autenticação Google Sheets ---
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build("sheets", "v4", credentials=creds)

# --- Obter dados da sheet ---
result = sheet.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=SHEET_NAME
).execute()
valores = result.get("values", [])

headers = valores[0]
rows = valores[1:]

# --- Mapear colunas ---
def idx(nome):
    return headers.index(nome)

# --- Dicionário: { "Maio": soma_total } ---
somas_por_mes = defaultdict(float)

for row in rows:
    row += [""] * len(headers)

    try:
        status = row[idx("renovada_no_painel_e_tabela_de_clientes")].strip().upper()
        estado = row[idx("estado_do_pedido")].strip().upper()
        total_str = row[idx("total")].replace("€", "").replace(",", ".").strip()
        data_hora_str = row[idx("data_hora")].strip()

        if status != "DADOS ENVIADOS" or estado != "PAGO" or not total_str:
            continue

        total = float(total_str)
        data_dt = datetime.strptime(data_hora_str, "%d-%m-%Y %H:%M")
        nome_mes = data_dt.strftime("%B")

        somas_por_mes[nome_mes] += total

    except Exception as e:
        print(f"⚠️ Erro na linha: {e}")
        continue

# --- Escrever na aba Contabilidade ---
valores_a_registar = []

for mes, total in somas_por_mes.items():
    valores_a_registar.append([
        mes, "receita_total", "Receita", f"{total:.2f}", "registo retroativo"
    ])

if valores_a_registar:
    sheet.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Contabilidade!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": valores_a_registar}
    ).execute()

    print("✅ Registos retroativos adicionados à Contabilidade:")
    for linha in valores_a_registar:
        print("   •", linha)
else:
    print("ℹ️ Nenhum registo retroativo encontrado para contabilizar.")
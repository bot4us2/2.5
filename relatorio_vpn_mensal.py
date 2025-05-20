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

# --- Preços de venda e custo ---
precos_venda = {
    "VPN 6 Meses": 6.00,
    "VPN 12 Meses": 10.00
}

custos_vpn = {
    "VPN 6 Meses": 2.5,
    "VPN 12 Meses": 5.0
}

# --- Agregador: {(mes, conta_vpn, tipo): [qtd, total_venda, total_custo]} ---
relatorio = defaultdict(lambda: [0, 0.0, 0.0])

for row in rows:
    row += [""] * len(headers)
    try:
        estado = row[idx("estado_do_pedido")].strip().upper()
        status = row[idx("renovada_no_painel_e_tabela_de_clientes")].strip().upper()
        data_str = row[idx("data_hora")].strip()

        if estado != "PAGO" or status != "DADOS ENVIADOS" or not data_str:
            continue

        data = datetime.strptime(data_str, "%d-%m-%Y %H:%M")
        mes = data.strftime("%B")
        conta_vpn = row[idx("conta_vpn")].strip() or "(vazio)"
        tipo_vpn = row[idx("vpn")].strip() or "Sem VPN"

        preco = precos_venda.get(tipo_vpn, 0.0)
        custo = custos_vpn.get(tipo_vpn, 0.0)

        chave = (mes, conta_vpn, tipo_vpn)
        relatorio[chave][0] += 1
        relatorio[chave][1] += preco
        relatorio[chave][2] += custo

    except Exception as e:
        print(f"⚠️ Erro ao processar linha: {e}")
        continue

# --- Imprimir resultado ---
print("\n📊 RELATÓRIO MENSAL DE VPNs\n")
print(f"{'Mês':<10} {'VPN':<20} {'Tipo':<15} {'Qtd':<5} {'Total €':<10} {'Custo €':<10} {'Lucro €'}")
print("-" * 80)

valores_para_sheet = [["Mês", "VPN", "Tipo", "Quantidade", "Total €", "Custo €", "Lucro €"]]

for (mes, conta_vpn, tipo_vpn), (qtd, total, custo) in sorted(relatorio.items()):
    lucro = total - custo
    print(f"{mes:<10} {conta_vpn:<20} {tipo_vpn:<15} {qtd:<5} {total:<10.2f} {custo:<10.2f} {lucro:.2f}")
    valores_para_sheet.append([mes, conta_vpn, tipo_vpn, qtd, round(total, 2), round(custo, 2), round(lucro, 2)])

# --- Guardar na Google Sheet (nova aba "Resumo VPN Mensal") ---
try:
    sheet.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Resumo VPN Mensal!A1",
        valueInputOption="RAW",
        body={"values": valores_para_sheet}
    ).execute()
    print("\n✅ Dados gravados na aba 'Resumo VPN Mensal'.")
except Exception as e:
    print(f"❌ Erro ao gravar na sheet: {e}")

print("\n✅ Fim do relatório.")

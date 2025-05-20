import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from email_utils_25 import enviar_email

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "Registo Diário"
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais_bot.json")
DESTINATARIO_RELATORIO = "luis.phoenix@tutanota.com"

# --- Autenticação Google Sheets ---
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

# --- Função para gerar relatório baseado em Registo Diário ---
def gerar_relatorio(periodo_nome: str, data_inicio: datetime, data_fim: datetime):
    result = sheet.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME
    ).execute()
    valores = result.get("values", [])
    if not valores:
        return "❌ Não foi possível obter dados da sheet."

    headers = valores[0]
    rows = valores[1:]
    idx = lambda nome: headers.index(nome)

    adesoes, renovacoes, expirados = [], [], []
    soma_total = 0.0

    for row in rows:
        row += [""] * (len(headers) - len(row))  # completar linhas curtas
        try:
            data_reg = datetime.strptime(row[idx("Data")], "%d/%m/%Y")
        except:
            continue

        if not (data_inicio.date() <= data_reg.date() <= data_fim.date()):
            continue

        tipo = row[idx("Tipo")].strip().lower()
        username = row[idx("Username")]
        email = row[idx("Email")]
        plano = row[idx("Plano")]
        total_str = row[idx("Total (€)")]
        origem = row[idx("Fonte")]

        linha_info = f"• {username} / {email} / {plano} [{origem}]"

        try:
            total = float(total_str.replace(",", "."))
        except:
            total = 0.0

        if tipo == "adesão":
            adesoes.append(linha_info)
            soma_total += total
        elif tipo == "renovação":
            renovacoes.append(linha_info)
            soma_total += total
        elif tipo == "expirado":
            expirados.append(f"• {username} / {email} [{origem}]")

    texto = f"RELATÓRIO {periodo_nome.upper()} – 4US\n\n"
    texto += f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\n"
    texto += "➕ Adesões:\n" + ("\n".join(adesoes) if adesoes else "Nenhuma adesão") + f"\n\nTotal: {len(adesoes)}\n\n"
    texto += "🔄 Renovações:\n" + ("\n".join(renovacoes) if renovacoes else "Nenhuma renovação") + f"\n\nTotal: {len(renovacoes)}\n\n"
    texto += "🔝 Expirados:\n" + ("\n".join(expirados) if expirados else "Nenhum serviço expirado") + f"\n\nTotal: {len(expirados)}\n\n"
    texto += f"💰 Total acumulado: {soma_total:.2f} €\n"

    return texto

# --- Relatórios semanais e mensais ---
def enviar_relatorio():
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)

    relatorio_semanal = gerar_relatorio("Semanal", inicio_semana, hoje)
    relatorio_mensal = gerar_relatorio("Mensal", inicio_mes, hoje)

    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Semanal – {hoje.strftime('%d/%m/%Y')} (automático)",
        corpo=relatorio_semanal,
        username="Relatório",
        motivo="Relatório semanal automático"
    )

    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Mensal – {hoje.strftime('%d/%m/%Y')} (automático)",
        corpo=relatorio_mensal,
        username="Relatório",
        motivo="Relatório mensal automático"
    )

# --- Função para gerar relatório VPN de meses fechados ---
def gerar_relatorio_vpn_fechado():
    SHEET_CLIENTES = "Tabela de Clientes 2"
    result = sheet.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_CLIENTES
    ).execute()
    valores = result.get("values", [])

    headers = valores[0]
    rows = valores[1:]
    def idx(nome): return headers.index(nome)

    precos_venda = {"VPN 6 Meses": 6.00, "VPN 12 Meses": 10.00}
    custos_vpn = {"VPN 6 Meses": 2.5, "VPN 12 Meses": 5.0}
    relatorio = defaultdict(lambda: [0, 0.0, 0.0])
    hoje = datetime.today()

    for row in rows:
        row += [""] * len(headers)
        try:
            estado = row[idx("estado_do_pedido")].strip().upper()
            status = row[idx("renovada_no_painel_e_tabela_de_clientes")].strip().upper()
            data_str = row[idx("data_hora")].strip()
            if estado != "PAGO" or status != "DADOS ENVIADOS" or not data_str:
                continue
            data = datetime.strptime(data_str, "%d-%m-%Y %H:%M")
            if data.year == hoje.year and data.month >= hoje.month:
                continue
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

    valores_para_sheet = [["Mês", "VPN", "Tipo", "Quantidade", "Total €", "Custo €", "Lucro €"]]
    for (mes, conta_vpn, tipo_vpn), (qtd, total, custo) in sorted(relatorio.items()):
        lucro = total - custo
        valores_para_sheet.append([mes, conta_vpn, tipo_vpn, qtd, round(total, 2), round(custo, 2), round(lucro, 2)])

    try:
        sheet.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="Resumo VPN Mensal!A1",
            valueInputOption="RAW",
            body={"values": valores_para_sheet}
        ).execute()
        print("\n✅ Relatório de VPNs atualizado na aba 'Resumo VPN Mensal'.")
    except Exception as e:
        print(f"❌ Erro ao gravar na aba 'Resumo VPN Mensal': {e}")

# --- Execução manual ---
if __name__ == "__main__":
    enviar_relatorio()
    gerar_relatorio_vpn_fechado()
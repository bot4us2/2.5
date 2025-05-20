# botp_25.py
import asyncio
import logging
import platform
import sys
from aiogram import types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from config_25 import bot, dp
from login_25 import register_handlers_login
from adesao_25 import register_handlers_adesao
from carregamentos_25 import register_handlers_carregamentos
from apoio_25 import register_handlers_apoio
from registo_diario_25 import registar_eventos_diarios
from envio_dados_ativacao_25 import monitor_ativacoes
from notificacao_renovacao_estado_teste_25 import verificar_notificacoes_renovacao
from monitor_revendedores_25 import monitor_resposta_revendedores


# --- Comando /start ---
@dp.message(lambda message: message.text == "/start")
async def menu_handler(message: types.Message):
    teclado_fixo = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Log In"), KeyboardButton(text="➕ Adesão")],
            [KeyboardButton(text="👥 Rev")]
        ],
        resize_keyboard=True
    )
    await message.answer("Olá! Bem-vindo ao BOT 4US 🙌\nEscolhe uma opção abaixo:", reply_markup=teclado_fixo)

# --- Comando /id para detetar chat_id ---
@dp.message(lambda message: message.text == "/id")
async def enviar_chat_id(message: types.Message):
    await message.answer(f"O chat_id deste grupo é: <code>{message.chat.id}</code>", parse_mode="HTML")
    print(f"📣 chat_id detectado: {message.chat.id}")

# --- Comando /menu (definições do bot) ---
async def configurar_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Iniciar o bot"),
        BotCommand(command="login", description="🔐 Log In"),
        BotCommand(command="adesao", description="➕ Adesão")
    ])

# --- Loop de notificações ---
async def loop_notificacoes():
    while True:
        print("🔁 A correr verificação de notificações de renovação...\n")
        try:
            stats = await verificar_notificacoes_renovacao()
            if stats:
                print("📊 RESUMO DA VERIFICAÇÃO DE RENOVAÇÕES:")
                for chave, valor in stats.items():
                    print(f"• {chave}: {valor}")
                print("✅ Verificação concluída.\n")
        except Exception as e:
            print(f"❌ Erro ao verificar notificações: {e}")
        await asyncio.sleep(3600)

# --- Loop de registo diário ---

async def loop_registo_diario():
    while True:
        print("🗓 A registar eventos no Registo Diário...")
        try:
            registar_eventos_diarios()
        except Exception as e:
            print(f"❌ Erro no registo diário: {e}")
        await asyncio.sleep(3600)  # corre de hora a hora


# --- Main ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await configurar_menu()

    register_handlers_login(dp)
    register_handlers_adesao(dp)
    register_handlers_carregamentos(dp)
    register_handlers_apoio(dp)

    print("✅ BOT 4US INICIADO")
    print("📡 A iniciar polling...")

    await asyncio.gather(
    dp.start_polling(bot),
    monitor_ativacoes(),
    loop_notificacoes(),
    monitor_resposta_revendedores(),
    loop_registo_diario(),
    loop_relatorio_vpn()  # ✅ Novo loop que gera relatório de VPNs 1x por semana
)
async def loop_relatorio_vpn():
    while True:
        try:
            from relatorio_4u_25 import gerar_relatorio_vpn_fechado
            gerar_relatorio_vpn_fechado()
        except Exception as e:
            print(f"❌ Erro no relatório de VPN: {e}")
        await asyncio.sleep(604800)  # aguarda 7 dias

# --- Execução ---
if __name__ == "__main__":
    try:
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
        sys.exit(1)



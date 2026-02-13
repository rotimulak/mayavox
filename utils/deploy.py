#!/usr/bin/env python3
"""
Скрипт автоматического деплоя Telegram бота на VPS.
"""

import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv

# Настройка UTF-8 для Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Загрузка переменных окружения
load_dotenv()

VPS_IP = os.getenv('VPS_IP')
VPS_PASSWORD = os.getenv('VPS_PASSWORD')
REMOTE_DIR = "/opt/masterskaya-bot"

def run_command(cmd):
    """Выполнить команду с выводом"""
    print(f"  $ {cmd}")
    result = os.system(cmd)
    if result != 0:
        print(f"  ❌ Ошибка при выполнении команды")
        return False
    return True

def main():
    print("=" * 80)
    print("🚀 Деплой Telegram бота на VPS")
    print("=" * 80)
    print()
    print(f"VPS IP: {VPS_IP}")
    print()

    if not VPS_IP or not VPS_PASSWORD:
        print("❌ Ошибка: VPS_IP или VPS_PASSWORD не найдены в .env")
        sys.exit(1)

    # Проверка наличия sshpass
    if os.system("which sshpass > /dev/null 2>&1") != 0:
        print("⚠️  Утилита sshpass не найдена")
        print("   Установите: brew install sshpass (Mac) или apt-get install sshpass (Linux)")
        print()
        print("📝 Альтернатива: используйте SSH ключи вместо пароля")
        print("   1. Скопируйте ваш публичный ключ на сервер:")
        print(f"      ssh-copy-id root@{VPS_IP}")
        print("   2. Запустите скрипт снова")
        print()
        use_password = False
    else:
        use_password = True

    ssh_cmd = f"sshpass -p '{VPS_PASSWORD}' ssh -o StrictHostKeyChecking=no root@{VPS_IP}"
    scp_cmd = f"sshpass -p '{VPS_PASSWORD}' scp -o StrictHostKeyChecking=no -r"

    if not use_password:
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no root@{VPS_IP}"
        scp_cmd = f"scp -o StrictHostKeyChecking=no -r"

    print("[1/6] Создание директории на сервере...")
    if not run_command(f"{ssh_cmd} 'mkdir -p {REMOTE_DIR}'"):
        sys.exit(1)

    print("\n[2/6] Копирование файлов на сервер...")
    if not run_command(f"{scp_cmd} app result .env root@{VPS_IP}:{REMOTE_DIR}/"):
        sys.exit(1)

    print("\n[3/6] Установка зависимостей на сервере...")
    install_cmd = f"""
cd {REMOTE_DIR} && \
apt-get update -qq && \
apt-get install -y python3 python3-pip && \
pip3 install -q python-telegram-bot requests python-dotenv
"""
    if not run_command(f"{ssh_cmd} '{install_cmd}'"):
        sys.exit(1)

    print("\n[4/6] Создание systemd сервиса...")
    service_content = f"""[Unit]
Description=Masterskaya Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_DIR}/app
ExecStart=/usr/bin/python3 {REMOTE_DIR}/app/telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

    # Создание временного файла с сервисом
    import tempfile
    temp_service = os.path.join(tempfile.gettempdir(), 'masterskaya-bot.service')
    with open(temp_service, 'w') as f:
        f.write(service_content)

    if not run_command(f"{scp_cmd} {temp_service} root@{VPS_IP}:/etc/systemd/system/"):
        sys.exit(1)

    if not run_command(f"{ssh_cmd} 'systemctl daemon-reload'"):
        sys.exit(1)

    print("\n[5/6] Запуск бота...")
    run_command(f"{ssh_cmd} 'systemctl stop masterskaya-bot 2>/dev/null || true'")

    if not run_command(f"{ssh_cmd} 'systemctl start masterskaya-bot'"):
        sys.exit(1)

    if not run_command(f"{ssh_cmd} 'systemctl enable masterskaya-bot'"):
        sys.exit(1)

    print("\n[6/6] Проверка статуса...")
    import time
    time.sleep(2)
    run_command(f"{ssh_cmd} 'systemctl status masterskaya-bot --no-pager'")

    print()
    print("=" * 80)
    print("✅ Деплой завершен успешно!")
    print("=" * 80)
    print()
    print("Полезные команды для управления ботом:")
    print()
    print(f"  Логи:        ssh root@{VPS_IP} 'journalctl -u masterskaya-bot -f'")
    print(f"  Статус:      ssh root@{VPS_IP} 'systemctl status masterskaya-bot'")
    print(f"  Остановить:  ssh root@{VPS_IP} 'systemctl stop masterskaya-bot'")
    print(f"  Запустить:   ssh root@{VPS_IP} 'systemctl start masterskaya-bot'")
    print(f"  Рестарт:     ssh root@{VPS_IP} 'systemctl restart masterskaya-bot'")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ Деплой прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)

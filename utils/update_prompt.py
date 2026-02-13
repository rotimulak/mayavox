#!/usr/bin/env python3
"""
Скрипт для обновления system_prompt.txt на VPS сервере.
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

def main():
    print("🔄 Обновление system_prompt.txt на сервере...")
    print()

    if not VPS_IP or not VPS_PASSWORD:
        print("❌ Ошибка: VPS_IP или VPS_PASSWORD не найдены в .env")
        sys.exit(1)

    try:
        import paramiko
    except ImportError:
        print("❌ Ошибка: Необходимо установить библиотеку paramiko")
        print("   Установите её командой: pip install paramiko")
        sys.exit(1)

    local_file = Path("app/config/system_prompt.txt")
    if not local_file.exists():
        print(f"❌ Файл не найден: {local_file}")
        sys.exit(1)

    print(f"📤 Подключение к {VPS_IP}...")

    # Создание SSH клиента
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключение
        ssh.connect(
            hostname=VPS_IP,
            username='root',
            password=VPS_PASSWORD,
            timeout=10
        )

        # Копирование файла через SFTP
        sftp = ssh.open_sftp()
        remote_path = f"{REMOTE_DIR}/app/config/system_prompt.txt"

        print(f"📁 Копирование {local_file} -> {remote_path}...")
        sftp.put(str(local_file), remote_path)
        sftp.close()
        print("✅ Файл скопирован")

        # Перезапуск бота
        print()
        print("🔄 Перезапуск бота...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart masterskaya-bot')
        stdout.channel.recv_exit_status()  # Ждем завершения команды

        # Проверка статуса
        print("📊 Проверка статуса...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status masterskaya-bot --no-pager')
        status_output = stdout.read().decode('utf-8')

        if 'active (running)' in status_output:
            print("✅ Бот успешно перезапущен и работает")
        else:
            print("⚠️  Бот перезапущен, но статус неясен:")
            print(status_output)

        print()
        print("=" * 60)
        print("✅ System prompt обновлен на сервере!")
        print("=" * 60)

    except paramiko.AuthenticationException:
        print("❌ Ошибка аутентификации. Проверьте пароль в .env")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"❌ SSH ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ Прервано пользователем")
        sys.exit(1)

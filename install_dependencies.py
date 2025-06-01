import subprocess
import sys
import os
import venv

VENV_DIR = "venv"

def create_virtualenv():
    if not os.path.exists(VENV_DIR):
        print("🔧 Створюю віртуальне середовище...")
        venv.create(VENV_DIR, with_pip=True)
        print("Віртуальне середовище створено.")
    else:
        print("Віртуальне середовище вже існує.")

def install_requirements():
    req_file = 'requirements.txt'
    if not os.path.exists(req_file):
        print("Файл requirements.txt не знайдено.")
        return

    # Використовуємо pip із середовища
    pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "pip")

    print("Встановлюю залежності з requirements.txt...")
    try:
        subprocess.check_call([pip_path, "install", "-r", req_file])
        print("Усі залежності успішно встановлено.")
    except subprocess.CalledProcessError as e:
        print("Помилка при встановленні залежностей:", e)

if __name__ == "__main__":
    create_virtualenv()
    install_requirements()

    print("\nЩоб активувати середовище, введи:")
    if os.name == "nt":
        print(r"venv\Scripts\activate")
    else:
        print("source venv/bin/activate")

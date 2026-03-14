#!/usr/bin/env python3
"""Secure Installation for OpenClaw Guardrails.
- Creates virtual environment (venv)
- Installs dependencies safely
- Configures initial baseline
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / "venv"
REQUIREMENTS = ROOT / "requirements.txt"

def create_venv():
    if not VENV_DIR.exists():
        print(f"创建虚拟环境: {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
    else:
        print("虚拟环境已存在。")

def install_deps():
    pip_exe = VENV_DIR / "bin" / "pip" if os.name != "nt" else VENV_DIR / "Scripts" / "pip.exe"
    if not REQUIREMENTS.exists():
        # Create default requirements if missing
        REQUIREMENTS.write_text("pyyaml\nrequests\n", encoding="utf-8")
    
    print("安装依赖项...")
    subprocess.run([str(pip_exe), "install", "-r", str(REQUIREMENTS)], check=True)

def setup_baseline():
    print("初始化安全基线...")
    # Trigger a baseline pin
    python_exe = VENV_DIR / "bin" / "python" if os.name != "nt" else VENV_DIR / "Scripts" / "python.exe"
    subprocess.run([str(python_exe), str(ROOT / "scripts" / "hash_pin.py")])

def main():
    try:
        create_venv()
        install_deps()
        setup_baseline()
        print("\n✅ OpenClaw Guardrails 安装成功！")
        print(f"请使用以下命令启动每日扫描：")
        print(f"source {VENV_DIR}/bin/activate && python3 {ROOT}/scripts/run_daily.py")
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

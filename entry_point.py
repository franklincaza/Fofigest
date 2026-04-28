"""
Fofigest Desktop — Punto de entrada para el ejecutable empaquetado con PyInstaller.
Inicia Waitress en un hilo daemon y abre la UI en una ventana PyWebView nativa.
"""
import sys
import os
import socket
import threading
import time


# ── 1. Resolver rutas base ────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _MEIPASS = sys._MEIPASS
    _EXE_DIR = os.path.dirname(sys.executable)
else:
    _MEIPASS = os.path.dirname(os.path.abspath(__file__))
    _EXE_DIR = _MEIPASS

if _MEIPASS not in sys.path:
    sys.path.insert(0, _MEIPASS)

# ── 2. Configurar entorno ANTES de importar Flask ────────────────────────────
DATA_DIR = os.path.join(_EXE_DIR, 'Fofigest_data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH  = os.path.join(DATA_DIR, 'Empresas.db').replace('\\', '/')
LOG_PATH = os.path.join(DATA_DIR, 'fofigest.log')

# Leer modo de BD desde Fofigest_data/db.mode
# Contenido "offline" → SQLite local
# Cualquier otro valor o archivo inexistente → Supabase PostgreSQL (por defecto)
_DB_MODE_FILE = os.path.join(DATA_DIR, 'db.mode')
_db_mode = 'online'
if os.path.exists(_DB_MODE_FILE):
    try:
        _db_mode = open(_DB_MODE_FILE, encoding='utf-8').read().strip().lower()
    except Exception:
        pass

if _db_mode == 'offline':
    os.environ['FOFIGEST_DB_URI'] = f'sqlite:///{DB_PATH}'
# Si es "online" (o cualquier otro valor) no se define FOFIGEST_DB_URI
# → app.py usará Supabase PostgreSQL

os.environ['FOFIGEST_DESKTOP'] = '1'
os.environ['FOFIGEST_LOG_PATH'] = LOG_PATH
os.environ['FOFIGEST_DB_MODE']  = _db_mode  # disponible para app.py

os.chdir(_EXE_DIR)

import config as _cfg
# offline → debug=True (usa SQLite local via FOFIGEST_DB_URI)
# online  → debug=False (app.py cae en la rama Supabase PostgreSQL)
_cfg.config['debug'] = (_db_mode == 'offline')

# ── 3. Deshabilitar flask_monitoringdashboard (requiere scipy, innecesario en desktop)
from unittest.mock import MagicMock
_dashboard_mock = MagicMock()
_dashboard_mock.bind = lambda app: None
sys.modules['flask_monitoringdashboard'] = _dashboard_mock

# ── 4. Importar la aplicación Flask ──────────────────────────────────────────
from app import app  # noqa: E402


# ── 5. Descubrir puerto libre ─────────────────────────────────────────────────
def _find_free_port(start: int = 5000, end: int = 5100) -> int:
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError('No se encontró ningún puerto libre en el rango 5000-5100')


# ── 7. Hilo del servidor Waitress ─────────────────────────────────────────────
def _run_server(port: int) -> None:
    try:
        from waitress import serve
        serve(app, host='127.0.0.1', port=port, threads=4, _quiet=True)
    except Exception as exc:
        import logging
        logging.critical(f'Waitress falló en el puerto {port}: {exc}')


def _wait_for_server(port: int, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                return True
        time.sleep(0.1)
    return False


# ── 8. Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    port = _find_free_port()
    url  = f'http://127.0.0.1:{port}'

    server_thread = threading.Thread(
        target=_run_server,
        args=(port,),
        daemon=True,
        name='fofigest-waitress',
    )
    server_thread.start()

    if not _wait_for_server(port, timeout=30.0):
        _show_error('Fofigest no pudo iniciar el servidor interno.\n'
                    f'Revisa el log en: {LOG_PATH}')
        sys.exit(1)

    try:
        import webview
        _icon_path = os.path.join(_MEIPASS, 'static', 'img', 'logo_F-Photoroom.ico')
        webview.create_window(
            title='Fofigest',
            url=url,
            width=1366,
            height=768,
            min_size=(800, 600),
            resizable=True,
        )
        webview.start(debug=False, icon=_icon_path)
    except Exception as exc:
        _show_error(f'No se pudo abrir la ventana de Fofigest:\n{exc}\n\n'
                    f'Abre manualmente en tu navegador: {url}')


def _show_error(msg: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('Fofigest — Error', msg)
        root.destroy()
    except Exception:
        print(f'[ERROR] {msg}', file=sys.stderr)


if __name__ == '__main__':
    main()

# build.spec — PyInstaller spec para Fofigest Desktop
# Genera un único ejecutable Windows sin consola visible.
# Uso: pyinstaller build.spec --noconfirm

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Archivos de datos a empaquetar ───────────────────────────────────────────
# Formato: (origen_en_disco, destino_dentro_del_exe)
datas = [
    ('templates',      'templates'),
    ('static',         'static'),
    ('models',         'models'),
    ('feature',        'feature'),
    ('services',       'services'),
    ('forms.py',       '.'),
    ('config.py',      '.'),
    ('masivos.py',     '.'),
]

# flask_monitoringdashboard excluido: requiere scipy y no es necesario en desktop

# Flask-CKEditor: incluye los estáticos del editor
try:
    datas += collect_data_files('flask_ckeditor')
except Exception:
    pass

# Plotly: incluye los schemas y templates de gráficas
try:
    datas += collect_data_files('plotly')
except Exception:
    pass

# PyWebView: archivos auxiliares del motor de ventana
try:
    datas += collect_data_files('webview')
except Exception:
    pass

# APScheduler: archivos de zona horaria y configuración
try:
    datas += collect_data_files('apscheduler')
except Exception:
    pass

# ── Hidden imports ────────────────────────────────────────────────────────────
# PyInstaller no detecta automáticamente todos los imports dinámicos de Flask.
hiddenimports = [
    # Flask y extensiones
    'flask',
    'flask.templating',
    'flask_login',
    'flask_wtf',
    'flask_wtf.csrf',
    'flask_sqlalchemy',
    'flask_mail',
    'flask_ckeditor',
    'flask_caching',
    'flask_caching.backends',
    'flask_caching.backends.simplecache',
    # flask_monitoringdashboard mockeado en entry_point.py — no necesita estar en el exe
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.sqlite.pysqlite',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.dialects.postgresql.psycopg2',
    'sqlalchemy.orm',
    'sqlalchemy.orm.decl_api',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.event',
    'sqlalchemy.pool',
    # Waitress (servidor WSGI embebido)
    'waitress',
    'waitress.utilities',
    'waitress.channel',
    'waitress.server',
    'waitress.task',
    # PyWebView (ventana nativa Windows)
    'webview',
    'webview.platforms.winforms',
    # pythonnet/clr: requerido por pywebview en Windows
    'clr',
    'clr._bootstrap',
    'System',
    'System.Windows.Forms',
    # Jinja2
    'jinja2',
    'jinja2.ext',
    'jinja2.loaders',
    # Werkzeug
    'werkzeug',
    'werkzeug.security',
    'werkzeug.middleware.proxy_fix',
    # Datos y visualización
    'pandas',
    'pandas.core.arrays.masked',
    'plotly',
    'plotly.express',
    'plotly.io',
    'plotly.graph_objects',
    'numpy',
    'openpyxl',
    'openpyxl.styles',
    'xlsxwriter',
    # Utilidades
    'markdown',
    'bleach',
    'bleach.css_sanitizer',
    'itsdangerous',
    'itsdangerous.url_safe',
    'cryptography',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives',
    'requests',
    'requests.adapters',
    'certifi',
    'charset_normalizer',
    'urllib3',
    # Fechas
    'dateutil',
    'dateutil.relativedelta',
    'pytz',
    'tzdata',
    'tzlocal',
    # APScheduler
    'apscheduler',
    'apscheduler.schedulers.background',
    'apscheduler.triggers.cron',
    'apscheduler.triggers.date',
    'apscheduler.triggers.interval',
    # Misceláneos
    'pkg_resources',
    'pkg_resources.py2_compat',
    'colorama',
    'pillow',
    'PIL',
    'PIL.Image',
    'tkinter',
    'tkinter.messagebox',
    'email.mime.text',
    'email.mime.multipart',
    'logging.handlers',
    'cachelib',
    'cachelib.simple',
    # psycopg2: driver PostgreSQL para conexión a Supabase en modo online
    'psycopg2',
    'psycopg2.extensions',
    'psycopg2.extras',
    'psycopg2._psycopg',
    # pywebpush: push notifications del navegador
    'pywebpush',
    'py_vapid',
    'http_ece',
    'cryptography.hazmat.primitives.asymmetric.ec',
    'cryptography.hazmat.primitives.serialization',
]

# Incluir todos los sub-módulos de algunos paquetes complejos
hiddenimports += collect_submodules('apscheduler')
hiddenimports += collect_submodules('waitress')
hiddenimports += collect_submodules('sqlalchemy.dialects.sqlite')
hiddenimports += collect_submodules('sqlalchemy.dialects.postgresql')

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ['entry_point.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Librerías de automatización de UI — no usadas en el servidor
        'PyAutoGUI',
        'pywhatkit',
        'wikipedia',
        'ascii_magic',
        'MouseInfo',
        'PyGetWindow',
        'PyMsgBox',
        'pyperclip',
        'PyRect',
        'PyScreeze',
        'pytweening',
        # Scipy y el dashboard de monitoreo no son necesarios en desktop
        'scipy',
        'flask_monitoringdashboard',
        # Herramientas de desarrollo
        'pytest',
        'IPython',
        'notebook',
        'jupyter_core',
        'nbformat',
        'sphinx',
        'docutils',
        # Matplotlib no está en requirements pero por si acaso
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Fofigest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                     # compresión UPX reduce ~30% el tamaño
    upx_exclude=[
        # Excluir DLLs que se corrompen con UPX
        'vcruntime140.dll',
        'python3*.dll',
        'api-ms-win*.dll',
    ],
    runtime_tmpdir=None,          # None = usa %TEMP% del sistema
    console=False,                # sin ventana de consola (windowed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Ícono: usa el logo de Fofigest si existe
    icon='static/img/logo_F-Photoroom.ico',
)

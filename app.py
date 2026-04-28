from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify,session, send_file,abort
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import models
import config
from datetime import datetime, timedelta
import random
import logging
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
import os
from itsdangerous import URLSafeTimedSerializer
from forms import EmpresaForm,ProyectoForm
import uuid
import hashlib
from datetime import datetime
import markdown
from flask_wtf.csrf import CSRFProtect
import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_ckeditor import CKEditor
from sqlalchemy import or_, and_
from io import BytesIO
from waitress import serve
import os
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template
from sqlalchemy import and_
from datetime import datetime
from flask import render_template
from sqlalchemy import extract
from sqlalchemy import desc  # Asegúrate de importar esto
import flask_monitoringdashboard as dashboard
from sqlalchemy import text


from feature.Reporte_sulfoquimica import ReporteSulfoquimica  # Importar la clase
import json


# ──────────────────────────────────────────────────────────
# TRAZABILIDAD — función auxiliar de registro inmutable
# ──────────────────────────────────────────────────────────
def registrar_trazabilidad(codigo_tarea, accion, cambios=None):
    """
    Registra un evento de auditoría sobre una tarea.

    :param codigo_tarea: str — código único de la tarea afectada.
    :param accion: str — 'CREACIÓN' | 'MODIFICACIÓN' | 'CAMBIO_ESTADO' | 'ELIMINACIÓN'
    :param cambios: list[dict] | None — cada dict: {'campo': str, 'anterior': str, 'nuevo': str}
                    Si es None se inserta un único registro sin campo/valores (usado en CREACIÓN y ELIMINACIÓN).
    """
    try:
        correo  = session.get('correo', 'sistema')
        rol     = session.get('username', 'sistema')
        empresa = session.get('empresa', None)
        ip      = request.remote_addr

        if not cambios:
            registro = models.TrazabilidadTarea(
                codigo_tarea=codigo_tarea,
                accion=accion,
                campo=None,
                valor_anterior=None,
                valor_nuevo=None,
                usuario_correo=correo,
                usuario_rol=rol,
                empresa_usuario=empresa,
                ip_address=ip,
            )
            models.db.session.add(registro)
        else:
            for c in cambios:
                val_ant = str(c.get('anterior', ''))[:500] if c.get('anterior') is not None else None
                val_nvo = str(c.get('nuevo', ''))[:500] if c.get('nuevo') is not None else None
                registro = models.TrazabilidadTarea(
                    codigo_tarea=codigo_tarea,
                    accion=accion,
                    campo=c.get('campo'),
                    valor_anterior=val_ant,
                    valor_nuevo=val_nvo,
                    usuario_correo=correo,
                    usuario_rol=rol,
                    empresa_usuario=empresa,
                    ip_address=ip,
                )
                models.db.session.add(registro)

        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        logging.error(f"Error al registrar trazabilidad [{accion}] tarea={codigo_tarea}: {str(e)}")


# Definimos el endpoint principal
host = config.config["host"]

# Configurar el logger
# En modo desktop FOFIGEST_LOG_PATH apunta a Fofigest_data/fofigest.log
_log_file = os.environ.get('FOFIGEST_LOG_PATH', 'log.log')
logging.basicConfig(
    filename=_log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d',
    encoding='utf-8'
)

# supabase reportes
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indsdmdtd3VoZnVubnBkZGNndnp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc4MzU3MzAsImV4cCI6MjA0MzQxMTczMH0.3kA18sH3ywz4B9TRHSkQ11kEqhk-l8fRa1Epq5UasVg'  # Reemplaza con tu clave de Supabase
bearer_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indsdmdtd3VoZnVubnBkZGNndnp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc4MzU3MzAsImV4cCI6MjA0MzQxMTczMH0.3kA18sH3ywz4B9TRHSkQ11kEqhk-l8fRa1Epq5UasVg'  # Reemplaza con tu Bearer Token



# Inicialización de la aplicación Flask
app = Flask(__name__)
dashboard.bind(app)
app.secret_key = 'GDSGODSGFY56D4F8asc8assS6854DCSX85Z13ZXC8478SD94C6XZ1asSDA6F48V4D615SVGZDS4ZV1_65CXZ<3F4'
# Generador de tokens seguros
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuración de la base de datos
# Prioridad de decisión:
#   1. FOFIGEST_DB_URI definido → usar esa URI tal cual (SQLite o PostgreSQL)
#   2. debug=True sin override  → SQLite de desarrollo local
#   3. Resto                    → Supabase PostgreSQL (producción / desktop online)
_SUPABASE_URI = (
    'postgresql://postgres.wlvgmwuhfunnpddcgvzu:I0P2EdBGUabioCtA'
    '@aws-0-us-west-1.pooler.supabase.com:6543/postgres'
)
_SUPABASE_ENGINE_OPTIONS = {
    'pool_pre_ping': True,   # descarta conexiones muertas (pgbouncer)
    'pool_recycle':  280,    # rota antes del cierre por inactividad de Supabase
}

debug = config.config["debug"]
_db_uri_override = os.environ.get('FOFIGEST_DB_URI')

if _db_uri_override:
    # Desktop offline (SQLite) o desktop online apuntando a otra BD vía env var
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri_override
    if _db_uri_override.startswith('postgresql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = _SUPABASE_ENGINE_OPTIONS
elif debug:
    # Desarrollo local sin env var → SQLite relativo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Empresas.db'
else:
    # Producción web o desktop con db.mode=online
    app.config['SQLALCHEMY_DATABASE_URI'] = _SUPABASE_URI
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = _SUPABASE_ENGINE_OPTIONS

# SQLALCHEMY_TRACK_MODIFICATIONS deshabilita el rastreo de modificaciones de objetos,
# ya que es innecesario y consume recursos. Es recomendable establecerlo en False.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor de correo (Gmail en este caso)
app.config['MAIL_PORT'] = 587  # Puerto SMTP (para Gmail)
app.config['MAIL_USE_TLS'] = True  # Usar TLS (seguridad)
app.config['MAIL_USE_SSL'] = False  # No usar SSL (se usa TLS)
app.config['MAIL_USERNAME'] = config.config["EMAIL"]  # Tu correo electrónico
app.config['MAIL_PASSWORD'] = config.config["contraseña_google"]  # Contraseña de tu correo (considera usar variables de entorno para mayor seguridad)
app.config['MAIL_DEFAULT_SENDER'] = ('Tu nombre', 'franklinranmirez07@hotmail.com')  # Nombre del remitente y correo por defecto
mail = Mail(app)
# Inicialización de la base de datos con la instancia de la aplicación Flask
models.db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
# Inicializa la extensión Session
ckeditor = CKEditor(app)
CKEDITOR_PKG_TYPE ="basic"

# Crear las tablas en la base de datos si no existen.
# Es recomendable envolver este código dentro de un app context
# para evitar problemas de conexión con la base de datos.
with app.app_context():
    models.db.create_all()  # Crear todas las tablas definidas en los modelos de SQLAlchemy
    # Migración manual: agrega columnas OTP si no existen (SQLite no las crea automáticamente)
    try:
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(models.db.engine)
        existing_cols = [col['name'] for col in inspector.get_columns('usuarios')]
        if 'otp_code' not in existing_cols:
            models.db.session.execute(text('ALTER TABLE usuarios ADD COLUMN otp_code VARCHAR(6)'))
        if 'otp_expiry' not in existing_cols:
            models.db.session.execute(text('ALTER TABLE usuarios ADD COLUMN otp_expiry TIMESTAMP'))
        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        app.logger.warning(f'OTP migration skipped: {e}')

    # Migración: columnas de facturación en tareas
    try:
        from sqlalchemy import inspect as sa_inspect
        inspector2 = sa_inspect(models.db.engine)
        existing_cols_tareas = [col['name'] for col in inspector2.get_columns('tareas')]
        if 'facturada' not in existing_cols_tareas:
            models.db.session.execute(text('ALTER TABLE tareas ADD COLUMN facturada BOOLEAN DEFAULT FALSE'))
        if 'cuenta_cobro_id' not in existing_cols_tareas:
            models.db.session.execute(text('ALTER TABLE tareas ADD COLUMN cuenta_cobro_id INTEGER'))
        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        app.logger.warning(f'Tareas billing migration skipped: {e}')

    # Migración: columna firma_imagen en perfil_pago
    try:
        inspector3 = sa_inspect(models.db.engine)
        existing_cols_perfil = [col['name'] for col in inspector3.get_columns('perfil_pago')]
        if 'firma_imagen' not in existing_cols_perfil:
            models.db.session.execute(text('ALTER TABLE perfil_pago ADD COLUMN firma_imagen TEXT'))
            models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        app.logger.warning(f'PerfilPago firma_imagen migration skipped: {e}')

    # Migración: sincronizar enum estado_cuenta con valores del modelo (solo PostgreSQL)
    if models.db.engine.dialect.name == 'postgresql':
        try:
            required_enum_vals = ['PENDIENTE', 'REVISI\u00d3N', 'APROBADA', 'PAGADA', 'RECHAZADA']
            with models.db.engine.connect() as raw_conn:
                existing_rows = raw_conn.execute(
                    text("SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid=t.oid WHERE t.typname='estado_cuenta'")
                ).fetchall()
                existing_enum_vals = {r[0] for r in existing_rows}
            for val in required_enum_vals:
                if val not in existing_enum_vals:
                    with models.db.engine.connect() as raw_conn2:
                        raw_conn2.execution_options(isolation_level='AUTOCOMMIT')
                        raw_conn2.execute(text(f"ALTER TYPE estado_cuenta ADD VALUE '{val}'"))
                    app.logger.info(f'estado_cuenta enum: added value {val!r}')
        except Exception as e:
            app.logger.warning(f'estado_cuenta enum migration skipped: {e}')

    # Crear directorio de colillas si no existe
    os.makedirs(os.path.join(app.root_path, 'static', 'colillas'), exist_ok=True)

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return models.db.session.get(models.Usuarios, int(user_id))
    

# Ruta para subir archivos y procesar datos
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verificar si se subió un archivo
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No selected file'
        
        if file:
            filename = secure_filename(file.filename)
            print("------------------------------------------------------------------")
            print(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Procesar el archivo Excel subido
            data = pd.read_excel("Task_Fofigest.xlsx")
            for index, row in data.iterrows():
                nueva_tarea = models.Tareas(
                    id=row['id'],
                    empresa=row['Empresa'],
                    codigo_proyecto=row['Codigo Proyecto'],
                    codigo_tarea=row['Codigo Tarea'],
                    titulo=row['Titulo'],
                    descripcion=row['Descripcion'],
                    fecha_inicio=pd.to_datetime(row['Fecha Inicio']),
                    fecha_fin=pd.to_datetime(row['Fecha Fin']),
                    responsable=row['Responsable'],
                    horas_dedicadas=row['Horas Dedicadas'],
                    horas_estimadas=row['Horas Estimadas'],
                    fecha_facturacion=pd.to_datetime(row['Fecha Facturacion']),
                    estado=row['Estado'],
                    tipo_consumo=row['Tipo Consumo'],
                    mes=row['Mes']
                )
                models.db.session.add(nueva_tarea)
            
            models.db.session.commit()
            return 'Archivo subido y datos cargados con éxito'

    return render_template('subir_datos.html')


#<___________________________________Vista___________________________________________________>

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def serve_sw():
    return send_file(os.path.join('static', 'js', 'sw.js'), mimetype='application/javascript')

@app.context_processor
def inject_user():
    return dict(username=session.get('username'))


# ─── Helpers de reglas de negocio — facturación ───────────────────────────────

def _check_tarea_bloqueada(tarea):
    """
    Verifica si una tarea no puede modificarse por estar vinculada a una cuenta de cobro.

    Reglas:
      - Cuenta en estado PAGADA → bloqueada para TODOS (incluye admin).
      - Facturada en otro estado → bloqueada solo para usuarios no-admin.

    Retorna (True, (response, status_code)) si bloqueada; (False, None) si libre.
    """
    if not tarea.facturada and not tarea.cuenta_cobro_id:
        return False, None
    cuenta = None
    if tarea.cuenta_cobro_id:
        cuenta = models.CuentaCobro.query.get(tarea.cuenta_cobro_id)
    if cuenta and cuenta.estado == 'PAGADA':
        return True, (
            jsonify({'ok': False, 'error': f'La tarea pertenece a la cuenta {cuenta.numero_cuenta} que ya fue PAGADA y no puede modificarse.'}),
            403
        )
    if session.get('username') not in ['admin', 'superadmin']:
        num = cuenta.numero_cuenta if cuenta else 'en cobro'
        return True, (
            jsonify({'ok': False, 'error': f'La tarea está incluida en la cuenta de cobro {num} y no puede modificarse.'}),
            403
        )
    return False, None


def _get_tareas_pagadas_ids(tareas_list):
    """Retorna un set de IDs de tareas cuya cuenta de cobro está en estado PAGADA."""
    if not tareas_list:
        return set()
    cc_ids = {t.cuenta_cobro_id for t in tareas_list if t.cuenta_cobro_id}
    if not cc_ids:
        return set()
    pagadas_cc_ids = {
        cc.id for cc in models.CuentaCobro.query.filter(
            models.CuentaCobro.id.in_(cc_ids),
            models.CuentaCobro.estado == 'PAGADA'
        ).all()
    }
    return {t.id for t in tareas_list if t.cuenta_cobro_id in pagadas_cc_ids}

# ─────────────────────────────────────────────────────────────────────────────


def buscar_tareas(clave_busqueda):
    """
    Endpoint para obtener las tareas filtradas por palabra clave, fecha de inicio, fecha de fin y estado.

    Parámetros de consulta (query parameters):
    - clave_busqueda: Palabra clave para buscar en el título o la descripción.
    - fecha_inicio: Fecha mínima de inicio de las tareas (formato 'YYYY-MM-DD').
    - fecha_fin: Fecha máxima de finalización de las tareas (formato 'YYYY-MM-DD').
    - estado: Estado de la tarea (PENDIENTE, PROGRESO, REVISIÓN, IMPEDIMENTOS, COMPLETADOS).

    :return: Lista de tareas que cumplen los criterios de búsqueda en formato JSON.
    """

    # Obtener parámetros de la URL
    clave_busqueda = request.args.get('clave_busqueda', default='', type=str)
    fecha_inicio = request.args.get('fecha_inicio', type=str)
    fecha_fin = request.args.get('fecha_fin', type=str)
    estado = request.args.get('estado', type=str)

    # Base de la consulta
    query = models.db.session.query(models.Tareas).filter(
        or_(
            models.Tareas.titulo.ilike(f'%{clave_busqueda}%'),
            models.Tareas.descripcion.ilike(f'%{clave_busqueda}%')
        )
    )

    # Filtrar por fecha de inicio si se proporciona
    if fecha_inicio:
        query = query.filter(models.Tareas.fecha_inicio >= fecha_inicio)
    
    # Filtrar por fecha de fin si se proporciona
    if fecha_fin:
        query = query.filter(models.Tareas.fecha_fin <= fecha_fin)
    
    # Filtrar por estado si se proporciona
    if estado:
        query = query.filter(models.Tareas.estado == estado)

    # Ejecutar la consulta y obtener los resultados
    tareas = query.all()

    return tareas

# Reporte Gantt principal
@app.route('/gannt', methods=['GET', 'POST'])
@login_required
def gannt():
    try:
        hoy = datetime.today()
        hace_doce_meses = hoy - relativedelta(months=12)

        permisos = session.get('username')
        empresa_usuario = session.get('empresa')

        # Obtener los proyectos según el tipo de usuario
        if permisos == 'usuario':
            proyectos_ = models.Proyecto.query.filter_by(empresa=empresa_usuario).all()
        else:
            proyectos_ = models.Proyecto.query.all()

        # Filtros base
        filtros = [
            models.Tareas.fecha_inicio >= hace_doce_meses,
            models.Tareas.fecha_inicio <= hoy,
            models.Tareas.fecha_inicio.isnot(None),
            models.Tareas.fecha_fin.isnot(None)
        ]

        # Aplicar filtro de empresa si es usuario
        if permisos == 'usuario':
            filtros.append(models.Tareas.empresa == empresa_usuario)

        # Si es POST, redirigir al proyecto seleccionado
        if request.method == 'POST':
            proyecto_id = request.form.get('proyecto_i')
            return redirect(f'/gannt/{proyecto_id}')

        # Obtener tareas
        #tareas = models.Tareas.query.filter(and_(*filtros)).all()
        tareas = models.Tareas.query.filter(and_(*filtros)).order_by(desc(models.Tareas.fecha_inicio)).all()


        # Construir data
        tareas_data = [{
            "id": str(tarea.codigo_tarea),
            "id_bd": tarea.id,
            "name": tarea.titulo,
            "start": tarea.fecha_inicio.strftime("%Y-%m-%d"),
            "end": tarea.fecha_fin.strftime("%Y-%m-%d"),
            "progress": round((tarea.horas_dedicadas / tarea.horas_estimadas) * 100, 1) if tarea.horas_estimadas else 0,
            "estado": tarea.estado or "PENDIENTE",
            "responsable": tarea.responsable or "",
            "horas_dedicadas": tarea.horas_dedicadas or 0,
            "horas_estimadas": tarea.horas_estimadas or 0,
            "codigo_proyecto": tarea.codigo_proyecto or ""
        } for tarea in tareas]

        return render_template('gantt.html', tareas_jsons=tareas_data, proyectos_=proyectos_)

    except Exception as e:
        logging.error(f"Error en /gannt: {str(e)}")
        flash("Hubo un error al cargar el gráfico de Gantt.", "danger")
        return render_template('gantt.html', tareas_jsons=[], proyectos_=[])


# Reporte Gantt por proyecto
@login_required
@app.route('/gannt/<project>', methods=['GET', 'POST'])
def gannt_project(project):
    try:
        hoy = datetime.today()
        hace_doce_meses = hoy - relativedelta(months=12)

        filtros = [
            models.Tareas.fecha_inicio >= hace_doce_meses,
            models.Tareas.fecha_inicio <= hoy,
            models.Tareas.fecha_inicio.isnot(None),
            models.Tareas.fecha_fin.isnot(None),
            models.Tareas.codigo_proyecto == project
        ]

        permisos = session.get('username')
        empresa_usuario = session.get('empresa')

        if permisos == 'usuario':
            filtros.append(models.Tareas.empresa == empresa_usuario)

        proyectos_ = models.Proyecto.query.all()
        #tareas = models.Tareas.query.filter(and_(*filtros)).all()
        tareas = models.Tareas.query.filter(and_(*filtros)).order_by(desc(models.Tareas.fecha_inicio)).all()


        tareas_data = [{
            "id": str(tarea.codigo_tarea),
            "id_bd": tarea.id,
            "name": tarea.titulo,
            "start": tarea.fecha_inicio.strftime("%Y-%m-%d"),
            "end": tarea.fecha_fin.strftime("%Y-%m-%d"),
            "progress": round((tarea.horas_dedicadas / tarea.horas_estimadas) * 100, 1) if tarea.horas_estimadas else 0,
            "estado": tarea.estado or "PENDIENTE",
            "responsable": tarea.responsable or "",
            "horas_dedicadas": tarea.horas_dedicadas or 0,
            "horas_estimadas": tarea.horas_estimadas or 0,
            "codigo_proyecto": tarea.codigo_proyecto or ""
        } for tarea in tareas]

        return render_template('gantt.html', tareas_jsons=tareas_data, proyectos_=proyectos_)

    except Exception as e:
        logging.error(f"Error en /gannt/<project>: {str(e)}")
        flash("Hubo un error al cargar el gráfico de Gantt.", "danger")
        return render_template('gantt.html', tareas_jsons=[], proyectos_=[])


# ─── API Endpoints para Gantt Enterprise ──────────────────────────────────────

@app.route('/api/gantt/tarea/<string:codigo_tarea>', methods=['PATCH'])
@login_required
def gantt_update_tarea(codigo_tarea):
    """Actualiza fechas, titulo, estado, responsable o progreso de una tarea."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"ok": False, "error": "JSON inválido"}), 400

        tarea = models.Tareas.query.filter_by(codigo_tarea=codigo_tarea).first()
        if not tarea:
            return jsonify({"ok": False, "error": "Tarea no encontrada"}), 404

        bloqueada, resp = _check_tarea_bloqueada(tarea)
        if bloqueada:
            return resp

        _gsnap = {
            'titulo': tarea.titulo, 'fecha_inicio': str(tarea.fecha_inicio),
            'fecha_fin': str(tarea.fecha_fin), 'estado': tarea.estado,
            'responsable': tarea.responsable, 'horas_estimadas': tarea.horas_estimadas,
            'horas_dedicadas': tarea.horas_dedicadas,
        }

        if 'titulo' in data and data['titulo'].strip():
            tarea.titulo = data['titulo'].strip()[:100]
        if 'fecha_inicio' in data:
            tarea.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        if 'fecha_fin' in data:
            tarea.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
        if 'estado' in data and data['estado'] in ('PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS'):
            tarea.estado = data['estado']
        if 'responsable' in data:
            tarea.responsable = data['responsable'].strip()[:100]
        if 'horas_estimadas' in data:
            he = float(data['horas_estimadas'])
            if he >= 0:
                tarea.horas_estimadas = he
        if 'progress' in data:
            prog = max(0.0, min(100.0, float(data['progress'])))
            tarea.horas_dedicadas = round((prog / 100.0) * (tarea.horas_estimadas or 0), 2)

        models.db.session.commit()
        _gsnap_new = {
            'titulo': tarea.titulo, 'fecha_inicio': str(tarea.fecha_inicio),
            'fecha_fin': str(tarea.fecha_fin), 'estado': tarea.estado,
            'responsable': tarea.responsable, 'horas_estimadas': tarea.horas_estimadas,
            'horas_dedicadas': tarea.horas_dedicadas,
        }
        _gcambios = [{'campo': k, 'anterior': _gsnap[k], 'nuevo': _gsnap_new[k]}
                     for k in _gsnap if str(_gsnap[k]) != str(_gsnap_new[k])]
        if _gcambios:
            _gaccion = 'CAMBIO_ESTADO' if len(_gcambios) == 1 and _gcambios[0]['campo'] == 'estado' else 'MODIFICACIÓN'
            registrar_trazabilidad(codigo_tarea, _gaccion, _gcambios)
        return jsonify({"ok": True})

    except (ValueError, KeyError) as e:
        models.db.session.rollback()
        return jsonify({"ok": False, "error": "Datos inválidos: " + str(e)}), 422
    except Exception as e:
        models.db.session.rollback()
        logging.error(f"Error PATCH /api/gantt/tarea/{codigo_tarea}: {str(e)}")
        return jsonify({"ok": False, "error": "Error interno"}), 500


@app.route('/api/gantt/tarea', methods=['POST'])
@login_required
def gantt_create_tarea():
    """Crea una nueva tarea desde el Gantt."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"ok": False, "error": "JSON inválido"}), 400

        required = ('titulo', 'fecha_inicio', 'fecha_fin', 'responsable', 'codigo_proyecto')
        for field in required:
            if not data.get(field):
                return jsonify({"ok": False, "error": f"Campo requerido: {field}"}), 422

        meses_es = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                    'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin    = datetime.strptime(data['fecha_fin'],    '%Y-%m-%d').date()
        mes = meses_es[fecha_inicio.month - 1]

        tipo_consumo_validos = ('Desarrollo','Reuniones','Desarrollo por control de cambio','Soporte','Oportunidad de mejora')
        tipo_consumo = data.get('tipo_consumo', 'Desarrollo')
        if tipo_consumo not in tipo_consumo_validos:
            tipo_consumo = 'Desarrollo'

        codigo_tarea = f"{data['codigo_proyecto'][:10]}-{uuid.uuid4().hex[:8]}"

        nueva = models.Tareas(
            empresa=data.get('empresa', session.get('empresa', '')),
            codigo_proyecto=data['codigo_proyecto'],
            codigo_tarea=codigo_tarea,
            titulo=data['titulo'].strip()[:100],
            descripcion=data.get('descripcion', 'Tarea creada desde Gantt'),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            responsable=data['responsable'].strip()[:100],
            horas_dedicadas=0.0,
            horas_estimadas=float(data.get('horas_estimadas', 8)),
            estado=data.get('estado', 'PENDIENTE'),
            tipo_consumo=tipo_consumo,
            mes=mes
        )
        models.db.session.add(nueva)
        models.db.session.commit()
        registrar_trazabilidad(codigo_tarea, 'CREACIÓN')

        return jsonify({
            "ok": True,
            "tarea": {
                "id": codigo_tarea,
                "id_bd": nueva.id,
                "name": nueva.titulo,
                "start": nueva.fecha_inicio.strftime('%Y-%m-%d'),
                "end": nueva.fecha_fin.strftime('%Y-%m-%d'),
                "progress": 0,
                "estado": nueva.estado,
                "responsable": nueva.responsable,
                "horas_dedicadas": 0,
                "horas_estimadas": nueva.horas_estimadas,
                "codigo_proyecto": nueva.codigo_proyecto
            }
        }), 201

    except (ValueError, KeyError) as e:
        models.db.session.rollback()
        return jsonify({"ok": False, "error": "Datos inválidos: " + str(e)}), 422
    except IntegrityError:
        models.db.session.rollback()
        return jsonify({"ok": False, "error": "El código de tarea ya existe, intenta de nuevo"}), 409
    except Exception as e:
        models.db.session.rollback()
        logging.error(f"Error POST /api/gantt/tarea: {str(e)}")
        return jsonify({"ok": False, "error": "Error interno"}), 500


@app.route('/api/gantt/tarea/<string:codigo_tarea>', methods=['DELETE'])
@login_required
def gantt_delete_tarea(codigo_tarea):
    """Elimina una tarea por su codigo_tarea."""
    try:
        tarea = models.Tareas.query.filter_by(codigo_tarea=codigo_tarea).first()
        if not tarea:
            return jsonify({"ok": False, "error": "Tarea no encontrada"}), 404
        bloqueada, resp = _check_tarea_bloqueada(tarea)
        if bloqueada:
            return resp
        registrar_trazabilidad(codigo_tarea, 'ELIMINACIÓN')
        models.db.session.delete(tarea)
        models.db.session.commit()
        return jsonify({"ok": True})
    except Exception as e:
        models.db.session.rollback()
        logging.error(f"Error DELETE /api/gantt/tarea/{codigo_tarea}: {str(e)}")
        return jsonify({"ok": False, "error": "Error interno"}), 500


# login 
@app.route("/")
def login():
    logging.info("Inicio de pagina ")
    return render_template("login.html")

@app.route("/", methods=['POST'])
def loginInp():
    v = config.config["version"]
    email = request.form.get('exampleInputEmail')
    password = request.form.get('exampleInputPassword')

    usuario = models.Usuarios.query.filter_by(correo=email).first()

    if usuario:
        stored = usuario.contraseña or ''
        # Soporta contraseñas hasheadas (werkzeug) y texto plano (usuarios legacy)
        try:
            password_ok = check_password_hash(stored, password)
        except Exception:
            password_ok = False
        if not password_ok:
            password_ok = (stored == password)

        if password_ok:
            login_user(usuario)
            logging.info(f"Inicio de sesión exitoso: {email}")
            session['username'] = usuario.permisos
            session['empresa'] = usuario.empresa
            session['correo'] = usuario.correo
            if usuario.permisos == 'usuario':
                redirect_url = f'/Reporte-Horas{usuario.empresa}'
            else:
                redirect_url = '/tablero'
            return render_template("splash.html", v=v, redirect_url=redirect_url)

    flash("Email o contraseña incorrectos", "danger")
    logging.warning(f"Intento de login fallido para: {email}")
    return render_template("login.html")

# Ruta del tablero
@app.route('/tablero', methods=['GET', 'POST'])
@login_required
def proyecto():
    """
    Ruta para mostrar el tablero de tareas con las tareas agrupadas por su estado.
    """
    # Configuración del host (si es necesario)
    host = config.config.get("host", "localhost")
    
    # Obtener todas las empresas, proyectos, y usuarios
    empresas = models.Empresas.query.all()
    proyectos = models.Proyecto.query.all()
    usuarios = models.Usuarios.query.all()
    
    # Consultar todas las tareas inicialmente
    tareas_PENDIENTE = models.Tareas.query.filter_by(estado='PENDIENTE')
    tareas_PROGRESO = models.Tareas.query.filter_by(estado='PROGRESO')
    tareas_REVISIÓN = models.Tareas.query.filter_by(estado='REVISIÓN')
    tareas_IMPEDIMENTOS = models.Tareas.query.filter_by(estado='IMPEDIMENTOS')
    tareas_COMPLETADOS = models.Tareas.query.filter_by(estado='COMPLETADOS')

    # Si se hace un POST (se envía el formulario de filtros)
    if request.method == 'POST':
        
        # Filtro por estado (opcional)
        estado = request.form.get('estado_')
        if estado:
            tareas_PENDIENTE = tareas_PENDIENTE.filter(models.Tareas.estado == estado)
            tareas_PROGRESO = tareas_PROGRESO.filter(models.Tareas.estado == estado)
            tareas_REVISIÓN = tareas_REVISIÓN.filter(models.Tareas.estado == estado)
            tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.filter(models.Tareas.estado == estado)
            tareas_COMPLETADOS = tareas_COMPLETADOS.filter(models.Tareas.estado == estado)

        # Filtro por responsable (opcional)
        responsable = request.form.get('responsable_')
        if responsable:
            tareas_PENDIENTE = tareas_PENDIENTE.filter(models.Tareas.responsable == responsable)
            tareas_PROGRESO = tareas_PROGRESO.filter(models.Tareas.responsable == responsable)
            tareas_REVISIÓN = tareas_REVISIÓN.filter(models.Tareas.responsable == responsable)
            tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.filter(models.Tareas.responsable == responsable)
            tareas_COMPLETADOS = tareas_COMPLETADOS.filter(models.Tareas.responsable == responsable)

        # Filtro por proyecto (opcional)
        proyecto = request.form.get('codigo_proyecto_')
        
        if proyecto:
            tareas_PENDIENTE = tareas_PENDIENTE.filter(models.Tareas.codigo_proyecto == proyecto)
            tareas_PROGRESO = tareas_PROGRESO.filter(models.Tareas.codigo_proyecto == proyecto)
            tareas_REVISIÓN = tareas_REVISIÓN.filter(models.Tareas.codigo_proyecto == proyecto)
            tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.filter(models.Tareas.codigo_proyecto == proyecto)
            tareas_COMPLETADOS = tareas_COMPLETADOS.filter(models.Tareas.codigo_proyecto == proyecto)

        # Filtro por mes (opcional)
        mes = request.form.get('mes_')
        if mes:
            tareas_PENDIENTE = tareas_PENDIENTE.filter(models.Tareas.mes == mes)
            tareas_PROGRESO = tareas_PROGRESO.filter(models.Tareas.mes == mes)
            tareas_REVISIÓN = tareas_REVISIÓN.filter(models.Tareas.mes == mes)
            tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.filter(models.Tareas.mes == mes)
            tareas_COMPLETADOS = tareas_COMPLETADOS.filter(models.Tareas.mes == mes)

        # Filtro por empresa (opcional)
        empresa = request.form.get('empresa_')
        if empresa:
            tareas_PENDIENTE = tareas_PENDIENTE.filter(models.Tareas.empresa == empresa)
            tareas_PROGRESO = tareas_PROGRESO.filter(models.Tareas.empresa == empresa)
            tareas_REVISIÓN = tareas_REVISIÓN.filter(models.Tareas.empresa == empresa)
            tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.filter(models.Tareas.empresa == empresa)
            tareas_COMPLETADOS = tareas_COMPLETADOS.filter(models.Tareas.empresa == empresa)

    # Ejecutar las consultas filtradas y convertirlas en listas
    tareas_PENDIENTE = tareas_PENDIENTE.all()
    tareas_PROGRESO = tareas_PROGRESO.all()
    tareas_REVISIÓN = tareas_REVISIÓN.all()
    tareas_IMPEDIMENTOS = tareas_IMPEDIMENTOS.all()
    tareas_COMPLETADOS = tareas_COMPLETADOS.all()

    # Calcular las horas estimadas y de ejecución de todas las tareas
    total_horas_ejecucion = sum((tarea.horas_dedicadas or 0) for tarea in models.Tareas.query.all())

    # Renderizar la plantilla con los datos obtenidos
    all_tareas_tablero = tareas_PENDIENTE + tareas_PROGRESO + tareas_REVISIÓN + tareas_IMPEDIMENTOS + tareas_COMPLETADOS
    tareas_pagadas_ids = _get_tareas_pagadas_ids(all_tareas_tablero)
    return render_template('tablero.html',
                           empresas=empresas,
                           host=host,
                           tareas_PENDIENTE=tareas_PENDIENTE,
                           tareas_PROGRESO=tareas_PROGRESO,
                           tareas_REVISIÓN=tareas_REVISIÓN,
                           tareas_IMPEDIMENTOS=tareas_IMPEDIMENTOS,
                           tareas_COMPLETADOS=tareas_COMPLETADOS,
                           proyectos=proyectos,
                           usuarios=usuarios,
                           total_horas_ejecucion=total_horas_ejecucion,
                           tareas_pagadas_ids=tareas_pagadas_ids)

# Nuevo usuario 
@app.route("/Nuevo_Usuario")
def Nuevo_Usuario():
    logging.info("Ingreso a pagina de creacion de usuarios ")
    empresas = models.Empresas.query.all()
    return render_template("Nuevo_Usuario.html",empresas=empresas)

@app.route("/Nuevo_Usuario", methods=['POST'])
def nuevo_usuario_post():
    if request.method == "POST":
        try:
            # Crear una nueva instancia del modelo Usuario
            data = models.Usuarios(
                nombres=request.form.get('Nombres'),
                apellidos=request.form.get('Apellidos'),
                correo=request.form.get('correo'),
                contraseña=generate_password_hash(request.form.get('Contraseña')),
                empresa=request.form.get('Empresa'),
                permisos="nuevo"
            )

            # Agregar el nuevo usuario a la base de datos
            models.db.session.add(data)
            models.db.session.commit()

            # Mostrar mensaje de éxito
            flash("El usuario se creó de manera exitosa", "success")
            return render_template("login.html") 
        
        except IntegrityError:
            
            
            # Manejo del error si el correo ya existe en la base de datos
            models.db.session.rollback()  # Revertir los cambios en la base de datos
            logging.error("El usuario ya existe en la base de datos")
            flash("El usuario no es valido", "danger")
            empresas = models.Empresas.query.all()
            return render_template("Nuevo_Usuario.html",empresas=empresas)

# Olvido las contraseñas
@app.route("/olvidaste")
def Olvidaste():
    logging.info("Ingreso a pagina de olvidaste contraseña ")
    empresas = models.Empresas.query.all()
    return render_template("Olvide_Contraseña.html",empresas=empresas)

@app.route("/olvidaste", methods=['POST'])
def olvidaste_post():
    if request.method == "POST":
        
        # Crear una nueva instancia del modelo Usuario
        correo=request.form.get('correo')
        empresa=request.form.get('Empresa')
        empresa = models.Empresas.query.filter_by(id=empresa).first()
        usuario = models.Usuarios.query.filter_by(correo=correo).first()
        # Generar la URL de restablecimiento
        token = serializer.dumps(correo, salt='password-reset-salt')
        reset_url = url_for('reset_with_token', token=token, _external=True)
        if usuario and empresa:
            try:
                # Crear el mensaje
                msg = Message('Restablecimiento de Contraseña - FOFIGEST', 
                            recipients=[f'{correo}'])  # Lista de destinatarios
                msg.body = 'Este es el cuerpo del correo en texto plano.'
                msg.html = f"""<p>Hola {usuario.nombres},</p>
                               <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en FOFIGEST.
                               Si tú no solicitaste este cambio, puedes ignorar este correo.</p>
                               <p>Para restablecer tu contraseña haz clic en el siguiente botón:</p>
                               <p><a href="{reset_url}" style="background:#5a67d8;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">Restablecer contraseña</a></p>
                               <p>O copia este enlace en tu navegador:<br><code>{reset_url}</code></p>
                               <p>Este enlace es válido por <strong>1 hora</strong> y solo puede usarse una vez.</p>
                               <p>Gracias por utilizar FOFIGEST.<br>El equipo de FOFIGEST</p>"""

                # Enviar el correo
                mail.send(msg)
                flash("Hemos enviado una solicitud para restablecer la contraseña a tu email", "success")
                logging.info("Hemos enviado una solicitud para restablecer la contraseña a tu email ")
                return render_template("Olvide_Contraseña.html") 
            except Exception as e:
                flash(f"Error :{e}", "danger")
                return str(e)

        flash("No se encontró una cuenta con ese correo o empresa", "danger")
        empresas = models.Empresas.query.all()
        return render_template("Olvide_Contraseña.html", empresas=empresas)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        # Verificar el token (con un tiempo de expiración, en este caso 3600 segundos o 1 hora)
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception as e:
        flash('El enlace de restablecimiento es inválido o ha expirado', 'danger')
        return redirect(url_for('Olvidaste'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('reset_with_token.html', token=token)
        usuario = models.Usuarios.query.filter_by(correo=email).first()
        if usuario:
            usuario.contraseña = generate_password_hash(new_password)
            models.db.session.commit()
            logging.info(f"Contraseña restablecida para: {email}")
        flash('Tu contraseña ha sido restablecida con éxito', 'success')
        return redirect(url_for('login'))

    return render_template('reset_with_token.html', token=token)


# OTP Login — paso 1: solicitar correo y enviar código
@app.route('/login-otp', methods=['GET', 'POST'])
def login_otp():
    if request.method == 'POST':
        correo = request.form.get('correo')
        usuario = models.Usuarios.query.filter_by(correo=correo).first()
        if usuario:
            otp = str(random.randint(100000, 999999))
            usuario.otp_code = otp
            usuario.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            models.db.session.commit()
            try:
                msg = Message('Código de acceso FOFIGEST', recipients=[correo])
                msg.html = f"""<p>Hola {usuario.nombres},</p>
                               <p>Tu código de acceso de un solo uso para FOFIGEST es:</p>
                               <h2 style="letter-spacing:10px;color:#5a67d8;font-size:2rem;">{otp}</h2>
                               <p>Este código es válido por <strong>10 minutos</strong>.</p>
                               <p>Si no solicitaste este código, ignora este mensaje.</p>
                               <p>El equipo de FOFIGEST</p>"""
                mail.send(msg)
                flash('Código enviado. Revisa tu correo electrónico.', 'success')
            except Exception as e:
                logging.error(f"Error enviando OTP a {correo}: {e}")
                flash('No se pudo enviar el código. Intenta de nuevo.', 'danger')
                return render_template('login_otp.html')
            session['otp_correo'] = correo
            return redirect(url_for('verify_otp'))
        else:
            flash('No existe una cuenta registrada con ese correo', 'danger')
    return render_template('login_otp.html')


# OTP Login — paso 2: verificar código de 6 dígitos
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    correo = session.get('otp_correo')
    if not correo:
        return redirect(url_for('login_otp'))

    if request.method == 'POST':
        otp_input = request.form.get('otp_code', '').strip()
        usuario = models.Usuarios.query.filter_by(correo=correo).first()
        if (usuario and usuario.otp_code and usuario.otp_expiry
                and usuario.otp_code == otp_input
                and usuario.otp_expiry > datetime.utcnow()):
            usuario.otp_code = None
            usuario.otp_expiry = None
            models.db.session.commit()
            login_user(usuario)
            session['username'] = usuario.permisos
            session['empresa'] = usuario.empresa
            session['correo'] = usuario.correo
            session.pop('otp_correo', None)
            logging.info(f"Login OTP exitoso: {correo}")
            v = config.config["version"]
            if usuario.permisos == 'usuario':
                redirect_url = f'/Reporte-Horas{usuario.empresa}'
            else:
                redirect_url = '/tablero'
            return render_template("splash.html", v=v, redirect_url=redirect_url)
        else:
            flash('Código incorrecto o expirado', 'danger')

    return render_template('verify_otp.html', correo=correo)


# empresa
@app.route('/empresa', methods=['GET', 'POST'])
@login_required
def empresa():
    form = EmpresaForm()
    host = config.config["host"]
    

    if form.validate_on_submit():
        # Buscar si ya existe una empresa con el NIT ingresado
        empresa_existente = models.Empresas.query.filter_by(nit=form.nit.data).first()

        if empresa_existente:
            # Si la empresa ya existe, se actualizan sus datos
            empresa_existente.empresa = form.empresa.data
            models.db.session.commit()
            flash('Empresa actualizada con éxito!', 'success')
        else:
            # Si no existe, se crea una nueva empresa
            nueva_empresa = models.Empresas(nit=form.nit.data, empresa=form.empresa.data)
            models.db.session.add(nueva_empresa)
            models.db.session.commit()
            flash('Empresa registrada con éxito!', 'success')

        # Redirigir para evitar reenvío de formularios
        return redirect(url_for('empresa'))

    # Obtener todas las empresas para mostrarlas en la tabla
    empresas = models.Empresas.query.all()
    

    return render_template('empresas.html', empresas=empresas, form=form,host=host)

# proyectos 
@app.route('/proyectos', methods=['GET'])
@login_required
def proyectos():  # Cambié de 'proyetos' a 'proyectos'
    # Obtener todas las proyectos para mostrarlas en la tabla
    proyectos = models.Proyecto.query.all()
    empresas = models.Empresas.query.all()
    usuarios = models.Usuarios.query.all()


    return render_template('proyectos.html', proyectos=proyectos, empresas=empresas ,usuarios=usuarios)

# Descripcion
@app.route('/submit-description', methods=['GET', 'POST'])
@login_required
def submit_description():
    print(request.form)  # Imprime los datos del formulario recibidos
    markdown_text = request.form.get('description')  # Usar get() para evitar KeyError
    if markdown_text is None:
        return "No description found", 400
    html_content = markdown.markdown(markdown_text)
    return render_template('description_preview.html', content=html_content)

# Función que convierte Markdown a HTML y lo muestra en una plantilla
@app.route('/render_markdown', methods=['POST', 'GET'])
@login_required
def render_markdown():
    if request.method == 'POST':
        # Obtener el contenido del formulario
        markdown_text = request.form.get('markdown_text', '')
        # Convertir el texto Markdown a HTML
        html_content = markdown.markdown(markdown_text)
        # Renderizar la plantilla con el HTML generado
        return render_template('markdown_result.html', content=html_content)
    return render_template('markdown_form.html')

# Tareas vista 
@app.route('/tareas', methods=['GET', 'POST'])
@login_required
def vista_tareas():
    """
    Obtener todas las tareas con los filtros seleccionados por el usuario.
    """
    proyectos = models.Proyecto.query.all()
    usuarios = models.Usuarios.query.all()
    empresas = models.Empresas.query.all()
    
    # Inicializa la consulta de tareas
    tareas_query = models.Tareas.query

    if request.method == 'POST':
    
        # Filtro por estado
        estado = request.form.get('estado_')
        if estado:
            tareas_query = tareas_query.filter(models.Tareas.estado == estado)

        # Filtro por responsable
        responsable = request.form.get('responsable_')
        if responsable:
            tareas_query = tareas_query.filter(models.Tareas.responsable == responsable)

        # Filtro por proyecto
        proyecto = request.form.get('proyecto_')
        if proyecto:
            tareas_query = tareas_query.filter(models.Tareas.codigo_proyecto == proyecto)
            

        # Filtro por mes
        mes = request.form.get('mes_')
        if mes:
            tareas_query = tareas_query.filter(models.Tareas.mes == mes)

        # Filtro por empresa
        empresa = request.form.get('empresa_')
        if empresa:
            tareas_query = tareas_query.filter(models.Tareas.empresa == empresa)

        # Filtro por fecha de inicio y fecha de fin
        fecha_inicio = request.form.get('fecha_inicio_')
        fecha_fin = request.form.get('fecha_fin_')
        if fecha_inicio and fecha_fin:
            tareas_query = tareas_query.filter(models.Tareas.fecha_inicio >= fecha_inicio, 
                                            models.Tareas.fecha_fin <= fecha_fin)

        # Obtener el resultado final de las tareas filtradas
        tareas = tareas_query.all()

    else:
        # Si no se ha enviado POST, muestra todas las tareas
        tareas = models.Tareas.query.all()

    # Calcular las horas estimadas y de ejecución
    total_horas_ejecucion = sum((tarea.horas_dedicadas or 0) for tarea in tareas)

    tareas_pagadas_ids = _get_tareas_pagadas_ids(tareas)
    return render_template("tareas.html", tareas=tareas,
                                        empresas=empresas,
                                        proyectos=proyectos,
                                        usuarios=usuarios,
                                        total_horas_ejecucion=total_horas_ejecucion,
                                        tareas_pagadas_ids=tareas_pagadas_ids)

# usuarios vista 
@app.route('/usuarios_admin', methods=['GET'])
@login_required
def vista_usuarios():
    """
   vista de usuarios CRUD para administrsr.
    """
    empresas = models.Empresas.query.all()

    return render_template("usuarios.html",host=host,empresas=empresas)

# Reporte de proyectos 
@app.route('/reporte')
@login_required
def obtener_tareas_reporte():
    try:
        # Consulta las tareas desde el modelo Tareas
        tareas = models.Tareas.query.all()

        # Convertir los datos de las tareas en una lista de diccionarios
        tareas_data = [{
            "codigo_proyecto": tarea.codigo_proyecto,
            "codigo_tarea": tarea.codigo_tarea,
            "descripcion": tarea.descripcion,
            "empresa": tarea.empresa,
            "estado": tarea.estado,
            "fecha_facturacion": tarea.fecha_facturacion,
            "fecha_fin": tarea.fecha_fin,
            "fecha_inicio": tarea.fecha_inicio,
            "horas_dedicadas": tarea.horas_dedicadas,
            "horas_estimadas": tarea.horas_estimadas,
            "id": tarea.id,
            "responsable": tarea.responsable,
            "titulo": tarea.titulo
        } for tarea in tareas]

        # Convertir a DataFrame
        df = pd.DataFrame(tareas_data)

        # Asegurarse de que las fechas sean del tipo datetime
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], errors='coerce')
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin'], errors='coerce')

        # Crear gráfico Gantt usando Plotly
        fig = px.timeline(df, x_start="fecha_inicio", x_end="fecha_fin", y="titulo", color="estado",
                        hover_name="descripcion", title="Tareas de proyectos")

        # Ajustar el diseño del gráfico (opcional)
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Tareas",
            plot_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="white"  # Color del texto blanco para coherencia con el tema oscuro
            )
        )

        # Convertir gráfico a HTML
        gantt_html = pio.to_html(fig, full_html=False)

        # Calcular métricas (ejemplo de horas dedicadas y estimadas por proyecto)
        metricas = df.groupby('codigo_proyecto')[['horas_dedicadas', 'horas_estimadas']].sum().reset_index()

        # Renderizar la plantilla con el gráfico y las métricas
        return render_template('reporte.html', gantt_html=gantt_html, metricas=metricas)
    except:
          # Obtener todas las proyectos para mostrarlas en la tabla
        proyectos = models.Proyecto.query.all()
        empresas = models.Empresas.query.all()
        usuarios = models.Usuarios.query.all()


        return render_template('proyectos.html', proyectos=proyectos, empresas=empresas ,usuarios=usuarios)

@app.route('/logout')
@app.route('/Reporte-Horas/logout')
@login_required
def logout():
    logout_user()  # Cerrar sesión
    session.pop('username', None)
    session.pop('empresa', None)
    session.pop('correo', None)
    return redirect(url_for('login'))


# Reporte de horas vista
@app.route('/Reporte-Horas<empresa>', methods=['GET','POST'])
@login_required
def vista_reporte_Horas(empresa):
    """
    Obtener todas las tareas con los filtros seleccionados por empresa.
    """
    out = empresa
    empresas = models.Empresas.query.all()


    if out == "Fofimatic S.A.S":
        tareas = models.Tareas.query.filter(
        models.Tareas.estado == 'COMPLETADOS'
                                    ).all()
        proyectos = models.Proyecto.query.all()
        usuarios = models.Usuarios.query.all()
            
    else:
        tareas = models.Tareas.query.filter(models.Tareas.empresa == out,
                                            models.Tareas.estado == 'COMPLETADOS').all()
        proyectos = models.Proyecto.query.filter(models.Proyecto.empresa == out).all()
        usuarios = models.Usuarios.query.all()

    if request.method == 'POST':
        out = session.get('empresa', 'Fofimatic S.A.S')

        # Obtener la consulta base de tareas, proyectos y usuarios según la empresa
        if out == "Fofimatic S.A.S":
            tareas_query = models.Tareas.query.filter(models.Tareas.estado == 'COMPLETADOS')
            proyectos = models.Proyecto.query.all()
            usuarios = models.Usuarios.query.all()
        else:
            tareas_query = models.Tareas.query.filter(models.Tareas.empresa == out, 
                                                    models.Tareas.estado == 'COMPLETADOS')
            proyectos = models.Proyecto.query.filter(models.Proyecto.empresa == out).all()
            usuarios = models.Usuarios.query.all()

        # Filtro por estado
        estado = request.form.get('estado')
        if estado:
            tareas_query = tareas_query.filter(models.Tareas.estado == estado)

        # Filtro por responsable
        responsable = request.form.get('responsable')
        if responsable:
            tareas_query = tareas_query.filter(models.Tareas.responsable == responsable)

        # Filtro por proyecto
        proyecto = request.form.get('proyecto_')
        if proyecto:
            tareas_query = tareas_query.filter(models.Tareas.codigo_proyecto == proyecto)

        # Filtro por mes
        mes = request.form.get('mes')
        if mes:
            tareas_query = tareas_query.filter(models.Tareas.mes == mes)

        # Filtro por empresa
        empresa_filter = request.form.get('empresa_')
        if empresa_filter:
            tareas_query = tareas_query.filter(models.Tareas.empresa == empresa_filter)

        # Filtro por fecha de inicio y fecha de fin
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            tareas_query = tareas_query.filter(models.Tareas.fecha_inicio >= fecha_inicio, 
                                            models.Tareas.fecha_fin <= fecha_fin)

        # Obtener el resultado final de las tareas filtradas
        tareas = tareas_query.all()


            
        

    # Calcular las horas estimadas y de ejecución
    #total_horas_estimadas = sum(tarea.horas_estimadas for tarea in tareas)
    total_horas_ejecucion = sum((tarea.horas_dedicadas or 0) for tarea in tareas)
    

    return render_template("Reporte de horas.html",
                           tareas=tareas,
                           proyectos=proyectos,
                           usuarios=usuarios,
                           empresas = empresas,
                           total_horas_ejecucion=total_horas_ejecucion)
                                                    
#Descarga del excel reporte → /Reporte-HorasDownloadFofimatic S.A
@app.route('/Reporte-HorasDownload<empresa>', methods=['GET', 'POST'])
@login_required
def descargar_reporte_excel(empresa):
    """
    Funcion remplazada por un js que descarga el reporte de horas en formato Excel. en el archivo html Reporte de horas.html
    """
    # Obtener los filtros del formulario
    estado = request.form.get('estado')
    responsable = request.form.get('responsable')
    proyecto = request.form.get('proyecto')
    mes = request.form.get('mes')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Consulta base de las tareas
    if empresa == "Fofimatic S.A.S":
        tareas_query = models.Tareas.query.filter(models.Tareas.estado == 'COMPLETADOS')
    else:
        tareas_query = models.Tareas.query.filter(models.Tareas.empresa == empresa, models.Tareas.estado == 'COMPLETADOS')

    # Aplicar los filtros si existen
    if estado:
        tareas_query = tareas_query.filter(models.Tareas.estado == estado)
    if responsable:
        tareas_query = tareas_query.filter(models.Tareas.responsable == responsable)
    if proyecto:
        tareas_query = tareas_query.filter(models.Tareas.codigo_proyecto == proyecto)
    if mes:
        tareas_query = tareas_query.filter(models.Tareas.mes == mes)
    if fecha_inicio and fecha_fin:
        tareas_query = tareas_query.filter(models.Tareas.fecha_inicio >= fecha_inicio, models.Tareas.fecha_fin <= fecha_fin)

    # Ejecutar la consulta
    tareas = tareas_query.all()

    # Crear la lista de diccionarios con los datos de las tareas
    data = []
    for tarea in tareas:
        data.append({
            'TIPO DE CONSUMO': tarea.tipo_consumo,
            'PROYECTO': tarea.codigo_proyecto,
            'TÍTULO': tarea.titulo,
            'FECHA INICIO': tarea.fecha_inicio,
            'FECHA LIMITE': tarea.fecha_fin,
            'HORAS REGISTRADOS': tarea.horas_dedicadas,
            'MES': tarea.mes,
            'EMPRESA': tarea.empresa
            # Añade otros campos que necesites
        })

    # Crear un DataFrame de pandas con los datos
    reporte = pd.DataFrame(data)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        reporte.to_excel(writer, index=False)

    output.seek(0)

    # Enviar el archivo Excel como respuesta para descarga
    return send_file(output, download_name='reporte_horas.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/download-backup')
@login_required
def download_backup():

    # En modo desktop la DB real está en FOFIGEST_DB_URI (ruta absoluta fuera del exe)
    _db_uri = os.environ.get('FOFIGEST_DB_URI', '')
    if _db_uri.startswith('sqlite:///'):
        DATABASE_PATH = _db_uri[len('sqlite:///'):]
        BACKUP_PATH   = DATABASE_PATH.replace('Empresas.db', 'Empresas_backup.db')
    else:
        DATABASE_PATH = os.path.join(app.root_path, 'instance', 'Empresas.db')
        BACKUP_PATH   = os.path.join(app.root_path, 'instance', 'Empresas_backup.db')

    try:
        # Generar un respaldo de la base de datos
        if os.path.exists(DATABASE_PATH):
            shutil.copy(DATABASE_PATH, BACKUP_PATH)
        else:
            abort(404, description="La base de datos no fue encontrada.")
        
        # Descargar el archivo de respaldo
        return send_file(BACKUP_PATH, as_attachment=True)

    except Exception as e:
        abort(500, description=f"Error al generar el respaldo: {str(e)}")

# Página log
@app.route("/log")  
@login_required
def log():
    import warnings

    # Ignorar advertencias relacionadas con `pd.to_datetime`
    warnings.filterwarnings("ignore", message="Could not infer format")

    try:
        # Leer el archivo de log
        log_df = pd.read_csv('log.log', 
                            sep=r'\s-\s',  # Expresión regular para manejar separadores con espacios
                            header=None,   
                            names=['Fecha', 'Nivel', 'Mensaje'],  # Columnas personalizadas
                            engine='python', 
                            encoding='utf-8',  # Codificación para evitar errores
                            on_bad_lines='skip')  # Ignora líneas mal formadas
        
        # Aplicar el icono de acuerdo al nivel de log en la columna Mensaje
        log_df['Estado'] = log_df.apply(lambda row: """<i class="text-center bi bi-check-circle-fill"></i>""" 
                                        if row['Nivel'] == 'INFO' else 
                                        """<i class="text-center bi bi-x-circle-fill"></i>""" 
                                        if row['Mensaje'] != row['Nivel'] else row['Mensaje'], axis=1)
        
        # Convertir la columna 'Fecha' a formato datetime
        log_df['Fecha'] = pd.to_datetime(log_df['Fecha'], errors='coerce')  # Convierte a NaT las fechas inválidas
        log_df = log_df[log_df['Fecha'] <= datetime.now()]  # Filtra las fechas válidas

    except Exception as e:
        logging.error(f"Error al leer o procesar el archivo log.log: {e}")
        return "Error al procesar el archivo de log"

    # Exportar a HTML, sin escapar los caracteres HTML
    html_content = log_df.to_html(index=False, escape=False, classes='table table-striped table-hover', table_id='logTable')

    # Agregar Bootstrap, DataTables y el script para manejar la tabla
    html_full = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
        <style>
            th {{
                text-align: center;  /* Estilo para centrar los encabezados */
            }}
        </style>
        <title>Log</title>
    </head>
    <body>
        <div class="container mt-5">
            <h2>Log de Eventos</h2>
            {html_content}
        </div>
        
        <!-- Scripts de DataTables y jQuery -->
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('#logTable').DataTable({{
                    "searching": true,   // Habilita la búsqueda en la tabla
                    "paging": true,      // Habilita la paginación
                    "info": true,        // Muestra información de la tabla
                    "ordering": true     // Habilita la opción de ordenar las columnas
                }});
            }});
        </script>
    </body>
    </html>
    """

    logging.info("Archivo HTML con Bootstrap y DataTables generado correctamente.")
    
    # Guardar el HTML en un archivo
    with open('templates/log.html', 'w', encoding='utf-8') as f:
        f.write(html_full)

    return render_template("log.html")

#</__________________________________Vista___________________________________________________>


#<__________________________________licencias_________________________________________________>

@app.route('/licencia/<int:id>', methods=['GET'])
def obtener_licencia(id):
    """
    Obtener una licencia específica por ID.

    Args:
        id (int): ID de la licencia.

    Returns:
        Response: JSON con los datos de la licencia y un código de estado HTTP 200.
    """
    # Buscar la licencia por ID, devuelve 404 si no existe
    licencia_ = models.Licencias.query.get_or_404(id)
    
    # Retornar la licencia serializada en formato JSON
    return jsonify(licencia_.serialize()), 200
#</__________________________________licencias________________________________________________>


#<__________________________________ Tareas___________________________________________________>
# Tareas 
@app.route('/actualizar_estado_tarea/<int:tarea_id>', methods=['POST'])
def actualizar_estado_tarea(tarea_id):
    data = request.get_json()
    nuevo_estado = data.get('nuevo_estado')

    # Obtener la tarea por ID
    tarea = models.Tareas.query.get_or_404(tarea_id)

    # Bloquear modificación por regla de facturación
    bloqueada, resp = _check_tarea_bloqueada(tarea)
    if bloqueada:
        return resp

    # Validar que el nuevo estado es válido
    if nuevo_estado not in ['PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS']:
        return jsonify({'message': 'Estado inválido'}), 400

    # Actualizar el estado de la tarea
    estado_anterior = tarea.estado
    tarea.estado = nuevo_estado

    # Guardar cambios en la base de datos
    try:
        models.db.session.commit()
        registrar_trazabilidad(tarea.codigo_tarea, 'CAMBIO_ESTADO',
                               [{'campo': 'estado', 'anterior': estado_anterior, 'nuevo': nuevo_estado}])
        return jsonify({'message': 'Estado actualizado correctamente'}), 200
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': 'Error al actualizar el estado'}), 500

@app.route('/tareas/json', methods=['GET'])
def obtener_tareas():
    """
    Obtener todas las tareas.
    """
    tareas = models.Tareas.query.all()
    return jsonify([tarea.serialize() for tarea in tareas]), 200

@app.route('/tareas/<int:id>', methods=['GET'])
def obtener_tarea(id):
    """
    Obtener una tarea específica por ID.
    """
    tarea = models.Tareas.query.get_or_404(id)
    return jsonify(tarea.serialize()), 200

@app.route('/outtareas', methods=['POST'])
def crear_tarea():
    """
    Crear una nueva tarea.
    Se espera un JSON con los siguientes campos:
    - empresa, codigo_proyecto, codigo_tarea, titulo, descripcion, 
      fecha_inicio, responsable, horas_estimadas, estado (opcional), fecha_fin (opcional), fecha_facturacion (opcional)
    """
    data = request.get_json()

    nueva_tarea = models.Tareas(
        empresa=data['empresa'],
        codigo_proyecto=data['codigo_proyecto'],
        codigo_tarea=data['codigo_tarea'],
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        detalles_editor=data['detalles_editor'],
        
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d'),
        responsable=data['responsable'],
        horas_estimadas=data['horas_estimadas'],
        horas_dedicadas=data['horas_dedicadas'],
        estado=data.get('estado', 'PENDIENTE'),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d') if 'fecha_fin' in data else None,
        fecha_facturacion=datetime.strptime(data['fecha_facturacion'], '%Y-%m-%d') if 'fecha_facturacion' in data else None,
        mes=data['mes']
    )

    models.db.session.add(nueva_tarea)
    models.db.session.commit()
    registrar_trazabilidad(nueva_tarea.codigo_tarea, 'CREACIÓN')
    return jsonify(nueva_tarea.serialize()), 201

@app.route('/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    """
    Actualizar una tarea existente por ID.
    Se espera un JSON con los campos que se desean actualizar.
    """
    tarea = models.Tareas.query.get_or_404(id)
    bloqueada, resp = _check_tarea_bloqueada(tarea)
    if bloqueada:
        return resp
    data = request.get_json()

    _snap = {
        'empresa': tarea.empresa, 'codigo_proyecto': tarea.codigo_proyecto,
        'codigo_tarea': tarea.codigo_tarea, 'titulo': tarea.titulo,
        'descripcion': tarea.descripcion,
        'detalles_editor': str(tarea.detalles_editor)[:500] if tarea.detalles_editor else None,
        'fecha_inicio': str(tarea.fecha_inicio), 'fecha_fin': str(tarea.fecha_fin),
        'responsable': tarea.responsable, 'horas_dedicadas': tarea.horas_dedicadas,
        'horas_estimadas': tarea.horas_estimadas,
        'fecha_facturacion': str(tarea.fecha_facturacion), 'estado': tarea.estado, 'mes': tarea.mes,
    }

    tarea.empresa = data.get('empresa', tarea.empresa)
    tarea.codigo_proyecto = data.get('codigo_proyecto', tarea.codigo_proyecto)
    tarea.codigo_tarea = data.get('codigo_tarea', tarea.codigo_tarea)
    tarea.titulo = data.get('titulo', tarea.titulo)
    tarea.descripcion = data.get('descripcion', tarea.descripcion)
    tarea.detalles_editor = data.get('detalles_editor')  
    tarea.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d') if 'fecha_inicio' in data else tarea.fecha_inicio
    tarea.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d') if 'fecha_fin' in data else tarea.fecha_fin
    tarea.responsable = data.get('responsable', tarea.responsable)
    tarea.horas_dedicadas = data.get('horas_dedicadas', tarea.horas_dedicadas)
    tarea.horas_estimadas = data.get('horas_estimadas', tarea.horas_estimadas)
    tarea.fecha_facturacion = datetime.strptime(data['fecha_facturacion'], '%Y-%m-%d') if 'fecha_facturacion' in data else tarea.fecha_facturacion
    tarea.estado = data.get('estado', tarea.estado)
    tarea.mes = data.get('mes', tarea.mes)

    models.db.session.commit()
    _snap_new = {
        'empresa': tarea.empresa, 'codigo_proyecto': tarea.codigo_proyecto,
        'codigo_tarea': tarea.codigo_tarea, 'titulo': tarea.titulo,
        'descripcion': tarea.descripcion,
        'detalles_editor': str(tarea.detalles_editor)[:500] if tarea.detalles_editor else None,
        'fecha_inicio': str(tarea.fecha_inicio), 'fecha_fin': str(tarea.fecha_fin),
        'responsable': tarea.responsable, 'horas_dedicadas': tarea.horas_dedicadas,
        'horas_estimadas': tarea.horas_estimadas,
        'fecha_facturacion': str(tarea.fecha_facturacion), 'estado': tarea.estado, 'mes': tarea.mes,
    }
    _campos_mod = [{'campo': k, 'anterior': _snap[k], 'nuevo': _snap_new[k]}
                   for k in _snap if str(_snap[k]) != str(_snap_new[k])]
    if _campos_mod:
        _solo_estado = (len(_campos_mod) == 1 and _campos_mod[0]['campo'] == 'estado')
        registrar_trazabilidad(tarea.codigo_tarea, 'CAMBIO_ESTADO' if _solo_estado else 'MODIFICACIÓN', _campos_mod)
    return jsonify(tarea.serialize()), 200

@app.route('/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    """
    Eliminar una tarea por su ID.
    """
    tarea = models.Tareas.query.get_or_404(id)
    bloqueada, resp = _check_tarea_bloqueada(tarea)
    if bloqueada:
        return resp
    registrar_trazabilidad(tarea.codigo_tarea, 'ELIMINACIÓN')
    models.db.session.delete(tarea)
    models.db.session.commit()
    return jsonify({'message': 'Tarea eliminada correctamente'}), 200

# Actualizar estado
@app.route('/tareas/<int:id>/estado', methods=['PUT'])
def actualizar_estado(id):
    """
    Actualizar el estado de una tarea existente por ID.
    Se espera un JSON con el campo 'estado'.
    """
    tarea = models.Tareas.query.get_or_404(id)
    bloqueada, resp = _check_tarea_bloqueada(tarea)
    if bloqueada:
        return resp
    data = request.get_json()

    if 'estado' not in data:
        return jsonify({'error': 'El campo estado es requerido'}), 400

    estado_anterior = tarea.estado
    tarea.estado = data['estado']

    models.db.session.commit()
    registrar_trazabilidad(tarea.codigo_tarea, 'CAMBIO_ESTADO',
                           [{'campo': 'estado', 'anterior': estado_anterior, 'nuevo': data['estado']}])
    return jsonify(tarea.serialize()), 200

@app.route('/b/api/tareas', methods=['GET'])
def obtener_tareasapi():
    """
    Endpoint para obtener las tareas filtradas por palabra clave, fecha de inicio, fecha de fin y estado.

    Parámetros de consulta (query parameters):
    - clave_busqueda: Palabra clave para buscar en el título o la descripción.
    - fecha_inicio: Fecha mínima de inicio de las tareas (formato 'YYYY-MM-DD').
    - fecha_fin: Fecha máxima de finalización de las tareas (formato 'YYYY-MM-DD').
    - estado: Estado de la tarea (PENDIENTE, PROGRESO, REVISIÓN, IMPEDIMENTOS, COMPLETADOS).

    :return: Lista de tareas que cumplen los criterios de búsqueda en formato JSON.
    """

    # Obtener parámetros de la URL
    clave_busqueda = request.args.get('clave_busqueda', default='', type=str)
    fecha_inicio = request.args.get('fecha_inicio', type=str)
    fecha_fin = request.args.get('fecha_fin', type=str)
    estado = request.args.get('estado', type=str)

    # Base de la consulta
    query = models.db.session.query(models.Tareas).filter(
        or_(
            models.Tareas.titulo.ilike(f'%{clave_busqueda}%'),
            models.Tareas.descripcion.ilike(f'%{clave_busqueda}%')
        )
    )

    # Filtrar por fecha de inicio si se proporciona
    if fecha_inicio:
        query = query.filter(models.Tareas.fecha_inicio >= fecha_inicio)
    
    # Filtrar por fecha de fin si se proporciona
    if fecha_fin:
        query = query.filter(models.Tareas.fecha_fin <= fecha_fin)
    
    # Filtrar por estado si se proporciona
    if estado:
        query = query.filter(models.Tareas.estado == estado)

    # Ejecutar la consulta y obtener los resultados
    tareas = query.all()

    # Convertir el resultado a JSON
    resultado = [
        {
            'id': tarea.id,
            'codigo_proyecto': tarea.codigo_proyecto,
            'codigo_tarea': tarea.codigo_tarea,
            'titulo': tarea.titulo,
            'descripcion': tarea.descripcion,
            'empresa': tarea.empresa,
            'responsable': tarea.responsable,
            'horas_dedicadas': tarea.horas_dedicadas,
            'horas_estimadas': tarea.horas_estimadas,
            'fecha_inicio': tarea.fecha_inicio.isoformat(),
            'fecha_fin': tarea.fecha_fin.isoformat() if tarea.fecha_fin else None,
            'fecha_facturacion': tarea.fecha_facturacion.isoformat() if tarea.fecha_facturacion else None,
            'estado': tarea.estado
        }
        for tarea in tareas
    ]

    # Devolver la respuesta en formato JSON
    return jsonify(resultado)

#</__________________________________ Tareas___________________________________________________>

#<__________________________________Empresas___________________________________________________>
# Definición de una ruta GET para obtener todas las empresas.
@app.route("/json/empresas", methods=['GET'])
def get_empresas():
    """
    Endpoint para obtener todas las empresas almacenadas en la base de datos.
    Realiza una consulta a la tabla 'Empresas' y retorna un listado en formato JSON.
    """
    empresas = models.Empresas.query.all()  # Consulta todas las filas de la tabla Empresas
    # Serializa la lista de empresas y la devuelve en formato JSON
    return jsonify({'Empresas': [empresa.serialize() for empresa in empresas]})

# Definición de una ruta GET para obtener una empresa específica por su ID.
@app.route('/json/empresa/<int:id>', methods=['GET'])
def obtener_empresa(id):
    empresa = models.Empresas.query.get(id)
    
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404

    return jsonify(empresa.serialize()), 200

# Definición de una ruta POST para crear una nueva empresa.
@app.route("/empresas", methods=['POST'])
def create_empresa():
    """
    Endpoint para crear una nueva empresa en la base de datos.
    Requiere un cuerpo de solicitud en formato JSON con los campos 'nit' y 'empresa'.
    
    :return: Un mensaje de éxito o error dependiendo del resultado de la operación.
    """
    # Obtener los datos enviados en la solicitud en formato JSON
    data = request.get_json()

    # Validación de los campos necesarios.
    # Buenas prácticas: validamos la presencia de datos requeridos antes de procesarlos.
    if not data or not 'nit' in data or not 'empresa' in data:
        return jsonify({'message': 'Datos faltantes o incompletos'}), 400

    # Crear una nueva instancia del modelo Empresas con los datos proporcionados
    nueva_empresa = models.Empresas(
        nit=data['nit'],
        empresa=data['empresa']
    )

    # Intentar agregar la nueva empresa a la base de datos y confirmar la transacción
    try:
        models.db.session.add(nueva_empresa)  # Agregar la nueva empresa a la sesión de la base de datos
        models.db.session.commit()  # Confirmar los cambios en la base de datos
        # Retornar un mensaje de éxito junto con los datos de la nueva empresa
        return jsonify({'message': 'Empresa creada exitosamente', 'empresa': nueva_empresa.serialize()}), 201
    except Exception as e:
        # Si ocurre un error, revertimos la transacción
        models.db.session.rollback()
        # Devolvemos un mensaje de error y el detalle del error
        return jsonify({'message': 'Error al crear la empresa', 'error': str(e)}), 500
  
# Definición de una ruta PUT para actualizar una empresa.
@app.route('/json/empresas/<int:id>', methods=['PUT'])
def actualizar_empresa(id):
    empresa = models.Empresas.query.get(id)
    
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404

    datos = request.get_json()

    if 'nit' in datos:
        empresa.nit = datos['nit']
    if 'empresa' in datos:
        empresa.empresa = datos['empresa']

    try:
        models.db.session.commit()
        return jsonify({'message': 'Empresa actualizada exitosamente', 'empresa': empresa.serialize()}), 200
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': f'Error al actualizar la empresa: {str(e)}'}), 500

# Definición de una ruta DELETE para eliminar una empresa por su ID.
@app.route('/empresas/<int:id>', methods=['DELETE'])
def delete_empresa(id):
    empresa = models.Empresas.query.get(id)
    
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404
    
    try:
        models.db.session.delete(empresa)
        models.db.session.commit()
        return jsonify({'message': f'Empresa con ID {id} eliminada exitosamente'}), 200
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': f'Error al eliminar la empresa: {str(e)}'}), 500

#</__________________________________Empresas___________________________________________________>

#<__________________________________proyectos___________________________________________________>

# Crear un nuevo proyecto (Create)aa
@app.route('/json/proyectos', methods=['POST'])
def create_proyecto():
    """
    Endpoint para crear un nuevo proyecto.
    Requiere un cuerpo de solicitud en formato JSON con los campos:
    'empresa', 'codigo_proyecto', 'nombre_proyecto', 'descripcion_proyecto'.
    """
    data = request.get_json()

    # Validar que los datos requeridos están presentes
    if not data or not 'empresa' in data or not 'codigo_proyecto' in data or not 'nombre_proyecto' in data or not 'descripcion_proyecto' in data:
        return jsonify({'message': 'Datos faltantes o incompletos'}), 400

    # Crear un nuevo proyecto con los datos proporcionados
    nuevo_proyecto = models.Proyecto(
        empresa=data['empresa'],
        codigo_proyecto=data['codigo_proyecto'],
        nombre_proyecto=data['nombre_proyecto'],
        descripcion_proyecto=data['descripcion_proyecto']
    )

    # Agregar el nuevo proyecto a la base de datos
    try:
        models.db.session.add(nuevo_proyecto)
        models.db.session.commit()
        return jsonify({'message': 'Proyecto creado exitosamente', 'proyecto': nuevo_proyecto.serialize()}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': 'Error al crear el proyecto', 'error': str(e)}), 500

# Leer todos los proyectos (Read)
@app.route('/json/proyectos', methods=['GET'])
def get_proyectos():
    """
    Endpoint para obtener la lista de todos los proyectos.
    Retorna todos los proyectos en formato JSON.
    """
    proyectos =  models.Proyecto.query.all()
    return jsonify({'Proyectos': [proyecto.serialize() for proyecto in proyectos]})

# Leer un proyecto específico por su código (Read by codigo_proyecto)
@app.route('/proyectos/<string:codigo_proyecto>', methods=['GET'])
def get_proyecto(codigo_proyecto):
    """
    Endpoint para obtener un proyecto específico a partir de su código de proyecto.
    """
    proyecto = models.Proyecto.query.filter_by(codigo_proyecto=codigo_proyecto).first()
    if proyecto:
        return jsonify(proyecto.serialize())
    else:
        return jsonify({'message': 'Proyecto no encontrado'}), 404

# Actualizar un proyecto (Update)
@app.route('/proyectos/<string:codigo_proyecto>', methods=['PUT'])
def update_proyecto(codigo_proyecto):
    """
    Endpoint para actualizar un proyecto existente.
    Se debe proporcionar el 'codigo_proyecto' en la URL y un cuerpo JSON con los campos actualizables.
    """
    data = request.get_json()
    proyecto =  models.Proyecto.query.filter_by(codigo_proyecto=codigo_proyecto).first()

    if not proyecto:
        return jsonify({'message': 'Proyecto no encontrado'}), 404

    # Actualizar los campos del proyecto si están presentes en el cuerpo de la solicitud
    if 'empresa' in data:
        proyecto.empresa = data['empresa']
    if 'nombre_proyecto' in data:
        proyecto.nombre_proyecto = data['nombre_proyecto']
    if 'descripcion_proyecto' in data:
        proyecto.descripcion_proyecto = data['descripcion_proyecto']

    try:
        models.db.session.commit()
        return jsonify({'message': 'Proyecto actualizado exitosamente', 'proyecto': proyecto.serialize()})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': 'Error al actualizar el proyecto', 'error': str(e)}), 500

# Eliminar un proyecto (Delete)
@app.route('/proyectos/<string:codigo_proyecto>', methods=['DELETE'])
def delete_proyecto(codigo_proyecto):
    """
    Endpoint para eliminar un proyecto a partir de su 'codigo_proyecto'.
    """
    try:
        # Buscar el proyecto por 'codigo_proyecto'
        proyecto = models.Proyecto.query.filter_by(codigo_proyecto=codigo_proyecto).first()

        if not proyecto:
            return jsonify({'message': 'Proyecto no encontrado'}), 404

        # Eliminar el proyecto
        models.db.session.delete(proyecto)
        models.db.session.commit()

        return jsonify({'message': 'Proyecto eliminado exitosamente'}), 200

    except Exception as e:
        # En caso de error, se hace un rollback y se devuelve el error
        models.db.session.rollback()
        return jsonify({'message': 'Error al eliminar el proyecto', 'error': str(e)}), 500
#</__________________________________proyecto___________________________________________________>

#<__________________________________usuarios___________________________________________________>

@app.route('/usuario', methods=['POST'])
def crear_usuario():
    try:
        data = models.Usuarios(
            nombres=request.json['nombres'],
            apellidos=request.json['apellidos'],
            correo=request.json['correo'],
            contraseña=request.json['contraseña'],
            empresa=request.json['empresa'],
            permisos=request.json['permisos']
        )
        models.db.session.add(data)
        models.db.session.commit()
        return jsonify(data.serialize()), 201
    except IntegrityError:
        models.db.session.rollback()
        return jsonify({"error": "El correo ya existe."}), 400
    
@app.route('/usuario/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = models.Usuarios.query.get(id)
    if usuario:
        return jsonify(usuario.serialize())
    else:
        return jsonify({"error": "Usuario no encontrado."}), 404
    
@app.route('/usuarios/json', methods=['GET'])
def obtener_usuarios():
    usuarios = models.Usuarios.query.all()
    return jsonify([usuario.serialize() for usuario in usuarios])

@app.route('/usuario/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    usuario = models.Usuarios.query.get(id)
    if usuario:
        usuario.nombres = request.json['nombres']
        usuario.apellidos = request.json['apellidos']
        usuario.correo = request.json['correo']
        usuario.contraseña = request.json['contraseña']
        usuario.empresa = request.json['empresa']
        usuario.permisos = request.json['permisos']
        models.db.session.commit()
        return jsonify(usuario.serialize())
    else:
        return jsonify({"error": "Usuario no encontrado."}), 404
    
@app.route('/usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = models.Usuarios.query.get(id)
    if usuario:
        models.db.session.delete(usuario)
        models.db.session.commit()
        return jsonify({"message": "Usuario eliminado."})
    else:
        return jsonify({"error": "Usuario no encontrado."}), 404


#</__________________________________usuarios___________________________________________________>


def auto_crear_tarea():

    """
    Crear una nueva tarea a partir de los datos de un archivo Excel.
    """
    import pandas as pd
    import time

    df = pd.read_excel("Task_Fofigest.xlsx")
    
    for i in range(len(df)):
        print("-----------------------------------------------------------")
        print("Ingresando datos: ", i)
       
        nueva_tarea = models.Tareas(
            empresa="SULFOQUIMICA SA",
            codigo_proyecto=df.iloc[i]['codigo_proyecto'],
            codigo_tarea=df.iloc[i]['codigo_tarea'],
            titulo=df.iloc[i]['titulo'],
            descripcion=df.iloc[i]['descripcion'],
            fecha_inicio=datetime.strptime(df.iloc[i]['fecha_inicio'], '%Y-%m-%d'),
            responsable=df.iloc[i]['responsable'],
            horas_estimadas=df.iloc[i]['horas_estimadas'],
            estado=df.iloc[i]['estado'],
            fecha_fin=datetime.strptime(df.iloc[i]['fecha_fin'], '%Y-%m-%d') if not pd.isna(df.iloc[i]['fecha_fin']) else None,
            fecha_facturacion=datetime.strptime(df.iloc[i]['fecha_facturacion'], '%Y-%m-%d') if not pd.isna(df.iloc[i]['fecha_facturacion']) else None,
            mes=df.iloc[i]['mes']
        )
        
        models.db.session.add(nueva_tarea)
        time.sleep(2)  # Espera de 2 segundos
        models.db.session.commit()
        time.sleep(2)  # Espera de 2 segundos
        
        print("Tarea creada para el registro: ", i)
        print("-----------------------------------------------------------")
    
    # Respuesta final después de crear todas las tareas
    return jsonify({"message": "Todas las tareas han sido creadas exitosamente"}), 201

@app.route('/auto_crear_tarea', methods=['POST'])
def ejecutar_auto_crear_tarea():
    return auto_crear_tarea()


# ── DASHBOARD GENERAL DE PROYECTOS ──────────────────────────────────────────

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    permisos = session.get('username')
    empresa_usuario = session.get('empresa')

    if permisos == 'usuario':
        tareas = models.Tareas.query.filter_by(empresa=empresa_usuario).all()
        proyectos = models.Proyecto.query.filter_by(empresa=empresa_usuario).all()
    else:
        tareas = models.Tareas.query.all()
        proyectos = models.Proyecto.query.all()

    empresas_rows = models.db.session.query(models.Tareas.empresa).distinct().all()
    empresas = sorted({r[0] for r in empresas_rows if r[0]})

    estados_enum = ['PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS']
    meses_enum = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    tipo_consumo_enum = ['Desarrollo', 'Reuniones', 'Desarrollo por control de cambio',
                         'Soporte', 'Oportunidad de mejora']

    return render_template('dashboard.html',
                           tareas=tareas,
                           proyectos=proyectos,
                           empresas=empresas,
                           estados_enum=estados_enum,
                           meses_enum=meses_enum,
                           tipo_consumo_enum=tipo_consumo_enum)


@app.route('/dashboard/tarea/<int:id>', methods=['PUT'])
@login_required
def dashboard_actualizar_tarea(id):
    tarea = models.Tareas.query.filter_by(id=id).first()
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    bloqueada, resp = _check_tarea_bloqueada(tarea)
    if bloqueada:
        return resp

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 422

    campos_texto = ['titulo', 'descripcion', 'responsable', 'estado', 'mes', 'tipo_consumo']
    campos_numero = ['horas_dedicadas', 'horas_estimadas']
    campos_fecha = ['fecha_inicio', 'fecha_fin', 'fecha_facturacion']

    for campo in campos_texto:
        if campo in data:
            setattr(tarea, campo, data[campo])

    for campo in campos_numero:
        if campo in data and data[campo] is not None:
            try:
                setattr(tarea, campo, float(data[campo]))
            except (ValueError, TypeError):
                return jsonify({'error': f'Valor numérico inválido para {campo}'}), 422

    for campo in campos_fecha:
        if campo in data:
            valor = data[campo]
            if valor:
                try:
                    valor = datetime.strptime(valor, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': f'Formato de fecha inválido para {campo}'}), 422
            else:
                valor = None
            setattr(tarea, campo, valor)

    try:
        models.db.session.commit()
        return jsonify(tarea.serialize()), 200
    except Exception as e:
        models.db.session.rollback()
        logging.error(f"Error actualizando tarea {id}: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


# ════════════════════════════════════════════════════════════════════════════
# MÓDULO CUENTA DE COBROS
# ════════════════════════════════════════════════════════════════════════════

MESES_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
            'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
EXTENSIONES_COLILLA = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_COLILLA_BYTES = 5 * 1024 * 1024  # 5 MB


def _correo_usuario(usuario_id):
    u = models.Usuarios.query.get(usuario_id)
    return u.correo if u else None


def _nombre_usuario(usuario_id):
    u = models.Usuarios.query.get(usuario_id)
    return f"{u.nombres} {u.apellidos}" if u else 'Usuario'


def _generar_numero_cuenta(anio):
    ultimo = models.CuentaCobro.query.filter(
        models.CuentaCobro.numero_cuenta.like(f'CC-{anio}-%')
    ).order_by(models.CuentaCobro.id.desc()).first()
    if ultimo:
        try:
            n = int(ultimo.numero_cuenta.split('-')[-1]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f'CC-{anio}-{n:03d}'


def _enviar_email_nueva_cuenta(cuenta):
    try:
        admin_email = config.config['EMAIL']
        detalles = cuenta.detalles
        total_horas = sum(d.horas_dedicadas for d in detalles)
        items_html = ''.join(
            f'<li>{d.titulo_tarea} ({d.codigo_tarea}) — {d.horas_dedicadas}h × '
            f'${float(d.precio_hora):,.0f} = ${float(d.subtotal):,.0f}</li>'
            for d in detalles
        )
        msg = Message(
            subject=f'Nueva cuenta de cobro #{cuenta.numero_cuenta} de {_nombre_usuario(cuenta.usuario_id)}',
            recipients=[admin_email]
        )
        msg.html = f"""
        <h2 style="color:#4e73df">Nueva Cuenta de Cobro</h2>
        <p><strong>N°:</strong> {cuenta.numero_cuenta}</p>
        <p><strong>Trabajador:</strong> {_nombre_usuario(cuenta.usuario_id)}</p>
        <p><strong>Período:</strong> {cuenta.mes} {cuenta.anio}</p>
        <p><strong>Empresa:</strong> {cuenta.empresa_pagadora}</p>
        <p><strong>Total horas:</strong> {total_horas}h</p>
        <p><strong>Valor total:</strong> ${float(cuenta.valor_total):,.0f} COP</p>
        <p><strong>Tareas incluidas:</strong></p><ul>{items_html}</ul>
        <p><a href="{host}admin/cuenta-cobro/{cuenta.id}" style="background:#4e73df;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;">
            Ver en Fofigest
        </a></p>"""
        mail.send(msg)
    except Exception as e:
        logging.error(f'Error enviando email nueva cuenta: {e}')


def _enviar_email_pago_procesado(cuenta, token):
    try:
        correo = _correo_usuario(cuenta.usuario_id)
        if not correo:
            return
        perfil = models.PerfilPago.query.filter_by(usuario_id=cuenta.usuario_id).first()
        datos_banco = ''
        if perfil:
            datos_banco = (f'<p>El pago se realizará en cuenta {perfil.tipo_cuenta} '
                           f'N° {perfil.numero_cuenta} del banco {perfil.banco} '
                           f'a nombre de {perfil.nombres_completos}.</p>')
        enlace = f'{host}confirmar-pago/{token}'
        msg = Message(
            subject=f'Tu pago ha sido procesado — Cuenta #{cuenta.numero_cuenta}',
            recipients=[correo]
        )
        msg.html = f"""
        <h2 style="color:#1cc88a">Pago Procesado</h2>
        <p>Hola {_nombre_usuario(cuenta.usuario_id)},</p>
        <p>Tu cuenta de cobro <strong>{cuenta.numero_cuenta}</strong> ha sido marcada como PAGADA.</p>
        <p><strong>Empresa:</strong> {cuenta.empresa_pagadora}</p>
        <p><strong>Período:</strong> {cuenta.mes} {cuenta.anio}</p>
        <p><strong>Valor:</strong> ${float(cuenta.valor_total):,.0f} COP</p>
        {datos_banco}
        <p>Por favor confirma que recibiste el pago haciendo clic en el siguiente enlace
        (es de un solo uso):</p>
        <p><a href="{enlace}" style="background:#1cc88a;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;">
            Confirmar / Reportar inconveniente
        </a></p>
        <p style="font-size:.85rem;color:#858796">Si tienes algún inconveniente, puedes reportarlo desde el mismo enlace.</p>"""
        mail.send(msg)
    except Exception as e:
        logging.error(f'Error enviando email pago procesado: {e}')


def _enviar_email_confirmacion_admin(cuenta, tipo, inconveniente=None):
    try:
        admin_email = config.config['EMAIL']
        nombre = _nombre_usuario(cuenta.usuario_id)
        if tipo == 'confirmado':
            asunto = f'Pago confirmado ✓ — #{cuenta.numero_cuenta}'
            cuerpo = f'<p>{nombre} confirmó que recibió el pago de la cuenta {cuenta.numero_cuenta}.</p>'
        else:
            asunto = f'Inconveniente reportado — #{cuenta.numero_cuenta}'
            cuerpo = (f'<p>{nombre} reportó un inconveniente en la cuenta {cuenta.numero_cuenta}:</p>'
                      f'<blockquote>{inconveniente}</blockquote>')
        msg = Message(subject=asunto, recipients=[admin_email])
        msg.html = f"""
        <h2 style="color:#4e73df">Fofigest — Cuenta de Cobro</h2>
        {cuerpo}
        <p><a href="{host}admin/cuenta-cobro/{cuenta.id}" style="background:#4e73df;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;">
            Ver detalle
        </a></p>"""
        mail.send(msg)
    except Exception as e:
        logging.error(f'Error enviando email confirmación admin: {e}')


# ── 2.1 Perfil de pago ───────────────────────────────────────────────────────

@app.route('/mi-perfil-pago', methods=['GET', 'POST'])
@login_required
def mi_perfil_pago():
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    perfil = models.PerfilPago.query.filter_by(usuario_id=usuario.id).first()

    if request.method == 'POST':
        try:
            if perfil is None:
                perfil = models.PerfilPago(usuario_id=usuario.id)
                models.db.session.add(perfil)
            perfil.nombres_completos = request.form.get('nombres_completos', '').strip()
            perfil.documento = request.form.get('documento', '').strip()
            perfil.tipo_cuenta = request.form.get('tipo_cuenta')
            perfil.banco = request.form.get('banco', '').strip()
            perfil.numero_cuenta = request.form.get('numero_cuenta', '').strip()
            perfil.firma_texto = request.form.get('firma_texto', '').strip() or None
            # firma_imagen se guarda por /api/guardar-firma (canvas JS) — no se sobreescribe aquí
            perfil.fecha_actualizado = datetime.now()
            models.db.session.commit()
            flash('Datos bancarios guardados correctamente.', 'success')
            logging.info(f'Perfil de pago actualizado para usuario {usuario.correo}')
            return redirect(url_for('mi_perfil_pago'))
        except Exception as e:
            models.db.session.rollback()
            logging.error(f'Error guardando perfil de pago: {e}')
            flash('Error al guardar los datos. Intenta de nuevo.', 'danger')

    return render_template('perfil_pago.html', perfil=perfil)


# ── 2.2 Cuentas de cobro (trabajador) ────────────────────────────────────────

@app.route('/mis-cuentas-cobro', methods=['GET'])
@login_required
def mis_cuentas_cobro():
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    cuentas = models.CuentaCobro.query.filter_by(usuario_id=usuario.id)\
        .order_by(models.CuentaCobro.fecha_creacion.desc()).all()
    return render_template('mis_cuentas_cobro.html', cuentas=cuentas)


@app.route('/nueva-cuenta-cobro', methods=['GET'])
@login_required
def nueva_cuenta_cobro_get():
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    perfil = models.PerfilPago.query.filter_by(usuario_id=usuario.id).first()
    if not perfil:
        flash('Debes registrar tus datos bancarios antes de crear una cuenta de cobro.', 'warning')
        return redirect(url_for('mi_perfil_pago'))
    empresas = models.Empresas.query.order_by(models.Empresas.empresa).all()
    anio_actual = datetime.now().year
    return render_template('nueva_cuenta_cobro.html', meses=MESES_ES,
                           perfil=perfil, empresas=empresas, anio_actual=anio_actual)


@app.route('/api/tareas-facturables', methods=['GET'])
@login_required
def tareas_facturables():
    mes = request.args.get('mes', '')
    anio = request.args.get('anio', type=int)
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    empresa = usuario.empresa

    query = models.Tareas.query.filter(
        models.Tareas.responsable == f"{usuario.nombres} {usuario.apellidos}",
        models.Tareas.estado == 'COMPLETADOS',
        models.Tareas.facturada == False
    )
    if mes:
        query = query.filter(models.Tareas.mes == mes)
    if anio:
        query = query.filter(
            models.db.extract('year', models.Tareas.fecha_inicio) == anio
        )

    tareas = query.all()
    resultado = [{
        'id': t.id,
        'codigo_tarea': t.codigo_tarea,
        'titulo': t.titulo,
        'horas_dedicadas': t.horas_dedicadas,
        'empresa': t.empresa,
        'codigo_proyecto': t.codigo_proyecto
    } for t in tareas]
    return jsonify(resultado)


@app.route('/api/guardar-firma', methods=['POST'])
@login_required
def guardar_firma():
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    perfil = models.PerfilPago.query.filter_by(usuario_id=usuario.id).first()
    if not perfil:
        return jsonify({'ok': False, 'error': 'Perfil no encontrado'}), 404
    data = request.get_json(silent=True) or {}
    firma = data.get('firma_imagen', '').strip()
    if firma and not firma.startswith('data:image/'):
        return jsonify({'ok': False, 'error': 'Formato de imagen inválido'}), 422
    perfil.firma_imagen = firma or None
    try:
        models.db.session.commit()
        logging.info(f'Firma guardada para usuario {usuario.correo}')
        return jsonify({'ok': True}), 200
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error guardando firma: {e}')
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/nueva-cuenta-cobro', methods=['POST'])
@login_required
def nueva_cuenta_cobro_post():
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    perfil = models.PerfilPago.query.filter_by(usuario_id=usuario.id).first()
    if not perfil:
        flash('Debes registrar tus datos bancarios primero.', 'warning')
        return redirect(url_for('mi_perfil_pago'))

    empresa_pagadora = request.form.get('empresa_pagadora', '').strip()
    nit_pagadora = request.form.get('nit_pagadora', '').strip()
    mes = request.form.get('mes', '')
    anio = request.form.get('anio', type=int)
    tareas_ids = request.form.getlist('tareas_ids[]')

    if not tareas_ids:
        flash('Debes seleccionar al menos una tarea.', 'danger')
        return redirect(url_for('nueva_cuenta_cobro_get'))

    if not empresa_pagadora or not nit_pagadora or not mes or not anio:
        flash('Completa todos los campos requeridos.', 'danger')
        return redirect(url_for('nueva_cuenta_cobro_get'))

    # Recolectar y validar tareas
    detalles_data = []
    for tid in tareas_ids:
        tarea = models.Tareas.query.get(int(tid))
        if not tarea or tarea.facturada:
            flash(f'La tarea ID {tid} no está disponible para facturar.', 'danger')
            return redirect(url_for('nueva_cuenta_cobro_get'))
        precio_hora_raw = request.form.get(f'precio_hora_{tid}', '0').replace(',', '.')
        try:
            precio_hora = float(precio_hora_raw)
        except ValueError:
            precio_hora = 0
        if precio_hora <= 0 or precio_hora > 10_000_000:
            flash('El precio por hora debe ser mayor a 0 y máximo 10.000.000 COP.', 'danger')
            return redirect(url_for('nueva_cuenta_cobro_get'))
        subtotal = round(tarea.horas_dedicadas * precio_hora, 2)
        detalles_data.append({
            'tarea': tarea,
            'precio_hora': precio_hora,
            'subtotal': subtotal
        })

    valor_total = sum(d['subtotal'] for d in detalles_data)

    # Aviso si ya existe cuenta en ese mes/año
    existe = models.CuentaCobro.query.filter(
        models.CuentaCobro.usuario_id == usuario.id,
        models.CuentaCobro.mes == mes,
        models.CuentaCobro.anio == anio,
        models.CuentaCobro.estado.in_(['PENDIENTE', 'REVISIÓN'])
    ).first()
    if existe:
        flash(f'Ya tienes una cuenta en estado {existe.estado} para {mes} {anio}. Se creará de todas formas.', 'warning')

    try:
        numero_cuenta = _generar_numero_cuenta(anio)
        concepto_items = '; '.join(
            f"{d['tarea'].titulo} ({d['tarea'].codigo_tarea})" for d in detalles_data
        )
        cuenta = models.CuentaCobro(
            numero_cuenta=numero_cuenta,
            usuario_id=usuario.id,
            empresa_pagadora=empresa_pagadora,
            nit_pagadora=nit_pagadora,
            concepto=concepto_items,
            valor_total=valor_total,
            mes=mes,
            anio=anio,
            estado='PENDIENTE'
        )
        models.db.session.add(cuenta)
        models.db.session.flush()

        for d in detalles_data:
            detalle = models.DetalleCuentaCobro(
                cuenta_cobro_id=cuenta.id,
                tarea_id=d['tarea'].id,
                codigo_tarea=d['tarea'].codigo_tarea,
                titulo_tarea=d['tarea'].titulo,
                horas_dedicadas=d['tarea'].horas_dedicadas,
                precio_hora=d['precio_hora'],
                subtotal=d['subtotal']
            )
            models.db.session.add(detalle)
            d['tarea'].facturada = True
            d['tarea'].cuenta_cobro_id = cuenta.id

        models.db.session.commit()
        logging.info(f'Cuenta de cobro {numero_cuenta} creada por {usuario.correo}')
        _enviar_email_nueva_cuenta(cuenta)
        flash(f'Cuenta de cobro {numero_cuenta} creada exitosamente.', 'success')
        return redirect(url_for('mis_cuentas_cobro'))
    except IntegrityError:
        models.db.session.rollback()
        flash('Error: número de cuenta duplicado. Intenta de nuevo.', 'danger')
        return redirect(url_for('nueva_cuenta_cobro_get'))
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error creando cuenta de cobro: {e}')
        flash('Error interno al crear la cuenta de cobro.', 'danger')
        return redirect(url_for('nueva_cuenta_cobro_get'))


@app.route('/cuenta-cobro/<int:id>', methods=['GET'])
@login_required
def detalle_cuenta_cobro(id):
    usuario = models.Usuarios.query.filter_by(correo=session.get('correo')).first_or_404()
    permisos = session.get('username')
    if permisos in ['admin', 'superadmin']:
        cuenta = models.CuentaCobro.query.get_or_404(id)
    else:
        cuenta = models.CuentaCobro.query.filter_by(id=id, usuario_id=usuario.id).first_or_404()
    perfil = models.PerfilPago.query.filter_by(usuario_id=cuenta.usuario_id).first()
    return render_template('detalle_cuenta_cobro.html', cuenta=cuenta, perfil=perfil)


# ── 2.3 Panel admin de cuentas de cobro ──────────────────────────────────────

def _check_admin():
    if session.get('username') not in ['admin', 'superadmin']:
        abort(403)


@app.route('/admin/cuentas-cobro', methods=['GET'])
@login_required
def admin_cuentas_cobro():
    _check_admin()
    estado_f = request.args.get('estado', '')
    mes_f = request.args.get('mes', '')
    anio_f = request.args.get('anio', type=int)
    busqueda = request.args.get('q', '')

    query = models.CuentaCobro.query
    if estado_f:
        query = query.filter(models.CuentaCobro.estado == estado_f)
    if mes_f:
        query = query.filter(models.CuentaCobro.mes == mes_f)
    if anio_f:
        query = query.filter(models.CuentaCobro.anio == anio_f)
    if busqueda:
        ids_match = [u.id for u in models.Usuarios.query.filter(
            or_(models.Usuarios.nombres.ilike(f'%{busqueda}%'),
                models.Usuarios.apellidos.ilike(f'%{busqueda}%'))
        ).all()]
        query = query.filter(models.CuentaCobro.usuario_id.in_(ids_match))

    cuentas = query.order_by(models.CuentaCobro.fecha_creacion.desc()).all()
    return render_template('admin_cuentas_cobro.html',
                           cuentas=cuentas, meses=MESES_ES,
                           estado_f=estado_f, mes_f=mes_f,
                           anio_f=anio_f or '', busqueda=busqueda)


@app.route('/admin/cuenta-cobro/<int:id>', methods=['GET'])
@login_required
def admin_detalle_cuenta_cobro(id):
    _check_admin()
    cuenta = models.CuentaCobro.query.get_or_404(id)
    perfil = models.PerfilPago.query.filter_by(usuario_id=cuenta.usuario_id).first()
    return render_template('admin_detalle_cuenta_cobro.html', cuenta=cuenta, perfil=perfil)


@app.route('/admin/cuenta-cobro/<int:id>/estado', methods=['POST'])
@login_required
def admin_cambiar_estado_cuenta(id):
    _check_admin()
    cuenta = models.CuentaCobro.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    observacion = request.form.get('observacion_admin', '').strip() or None

    estados_validos = ['PENDIENTE', 'REVISIÓN', 'APROBADA', 'PAGADA', 'RECHAZADA']
    if nuevo_estado not in estados_validos:
        flash('Estado inválido.', 'danger')
        return redirect(url_for('admin_detalle_cuenta_cobro', id=id))

    try:
        cuenta.estado = nuevo_estado
        cuenta.observacion_admin = observacion

        if nuevo_estado == 'PAGADA':
            cuenta.fecha_pago = datetime.now()
            token = str(uuid.uuid4())
            confirmacion = models.ConfirmacionPago.query.filter_by(cuenta_cobro_id=cuenta.id).first()
            if confirmacion is None:
                confirmacion = models.ConfirmacionPago(cuenta_cobro_id=cuenta.id)
                models.db.session.add(confirmacion)
            confirmacion.confirmado = False
            confirmacion.token_confirmacion = token
            confirmacion.fecha_confirmacion = None
            models.db.session.commit()
            logging.info(f'Cuenta {cuenta.numero_cuenta} marcada PAGADA por {session.get("correo")}')
            _enviar_email_pago_procesado(cuenta, token)
            flash(f'Estado actualizado a PAGADA. Se envió email de confirmación al trabajador.', 'success')

        elif nuevo_estado == 'RECHAZADA':
            tareas_liberadas = []
            for detalle in cuenta.detalles:
                if detalle.tarea_id:
                    t = models.Tareas.query.get(detalle.tarea_id)
                    if t:
                        t.facturada = False
                        t.cuenta_cobro_id = None
                        tareas_liberadas.append(t.codigo_tarea)
            models.db.session.commit()
            logging.info(
                f'Cuenta {cuenta.numero_cuenta} RECHAZADA por {session.get("correo")}. '
                f'Tareas liberadas: {tareas_liberadas}'
            )
            flash(f'Cuenta rechazada. {len(tareas_liberadas)} tarea(s) liberadas para re-facturación.', 'success')
        else:
            models.db.session.commit()
            flash('Estado actualizado correctamente.', 'success')

    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error cambiando estado cuenta {id}: {e}')
        flash('Error al actualizar el estado.', 'danger')

    return redirect(url_for('admin_detalle_cuenta_cobro', id=id))


@app.route('/admin/cuenta-cobro/<int:id>/colilla', methods=['POST'])
@login_required
def admin_subir_colilla(id):
    _check_admin()
    cuenta = models.CuentaCobro.query.get_or_404(id)
    archivo = request.files.get('colilla')
    if not archivo or archivo.filename == '':
        flash('No se seleccionó ningún archivo.', 'danger')
        return redirect(url_for('admin_detalle_cuenta_cobro', id=id))

    ext = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
    if ext not in EXTENSIONES_COLILLA:
        flash('Extensión no permitida. Use PDF, PNG, JPG o JPEG.', 'danger')
        return redirect(url_for('admin_detalle_cuenta_cobro', id=id))

    archivo.seek(0, 2)
    tamaño = archivo.tell()
    archivo.seek(0)
    if tamaño > MAX_COLILLA_BYTES:
        flash('El archivo supera el límite de 5 MB.', 'danger')
        return redirect(url_for('admin_detalle_cuenta_cobro', id=id))

    try:
        nombre_seguro = secure_filename(archivo.filename)
        nombre_unico = f'{cuenta.numero_cuenta}_{uuid.uuid4().hex[:8]}_{nombre_seguro}'
        ruta = os.path.join(app.root_path, 'static', 'colillas', nombre_unico)
        archivo.save(ruta)
        colilla = models.ColillaPago(
            cuenta_cobro_id=cuenta.id,
            archivo_nombre=nombre_seguro,
            archivo_url=f'/static/colillas/{nombre_unico}',
            subido_por=session.get('correo', 'admin')
        )
        models.db.session.add(colilla)
        models.db.session.commit()
        logging.info(f'Colilla subida para cuenta {cuenta.numero_cuenta} por {session.get("correo")}')
        flash('Colilla subida correctamente.', 'success')
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error subiendo colilla: {e}')
        flash('Error al subir el archivo.', 'danger')

    return redirect(url_for('admin_detalle_cuenta_cobro', id=id))


@app.route('/admin/cuenta-cobro/<int:id>/desbloquear-tarea/<int:tarea_id>', methods=['POST'])
@login_required
def admin_desbloquear_tarea(id, tarea_id):
    _check_admin()
    cuenta = models.CuentaCobro.query.get_or_404(id)
    detalle = models.DetalleCuentaCobro.query.filter_by(
        cuenta_cobro_id=cuenta.id, tarea_id=tarea_id).first_or_404()
    try:
        tarea = models.Tareas.query.get(tarea_id)
        if tarea:
            tarea.facturada = False
            tarea.cuenta_cobro_id = None
        models.db.session.delete(detalle)
        models.db.session.flush()
        cuenta.valor_total = sum(d.subtotal for d in cuenta.detalles)
        models.db.session.commit()
        logging.info(
            f'Tarea {tarea_id} desvinculada de cuenta {cuenta.numero_cuenta} '
            f'por {session.get("correo")}'
        )
        return jsonify({'ok': True, 'nuevo_total': float(cuenta.valor_total)})
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error desvinculando tarea {tarea_id}: {e}')
        return jsonify({'ok': False, 'error': 'Error interno'}), 500


# ── 2.4 Confirmación de pago (pública vía token) ─────────────────────────────

@app.route('/confirmar-pago/<token>', methods=['GET'])
def confirmar_pago_get(token):
    conf = models.ConfirmacionPago.query.filter_by(token_confirmacion=token).first_or_404()
    cuenta = conf.cuenta
    ya_usado = conf.confirmado or conf.inconveniente is not None
    return render_template('confirmar_pago.html', conf=conf, cuenta=cuenta, ya_usado=ya_usado)


@app.route('/confirmar-pago/<token>/aceptar', methods=['POST'])
def confirmar_pago_aceptar(token):
    conf = models.ConfirmacionPago.query.filter_by(token_confirmacion=token).first_or_404()
    if conf.confirmado or conf.inconveniente:
        return redirect(url_for('confirmar_pago_get', token=token))
    try:
        conf.confirmado = True
        conf.fecha_confirmacion = datetime.now()
        models.db.session.commit()
        logging.info(f'Pago confirmado para cuenta {conf.cuenta.numero_cuenta}')
        _enviar_email_confirmacion_admin(conf.cuenta, 'confirmado')
        return render_template('confirmar_pago.html', conf=conf, cuenta=conf.cuenta,
                               ya_usado=True, mensaje='¡Gracias! Confirmación registrada exitosamente.')
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error confirmando pago token {token}: {e}')
        return render_template('confirmar_pago.html', conf=conf, cuenta=conf.cuenta,
                               ya_usado=False, error='Error al procesar la confirmación.')


@app.route('/confirmar-pago/<token>/inconveniente', methods=['POST'])
def confirmar_pago_inconveniente(token):
    conf = models.ConfirmacionPago.query.filter_by(token_confirmacion=token).first_or_404()
    if conf.confirmado or conf.inconveniente:
        return redirect(url_for('confirmar_pago_get', token=token))
    texto = request.form.get('inconveniente', '').strip()
    if not texto:
        return redirect(url_for('confirmar_pago_get', token=token))
    try:
        conf.inconveniente = texto
        conf.fecha_inconveniente = datetime.now()
        conf.cuenta.estado = 'REVISIÓN'
        models.db.session.commit()
        logging.info(f'Inconveniente reportado para cuenta {conf.cuenta.numero_cuenta}')
        _enviar_email_confirmacion_admin(conf.cuenta, 'inconveniente', inconveniente=texto)
        return render_template('confirmar_pago.html', conf=conf, cuenta=conf.cuenta,
                               ya_usado=True, mensaje='Inconveniente reportado. El administrador revisará tu caso.')
    except Exception as e:
        models.db.session.rollback()
        logging.error(f'Error reportando inconveniente token {token}: {e}')
        return render_template('confirmar_pago.html', conf=conf, cuenta=conf.cuenta,
                               ya_usado=False, error='Error al reportar el inconveniente.')


# ──────────────────────────────────────────────────────────
# TRAZABILIDAD — rutas de consulta (solo lectura)
# ──────────────────────────────────────────────────────────

@app.route('/trazabilidad', methods=['GET'])
@login_required
def vista_trazabilidad():
    permisos = session.get('username', '')
    if permisos not in ('admin', 'dev', 'superadmin'):
        abort(403)

    codigo_tarea = request.args.get('codigo_tarea', '').strip()
    accion       = request.args.get('accion', '').strip()
    usuario      = request.args.get('usuario', '').strip()
    desde        = request.args.get('desde', '').strip()
    hasta        = request.args.get('hasta', '').strip()

    q = models.TrazabilidadTarea.query

    if codigo_tarea:
        q = q.filter(models.TrazabilidadTarea.codigo_tarea.ilike(f'%{codigo_tarea}%'))
    if accion:
        q = q.filter(models.TrazabilidadTarea.accion == accion)
    if usuario:
        q = q.filter(models.TrazabilidadTarea.usuario_correo.ilike(f'%{usuario}%'))
    if desde:
        try:
            q = q.filter(models.TrazabilidadTarea.fecha_hora >= datetime.strptime(desde, '%Y-%m-%d'))
        except ValueError:
            pass
    if hasta:
        try:
            q = q.filter(models.TrazabilidadTarea.fecha_hora < datetime.strptime(hasta, '%Y-%m-%d') + timedelta(days=1))
        except ValueError:
            pass

    registros = q.order_by(models.TrazabilidadTarea.fecha_hora.desc()).limit(500).all()

    return render_template('trazabilidad.html',
                           registros=registros,
                           filtros={'codigo_tarea': codigo_tarea, 'accion': accion,
                                    'usuario': usuario, 'desde': desde, 'hasta': hasta})


@app.route('/trazabilidad/<string:codigo_tarea>/json', methods=['GET'])
@login_required
def trazabilidad_tarea_json(codigo_tarea):
    permisos = session.get('username', '')
    if permisos not in ('admin', 'dev', 'superadmin'):
        abort(403)
    registros = (models.TrazabilidadTarea.query
                 .filter_by(codigo_tarea=codigo_tarea)
                 .order_by(models.TrazabilidadTarea.fecha_hora.asc())
                 .all())
    return jsonify([r.serialize() for r in registros]), 200


if __name__ == '__main__':
        # Se obtiene la configuración de debug desde el archivo config.py
        debug = config.config["debug"]
        v=config.config["version"]
        logging.info(f"version del desarrollo {v} ")
    
        if debug:
                logging.info("mode de debug esta True ")
                print("mode de debug esta True ")
                app.run(host="0.0.0.0",debug=debug, port=5000)
                
                  

        else:
                # Inicia el servidor Flask con debug activado (según configuración) en el puerto 5000
                logging.info("mode de debug esta falso , aplicacion en producciion")
                print("mode de debug esta falso , aplicacion en produccion")
                serve(app,host="0.0.0.0", port=5000 , threads=2)
                

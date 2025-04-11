from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify,session, send_file,abort
import os
from models import models  
import config 
from datetime import datetime
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
from werkzeug.security import check_password_hash
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


# Definimos el endpoint principal
host = config.config["host"]

# Configurar el logger
logging.basicConfig(
    filename='log.log',  # Nombre del archivo de log
    level=logging.INFO,  # Nivel de registro (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d',
    encoding='utf-8' # Formato del mensaje
)

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'GDSGODSGFY56D4F8asc8assS6854DCSX85Z13ZXC8478SD94C6XZ1asSDA6F48V4D615SVGZDS4ZV1_65CXZ<3F4'
# Generador de tokens seguros
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuración de la base de datos usando SQLite

debug = config.config["debug"]

if debug:

    # SQLALCHEMY_DATABASE_URI define la ubicación de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Empresas.db'
else:
    # Configuración de la base de datos Supabase
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.wlvgmwuhfunnpddcgvzu:I0P2EdBGUabioCtA@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

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

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return models.Usuarios.query.get(int(user_id))
    

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
    return send_file('sw.js', mimetype='application/javascript')

@app.context_processor
def inject_user():
    return dict(username=session.get('username'))

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

# Reporte gannt 

@app.route('/gannt')
def gannt():
    try:
        hoy = datetime.today()
        hace_tres_meses = hoy - relativedelta(months=3)

        tareas = models.Tareas.query.filter(
            and_(
                models.Tareas.fecha_inicio >= hace_tres_meses,
                models.Tareas.fecha_inicio <= hoy,
                models.Tareas.fecha_inicio.isnot(None),
                models.Tareas.fecha_fin.isnot(None)
            )
        ).all()

        tareas_data = [{
            "id": str(tarea.codigo_proyecto),
            "name": tarea.titulo,
            "start": tarea.fecha_inicio.strftime("%Y-%m-%d") if tarea.fecha_inicio else "2024-01-01",
            "end": tarea.fecha_fin.strftime("%Y-%m-%d") if tarea.fecha_fin else "2024-01-02",   
            "progress": (tarea.horas_dedicadas / tarea.horas_estimadas) * 100 if tarea.horas_estimadas else 0,
            # Descomenta si los necesitas en el frontend:
            # "estado": tarea.estado,
            # "responsable": tarea.responsable,
            # "codigo_proyecto": tarea.codigo_proyecto,
            # "empresa": tarea.empresa
            } for tarea in tareas]

        return render_template('gantt.html', tareas_jsons=tareas_data)
        
    except Exception as e:
        print(f"Error en /gannt: {e}")
        #return render_template('gantt.html', tareas_jsons=[])




    
# login 
@app.route("/")
def login():
    logging.info("Inicio de pagina ")
    return render_template("login.html")

@app.route("/", methods=['POST'])
def loginInp():
    email = request.form.get('exampleInputEmail')
    password = request.form.get('exampleInputPassword')

    # Consultar si el usuario existe
    usuario = models.Usuarios.query.filter_by(correo=email).first()

    if usuario :

        # Si el usuario existe y la contraseña es correcta, iniciar sesión
        login_user(usuario)
        logging.info(f"Inicio de sesión exitoso {email}")
        session['username'] = usuario.permisos
        session['empresa'] = usuario.empresa
        session['correo'] = usuario.correo 

        if  session['username'] == "admin" or session['username'] == "dev" :
            return render_template("splash.html") # Redirigir al tablero
            
        else:   
            return render_template("splash.html") # Redirigir al tablero
          
    else:
        # Si no se encuentra el usuario o la contraseña es incorrecta
        flash("Email o contraseña incorrectos", "danger")
        logging.warning("Email o contraseña incorrectos")
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
    total_horas_ejecucion = sum(tarea.horas_dedicadas for tarea in models.Tareas.query.all())

    # Renderizar la plantilla con los datos obtenidos
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
                           total_horas_ejecucion=total_horas_ejecucion)

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
                contraseña=request.form.get('Contraseña'),
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
                msg.html = """<p>Hola </p>

                               <p> Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en FOFIGEST. Si tú no solicitaste este cambio, puedes ignorar este correo y tu contraseña permanecerá sin cambios.</p>

                               <p> Para restablecer tu contraseña, haz clic en el siguiente enlace o cópialo y pégalo en tu navegador:</p>

                               <p> {reset_url}</p>

                               <p> Este enlace será válido durante 1 hora y solo puede ser utilizado una vez. Si no realizas el restablecimiento en ese tiempo, deberás solicitar otro enlace.</p>

                               <p> Si tienes alguna duda o necesitas asistencia adicional, no dudes en contactarnos respondiendo a este correo.</p>

                               <p> Gracias por utilizar FOFIGEST.</p>

                               <p> Saludos,
                                El equipo de FOFIGESTL</p>"""

                # Enviar el correo
                mail.send(msg)
                flash("Hemos enviado una solicitud para restablecer la contraseña a tu email", "success")
                logging.info("Hemos enviado una solicitud para restablecer la contraseña a tu email ")
                return render_template("Olvide_Contraseña.html") 
            except Exception as e:
                flash(f"Error :{e}", "danger")
                return str(e)

        # Mostrar mensaje de éxito
        
        return 

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        # Verificar el token (con un tiempo de expiración, en este caso 3600 segundos o 1 hora)
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception as e:
        flash('El enlace de restablecimiento es inválido o ha expirado', 'error')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        # Aquí deberías actualizar la contraseña en la base de datos
        flash('Tu contraseña ha sido restablecida con éxito', 'success')
        return redirect(url_for('login'))

    return render_template('reset_with_token.html', token=token)

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
    total_horas_ejecucion = sum(tarea.horas_dedicadas for tarea in tareas)

    return render_template("tareas.html", tareas=tareas,
                                        empresas=empresas,
                                        proyectos=proyectos,
                                        usuarios=usuarios,
                                        total_horas_ejecucion=total_horas_ejecucion)


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
    total_horas_ejecucion = sum(tarea.horas_dedicadas for tarea in tareas)
  
 
    

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

    # Ruta del archivo original de la base de datos
    DATABASE_PATH = os.path.join(app.root_path, 'instance', 'Empresas.db')

    # Ruta temporal para almacenar el respaldo de la base de datos
    BACKUP_PATH = os.path.join(app.root_path, 'instance', 'Empresas_backup.db')

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

    # Validar que el nuevo estado es válido
    if nuevo_estado not in ['PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS']:
        return jsonify({'message': 'Estado inválido'}), 400

    # Actualizar el estado de la tarea
    tarea.estado = nuevo_estado

    # Guardar cambios en la base de datos
    try:
        models.db.session.commit()
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
    return jsonify(nueva_tarea.serialize()), 201


@app.route('/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    """
    Actualizar una tarea existente por ID.
    Se espera un JSON con los campos que se desean actualizar.
    """
    tarea =  models.Tareas.query.get_or_404(id)
    data = request.get_json()

    tarea.empresa = data.get('empresa', tarea.empresa)
    tarea.codigo_proyecto = data.get('codigo_proyecto', tarea.codigo_proyecto)
    tarea.codigo_tarea = data.get('codigo_tarea', tarea.codigo_tarea)
    tarea.titulo = data.get('titulo', tarea.titulo)
    tarea.descripcion = data.get('descripcion', tarea.descripcion)
    tarea.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d') if 'fecha_inicio' in data else tarea.fecha_inicio
    tarea.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d') if 'fecha_fin' in data else tarea.fecha_fin
    tarea.responsable = data.get('responsable', tarea.responsable)
    tarea.horas_dedicadas = data.get('horas_dedicadas', tarea.horas_dedicadas)
    tarea.horas_estimadas = data.get('horas_estimadas', tarea.horas_estimadas)
    tarea.fecha_facturacion = datetime.strptime(data['fecha_facturacion'], '%Y-%m-%d') if 'fecha_facturacion' in data else tarea.fecha_facturacion
    tarea.estado = data.get('estado', tarea.estado)
    tarea.mes = data.get('mes', tarea.mes)

    models.db.session.commit()
    return jsonify(tarea.serialize()), 200

@app.route('/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    """
    Eliminar una tarea por su ID.
    """
    tarea = models.Tareas.query.get_or_404(id)
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
    data = request.get_json()

    if 'estado' not in data:
        return jsonify({'error': 'El campo estado es requerido'}), 400

    tarea.estado = data['estado']

    models.db.session.commit()

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
                


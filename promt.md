analiza este templade de :

```
{% extends 'Base.html' %}

{% block content %}
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" />
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">

<div class="container-fluid bg-light py-5">
    <div class="card p-4 shadow">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-center">TAREAS</h2>
            {% if session['username'] == "admin" %}
            <button type="button" class="btn btn-primary btn-lg d-flex align-items-center" data-bs-toggle="modal" data-bs-target="#tareasform" onclick="limpiarFormulario();generarCodigoUnico()">
                <span class="material-icons-outlined mr-2">add</span>
                <span>Agregar Tarea</span>
            </button>
            {% endif %}
        </div>
        
        <!-- Filtros -->
        <form method="GET" action="/tareas">
            <div class="row mb-4">
                <div class="col-md-3">
                    <label for="estado">Filtrar Estado</label>
                    <select class="form-control" id="estado" name="estado" onchange="this.form.submit();">
                        <option value="" {% if not estado %}selected{% endif %}>Todos los estados</option>
                        <option value="PENDIENTE" {% if estado == "PENDIENTE" %}selected{% endif %}>PENDIENTE</option>
                        <option value="PROGRESO" {% if estado == "PROGRESO" %}selected{% endif %}>PROGRESO</option>
                        <option value="REVISIÓN" {% if estado == "REVISIÓN" %}selected{% endif %}>REVISIÓN</option>
                        <option value="IMPEDIMENTOS" {% if estado == "IMPEDIMENTOS" %}selected{% endif %}>IMPEDIMENTOS</option>
                        <option value="COMPLETADOS" {% if estado == "COMPLETADOS" %}selected{% endif %}>COMPLETADOS</option>
                    </select>
                </div>

                <div class="col-md-3">
                    <label for="responsable">Filtrar Responsables</label>
                    <select class="form-control" id="responsable" name="responsable" onchange="this.form.submit();">
                        <option value="" {% if not responsable %}selected{% endif %}>Todos los responsables</option>
                        {% for usuario in usuarios %}
                        <option value="{{ usuario.nombres }}" {% if responsable == usuario.nombres %}selected{% endif %}>
                            {{ usuario.nombres }} {{ usuario.apellidos }}
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div class="col-md-3">
                    <label for="proyecto">Filtrar Proyecto</label>
                    <select class="form-control" id="proyecto" name="proyecto" onchange="this.form.submit();">
                        <option value="" {% if not proyecto_filtro %}selected{% endif %}>Todos los proyectos</option>
                        {% for proyecto_item in proyectos %}
                        <option value="{{ proyecto_item.codigo_proyecto }}" {% if proyecto_filtro == proyecto_item.codigo_proyecto %}selected{% endif %}>
                            {{ proyecto_item.nombre_proyecto }}
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div class="col-md-3">
                    <label for="empresa">Filtrar Empresa</label>
                    <select class="form-control" id="empresa" name="empresa" onchange="this.form.submit();">
                        <option value="" {% if not empresa_filtro %}selected{% endif %}>Todas las empresas</option>
                        {% for empresa_item in empresas %}
                        <option value="{{ empresa_item.empresa }}" {% if empresa_filtro == empresa_item.empresa %}selected{% endif %}>
                            {{ empresa_item.empresa }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </div>
        </form>

        <!-- Tabla de Tareas -->
        <div class="row">
            <div class="table-responsive">
                <table class="table table-bordered table-striped table-hover" id="dataTable" width="100%" cellspacing="0">
                    <thead class="thead-dark">
                        <tr>
                            <th>ID</th>
                            <th>EMPRESA</th>
                            <th>CODIGO PROYECTO</th>
                            <th>CODIGO TAREA</th>
                            <th>TITULO</th>
                            <th>DESCRIPCION</th>
                            <th>FECHA INICIO</th>
                            <th>FECHA FIN</th>
                            <th>HORAS DEDICADAS</th>
                            <th>HORAS ESTIMADAS</th>
                            <th>FECHA FACTURACION</th>
                            <th>ESTADO</th>
                            <th>RESPONSABLE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for tarea in tareas %}
                        <tr>
                            <td class="position-relative" data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})" onmouseover="showDeleteIcon({{ tarea.id }})" onmouseout="hideDeleteIcon({{ tarea.id }})">
                                {{ tarea.id }}
                                <span class="delete-icon material-icons-outlined position-absolute text-danger" id="delete-icon-{{ tarea.id }}" style="display: none; right: 5px; cursor: pointer;" onclick="event.stopPropagation(); eliminarTarea({{ tarea.id }})">delete</span>
                            </td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.empresa }}</td>                               
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.codigo_proyecto }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.codigo_tarea }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.titulo }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.descripcion }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_inicio }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_fin }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.horas_dedicadas }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.horas_estimadas }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_facturacion }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.estado }}</td>
                            <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.responsable }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Modal para Crear/Editar Tareas -->
<div class="modal fade modal-fullscreen-xxl-down" id="tareasform" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Registrar tarea</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <!-- Formulario para Crear/Editar tareas -->
                <form id="formTarea" method="POST">
                    <input type="hidden" id="tareaId" name="tareaId" />

                    <div class="form-group">
                        <label for="Empresa">Empresa</label>
                        <select class="form-control" id="empresa" name="empresa" required>
                            <option value="" disabled selected>Selecciona la empresa</option>
                            {% for empresa_item in empresas %}
                            <option value="{{ empresa_item.empresa }}">{{ empresa_item.empresa }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="Proyecto">Proyecto</label>
                        <select class="form-control" id="codigo_proyecto" name="codigo_proyecto" required>
                            <option value="" disabled selected>Selecciona el proyecto</option>
                            {% for proyecto_item in proyectos %}
                            <option value="{{ proyecto_item.codigo_proyecto }}">{{ proyecto_item.nombre_proyecto }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="codigo_tarea">Código Tarea</label>
                        <input type="text" class="form-control" id="codigo_tarea" name="codigo_tarea" onclick="generarCodigoUnico()" required>
                    </div>
                    <div class="form-group">
                        <label for="titulo">Título</label>
                        <input type="text" class="form-control" id="titulo" name="titulo" required>
                    </div>
                    <div class="form-group">
                        <label for="descripcion">Descripción</label>
                        <textarea class="form-control" id="descripcion" name="descripcion" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="fecha_inicio">Fecha Inicio</label>
                        <input type="date" class="form-control" id="fecha_inicio" name="fecha_inicio" required>
                    </div>
                    <div class="form-group">
                        <label for="fecha_fin">Fecha Fin</label>
                        <input type="date" class="form-control" id="fecha_fin" name="fecha_fin">
                    </div>
                    <div class="form-group">
                        <label for="horas_estimadas">Horas Estimadas</label>
                        <input type="number" class="form-control" id="horas_estimadas" name="horas_estimadas" required>
                    </div>
                    <div class="form-group">
                        <label for="horas_dedicadas">Horas Dedicadas</label>
                        <input type="number" class="form-control" id="horas_dedicadas" name="horas_dedicadas" value="0">
                    </div>
                    <div class="form-group">
                        <label for="fecha_facturacion">Fecha Facturación</label>
                        <input type="date" class="form-control" id="fecha_facturacion" name="fecha_facturacion">
                    </div>

                    <div class="form-group">
                        <label for="estado">Estado</label>
                        <select class="form-control" id="estado" name="estado" required>
                            <option value="PENDIENTE" selected>PENDIENTE</option>
                            <option value="PROGRESO">PROGRESO</option>
                            <option value="REVISIÓN">REVISIÓN</option>
                            <option value="IMPEDIMENTOS">IMPEDIMENTOS</option>
                            {% if session['username'] == "admin" %}
                            <option value="COMPLETADOS">COMPLETADOS</option>
                            {% endif %}
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="responsable">Responsable</label>
                        <select class="form-control" id="responsable" name="responsable" required>
                            <option value="" disabled selected>Selecciona el responsable</option>
                            {% for usuario in usuarios %}
                            <option value="{{ usuario.nombres }}">{{ usuario.nombres }} {{ usuario.apellidos }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="modal-footer">
                        <button type="submit" class="btn btn-primary">Guardar</button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
    function showDeleteIcon(id) {
        document.getElementById('delete-icon-' + id).style.display = 'inline';
    }
    
    function editarTarea(id) {
        // Obtener los detalles de la tarea por ID y rellenar el formulario para editar
        fetch(`/tareas/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('tareaId').value = data.id;
            document.getElementById('empresa').value = data.empresa;
            document.getElementById('codigo_proyecto').value = data.codigo_proyecto;
            document.getElementById('codigo_tarea').value = data.codigo_tarea;
            document.getElementById('titulo').value = data.titulo;
            document.getElementById('descripcion').value = data.descripcion;
            document.getElementById('fecha_inicio').value = data.fecha_inicio.split('T')[0];
            document.getElementById('fecha_fin').value = data.fecha_fin ? data.fecha_fin.split('T')[0] : '';
            document.getElementById('horas_estimadas').value = data.horas_estimadas;
            document.getElementById('horas_dedicadas').value = data.horas_dedicadas;
            document.getElementById('estado').value = data.estado;
            document.getElementById('responsable').value = data.responsable;
        });
    }
    
    function eliminarTarea(id) {
        if (confirm('¿Estás seguro de que deseas eliminar esta tarea?')) {
            fetch(`/tareas/${id}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                }
            });
        }
    }
    
    document.getElementById('formTarea').addEventListener('submit', function(event) {
        event.preventDefault();
    
        const id = document.getElementById('tareaId').value;
        const method = id ? 'PUT' : 'POST';  // Usar PUT si es edición, POST si es creación
        const url = id ? `/tareas/${id}` : '/tareas';
    
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                empresa: document.getElementById('empresa').value,
                codigo_proyecto: document.getElementById('codigo_proyecto').value,
                codigo_tarea: document.getElementById('codigo_tarea').value,
                titulo: document.getElementById('titulo').value,
                descripcion: document.getElementById('descripcion').value,
                fecha_inicio: document.getElementById('fecha_inicio').value,
                fecha_fin: document.getElementById('fecha_fin').value,
                horas_estimadas: document.getElementById('horas_estimadas').value,
                horas_dedicadas: document.getElementById('horas_dedicadas').value,
                estado: document.getElementById('estado').value,
                responsable: document.getElementById('responsable').value
            })
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    });
    
    function limpiarFormulario() {
        document.getElementById('formTarea').reset();
        document.getElementById('tareaId').value = '';
    }
    
    function generarCodigoUnico() {
        const now = new Date();
        const timestamp = now.getFullYear().toString() + 
                          (now.getMonth() + 1).toString().padStart(2, '0') + 
                          now.getDate().toString().padStart(2, '0') + 
                          now.getHours().toString().padStart(2, '0') + 
                          now.getMinutes().toString().padStart(2, '0') + 
                          now.getSeconds().toString().padStart(2, '0') + 
                          now.getMilliseconds().toString().padStart(3, '0');
        
        const randomPart = Math.random().toString(36).substring(2, 10);
    
        const uniqueCode = `${timestamp}-${randomPart}`;
    
        document.getElementById('codigo_tarea').value = uniqueCode;  // Asignar el código al input de 'codigo'
        return uniqueCode;
    }
    </script>
    {% endblock %}
    



```
ahora analiza este models:
```
# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

class Empresas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, unique=True)
    empresa = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'nit': self.nit,
            'empresa': self.empresa
        }

class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    codigo_proyecto = db.Column(db.String(50), nullable=False, unique=True)
    nombre_proyecto = db.Column(db.String(100), nullable=False)
    descripcion_proyecto = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'empresa': self.empresa,
            'codigo_proyecto': self.codigo_proyecto,
            'nombre_proyecto': self.nombre_proyecto,
            'descripcion_proyecto': self.descripcion_proyecto
        }

class Tareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    codigo_proyecto = db.Column(db.String(50), nullable=False)
    codigo_tarea = db.Column(db.String(50), nullable=False, unique=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)  # Se mantiene db.Text para permitir cualquier tamaño de texto
    fecha_inicio = db.Column(db.Date, nullable=False)  # Fecha de inicio del proyecto
    fecha_fin = db.Column(db.Date, nullable=True)  # Fecha de fin del proyecto
    responsable = db.Column(db.String(100), nullable=False)  # Responsable asignado a la tarea
    horas_dedicadas = db.Column(db.Float, nullable=False, default=0)  # Horas dedicadas
    horas_estimadas = db.Column(db.Float, nullable=False)  # Horas estimadas para completar la tarea
    fecha_facturacion = db.Column(db.Date, nullable=True)  # Fecha de facturación
    estado = db.Column(db.Enum('PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS', name='estado_tarea'), nullable=False, default='PENDIENTE')  # Estado de la tarea

    def serialize(self):
        return {
            'id': self.id,
            'empresa': self.empresa,
            'codigo_proyecto': self.codigo_proyecto,
            'codigo_tarea': self.codigo_tarea,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
            'responsable': self.responsable,
            'horas_dedicadas': self.horas_dedicadas,
            'horas_estimadas': self.horas_estimadas,
            'fecha_facturacion': self.fecha_facturacion.strftime('%Y-%m-%d') if self.fecha_facturacion else None,
            'estado': self.estado
        }

class SubTareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_tarea = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'codigo_tarea': self.codigo_tarea,
            'titulo': self.titulo,
            'descripcion': self.descripcion
        }

class Usuarios(UserMixin,db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50))
    apellidos = db.Column(db.String(50))
    correo = db.Column(db.String(100), unique=True)
    contraseña = db.Column(db.String(100))
    empresa = db.Column(db.String(50))
    permisos = db.Column(db.String(20))

    def serialize(self):
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'empresa': self.empresa,
            'correo': self.correo,
            'permisos': self.permisos
        }
```
ahora analiza tambien el el modulo app:
```
# aap.py
from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify,session
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
app.secret_key = 'clave_secreta'
# Generador de tokens seguros
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuración de la base de datos usando SQLite
# SQLALCHEMY_DATABASE_URI define la ubicación de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Empresas.db'

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

#<___________________________________Vista___________________________________________________>


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
            
        return redirect(url_for('obtener_tareas_reporte') ) # Redirigir al tablero
          
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
    # Obtener todas las empresas y tareas por estado
    empresas = models.Empresas.query.all()
    tareas = models.Tareas.query.all()
    proyectos = models.Proyecto.query.all()
    usuarios = models.Usuarios.query.all()

    if request.method == 'POST':
        # Procesar búsqueda por palabra clave
        
        palabra_clave = request.form['searchInput']
        try:
            tareas_PENDIENTE=buscar_tareas(palabra_clave)
        except:
            tareas_PENDIENTE = models.Tareas.query.filter_by(estado='PENDIENTE').all()
        print(tareas_PENDIENTE)
      

    tareas_PENDIENTE = models.Tareas.query.filter_by(estado='PENDIENTE').all()
    tareas_PROGRESO = models.Tareas.query.filter_by(estado='PROGRESO').all()
    tareas_REVISIÓN = models.Tareas.query.filter_by(estado='REVISIÓN').all()
    tareas_IMPEDIMENTOS = models.Tareas.query.filter_by(estado='IMPEDIMENTOS').all()
    tareas_COMPLETADOS = models.Tareas.query.filter_by(estado='COMPLETADOS').all()
    
    

   
    

    # Configuración del host (si es necesario)
    host = config.config.get("host", "localhost")
    
    # Renderizar la plantilla con los datos obtenidos
    return render_template('tablero.html',
                           empresas=empresas,
                           host=host,
                           tareas_PENDIENTE=tareas_PENDIENTE,
                           tareas_PROGRESO=tareas_PROGRESO,
                           tareas_REVISIÓN=tareas_REVISIÓN,
                           tareas_IMPEDIMENTOS=tareas_IMPEDIMENTOS,
                           tareas_COMPLETADOS=tareas_COMPLETADOS,
                           tareas=tareas,
                           proyectos=proyectos,
                           usuarios=usuarios)

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
@app.route('/tareas', methods=['GET'])
@login_required
def vista_tareas():
    """
    Obtener todas las tareas con los filtros seleccionados por el usuario.
    """
    # Obtener los filtros seleccionados por el usuario
    estado = request.args.get('estado', '')  # Filtro de estado
    responsable = request.args.get('responsable', '')  # Filtro de responsable
    proyecto = request.args.get('proyecto', '')  # Filtro de proyecto
    empresa = request.args.get('empresa', '')  # Filtro de empresa

    # Consulta base sin filtros
    query = models.Tareas.query

    # Aplicar filtro de estado si existe
    if estado:
        query = query.filter(models.Tareas.estado == estado)

    # Aplicar filtro de responsable si existe
    if responsable:
        query = query.filter(models.Tareas.responsable == responsable)

    # Aplicar filtro de proyecto si existe
    if proyecto:
        query = query.filter(models.Tareas.codigo_proyecto == proyecto)

    # Aplicar filtro de empresa si existe
    if empresa:
        query = query.filter(models.Tareas.empresa == empresa)

    # Obtener los resultados de la consulta filtrada
    tareas = query.all()

    # Obtener datos adicionales para el formulario de filtrado
    empresas = models.Empresas.query.all()
    proyectos = models.Proyecto.query.all()
    usuarios = models.Usuarios.query.all()

    return render_template("tareas.html", tareas=tareas,
                                        empresas=empresas,
                                        proyectos=proyectos,
                                        usuarios=usuarios)

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
@login_required
def logout():
    logout_user()  # Cerrar sesión
    session.pop('username', None)
    session.pop('empresa', None)
    session.pop('correo', None)
    return redirect(url_for('login'))
#</__________________________________Vista___________________________________________________>

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

@app.route('/tareas', methods=['POST'])
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
        estado=data.get('estado', 'PENDIENTE'),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d') if 'fecha_fin' in data else None,
        fecha_facturacion=datetime.strptime(data['fecha_facturacion'], '%Y-%m-%d') if 'fecha_facturacion' in data else None
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


if __name__ == '__main__':
    # Se obtiene la configuración de debug desde el archivo config.py
    produccion = config.config["debug"]
    
    # Inicia el servidor Flask con debug activado (según configuración) en el puerto 5000
    app.run(host="0.0.0.0",debug=produccion, port=5000)




```

→ revisa tareas.html corrige los siguientes errores en la consola :

Traceback (most recent call last):
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\sql\sqltypes.py", line 1619, in _object_value_for_elem
    return self._object_lookup[elem]
           ^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: ''

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 1498, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 1476, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 1473, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 882, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 880, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask\app.py", line 865, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\flask_login\utils.py", line 290, in decorated_view
    return current_app.ensure_sync(func)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\app.py", line 172, in proyecto
    tareas = models.Tareas.query.all()
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\orm\query.py", line 2673, in all
    return self._iter().all()  # type: ignore
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 1769, in all
    return self._allrows()
           ^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 548, in _allrows
    rows = self._fetchall_impl()
           ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 1676, in _fetchall_impl
    return self._real_result._fetchall_impl()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 2270, in _fetchall_impl
    return list(self.iterator)
           ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\orm\loading.py", line 219, in chunks
    fetch = cursor._raw_all_rows()
            ^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 541, in _raw_all_rows
    return [make_row(row) for row in rows]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\engine\result.py", line 541, in <listcomp>
    return [make_row(row) for row in rows]
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "lib\\sqlalchemy\\cyextension\\resultproxy.pyx", line 22, in sqlalchemy.cyextension.resultproxy.BaseRow.__init__
  File "lib\\sqlalchemy\\cyextension\\resultproxy.pyx", line 79, in sqlalchemy.cyextension.resultproxy._apply_processors
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\sql\sqltypes.py", line 1739, in process
    value = self._object_value_for_elem(value)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\FRANKLIN\Downloads\Desarrollos\FofiGest\.venv\Lib\site-packages\sqlalchemy\sql\sqltypes.py", line 1621, in _object_value_for_elem
    raise LookupError(
LookupError: '' is not among the defined enum values. Enum name: estado_tarea. Possible values: PENDIENTE, PROGRESO, REVISIÓN, ..., COMPLETADOS

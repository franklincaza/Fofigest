# Instrucciones de Claude Code para Fofigest

Estas instrucciones aplican a todo el proyecto. Usa [BRAND_IDENTITY.md](d:/App.Proyectos/Fofigest/BRAND_IDENTITY.md) como referencia maestra cuando generes o modifiques interfaz, estilos o templates.

---

## 1. Contexto del proyecto

Fofigest v4.0 es un sistema de gestión de proyectos y tareas (tipo Jira/tablero kanban) desarrollado en Flask para la empresa Fofimatic S.A.S. Gestiona empresas cliente, proyectos, tareas con horas estimadas/dedicadas, usuarios con permisos y reportes de horas.

**Archivos clave:**
- `app.py` — TODAS las rutas, lógica de negocio e inicialización (~1800 líneas). NO dispersar rutas a otros archivos.
- `models/models.py` — todos los modelos SQLAlchemy.
- `config.py` — dict `config` con debug flag, email, host y versión.
- `forms.py` — `EmpresaForm`, `ProyectoForm` (Flask-WTF).
- `feature/Reporte_sulfoquimica.py` — clase `ReporteSulfoquimica` para API REST externa Supabase.
- `templates/` — todos extienden `templates/Base.html` salvo excepciones justificadas.
- `static/css/style.css` y `static/css/sb-admin-2.css` — estilos.

---

## 2. Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Framework | Flask | 3.0.3 |
| ORM | Flask-SQLAlchemy / SQLAlchemy | 3.1.1 / 2.0.34 |
| Auth | Flask-Login + Werkzeug | 0.6.3 / 3.0.4 |
| Formularios | Flask-WTF + WTForms | 1.2.1 / 3.1.2 |
| Editor rico | Flask-CKEditor | 1.0.0 |
| Email | Flask-Mail (Gmail SMTP port 587 TLS) | 0.10.0 |
| Tokens | itsdangerous URLSafeTimedSerializer | 2.2.0 |
| Templates | Jinja2 | 3.1.4 |
| Servidor prod | Waitress | 3.0.0 |
| BD desarrollo | SQLite (`instance/Empresas.db`) | — |
| BD producción | PostgreSQL en Supabase (psycopg2-binary) | 2.9.9 |
| Análisis | Pandas + Plotly + XlsxWriter | 2.2.2 / 5.24.1 / 3.2.0 |
| Monitoreo | Flask-MonitoringDashboard | 3.3.2 |
| UI | Bootstrap 5.3.3 + SB Admin 2 v4.1.3 + Font Awesome 5 + SweetAlert2 | — |
| Import Excel | openpyxl | 3.1.5 |
| PWA | manifest.json + sw.js | — |

---

## 3. Base de datos y modelos

### Configuración de entorno (config.py + app.py)
```python
# config.py
config = {
    "debug": False,           # True = SQLite, False = PostgreSQL Supabase
    "contraseña_google": "...",
    "EMAIL": "fofimaticsas@gmail.com",
    "host": "http://127.0.0.1:5000/",
    "version": "4.0"
}

# app.py — selección automática
if config['debug']:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Empresas.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.wlvgmwuhfunnpddcgvzu:...@aws-0-us-west-1.pooler.supabase.com:6543/postgres'
```

### Modelos (models/models.py)

#### `Empresas`
```python
id, nit (unique, String 20), empresa (String 100)
```

#### `Proyecto`
```python
id, empresa (String 100), codigo_proyecto (unique, String 50),
nombre_proyecto (String 100), descripcion_proyecto (Text)
```

#### `Tareas` — modelo central
```python
id, empresa, codigo_proyecto, codigo_tarea (unique),
titulo (String 100), descripcion (Text),
fecha_inicio (Date), fecha_fin (Date, nullable),
responsable (String), horas_dedicadas (Float), horas_estimadas (Float),
fecha_facturacion (Date, nullable),
estado: Enum('PENDIENTE','PROGRESO','REVISIÓN','IMPEDIMENTOS','COMPLETADOS'),
detalles_editor (JSON),   # Rich text CKEditor
tipo_consumo: Enum('Desarrollo','Reuniones','Desarrollo por control de cambio','Soporte','Oportunidad de mejora'),
mes: Enum('Enero','Febrero','Marzo','Abril','Mayo','Junio',
          'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre')
```

#### `SubTareas`
```python
id, codigo_tarea (String referencial), titulo, descripcion
```

#### `Usuarios` (UserMixin)
```python
id, nombres (String 50), apellidos (String 50), correo (unique, String 100),
contraseña (String 256),   # werkzeug hash; legacy puede ser texto plano
empresa (String 50), permisos (String 20),   # 'admin'|'superadmin'|'usuario'|'nuevo'
otp_code (String 6, nullable), otp_expiry (DateTime, nullable)
```

#### `Licencias`
```python
id, nit (unique, String 20), empresa (String 100), licencia (String 100)
```

**Todos los modelos tienen `.serialize()` → dict JSON-friendly.**

### Cálculo de progreso Gantt
```python
progress = round((tarea.horas_dedicadas / tarea.horas_estimadas) * 100, 1) if tarea.horas_estimadas else 0
```

### Migración automática de columnas OTP
Al arrancar `app.py`, si las columnas `otp_code`/`otp_expiry` no existen en la tabla `usuarios`, se ejecutan `ALTER TABLE` con SQL raw para agregarlas. Es una migración de emergencia, no usar SQLAlchemy Migrate.

---

## 4. Sistema de autenticación y permisos

### Variables de sesión Flask
```python
# Login exitoso → se establecen SIEMPRE estas tres variables
session['username'] = usuario.permisos   # CUIDADO: no es el nombre, es el nivel de permiso
session['empresa']  = usuario.empresa    # Nombre de la empresa del usuario
session['correo']   = usuario.correo     # Email del usuario logueado
```

### Niveles de permiso
| Permiso | Acceso |
|---------|--------|
| `'superadmin'` | Acceso total, todos los datos de todas las empresas |
| `'admin'` | Acceso total, todos los datos de todas las empresas |
| `'usuario'` | Solo ve datos de su propia empresa (`session['empresa']`) |
| `'nuevo'` | Cuenta creada pero sin permisos asignados aún |

### Filtrado por empresa en rutas
```python
permisos = session.get('username')
empresa_usuario = session.get('empresa')

if permisos == 'usuario':
    query = query.filter(models.Tareas.empresa == empresa_usuario)
# admin/superadmin: sin filtro adicional
```

### Flujos de autenticación

#### Login estándar (`POST /`)
```python
usuario = models.Usuarios.query.filter_by(correo=correo).first()
# Prioridad 1: hash werkzeug
if check_password_hash(usuario.contraseña, password):
    login_user(usuario)
# Prioridad 2: fallback texto plano (legacy)
elif usuario.contraseña == password:
    login_user(usuario)
```

#### Login OTP (`/login-otp` → `/verify-otp`)
```python
# Paso 1: generar y enviar código
otp = str(random.randint(100000, 999999))
usuario.otp_code = otp
usuario.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
session['otp_correo'] = correo   # Persiste entre pasos
# Enviar email con otp

# Paso 2: verificar
if usuario.otp_code == otp_input and datetime.utcnow() < usuario.otp_expiry:
    usuario.otp_code = None      # Limpiar tras uso
    usuario.otp_expiry = None
    login_user(usuario)
```

#### Password Reset (`/olvidaste` → `/reset/<token>`)
```python
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
token = serializer.dumps(correo, salt='password-reset-salt')
# En reset:
correo = serializer.loads(token, salt='password-reset-salt', max_age=3600)
usuario.contraseña = generate_password_hash(nueva_password)
```

### Post-login redirect (splash.html como intermediario)
```python
if usuario.permisos == 'usuario':
    redirect_url = f'/Reporte-Horas{usuario.empresa}'
else:
    redirect_url = '/tablero'
return render_template("splash.html", v=v, redirect_url=redirect_url)
```

### Logout
```python
logout_user()
session.pop('username', None)
session.pop('empresa', None)
session.pop('correo', None)
return redirect(url_for('login'))
```

---

## 5. Mapa completo de rutas

### Vistas HTML
| Ruta | Método | Auth | Template | Descripción |
|------|--------|------|----------|-------------|
| `/` | GET | No | `login.html` | Página de login |
| `/` | POST | No | — | Autenticación |
| `/tablero` | GET/POST | Sí | `tablero.html` | Kanban por estado + filtros |
| `/tareas` | GET/POST | Sí | `tareas.html` | Lista de tareas |
| `/proyectos` | GET | Sí | `proyectos.html` | Lista de proyectos |
| `/empresa` | GET/POST | Sí | `empresas.html` | CRUD empresas (FlaskForm) |
| `/gannt` | GET/POST | Sí | `gantt.html` | Gantt global (12 meses) |
| `/gannt/<project>` | GET/POST | Sí | `gantt.html` | Gantt por proyecto |
| `/Reporte-Horas<empresa>` | GET/POST | Sí | `Reporte de horas.html` | Horas COMPLETADOS |
| `/Reporte-HorasDownload<empresa>` | GET/POST | Sí | — | Excel download (deprecated) |
| `/reporte` | GET | Sí | `reporte.html` | Gráfico Plotly |
| `/reporte_horas_sulfoquimica` | GET | No | `Reporte_sulfoquimica.html` | Reporte externo |
| `/usuarios_admin` | GET | Sí | `usuarios.html` | Admin de usuarios |
| `/Nuevo_Usuario` | GET/POST | No | `Nuevo_Usuario.html` | Auto-registro |
| `/olvidaste` | GET/POST | No | `Olvide_Contraseña.html` | Olvidé contraseña |
| `/reset/<token>` | GET/POST | No | `reset_with_token.html` | Reset con token |
| `/login-otp` | GET/POST | No | `login_otp.html` | OTP paso 1 |
| `/verify-otp` | GET/POST | No | `verify_otp.html` | OTP paso 2 |
| `/logout` | GET | Sí | — | Cerrar sesión |
| `/download-backup` | GET | Sí | — | Descarga SQLite |
| `/log` | GET | Sí | `log.html` (dinámico) | Visor de log |
| `/upload` | GET/POST | No | `subir_datos.html` | Importar Excel |
| `/submit-description` | GET/POST | Sí | `description_preview.html` | Preview markdown |
| `/render_markdown` | GET/POST | Sí | `markdown_form.html` | Editor markdown |
| `/manifest.json` | GET | No | — | PWA manifest |
| `/sw.js` | GET | No | — | Service Worker |

### API REST (retornan JSON)
| Ruta | Método | Descripción |
|------|--------|-------------|
| `/tareas/json` | GET | Todas las tareas |
| `/tareas/<id>` | GET | Tarea por ID |
| `/outtareas` | POST | Crear tarea (desde UI) |
| `/tareas/<id>` | PUT | Actualizar tarea completa |
| `/tareas/<id>` | DELETE | Eliminar tarea |
| `/tareas/<id>/estado` | PUT | Actualizar solo estado |
| `/actualizar_estado_tarea/<id>` | POST | Actualizar estado (kanban drag & drop) |
| `/b/api/tareas` | GET | Búsqueda: `?clave_busqueda=&fecha_inicio=&fecha_fin=&estado=` |
| `/api/gantt/tarea/<codigo>` | PATCH | Actualizar tarea desde Gantt |
| `/api/gantt/tarea` | POST | Crear tarea desde Gantt |
| `/api/gantt/tarea/<codigo>` | DELETE | Eliminar tarea desde Gantt |
| `/json/empresas` | GET | Todas las empresas |
| `/json/empresa/<id>` | GET | Empresa por ID |
| `/empresas` | POST | Crear empresa |
| `/json/empresas/<id>` | PUT | Actualizar empresa |
| `/empresas/<id>` | DELETE | Eliminar empresa |
| `/json/proyectos` | GET | Todos los proyectos |
| `/json/proyectos` | POST | Crear proyecto |
| `/proyectos/<codigo>` | GET | Proyecto por código |
| `/proyectos/<codigo>` | PUT | Actualizar proyecto |
| `/proyectos/<codigo>` | DELETE | Eliminar proyecto |
| `/usuario` | POST | Crear usuario (API) |
| `/usuario/<id>` | GET | Usuario por ID |
| `/usuario/<id>` | PUT | Actualizar usuario |
| `/usuarios/json` | GET | Todos los usuarios |
| `/licencia/<id>` | GET | Licencia por ID |
| `/reporte_horas_chart` | GET | JSON reporte Sulfoquimica (generar_reporte) |
| `/reporte_horas_chart_dev` | GET | JSON tabla por responsable |

---

## 6. Patrones de código backend

### Manejo de errores en rutas
```python
try:
    models.db.session.add(objeto)
    models.db.session.commit()
    flash("Éxito", "success")
except IntegrityError:
    models.db.session.rollback()
    flash("El registro ya existe", "danger")
except Exception as e:
    models.db.session.rollback()
    logging.error(f"Error en /ruta: {str(e)}")
    flash("Error interno", "danger")
```

### Respuestas JSON de la API
```python
return jsonify(modelo.serialize()), 200            # Éxito con objeto
return jsonify([m.serialize() for m in lista]), 200 # Éxito con lista
return jsonify({'message': 'Not found'}), 404      # No encontrado
return jsonify({'ok': False, 'error': '...'}), 422 # Validación fallida
return jsonify({'ok': True}), 200                  # Éxito sin datos (Gantt API)
return jsonify({'error': '...'}), 500              # Error interno
```

### Filtros en cadena SQLAlchemy
```python
query = models.Tareas.query
if empresa_filtro:
    query = query.filter(models.Tareas.empresa == empresa_filtro)
if estado:
    query = query.filter(models.Tareas.estado == estado)
if responsable:
    query = query.filter(models.Tareas.responsable == responsable)
tareas = query.all()
```

### Context processor (disponible en TODOS los templates)
```python
@app.context_processor
def inject_user():
    return dict(username=session.get('username', ''))
# En Jinja2: {{ username }} devuelve el nivel de permiso del usuario
```

### Generación de código de tarea (Gantt)
```python
import uuid
codigo_tarea = f"{codigo_proyecto[:10]}-{uuid.uuid4().hex[:8]}"
```

### Asignación de mes en español
```python
meses_es = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
            'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
mes = meses_es[fecha_inicio.month - 1]
```

### Logging
```python
import logging
logging.basicConfig(filename='log.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d')
logging.info("acción exitosa")
logging.warning("advertencia")
logging.error(f"error: {str(e)}")
```

---

## 7. Feature: ReporteSulfoquimica

Clase en `feature/Reporte_sulfoquimica.py`. Consulta directamente la API REST de Supabase (independiente del ORM local).

```python
from feature.Reporte_sulfoquimica import ReporteSulfoquimica

reporte = ReporteSulfoquimica(api_key, bearer_token, empresa='SULFOQUIMICA SA')
reporte.obtener_datos()      # GET https://wlvgmwuhfunnpddcgvzu.supabase.co/rest/v1/tareas?select=*
reporte.limpiar_fechas()     # Convierte fecha_inicio string → datetime
reporte.filtrar_datos()      # Filtra: empresa=SULFOQUIMICA SA, estado=COMPLETADOS, year=current
resultado = reporte.generar_reporte()                   # Dict agrupado por año/mes/proyecto, suma horas_dedicadas
tabla = reporte.generar_tabla_por_responsable()         # Dict agrupado por responsable
```

Credenciales Supabase (`api_key`, `bearer_token`) están hardcodeadas en `app.py` y se pasan al instanciar la clase.

---

## 8. Formularios WTF (forms.py)

```python
class EmpresaForm(FlaskForm):
    nit = StringField('NIT', validators=[DataRequired(), Length(max=20)])
    empresa = StringField('Nombre de la Empresa', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Guardar')

class ProyectoForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired(), Length(max=100)])
    codigo_proyecto = StringField('Código del Proyecto', validators=[DataRequired(), Length(max=50)])
    nombre_proyecto = StringField('Nombre del Proyecto', validators=[DataRequired(), Length(max=100)])
    descripcion_proyecto = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Guardar')
```

CSRFProtect está habilitado globalmente — todos los formularios HTML necesitan `{{ form.hidden_tag() }}` o `{{ csrf_token() }}`.

---

## 9. Importación de datos Excel

```python
# Ruta POST /upload — usa openpyxl via pandas
df = pd.read_excel(file)
for _, row in df.iterrows():
    tarea = models.Tareas(
        empresa=row['empresa'],
        codigo_proyecto=row['codigo_proyecto'],
        ...
    )
    models.db.session.add(tarea)
models.db.session.commit()
```

---

## 10. Inicialización de la aplicación

```python
# app.py — orden de inicialización
from flask_monitoring_dashboard import dashboard
dashboard.bind(app)           # Antes que todo

CSRFProtect(app)
CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return models.Usuarios.query.get(int(user_id))

# OTP column migration (raw SQL, ejecuta al inicio)
with app.app_context():
    models.db.create_all()
    # ALTER TABLE usuarios ADD COLUMN otp_code ... (si no existe)
```

---

## 11. Convenciones de código (IMPORTANTE)

### Backend
- **NUNCA** crear nuevos archivos de rutas — todo va en `app.py`.
- `session['username']` almacena el nivel de **permiso** (no el nombre del usuario).
- Nuevo usuario → `permisos='nuevo'` por defecto hasta que admin asigne rol.
- Passwords: siempre usar `generate_password_hash` / `check_password_hash` de werkzeug. El fallback plaintext es solo para usuarios legacy ya existentes.
- Formato de fechas en formularios HTML: `'%Y-%m-%d'` → `datetime.strptime(value, '%Y-%m-%d').date()`.
- `codigo_tarea` siempre con formato `f"{codigo_proyecto[:10]}-{uuid.uuid4().hex[:8]}"`.
- Acceso a versión: `config.config["version"]` → `"4.0"`.
- Log file: `log.log` en la raíz del proyecto.
- En queries: si `permisos == 'usuario'`, siempre filtrar por `empresa == session['empresa']`.
- Hacer `db.session.rollback()` en todo bloque `except` que involucre la BD.

### UI e identidad visual
- Mantener el lenguaje visual existente. No rediseñar desde cero.
- Usar siempre la tipografía `Nunito`.
- No inventar colores fuera de la paleta de marca.
- Priorizar componentes Bootstrap/SB Admin 2 antes de crear variantes nuevas.
- Preservar consistencia entre vistas nuevas y templates existentes.

### Paleta de marca
- Primario: `#4e73df` / Hover: `#2e59d9`
- Éxito: `#1cc88a` / Info: `#36b9cc` / Advertencia: `#f6c23e` / Peligro: `#e74a3b`
- Texto secundario: `#858796` / Fondo: `#f8f9fc`
- Bordes suaves: `#e3e6f0` y `#d1d3e2` / Texto principal: `#3a3b45`

### Criterios para generar UI
- Contenido principal → `card shadow mb-4`; encabezados → `card-header py-3` con título `text-primary`.
- Formularios: `form-group`, `form-control`, labels `fw-semibold`.
- Botones: principal `btn btn-primary`, cancelar `btn btn-secondary`, eliminar `btn btn-danger`, exportar `btn btn-success`.
- Tablas: `table-responsive` + `table table-bordered table-hover`.
- Confirmaciones destructivas → SweetAlert2. Iconos → Font Awesome 5.

### Layout y responsive
- Extender `templates/Base.html` para nuevas vistas.
- Grid Bootstrap: `col-sm-*`, `col-md-*`, `col-lg-*`. Funcional desde 375px.
- No reemplazar componentes existentes por versiones incompatibles.
- No cambiar nombres, rutas o bloques Jinja sin necesidad funcional.

### CSS
- Preferir clases Bootstrap sobre `style="..."`.
- `border-radius` cercano a `0.35rem`. Reutilizar clases de `style.css` y `sb-admin-2.css`.
- Modo oscuro: verificar compatibilidad con `.modo-oscuro` si tocas componentes que lo usen.

### Prioridad de decisión
Cuando haya conflicto, priorizar:
1. Estructura y componentes existentes en `templates/`.
2. Reglas de [BRAND_IDENTITY.md](d:/App.Proyectos/Fofigest/BRAND_IDENTITY.md).
3. Bootstrap/SB Admin 2 tal como están usados en Fofigest.

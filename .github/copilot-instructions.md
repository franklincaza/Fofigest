# Instrucciones de Copilot para Fofigest

Estas instrucciones aplican a todo el proyecto. Usa [BRAND_IDENTITY.md](d:/App.Proyectos/Fofigest/BRAND_IDENTITY.md) como referencia maestra cuando generes o modifiques interfaz, estilos o templates.

---

## 1. Contexto del proyecto

Fofigest v4.0 es un sistema de gestión de proyectos y tareas (tipo Jira/tablero kanban) desarrollado en Flask para la empresa Fofimatic S.A.S. Gestiona empresas cliente, proyectos, tareas con horas estimadas/dedicadas, usuarios con permisos y reportes de horas.

- Entrada principal: `app.py` — todas las rutas, lógica de negocio e inicialización.
- ORM: `models/models.py` — todos los modelos SQLAlchemy.
- Config central: `config.py` — clave `config` dict con debug flag, email, host y versión.
- Formularios WTF: `forms.py` — `EmpresaForm`, `ProyectoForm`.
- Feature modular: `feature/Reporte_sulfoquimica.py` — clase `ReporteSulfoquimica` para API externa.
- Templates: `templates/` — todos extienden `templates/Base.html` salvo excepciones.
- Estilos: `static/css/style.css` y `static/css/sb-admin-2.css`.

---

## 2. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | Flask 3.0.3 |
| ORM | Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.34 |
| Auth | Flask-Login 0.6.3 + Werkzeug password hashing |
| Formularios | Flask-WTF 1.2.1 + WTForms 3.1.2 |
| Editor rico | Flask-CKEditor 1.0.0 |
| Email | Flask-Mail 0.10.0 (Gmail SMTP, puerto 587, TLS) |
| Tokens | itsdangerous 2.2.0 (`URLSafeTimedSerializer`) |
| Templates | Jinja2 3.1.4 |
| Servidor prod | Waitress 3.0.0 |
| BD desarrollo | SQLite (`instance/Empresas.db`) |
| BD producción | PostgreSQL en Supabase |
| Análisis | Pandas 2.2.2 + Plotly 5.24.1 + XlsxWriter 3.2.0 |
| Monitoreo | Flask-MonitoringDashboard 3.3.2 |
| UI | Bootstrap 5.3.3 + SB Admin 2 v4.1.3 + Font Awesome 5 + SweetAlert2 |
| PWA | manifest.json + service worker (sw.js) |

---

## 3. Base de datos y modelos

### Configuración de entorno
```python
# Desarrollo (debug=True en config.py)
SQLALCHEMY_DATABASE_URI = 'sqlite:///Empresas.db'

# Producción (debug=False)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.wlvgmwuhfunnpddcgvzu:...@aws-0-us-west-1.pooler.supabase.com:6543/postgres'
```

### Modelos (models/models.py)

#### `Empresas`
```python
id, nit (unique, str 20), empresa (str 100)
```

#### `Proyecto`
```python
id, empresa (str 100), codigo_proyecto (unique, str 50),
nombre_proyecto (str 100), descripcion_proyecto (Text)
```

#### `Tareas` — modelo central
```python
id, empresa, codigo_proyecto, codigo_tarea (unique),
titulo, descripcion (Text), fecha_inicio (Date), fecha_fin (Date, nullable),
responsable, horas_dedicadas (Float), horas_estimadas (Float),
fecha_facturacion (Date, nullable),
estado: Enum('PENDIENTE','PROGRESO','REVISIÓN','IMPEDIMENTOS','COMPLETADOS'),
detalles_editor (JSON),  # Rich text del CKEditor
tipo_consumo: Enum('Desarrollo','Reuniones','Desarrollo por control de cambio','Soporte','Oportunidad de mejora'),
mes: Enum('Enero','Febrero',...,'Diciembre')
```

#### `SubTareas`
```python
id, codigo_tarea (FK referencial str), titulo, descripcion
```

#### `Usuarios` (UserMixin)
```python
id, nombres (str 50), apellidos (str 50), correo (unique, str 100),
contraseña (hash str 256), empresa (str 50),
permisos: str — valores: 'admin', 'superadmin', 'usuario', 'nuevo'
otp_code (str 6, nullable), otp_expiry (DateTime, nullable)
```

#### `Licencias`
```python
id, nit (unique, str 20), empresa (str 100), licencia (str 100)
```

Todos los modelos implementan `.serialize()` que retorna un dict JSON-friendly.

### Cálculo de progreso Gantt
```python
progress = round((tarea.horas_dedicadas / tarea.horas_estimadas) * 100, 1) if tarea.horas_estimadas else 0
```

---

## 4. Sistema de autenticación y permisos

### Sesión Flask
Al hacer login se guardan en sesión:
```python
session['username'] = usuario.permisos   # 'admin'|'superadmin'|'usuario'|'nuevo'
session['empresa']  = usuario.empresa    # Nombre de la empresa
session['correo']   = usuario.correo     # Correo del usuario
```

### Lógica de permisos en rutas
```python
permisos = session.get('username')
empresa_usuario = session.get('empresa')

if permisos == 'usuario':
    # Filtrar datos solo a su empresa
    query = query.filter(models.Tareas.empresa == empresa_usuario)
# admin/superadmin ven todos los datos
```

### Flujos de autenticación
1. **Login estándar** (`/` POST): email + password con soporte de hash werkzeug y texto plano (legacy).
2. **Login OTP** (`/login-otp` → `/verify-otp`): OTP de 6 dígitos enviado por email, válido 10 minutos. Se guarda `session['otp_correo']` entre pasos.
3. **Password reset** (`/olvidaste` → `/reset/<token>`): token `URLSafeTimedSerializer` válido 1 hora, salt `'password-reset-salt'`.

### Post-login redirect
```python
if usuario.permisos == 'usuario':
    redirect_url = f'/Reporte-Horas{usuario.empresa}'
else:
    redirect_url = '/tablero'
return render_template("splash.html", v=v, redirect_url=redirect_url)  # Splash intermedio
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

### Vistas (HTML)
| Ruta | Método | Auth | Descripción |
|------|--------|------|-------------|
| `/` | GET | No | Login page |
| `/` | POST | No | Autenticación |
| `/tablero` | GET/POST | Sí | Kanban con tareas por estado + filtros |
| `/tareas` | GET/POST | Sí | Lista de tareas con filtros |
| `/proyectos` | GET | Sí | Lista de proyectos |
| `/empresa` | GET/POST | Sí | CRUD de empresas (FlaskForm) |
| `/gannt` | GET/POST | Sí | Gantt global (12 meses) |
| `/gannt/<project>` | GET/POST | Sí | Gantt por proyecto |
| `/Reporte-Horas<empresa>` | GET/POST | Sí | Reporte de horas COMPLETADOS |
| `/Reporte-HorasDownload<empresa>` | GET/POST | Sí | Excel download (deprecated, reemplazado por JS) |
| `/reporte` | GET | Sí | Reporte con gráfico Plotly |
| `/reporte_horas_sulfoquimica` | GET | No | Reporte HTML Sulfoquimica |
| `/usuarios_admin` | GET | Sí | Vista admin de usuarios |
| `/Nuevo_Usuario` | GET/POST | No | Auto-registro de usuario |
| `/olvidaste` | GET/POST | No | Olvidé contraseña |
| `/reset/<token>` | GET/POST | No | Reset con token |
| `/login-otp` | GET/POST | No | Login OTP paso 1 |
| `/verify-otp` | GET/POST | No | Login OTP paso 2 |
| `/logout` | GET | Sí | Cerrar sesión |
| `/download-backup` | GET | Sí | Descarga SQLite backup |
| `/log` | GET | Sí | Visor de log (genera log.html dinámico) |
| `/upload` | POST | No | Importar tareas desde Excel |
| `/submit-description` | GET/POST | Sí | Preview markdown |
| `/render_markdown` | GET/POST | Sí | Render markdown |
| `/manifest.json` | GET | No | PWA manifest |
| `/sw.js` | GET | No | Service Worker |

### API REST (JSON)
| Ruta | Método | Descripción |
|------|--------|-------------|
| `/tareas/json` | GET | Todas las tareas |
| `/tareas/<id>` | GET | Tarea por ID |
| `/outtareas` | POST | Crear tarea (desde UI) |
| `/tareas/<id>` | PUT | Actualizar tarea completa |
| `/tareas/<id>` | DELETE | Eliminar tarea |
| `/tareas/<id>/estado` | PUT | Actualizar solo estado |
| `/actualizar_estado_tarea/<id>` | POST | Actualizar estado (kanban drag) |
| `/b/api/tareas` | GET | Búsqueda con query params |
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
| `/reporte_horas_chart` | GET | Reporte Sulfoquimica JSON |
| `/reporte_horas_chart_dev` | GET | Tabla por responsable JSON |

---

## 6. Patrones de desarrollo backend

### Manejo de errores
```python
try:
    # operacion DB
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

### Logging
```python
logging.basicConfig(filename='log.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("acción exitosa")
logging.warning("alerta")
logging.error("error con detalle")
```

### Respuestas JSON API
```python
return jsonify(modelo.serialize()), 200          # OK
return jsonify({'message': 'texto'}), 404        # Not found
return jsonify({'ok': False, 'error': '...'}), 422  # Validation
return jsonify({'ok': True}), 200                # Gantt API pattern
```

### Filtros en cadena (SQLAlchemy)
```python
query = models.Tareas.query
if estado:
    query = query.filter(models.Tareas.estado == estado)
if responsable:
    query = query.filter(models.Tareas.responsable == responsable)
tareas = query.all()
```

### Contexto inyectado en todos los templates
```python
@app.context_processor
def inject_user():
    return dict(username=session.get('username', ''))
```

### Upload de Excel (pandas)
```python
# Ruta /upload — POST con archivo Excel
df = pd.read_excel(file)
for _, row in df.iterrows():
    tarea = models.Tareas(...)
    models.db.session.add(tarea)
models.db.session.commit()
```

---

## 7. Feature: ReporteSulfoquimica

Clase en `feature/Reporte_sulfoquimica.py` que consulta la API REST de Supabase directamente.

```python
reporte = ReporteSulfoquimica(api_key, bearer_token, empresa='SULFOQUIMICA SA')
reporte.obtener_datos()       # GET a Supabase REST API
reporte.limpiar_fechas()      # Convierte fecha_inicio a datetime
reporte.filtrar_datos()       # Filtra por empresa + estado COMPLETADOS + año actual
resultado = reporte.generar_reporte()                    # Agrupado por mes/proyecto
tabla = reporte.generar_tabla_por_responsable()          # Agrupado por responsable
```

---

## 8. Formularios WTF (forms.py)

```python
class EmpresaForm(FlaskForm):
    nit = StringField('NIT', validators=[DataRequired(), Length(max=20)])
    empresa = StringField('Nombre de la Empresa', validators=[DataRequired(), Length(max=100)])

class ProyectoForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired(), Length(max=100)])
    codigo_proyecto = StringField('Código del Proyecto', validators=[DataRequired(), Length(max=50)])
    nombre_proyecto = StringField('Nombre del Proyecto', validators=[DataRequired(), Length(max=100)])
    descripcion_proyecto = TextAreaField('Descripción', validators=[DataRequired()])
```

---

## 9. Convenciones y reglas de código

## Reglas de identidad visual

- Mantener el lenguaje visual existente. No redisenar la aplicacion desde cero ni introducir otro sistema visual.
- Usar siempre la tipografia `Nunito` para la interfaz general.
- No inventar colores nuevos si el caso ya esta cubierto por la paleta de marca.
- Priorizar componentes Bootstrap/SB Admin 2 antes de crear variantes nuevas.
- Preservar consistencia entre vistas nuevas y templates existentes.

## Paleta de marca

- Primario: `#4e73df`
- Hover primario: `#2e59d9`
- Exito: `#1cc88a`
- Info: `#36b9cc`
- Advertencia: `#f6c23e`
- Peligro: `#e74a3b`
- Secundario texto: `#858796`
- Fondo pagina: `#f8f9fc`
- Bordes suaves: `#e3e6f0` y `#d1d3e2`
- Texto oscuro principal: `#3a3b45`

## Criterios para generar UI

- Todo bloque principal de contenido debe ir dentro de cards Bootstrap del estilo `card shadow mb-4`.
- Los encabezados de card deben usar `card-header py-3` con titulos en `text-primary`.
- Los formularios deben usar `form-group`, `form-control`, labels con `fw-semibold` y acciones alineadas al final.
- La accion principal debe usar `btn btn-primary`.
- Cancelar debe usar `btn btn-secondary`.
- Eliminar o acciones destructivas deben usar `btn btn-danger`.
- Exportar o descargar debe usar `btn btn-success` o `btn btn-outline-success`.
- Las tablas deben ir en `table-responsive` y usar `table table-bordered table-hover`.
- Las notificaciones importantes o confirmaciones destructivas deben usar SweetAlert2.
- Usar Font Awesome 5 para iconografia. No mezclar librerias de iconos sin necesidad.

## Layout y responsive

- Extender `templates/Base.html` para nuevas vistas salvo que exista una razon clara para no hacerlo.
- Usar el grid de Bootstrap para responsive (`col-sm-*`, `col-md-*`, `col-lg-*`).
- Validar que nuevos componentes funcionen bien en movil desde 375px en adelante.
- Respetar el patron visual actual de navbar, cards, tablas, formularios y modales.

## CSS y estilos

- Preferir clases utilitarias de Bootstrap antes que estilos inline.
- Evitar `style="..."` salvo casos puntuales y justificados.
- Mantener `border-radius` cercano a `0.35rem` en botones, inputs y cards.
- Reutilizar clases existentes en `style.css` y `sb-admin-2.css` antes de agregar clases nuevas.
- Si agregas CSS nuevo, hazlo de forma localizada, legible y consistente con el estilo existente.

## Modo oscuro

- Si tocas componentes que puedan renderizarse en modo oscuro, verificar compatibilidad con `.modo-oscuro`.
- Asegurar contraste suficiente entre texto, fondo, bordes y estados interactivos.

## Al modificar templates

- No reemplazar componentes existentes por versiones visualmente incompatibles.
- No cambiar nombres, rutas o bloques Jinja sin necesidad funcional.
- Mantener textos, labels y acciones claros y consistentes con el resto de la app.
- Cuando haya duda sobre estilo, seguir el patron mas cercano ya implementado en `templates/`.

## Prioridad de decision

Cuando haya conflicto entre ideas nuevas y la estetica actual, priorizar:

1. La estructura y componentes ya existentes en `templates/`.
2. Las reglas de [BRAND_IDENTITY.md](d:/App.Proyectos/Fofigest/BRAND_IDENTITY.md).
3. Bootstrap/SB Admin 2 tal como ya estan usados en Fofigest.

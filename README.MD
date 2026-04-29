<div align="center">
  
  <img src="static/img/logo_F-Photoroom_512.png" alt="Fofigest Logo" width="150"/>
  
  # 🚀 Fofigest
  
  ### Sistema Inteligente de Gestión de Proyectos y Tareas
  
  <p align="center">
    <strong>Gestión ágil de proyectos con control de horas, reportes avanzados y visualización Gantt en tiempo real</strong>
  </p>
  
  [![Version](https://img.shields.io/badge/version-4.0.4-blue.svg)](https://github.com/franklincaza/Fofigest)
  [![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/flask-3.0.3-red.svg)](https://flask.palletsprojects.com/)
  [![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()
  
  [🌐 Demo](#) • [📖 Documentación](#características) • [🎯 Roadmap](#roadmap) • [💬 Reportar Bug](https://github.com/franklincaza/Fofigest/issues)

</div>

---

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🎨 Capturas de Pantalla](#-capturas-de-pantalla)
- [🛠️ Tecnologías](#️-tecnologías)
- [⚡ Inicio Rápido](#-inicio-rápido)
- [📦 Instalación](#-instalación)
- [🚀 Despliegue](#-despliegue)
- [⚙️ Configuración](#️-configuración)
- [📱 PWA](#-pwa)
- [🗺️ Roadmap](#-roadmap)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

---

## ✨ Características

<div align="center">

| 🎯 **Gestión Inteligente** | 📊 **Análisis Avanzado** | 🔐 **Seguridad** |
|:--:|:--:|:--:|
| Tablero Kanban interactivo | Reportes por empresa/proyecto | Autenticación multi-nivel |
| Gestión de múltiples empresas | Gráficos Plotly dinámicos | Login OTP por email |
| Proyectos y tareas ilimitadas | Exportación a Excel | Recuperación de contraseña |
| Control de horas estimadas/dedicadas | Análisis de consumo por tipo | Permisos granulares (admin/usuario) |

</div>

### 🌟 Destacados

- **📈 Gantt Interactivo**: Visualización de cronogramas por proyecto con actualización en tiempo real
- **⏱️ Control de Horas**: Registro preciso de horas estimadas vs. dedicadas por tarea
- **🎨 Editor Rico**: Integración con CKEditor para descripciones detalladas
- **🔄 Estados Personalizables**: Sistema de estados (Pendiente → En Progreso → Revisión → Completado)
- **📧 Notificaciones Email**: Alertas automáticas y recuperación de contraseña
- **🌙 Modo Oscuro**: Interfaz adaptable para trabajo prolongado
- **📱 Progressive Web App**: Instalable en dispositivos móviles y escritorio
- **🔍 Búsqueda Avanzada**: Filtros multi-criterio en tiempo real
- **📊 Dashboard Inteligente**: Monitoreo de desempeño con Flask-MonitoringDashboard
- **💾 Backup Automático**: Descarga de respaldos de base de datos

---

## 🎨 Capturas de Pantalla

<div align="center">

### 🏠 Tablero Kanban
<img src="docs/screenshots/tablero.png" alt="Tablero Kanban" width="800"/>

### 📊 Diagrama Gantt
<img src="docs/screenshots/gantt.png" alt="Gantt Chart" width="800"/>

### 📈 Reportes de Horas
<img src="docs/screenshots/reporte.png" alt="Reportes" width="800"/>

</div>

> **Nota**: Las capturas de pantalla se actualizan con cada release

---

## 🛠️ Tecnologías

<div align="center">

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

### Frontend

![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### Librerías y Herramientas

![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Waitress](https://img.shields.io/badge/Waitress-WSGI-green?style=for-the-badge)

</div>

### 📚 Stack Completo

| Categoría | Tecnología | Versión |
|-----------|-----------|---------|
| **Framework** | Flask | 3.0.3 |
| **ORM** | SQLAlchemy | 2.0.34 |
| **Autenticación** | Flask-Login | 0.6.3 |
| **Formularios** | WTForms | 3.1.2 |
| **Editor Rico** | Flask-CKEditor | 1.0.0 |
| **Email** | Flask-Mail | 0.10.0 |
| **Tokens** | itsdangerous | 2.2.0 |
| **Templates** | Jinja2 | 3.1.4 |
| **Servidor Prod** | Waitress | 3.0.0 |
| **BD Desarrollo** | SQLite | - |
| **BD Producción** | PostgreSQL (Supabase) | - |
| **Análisis** | Pandas | 2.2.2 |
| **Gráficos** | Plotly | 5.24.1 |
| **Excel** | XlsxWriter | 3.2.0 |
| **Monitoreo** | Flask-MonitoringDashboard | 3.3.2 |
| **UI** | Bootstrap + SB Admin 2 | 5.3.3 + 4.1.3 |

---

## ⚡ Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/franklincaza/Fofigest.git
cd Fofigest

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python app.py
```

🎉 **¡Listo!** Abre tu navegador en `http://127.0.0.1:5000`

---

## 📦 Instalación

### Requisitos Previos

- **Python 3.8+** instalado
- **Git** para clonar el repositorio
- **PostgreSQL** (opcional, para producción)
- **SMTP Gmail** configurado (para notificaciones)

### Instalación Paso a Paso

#### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/franklincaza/Fofigest.git
cd Fofigest
```

#### 2️⃣ Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

#### 3️⃣ Instalar Dependencias

```bash
# Producción
pip install -r requirements.txt

# Desktop (con PyInstaller)
pip install -r requirements_desktop.txt
```

#### 4️⃣ Configurar Variables

Edita `config.py` con tus credenciales:

```python
config = {
    "debug": True,  # False para producción
    "EMAIL": "tu-email@gmail.com",
    "contraseña_google": "tu-app-password",
    "host": "http://127.0.0.1:5000/",
    "version": "4.0.4"
}
```

#### 5️⃣ Inicializar Base de Datos

```bash
# En modo desarrollo, la BD SQLite se crea automáticamente
python app.py
```

#### 6️⃣ (Opcional) Generar Claves VAPID para PWA

```bash
python generar_vapid.py
# Copia las claves generadas a config.py
```

---

## 🚀 Despliegue

### 🔧 Desarrollo Local

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar servidor Flask
python app.py
```

- **URL**: `http://127.0.0.1:5000`
- **Base de Datos**: SQLite (`instance/Empresas.db`)
- **Modo Debug**: Activado

### 🌐 Producción (Waitress)

```bash
# Configurar en config.py
config = {
    "debug": False,
    # ... otras configuraciones
}

# Ejecutar con Waitress
waitress-serve --host=0.0.0.0 --port=8080 app:app
```

- **Servidor**: Waitress WSGI
- **Base de Datos**: PostgreSQL (Supabase)
- **Modo Debug**: Desactivado

### ☁️ Despliegue en la Nube

#### Supabase (PostgreSQL)

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Obtén tu connection string
3. Actualiza `app.py`:

```python
if not config["debug"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host:port/db'
```

#### Azure

```bash
# Ejecutar script de despliegue
Deploy_azure.bat
```

#### Docker (Próximamente)

```dockerfile
# Dockerfile incluido en futuras versiones
```

### 💻 Versión Desktop

```bash
# Compilar ejecutable con PyInstaller
pyinstaller build.spec

# Ejecutar instalador
deploy_deskt.bat
```

---

## ⚙️ Configuración

### Archivo `config.py`

```python
config = {
    # Modo de ejecución
    "debug": True,  # True = Desarrollo (SQLite), False = Producción (PostgreSQL)
    
    # Email SMTP (Gmail)
    "EMAIL": "fofimaticsas@gmail.com",
    "contraseña_google": "qkyh jfuw tixt fkcs",  # App Password de Gmail
    
    # Host de la aplicación
    "host": "http://127.0.0.1:5000/",
    
    # Versión
    "version": "4.0.4",
    
    # PWA - Claves VAPID (genera con generar_vapid.py)
    "VAPID_PUBLIC_KEY": "tu-clave-publica",
    "VAPID_PRIVATE_KEY": "tu-clave-privada",
    "VAPID_EMAIL": "mailto:tu-email@gmail.com"
}
```

### Variables de Entorno (Recomendado)

```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///Empresas.db
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password
```

### Configuración de Email (Gmail)

1. Habilita la verificación en 2 pasos en tu cuenta Gmail
2. Genera una **Contraseña de Aplicación**:
   - Ir a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Selecciona "Correo" y "Otro"
   - Copia la contraseña generada (16 caracteres)
3. Pega la contraseña en `config["contraseña_google"]`

---

## 📱 PWA

Fofigest es una **Progressive Web App** instalable en dispositivos móviles y escritorio.

### Características PWA

- ✅ **Instalable**: Agrega a pantalla de inicio
- ✅ **Offline Ready**: Service Worker implementado
- ✅ **Notificaciones Push**: Con soporte VAPID
- ✅ **Responsive**: Diseño adaptable desde 375px
- ✅ **Icons**: Múltiples resoluciones (144px, 192px, 512px)

### Instalar como App

1. Abre Fofigest en Chrome/Edge
2. Clic en el ícono de instalación (⊕) en la barra de direcciones
3. Confirma "Instalar"
4. ¡Listo! Accede desde tu escritorio o app drawer

---

## 🗺️ Roadmap

### ✅ Versión 4.0 (Actual)

- [x] Sistema de autenticación completo (Login, OTP, Reset)
- [x] Tablero Kanban drag & drop
- [x] Gantt chart interactivo
- [x] Reportes de horas con Plotly
- [x] Exportación a Excel
- [x] PWA con service worker
- [x] Modo oscuro
- [x] Multi-empresa

### 🚧 Versión 4.1 (En Progreso)

- [ ] API RESTful documentada (Swagger/OpenAPI)
- [ ] Integración con calendario (Google Calendar, Outlook)
- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Chat interno por proyecto
- [ ] Sistema de comentarios en tareas
- [ ] Adjuntos de archivos

### 🔮 Versión 5.0 (Futuro)

- [ ] Dashboard con IA predictiva
- [ ] Integración con Jira/Trello (importar/exportar)
- [ ] App móvil nativa (React Native)
- [ ] Modo colaborativo en tiempo real
- [ ] Integración con GitHub/GitLab
- [ ] Facturación automática

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Aquí te explicamos cómo participar:

### 🍴 Fork del Proyecto

```bash
# 1. Haz fork del repositorio en GitHub
# 2. Clona tu fork
git clone https://github.com/TU-USUARIO/Fofigest.git
cd Fofigest

# 3. Crea una rama para tu feature
git checkout -b feature/nueva-funcionalidad

# 4. Realiza tus cambios y commitea
git add .
git commit -m "✨ Agrega nueva funcionalidad increíble"

# 5. Push a tu fork
git push origin feature/nueva-funcionalidad

# 6. Abre un Pull Request
```

### 📝 Guía de Estilo

- **Python**: Sigue [PEP 8](https://pep8.org/)
- **JavaScript**: Standard JS
- **Commits**: Usa [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` Nueva funcionalidad
  - `fix:` Corrección de bug
  - `docs:` Documentación
  - `style:` Formato, estilos
  - `refactor:` Refactorización de código
  - `test:` Tests
  - `chore:` Tareas de mantenimiento

### 🐛 Reportar Bugs

Abre un [Issue](https://github.com/franklincaza/Fofigest/issues) con:

1. **Descripción** del problema
2. **Pasos** para reproducir
3. **Resultado esperado** vs **resultado actual**
4. **Screenshots** (si aplica)
5. **Entorno**: SO, versión de Python, navegador

### 💡 Proponer Features

Abre un [Issue](https://github.com/franklincaza/Fofigest/issues) con el tag `enhancement` explicando:

1. **Problema** que resuelve
2. **Solución propuesta**
3. **Alternativas** consideradas
4. **Mockups** (opcional pero apreciado)

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**.

```
MIT License

Copyright (c) 2024 Fofimatic S.A.S.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

## 🌟 ¡Dale una Estrella!

Si Fofigest te ha sido útil, **considera darle una ⭐ en GitHub**. ¡Ayuda a que más personas descubran este proyecto!

---

### 🔗 Enlaces Rápidos

[🏠 Inicio](https://github.com/franklincaza/Fofigest) • 
[📖 Wiki](https://github.com/franklincaza/Fofigest/wiki) • 
[🐛 Reportar Bug](https://github.com/franklincaza/Fofigest/issues) • 
[💡 Nueva Idea](https://github.com/franklincaza/Fofigest/issues/new?labels=enhancement) • 
[📧 Contacto](mailto:fofimaticsas@gmail.com)

---

### 👨‍💻 Desarrollado con ❤️ por

**Fofimatic S.A.S.**

Soluciones tecnológicas para la gestión empresarial moderna

[🌐 Sitio Web](#) • [💼 LinkedIn](#) • [📧 Email](mailto:fofimaticsas@gmail.com)

---

<sub>© 2024 Fofimatic S.A.S. Todos los derechos reservados.</sub>

</div> 




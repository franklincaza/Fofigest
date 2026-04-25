# Fofigest — Referencia de Identidad de Marca (Brand Identity)

> **Uso:** Antes de crear o modificar cualquier componente de front-end (formularios, tablas, modales, botones, cards, etc.), consulta este archivo para garantizar coherencia visual con la aplicación.

---

## 1. Datos Generales

| Campo | Valor |
|---|---|
| Aplicación | Fofigest — Gestión de Proyectos y Tareas |
| Framework backend | Flask (Python) |
| Framework CSS principal | Bootstrap **5.3.3** (CDN) + SB Admin 2 v4.1.3 (local) |
| Template base | `templates/Base.html` |
| CSS personalizados | `static/css/style.css`, `static/css/sb-admin-2.css` |

---

## 2. Paleta de Colores

### 2.1 Colores Primarios de Marca

| Nombre | Hex | Uso |
|---|---|---|
| **Azul Primario** | `#4e73df` | Botones principales, enlaces activos, paginación |
| **Azul Hover** | `#2e59d9` | Estado hover de botón primario |
| **Verde Éxito** | `#1cc88a` | Indicadores de éxito, badges |
| **Cyan Info** | `#36b9cc` | Información, badges info |
| **Amarillo Advertencia** | `#f6c23e` | Alertas, badges warning |
| **Rojo Peligro** | `#e74a3b` | Errores, eliminaciones, badges danger |
| **Gris Secundario** | `#858796` | Texto secundario, botones secundarios |

### 2.2 Colores Neutros / Fondos

| Nombre | Hex | Uso |
|---|---|---|
| **Fondo página** | `#f8f9fc` | Body, card headers, bg-light |
| **Blanco** | `#ffffff` | Cards, modales, inputs |
| **Gris claro** | `#eaecf4` | Bordes suaves, breadcrumbs, inputs deshabilitados |
| **Gris borde** | `#e3e6f0` | Bordes de cards y tablas |
| **Gris borde input** | `#d1d3e2` | Bordes de form-control |
| **Gris texto** | `#858796` | Texto base del body |
| **Gris texto oscuro** | `#5a5c69` | Headers de tabla dark, btn-dark |
| **Negro texto** | `#3a3b45` | Texto dark principal |

### 2.3 Colores Personalizados (style.css)

| Nombre | Hex | Uso |
|---|---|---|
| **Logo box** | `#090909` | Fondo del contenedor circular del logo en navbar |
| **Fondo splash** | `linear-gradient(135deg, #fbfeff, #ffffff)` | Pantalla splash |
| **Gradiente original** | `linear-gradient(135deg, #00a0e3, #0077b6, #023e8a)` | Disponible para uso en headers / banners |

### 2.4 Modo Oscuro (clase `.modo-oscuro`)

| Elemento | Color |
|---|---|
| Fondo body | `#121212` |
| Cards / Modales | `#1e1e1e` |
| Texto | `#e0e0e0` |
| Inputs / Selects | `#2e2e2e` |
| Celdas tabla | `#2a2a2a` |
| Bordes inputs | `#555` |

---

## 3. Tipografía

### 3.1 Familias de Fuentes

| Rol | Fuente | Weights disponibles |
|---|---|---|
| **Fuente principal** | `Nunito` (Google Fonts) | 200, 300, 400, 600, 700, 900 |
| **Loader / Splash** | `Poppins` | 400 |
| **Fallback** | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` | — |
| **Monospace** | `SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace` | — |

**CDN Google Fonts:**
```html
<link href="https://fonts.googleapis.com/css?family=Nunito:200,300,400,600,700,900" rel="stylesheet">
```

### 3.2 Escala Tipográfica

| Elemento | Tamaño | Peso |
|---|---|---|
| `h1 / .h1` | 2.5rem (40px) | 400 |
| `h2 / .h2` | 2rem (32px) | 400 |
| `h3 / .h3` | 1.75rem (28px) | 400 |
| `h4 / .h4` | 1.5rem (24px) | 400 |
| `h5 / .h5` | 1.25rem (20px) | 400 |
| `h6 / .h6` | 1rem (16px) | 400 |
| Body base | 1rem (16px) | 400 |
| `.lead` | 1.25rem | 300 |
| `.small` / `small` | 0.875rem (80%) | 400 |
| Line-height base | 1.5 | — |

---

## 4. Espaciado

Escala base de espaciado usada en toda la aplicación:

| Token | Valor |
|---|---|
| xs | 0.25rem (4px) |
| sm | 0.375rem (6px) |
| md | 0.5rem (8px) |
| lg | 0.75rem (12px) |
| xl | 1rem (16px) |
| 2xl | 1.25rem (20px) |
| 3xl | 1.5rem (24px) |
| 4xl | 2rem (32px) |

---

## 5. Border Radius

| Componente | Radio |
|---|---|
| **Estándar** (cards, inputs, botones, badges) | `0.35rem` |
| Botones pequeños (`.btn-sm`) | `0.2rem` |
| Botones grandes (`.btn-lg`) | `0.3rem` |
| `.badge-pill` | `10rem` (completamente redondo) |
| Logo box | `50%` (círculo) |
| Gantt card | `16px` |
| Gantt container | `10px` |

---

## 6. Componentes — Estilos de Referencia

### 6.1 Botones

```html
<!-- Primario -->
<button class="btn btn-primary">Guardar</button>

<!-- Secundario -->
<button class="btn btn-secondary">Cancelar</button>

<!-- Éxito / Peligro -->
<button class="btn btn-success">Confirmar</button>
<button class="btn btn-danger">Eliminar</button>

<!-- Outline -->
<button class="btn btn-outline-primary">Ver detalles</button>

<!-- Tamaños -->
<button class="btn btn-primary btn-sm">Pequeño</button>
<button class="btn btn-primary btn-lg">Grande</button>
```

**Propiedades clave de `.btn`:**
- Padding: `0.375rem 0.75rem`
- Border-radius: `0.35rem`
- Transition: `0.15s ease-in-out`
- Focus shadow: `0 0 0 0.2rem rgba(78, 115, 223, 0.25)`

**Botón especial — expandible (`.btn-expand`):**
- Ancho inicial: `100%`, hover expande a `300px` con transición de `0.5s`

### 6.2 Formularios

```html
<div class="form-group">
  <label class="fw-semibold">Campo requerido</label>
  <input type="text" class="form-control" placeholder="Ingresa valor...">
  <small class="form-text text-muted">Texto de ayuda</small>
</div>

<!-- Input group con icono -->
<div class="input-group">
  <div class="input-group-prepend">
    <span class="input-group-text"><i class="fas fa-user"></i></span>
  </div>
  <input type="text" class="form-control" placeholder="Usuario">
</div>

<!-- Select personalizado -->
<select class="custom-select form-control">
  <option>Opción 1</option>
</select>
```

**Propiedades clave de `.form-control`:**
- Height: `calc(1.5em + 0.75rem + 2px)`
- Border: `1px solid #d1d3e2`
- Border-radius: `0.35rem`
- Color texto: `#6e707e`
- Placeholder: `#858796`
- Focus border: `#bac8f3`
- Focus shadow: `0 0 0 0.2rem rgba(78, 115, 223, 0.25)`
- Disabled background: `#eaecf4`

### 6.3 Cards

```html
<div class="card shadow mb-4">
  <div class="card-header py-3">
    <h6 class="m-0 font-weight-bold text-primary">Título de Card</h6>
  </div>
  <div class="card-body">
    Contenido aquí
  </div>
  <div class="card-footer text-muted">
    Pie de card
  </div>
</div>
```

**Propiedades clave:**
- Border: `1px solid #e3e6f0`
- Border-radius: `0.35rem`
- Card body padding: `1.25rem`
- Header/Footer background: `#f8f9fc`
- Header/Footer padding: `0.75rem 1.25rem`

### 6.4 Tablas

```html
<div class="table-responsive">
  <table class="table table-bordered table-hover">
    <thead class="thead-light">
      <tr>
        <th>Columna 1</th>
        <th>Columna 2</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Valor 1</td>
        <td>Valor 2</td>
      </tr>
    </tbody>
  </table>
</div>
```

**Propiedades clave:**
- Cell padding: `0.75rem` (`0.3rem` para `.table-sm`)
- Border color: `#e3e6f0`
- Striped alternate: `rgba(0,0,0,0.05)`
- Hover background: `rgba(0,0,0,0.075)`

### 6.5 Alertas / Notificaciones

```html
<!-- Alerta Bootstrap estática -->
<div class="alert alert-success alert-dismissible fade show" role="alert">
  Operación exitosa
  <button type="button" class="close" data-dismiss="alert">&times;</button>
</div>

<!-- SweetAlert2 (preferido para acciones importantes) -->
<script>
Swal.fire({ icon: 'success', title: 'Guardado', text: 'El registro fue guardado.' });
</script>
```

### 6.6 Badges

```html
<span class="badge badge-primary">Activo</span>
<span class="badge badge-pill badge-success">Completado</span>
<span class="badge badge-warning">Pendiente</span>
<span class="badge badge-danger">Error</span>
```

### 6.7 Paginación

```html
<nav>
  <ul class="pagination">
    <li class="page-item"><a class="page-link" href="#">Anterior</a></li>
    <li class="page-item active"><a class="page-link" href="#">1</a></li>
    <li class="page-item"><a class="page-link" href="#">2</a></li>
    <li class="page-item"><a class="page-link" href="#">Siguiente</a></li>
  </ul>
</nav>
```

### 6.8 Modales

```html
<div class="modal fade" id="miModal" tabindex="-1" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Título del Modal</h5>
        <button type="button" class="close" data-dismiss="modal">&times;</button>
      </div>
      <div class="modal-body cu-modal__body">
        <!-- Contenido (min-height: 300px) -->
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
        <button class="btn btn-primary">Guardar</button>
      </div>
    </div>
  </div>
</div>
```

### 6.9 Progress Bars

```html
<div class="progress mb-3">
  <div class="progress-bar bg-primary" style="width: 70%">70%</div>
</div>
<div class="progress mb-3">
  <div class="progress-bar bg-success progress-bar-striped" style="width: 50%"></div>
</div>
```

---

## 7. Íconos

### 7.1 Font Awesome 5.15.4

**CDN:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
```

**Íconos usados en la aplicación (referencia):**

| Ícono FA | Contexto |
|---|---|
| `fa-sign-in-alt` | Login |
| `fa-eye` / `fa-eye-slash` | Mostrar/ocultar contraseña |
| `fa-mobile-alt` | OTP / 2FA |
| `fa-bar-chart-line` | Reportes / Gantt |
| `fa-file-earmark-spreadsheet` | Exportar / Excel |
| `fa-list-task` | Tareas |
| `fa-building` | Empresas |
| `fa-kanban` | Proyectos / Kanban |
| `fa-controller` | Administración |
| `fa-database` | Base de datos |
| `fa-box-arrow-right` | Cerrar sesión |

**Uso:**
```html
<i class="fas fa-edit"></i>
<i class="fas fa-trash-alt text-danger"></i>
<i class="fas fa-plus-circle text-success"></i>
```

### 7.2 Bootstrap Icons (SVG inline)

Usado en menús de navegación (width=16, height=16, fill=currentColor).

---

## 8. Imágenes y Logos

### 8.1 Archivos de Logo

| Archivo | Ruta | Uso |
|---|---|---|
| `Logo.png` | `static/img/Logo.png` | Logo original |
| `Fofigest.png` | `static/img/Fofigest.png` | Logo en navbar y footer de todas las vistas |
| `logo_F-Photoroom.png` | `static/img/logo_F-Photoroom.png` | Logo principal editado (Photoroom) |
| `logo_F-Photoroom.ico` | `static/img/logo_F-Photoroom.ico` | Favicon del sitio |
| `logo_F-Photoroom_144.png` | `static/img/logo_F-Photoroom_144.png` | PWA icon 144×144 |
| `logo_F-Photoroom_192.png` | `static/img/logo_F-Photoroom_192.png` | PWA icon 192×192 |
| `logo_F-Photoroom_512.png` | `static/img/logo_F-Photoroom_512.png` | PWA icon 512×512 |
| `logo_F-Photoroom600.png` | `static/img/logo_F-Photoroom600.png` | 600×600 alta res |
| `logo_F-Photoroom1200.png` | `static/img/logo_F-Photoroom1200.png` | 1200×1200 máxima res |
| `building-icon-1200x1200 (1).png` | `static/img/building-icon-1200x1200 (1).png` | Ícono de empresa/edificio |

### 8.2 Uso del Logo en Templates

```html
<!-- Navbar -->
<img src="{{ url_for('static', filename='img/Fofigest.png') }}" height="40" alt="Fofigest">

<!-- Favicon (en <head>) -->
<link rel="icon" href="{{ url_for('static', filename='img/logo_F-Photoroom.ico') }}" type="image/x-icon">
```

### 8.3 Contenedor de Logo (`.logo-container` + `.logo-box`)

```html
<div class="logo-container">
  <div class="logo-box">
    <!-- Fondo circular negro (#090909), 30×30px, border-radius 50% -->
    <img src="..." alt="Logo">
  </div>
</div>
```

---

## 9. Librerías Externas (CDN)

| Librería | Versión | CDN / Uso |
|---|---|---|
| Bootstrap CSS | 5.3.3 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css` |
| Bootstrap JS | 5.3.3 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js` |
| Font Awesome | 5.15.4 | `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css` |
| Google Fonts (Nunito) | — | `https://fonts.googleapis.com/css?family=Nunito:200,300,400,600,700,900` |
| jQuery | 3.6.0 | `https://code.jquery.com/jquery-3.6.0.min.js` |
| SweetAlert2 | 11 | `https://cdn.jsdelivr.net/npm/sweetalert2@11` |
| Frappe Gantt | latest | `https://unpkg.com/frappe-gantt/dist/frappe-gantt.umd.js` |
| SB Admin 2 | 4.1.3 | `static/css/sb-admin-2.css` (local) |

---

## 10. Diseño Responsivo — Breakpoints

| Breakpoint | Ancho mínimo | Clase Bootstrap |
|---|---|---|
| Extra small | 0px | (default) |
| Small | 576px | `col-sm-*` |
| Medium | 768px | `col-md-*` |
| Large | 992px | `col-lg-*` |
| Extra large | 1200px | `col-xl-*` |

**Comportamiento especial:**
- En móvil landscape (max-width: 768px + orientación landscape): se muestra mensaje "gira tu dispositivo" y se oculta `#contenido-principal`.
- La navegación usa `offcanvas drawer` en móvil.

---

## 11. Animaciones y Transiciones

| Elemento | Valor |
|---|---|
| Transición estándar de componentes | `0.15s ease-in-out` |
| Progress bar fill | `width 0.6s ease` |
| `.btn-expand` hover | `width 0.5s ease-in-out` |
| Logo hover (navbar) | `transform: scale(1.05)` |
| Splash word cycle | `10s infinite` (animación CSS) |
| Fade-in splash | `1s ease-in-out` |
| Zoom-in splash | `0.8s ease-out` |
| `prefers-reduced-motion` | Todas las transiciones se deshabilitan |

---

## 12. Sombras

| Uso | Valor CSS |
|---|---|
| Cards estándar | `class="shadow"` (Bootstrap) |
| Cards sutiles | `class="shadow-sm"` |
| Card de login | `box-shadow: 0 4px 20px rgba(0,0,0,0.25)` |
| Gantt card | `box-shadow: 0 0 20px rgba(0,0,0,0.05)` |
| Foco de inputs/botones | `0 0 0 0.2rem rgba(78, 115, 223, 0.25)` |

---

## 13. Reglas de Diseño para Nuevos Componentes

Al crear cualquier componente nuevo (formulario, tabla, modal, card, etc.) seguir estas reglas:

1. **Tipografía:** Usar siempre `font-family: 'Nunito', sans-serif`. La fuente ya está cargada globalmente.

2. **Colores:** No inventar colores nuevos. Usar los de la paleta definida en la sección 2. Para estados: primary=`#4e73df`, success=`#1cc88a`, warning=`#f6c23e`, danger=`#e74a3b`.

3. **Cards:** Todo bloque de contenido va dentro de `<div class="card shadow mb-4">`. Incluir `card-header` con título en `text-primary font-weight-bold`.

4. **Formularios:** Usar siempre `form-group` + `form-control`. Labels con clase `fw-semibold`. Agrupar botones de acción en `d-flex justify-content-end gap-2` al final del form.

5. **Botones:** Acción principal = `btn-primary`. Cancelar = `btn-secondary`. Eliminar = `btn-danger`. Exportar/descargar = `btn-success` o `btn-outline-success`.

6. **Tablas:** Siempre dentro de `<div class="table-responsive">`. Usar `table table-bordered table-hover`. Headers con `thead-light`.

7. **Íconos:** Usar Font Awesome 5 (`fas`, `far`, `fab`). No mezclar con otras librerías de íconos.

8. **Alertas/Notificaciones:** Para confirmaciones destructivas usar SweetAlert2. Para mensajes flash usar `.alert` de Bootstrap con `alert-dismissible`.

9. **Modo oscuro:** Si el template puede estar en modo oscuro, validar que los colores de texto/fondo sean legibles con la clase `.modo-oscuro`.

10. **Border-radius:** Usar siempre `0.35rem` para inputs, cards y botones (ya está en Bootstrap/SB Admin). No usar valores arbitrarios.

11. **Responsive:** Usar el grid de Bootstrap (`col-md-*`, `col-lg-*`). Probar siempre en mobile (375px+).

12. **Espaciado:** Usar clases de utilidad Bootstrap (`mb-3`, `mt-4`, `py-3`, `px-4`, etc.). No usar `margin`/`padding` inline salvo casos excepcionales.

---

## 14. Estructura de Template Estándar

```html
{% extends "Base.html" %}
{% block content %}

<!-- Título de página -->
<div class="d-sm-flex align-items-center justify-content-between mb-4">
  <h1 class="h3 mb-0 text-gray-800">Título de la Sección</h1>
  <button class="btn btn-sm btn-primary shadow-sm">
    <i class="fas fa-plus fa-sm text-white-50"></i> Nueva acción
  </button>
</div>

<!-- Contenido principal -->
<div class="row">
  <div class="col-12">
    <div class="card shadow mb-4">
      <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">Subtítulo</h6>
      </div>
      <div class="card-body">
        <!-- Contenido aquí -->
      </div>
    </div>
  </div>
</div>

{% endblock %}
```

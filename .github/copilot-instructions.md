# Instrucciones de Copilot para Fofigest

Estas instrucciones aplican a todo el proyecto. Usa [BRAND_IDENTITY.md](d:/App.Proyectos/Fofigest/BRAND_IDENTITY.md) como referencia maestra cuando generes o modifiques interfaz, estilos o templates.

## Contexto del proyecto

- La aplicacion es Fofigest, un sistema de gestion de proyectos y tareas con Flask.
- El layout base vive en `templates/Base.html`.
- La UI usa Bootstrap 5.3.3 y SB Admin 2 v4.1.3.
- Los estilos personalizados viven principalmente en `static/css/style.css` y `static/css/sb-admin-2.css`.

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

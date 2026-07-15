#!/usr/bin/env python3
"""
Fofigest MCP Server — v1.0
Servidor MCP oficial para Fofigest. Permite a los usuarios de la app interactuar
con tareas y proyectos directamente desde Claude Desktop / VSCode / cualquier
cliente MCP compatible.

Seguridad:
  - Se autentica contra el servidor Fofigest usando una API Key personal.
  - Los permisos del usuario en la app se aplican en el servidor (no en este script).
  - Este archivo nunca contiene contraseñas ni datos sensibles.

Instalación:
  pip install mcp httpx

Configuración inicial (una sola vez):
  1. Inicia sesión en Fofigest → Mis API Keys → Generar nueva clave.
  2. Crea el archivo ~/.fofigest_mcp.json con:
     {
       "server_url": "http://tu-servidor-fofigest:5000",
       "api_key": "fgt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     }

Configuración en Claude Desktop (claude_desktop_config.json):
  {
    "mcpServers": {
      "fofigest": {
        "command": "python",
        "args": ["ruta/completa/a/mcp_fofigest.py"]
      }
    }
  }

Configuración en VSCode (.vscode/mcp.json):
  {
    "servers": {
      "fofigest": {
        "type": "stdio",
        "command": "python",
        "args": ["${workspaceFolder}/mcp_fofigest.py"]
      }
    }
  }
"""

import json
import os
import sys

# ── Dependencias (instala con: pip install mcp httpx) ─────────────────────────
try:
    import httpx
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(
        f"[Fofigest MCP] Dependencias faltantes: {e}\n"
        "Ejecuta: pip install mcp httpx",
        file=sys.stderr,
    )
    sys.exit(1)

# ── Configuración ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".fofigest_mcp.json")
PORT_FILE   = os.path.join(os.path.expanduser("~"), ".fofigest_port")


def _load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"Archivo de configuración no encontrado: {CONFIG_PATH}\n"
            "Crea el archivo con el contenido:\n"
            "{\n"
            '  "server_url": "http://127.0.0.1:5000",\n'
            '  "api_key": "fgt_..."\n'
            "}\n"
            "Genera tu API key en Fofigest → Mis API Keys."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    if "server_url" not in cfg or "api_key" not in cfg:
        raise ValueError(
            f"El archivo {CONFIG_PATH} debe tener los campos 'server_url' y 'api_key'."
        )
    # Auto-descubrir puerto para instalaciones de escritorio (EXE).
    # El EXE escribe ~/.fofigest_port con el puerto activo en cada arranque.
    # Solo aplica cuando server_url apunta a localhost.
    is_local = any(h in cfg["server_url"] for h in ("127.0.0.1", "localhost"))
    if is_local and os.path.exists(PORT_FILE):
        try:
            port = int(open(PORT_FILE, encoding="utf-8").read().strip())
            cfg["server_url"] = f"http://127.0.0.1:{port}"
        except Exception:
            pass  # Mantener el server_url original si el archivo es ilegible
    return cfg


try:
    _cfg = _load_config()
    _BASE_URL = _cfg["server_url"].rstrip("/")
    _HEADERS = {
        "X-Fofigest-API-Key": _cfg["api_key"],
        "Content-Type":       "application/json",
        "Accept":             "application/json",
    }
except Exception as _e:
    print(f"[Fofigest MCP] Error de configuración: {_e}", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP(
    "Fofigest",
    instructions=(
        "Servidor MCP de Fofigest para gestión de tareas y proyectos. "
        "Los permisos disponibles dependen del rol del usuario autenticado. "
        "Usa mi_perfil() para ver qué herramientas están habilitadas para tu cuenta."
    ),
)

# ── Helpers HTTP ───────────────────────────────────────────────────────────────


def _get(path: str, params: dict = None) -> dict:
    r = httpx.get(f"{_BASE_URL}{path}", headers=_HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, data: dict) -> dict:
    r = httpx.post(f"{_BASE_URL}{path}", headers=_HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def _patch(path: str, data: dict) -> dict:
    r = httpx.patch(f"{_BASE_URL}{path}", headers=_HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def _delete(path: str) -> dict:
    r = httpx.delete(f"{_BASE_URL}{path}", headers=_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _err(e: httpx.HTTPStatusError) -> str:
    try:
        body = e.response.json()
        return body.get("error", body.get("message", str(body)))
    except Exception:
        return str(e)


# ══════════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS MCP
# ══════════════════════════════════════════════════════════════════════════════

# ── Identidad ─────────────────────────────────────────────────────────────────


@mcp.tool()
def mi_perfil() -> str:
    """
    Muestra la información del usuario autenticado: nombre, rol, empresa y las
    herramientas MCP disponibles para su nivel de permisos.
    """
    try:
        d = _get("/api/mcp/me")
        u = d["usuario"]
        tools = d.get("herramientas", [])
        return (
            f"Usuario:   {u['nombres']} {u['apellidos']}\n"
            f"Correo:    {u['correo']}\n"
            f"Rol:       {u['permisos']}\n"
            f"Empresa:   {u['empresa']}\n\n"
            f"Herramientas disponibles ({len(tools)}):\n"
            + "\n".join(f"  • {t}" for t in tools)
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


# ── CRUD Tareas ───────────────────────────────────────────────────────────────


@mcp.tool()
def listar_tareas(
    proyecto: str = None,
    estado: str = None,
    responsable: str = None,
    empresa: str = None,
    mes: str = None,
) -> str:
    """
    Lista las tareas disponibles según permisos. Admite filtros opcionales.

    Args:
        proyecto:    Código del proyecto (ej: 'PRY-001').
        estado:      PENDIENTE | PROGRESO | REVISIÓN | IMPEDIMENTOS | COMPLETADOS
        responsable: Email o nombre del responsable asignado.
        empresa:     Nombre de la empresa (admin/dev pueden ver todas).
        mes:         Mes de la tarea (Enero, Febrero … Diciembre).
    """
    try:
        params = {}
        if proyecto:    params["proyecto"]    = proyecto
        if estado:      params["estado"]      = estado
        if responsable: params["responsable"] = responsable
        if empresa:     params["empresa"]     = empresa
        if mes:         params["mes"]         = mes
        d = _get("/api/mcp/tareas", params)
        tareas = d.get("tareas", [])
        if not tareas:
            return "No se encontraron tareas con los filtros indicados."
        lines = [f"Tareas encontradas: {len(tareas)}\n"]
        for t in tareas:
            lines.append(f"[{t['codigo_tarea']}] {t['titulo']}")
            lines.append(
                f"  Estado: {t['estado']}  |  Proyecto: {t['codigo_proyecto']}  "
                f"|  Responsable: {t['responsable']}"
            )
            lines.append(
                f"  Horas: {t['horas_dedicadas']}/{t['horas_estimadas']}h  "
                f"|  Empresa: {t['empresa']}"
            )
            if t.get("fecha_fin"):
                lines.append(f"  Fecha fin: {t['fecha_fin']}")
            lines.append("")
        return "\n".join(lines).strip()
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def obtener_tarea(codigo_tarea: str) -> str:
    """
    Obtiene el detalle completo de una tarea por su código único.

    Args:
        codigo_tarea: Código único de la tarea (ej: 'T-001').
    """
    try:
        d = _get(f"/api/mcp/tareas/{codigo_tarea}")
        t = d["tarea"]
        lines = [
            f"TAREA: {t['titulo']}",
            f"Código:           {t['codigo_tarea']}",
            f"Proyecto:         {t['codigo_proyecto']}  |  Empresa: {t['empresa']}",
            f"Estado:           {t['estado']}",
            f"Responsable:      {t['responsable']}",
            f"Horas estimadas:  {t['horas_estimadas']}h  |  Horas dedicadas: {t['horas_dedicadas']}h",
            f"Fecha inicio:     {t['fecha_inicio']}  |  Fecha fin: {t.get('fecha_fin') or 'Sin definir'}",
            f"Tipo consumo:     {t['tipo_consumo']}  |  Mes: {t['mes']}",
            f"Facturada:        {'Sí' if t['facturada'] else 'No'}",
        ]
        if t.get("descripcion"):
            lines.append(f"\nDescripción:\n{t['descripcion'][:600]}")
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def crear_tarea(
    empresa: str,
    codigo_proyecto: str,
    codigo_tarea: str,
    titulo: str,
    descripcion: str,
    fecha_inicio: str,
    responsable: str,
    horas_estimadas: float,
    tipo_consumo: str = "Desarrollo",
    mes: str = "Enero",
    estado: str = "PENDIENTE",
    fecha_fin: str = None,
) -> str:
    """
    Crea una nueva tarea. Requiere rol admin o dev.

    Args:
        empresa:         Empresa cliente a la que pertenece la tarea.
        codigo_proyecto: Código del proyecto (debe existir).
        codigo_tarea:    Código único para la nueva tarea (ej: 'T-045').
        titulo:          Título descriptivo de la tarea.
        descripcion:     Descripción detallada del trabajo a realizar.
        fecha_inicio:    Fecha de inicio en formato YYYY-MM-DD.
        responsable:     Email del usuario responsable.
        horas_estimadas: Horas estimadas para completar la tarea.
        tipo_consumo:    Desarrollo | Reuniones | Desarrollo por control de cambio |
                         Soporte | Oportunidad de mejora
        mes:             Mes de facturación (Enero … Diciembre). Default: Enero.
        estado:          PENDIENTE | PROGRESO | REVISIÓN | IMPEDIMENTOS | COMPLETADOS.
                         Default: PENDIENTE.
        fecha_fin:       Fecha límite en formato YYYY-MM-DD (opcional).
    """
    try:
        payload = {
            "empresa": empresa, "codigo_proyecto": codigo_proyecto,
            "codigo_tarea": codigo_tarea, "titulo": titulo,
            "descripcion": descripcion, "fecha_inicio": fecha_inicio,
            "responsable": responsable, "horas_estimadas": horas_estimadas,
            "tipo_consumo": tipo_consumo, "mes": mes, "estado": estado,
        }
        if fecha_fin:
            payload["fecha_fin"] = fecha_fin
        d = _post("/api/mcp/tareas", payload)
        t = d["tarea"]
        return (
            f"Tarea creada exitosamente.\n"
            f"Código:      {t['codigo_tarea']}\n"
            f"Título:      {t['titulo']}\n"
            f"Estado:      {t['estado']}\n"
            f"Responsable: {t['responsable']}\n"
            f"Proyecto:    {t['codigo_proyecto']}"
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def actualizar_tarea(
    codigo_tarea: str,
    titulo: str = None,
    descripcion: str = None,
    responsable: str = None,
    horas_estimadas: float = None,
    fecha_fin: str = None,
    tipo_consumo: str = None,
    mes: str = None,
) -> str:
    """
    Actualiza campos de una tarea existente (actualización parcial). Requiere rol admin o dev.
    Solo se modifican los campos que se proporcionen.

    Args:
        codigo_tarea:    Código de la tarea a actualizar.
        titulo:          Nuevo título.
        descripcion:     Nueva descripción.
        responsable:     Email del nuevo responsable.
        horas_estimadas: Nuevas horas estimadas.
        fecha_fin:       Nueva fecha límite en formato YYYY-MM-DD.
        tipo_consumo:    Nuevo tipo de consumo.
        mes:             Nuevo mes de facturación.
    """
    try:
        payload = {}
        if titulo           is not None: payload["titulo"]           = titulo
        if descripcion      is not None: payload["descripcion"]      = descripcion
        if responsable      is not None: payload["responsable"]      = responsable
        if horas_estimadas  is not None: payload["horas_estimadas"]  = horas_estimadas
        if fecha_fin        is not None: payload["fecha_fin"]        = fecha_fin
        if tipo_consumo     is not None: payload["tipo_consumo"]     = tipo_consumo
        if mes              is not None: payload["mes"]              = mes
        if not payload:
            return "No se proporcionaron campos para actualizar."
        d = _patch(f"/api/mcp/tareas/{codigo_tarea}", payload)
        t = d["tarea"]
        cambios = list(payload.keys())
        return (
            f"Tarea {codigo_tarea} actualizada.\n"
            f"Campos modificados: {', '.join(cambios)}\n"
            f"Título:      {t['titulo']}\n"
            f"Responsable: {t['responsable']}\n"
            f"Estado:      {t['estado']}"
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def eliminar_tarea(codigo_tarea: str, confirmar: bool = False) -> str:
    """
    Elimina permanentemente una tarea. Solo admin/superadmin.
    La tarea no puede estar facturada. Esta acción es irreversible.

    Args:
        codigo_tarea: Código de la tarea a eliminar.
        confirmar:    Debe ser True para ejecutar la eliminación.
                      Si es False (default) se muestra un mensaje de confirmación.
    """
    if not confirmar:
        return (
            f"Estás a punto de eliminar la tarea '{codigo_tarea}'. "
            "Esta acción es IRREVERSIBLE. "
            "Llama de nuevo con confirmar=True para proceder."
        )
    try:
        d = _delete(f"/api/mcp/tareas/{codigo_tarea}")
        return d.get("message", f"Tarea {codigo_tarea} eliminada.")
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def cambiar_estado_tarea(codigo_tarea: str, nuevo_estado: str) -> str:
    """
    Cambia el estado de ejecución de una tarea. Requiere rol admin o dev.
    IMPORTANTE: mover una tarea a COMPLETADOS requiere rol admin — los usuarios
    con rol dev no pueden usar ese estado destino.

    Args:
        codigo_tarea: Código de la tarea.
        nuevo_estado: PENDIENTE | PROGRESO | REVISIÓN | IMPEDIMENTOS | COMPLETADOS
                      (COMPLETADOS solo disponible para admin)
    """
    try:
        d = _patch(f"/api/mcp/tareas/{codigo_tarea}/estado", {"estado": nuevo_estado})
        t = d["tarea"]
        return (
            f"Estado de '{codigo_tarea}' actualizado a {t['estado']}.\n"
            f"Tarea: {t['titulo']} | Responsable: {t['responsable']}"
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def registrar_horas(codigo_tarea: str, horas: float, nota: str = None) -> str:
    """
    Registra horas trabajadas en una tarea (suma al total actual).
    Admin/dev pueden registrar en cualquier tarea. Los usuarios 'usuario' solo
    pueden registrar horas en tareas donde son el responsable.

    Args:
        codigo_tarea: Código de la tarea.
        horas:        Número de horas a agregar (puede ser decimal, ej: 1.5).
        nota:         Nota opcional describiendo el trabajo realizado (no se persiste,
                      solo sirve como contexto para el registro de trazabilidad).
    """
    try:
        payload = {"horas": horas}
        if nota:
            payload["nota"] = nota
        d = _patch(f"/api/mcp/tareas/{codigo_tarea}/horas", payload)
        t = d["tarea"]
        pct = d["tarea"].get("porcentaje_completado", 0)
        return (
            f"{horas}h registradas en '{codigo_tarea}'.\n"
            f"Total acumulado: {t['horas_dedicadas']}h / {t['horas_estimadas']}h estimadas "
            f"({pct}% del tiempo estimado consumido)"
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def asignar_tarea(codigo_tarea: str, responsable: str) -> str:
    """
    Asigna o reasigna una tarea a un responsable. Requiere rol admin o dev.
    Se envía notificación automática al nuevo responsable.

    Args:
        codigo_tarea: Código de la tarea a reasignar.
        responsable:  Email del nuevo responsable.
    """
    try:
        d = _patch(f"/api/mcp/tareas/{codigo_tarea}", {"responsable": responsable})
        t = d["tarea"]
        return (
            f"Tarea '{codigo_tarea}' asignada a {t['responsable']}.\n"
            f"Título: {t['titulo']} | Estado: {t['estado']}"
        )
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


# ── Proyectos ─────────────────────────────────────────────────────────────────


@mcp.tool()
def listar_proyectos(empresa: str = None) -> str:
    """
    Lista todos los proyectos accesibles según permisos del usuario.
    Los usuarios 'usuario' solo ven proyectos de su propia empresa.

    Args:
        empresa: Filtrar por empresa (solo admin/dev pueden ver otras empresas).
    """
    try:
        params = {}
        if empresa:
            params["empresa"] = empresa
        d = _get("/api/mcp/proyectos", params)
        proyectos = d.get("proyectos", [])
        if not proyectos:
            return "No se encontraron proyectos."
        lines = [f"Proyectos encontrados: {len(proyectos)}\n"]
        for p in proyectos:
            lines.append(f"[{p['codigo_proyecto']}] {p['nombre_proyecto']}")
            lines.append(f"  Empresa: {p['empresa']}")
            if p.get("descripcion_proyecto"):
                lines.append(f"  Descripción: {p['descripcion_proyecto'][:120]}")
            lines.append("")
        return "\n".join(lines).strip()
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


@mcp.tool()
def resumen_proyecto(codigo_proyecto: str) -> str:
    """
    Genera un resumen completo de un proyecto: duración estimada, progreso,
    distribución de estados, horas estimadas vs. reales y equipo asignado.

    Args:
        codigo_proyecto: Código único del proyecto (ej: 'PRY-001').
    """
    try:
        d = _get(f"/api/mcp/proyectos/{codigo_proyecto}/resumen")
        p = d["proyecto"]
        r = d["resumen"]
        lines = [
            f"PROYECTO: {p['nombre_proyecto']} [{p['codigo_proyecto']}]",
            f"Empresa: {p['empresa']}",
            "",
            "── PROGRESO ──────────────────────────────",
            f"Total tareas:      {r['total_tareas']}",
            f"  Pendiente:       {r['por_estado'].get('PENDIENTE',    0)}",
            f"  En progreso:     {r['por_estado'].get('PROGRESO',     0)}",
            f"  En revisión:     {r['por_estado'].get('REVISIÓN',     0)}",
            f"  Con impedimentos:{r['por_estado'].get('IMPEDIMENTOS', 0)}",
            f"  Completadas:     {r['por_estado'].get('COMPLETADOS',  0)}",
            f"Completado:        {r['porcentaje_completado']}%",
            "",
            "── HORAS ─────────────────────────────────",
            f"Estimadas:  {r['horas_estimadas_total']}h",
            f"Dedicadas:  {r['horas_dedicadas_total']}h",
            f"Restantes:  {r['horas_restantes']}h",
        ]
        if r.get("fecha_inicio_proyecto"):
            lines += [
                "",
                "── FECHAS ────────────────────────────────",
                f"Inicio estimado:   {r['fecha_inicio_proyecto']}",
                f"Fin estimado:      {r.get('fecha_fin_proyecto') or 'Sin definir'}",
            ]
            if r.get("duracion_dias") is not None:
                lines.append(f"Duración total:    {r['duracion_dias']} días")
        if r.get("responsables"):
            lines += ["", "── EQUIPO ────────────────────────────────"]
            for resp, count in sorted(r["responsables"].items(), key=lambda x: -x[1]):
                lines.append(f"  {resp}: {count} tarea(s)")
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


# ── Usuarios (admin/dev) ──────────────────────────────────────────────────────


@mcp.tool()
def listar_usuarios(rol: str = None) -> str:
    """
    Lista los usuarios del sistema. Solo disponible para admin y dev.

    Args:
        rol: Filtrar por rol: admin | superadmin | dev | usuario | nuevo
    """
    try:
        params = {}
        if rol:
            params["rol"] = rol
        d = _get("/api/mcp/usuarios", params)
        usuarios = d.get("usuarios", [])
        if not usuarios:
            return "No se encontraron usuarios."
        lines = [f"Usuarios: {len(usuarios)}\n"]
        for u in usuarios:
            nombre = f"{u['nombres']} {u['apellidos']}".strip()
            lines.append(f"• {nombre} <{u['correo']}> — {u['permisos']} [{u['empresa']}]")
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {_err(e)}"


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()

# Contexto MCP — Fofigest

## ¿Qué es el MCP de Fofigest?

El servidor MCP (Model Context Protocol) de Fofigest permite a los usuarios de la aplicación
interactuar con tareas y proyectos directamente desde su asistente de IA (Claude Desktop, VSCode,
Cursor, etc.) sin exponer contraseñas ni datos sensibles.

---

## Arquitectura de seguridad

```
Claude Desktop / VSCode
        │ stdio (proceso local)
        ▼
mcp_fofigest.py  ← script distribuible, solo necesita httpx + mcp
        │ HTTP  X-Fofigest-API-Key
        ▼
Flask /api/mcp/* ← valida la clave, carga el usuario, aplica RBAC
        │
        ▼
Base de datos (SQLite / PostgreSQL Supabase)
```

**Principios clave:**
- El archivo `mcp_fofigest.py` nunca se conecta directamente a la BD. Solo llama a la API Flask.
- Las API Keys se almacenan como hashes SHA-256 (irreversibles) en la tabla `api_keys`.
- Los permisos se aplican siempre en el servidor (RBAC del lado del servidor), nunca solo en el cliente.
- Una API Key comprometida puede revocarse desde la UI en `/mis-api-keys` sin afectar la cuenta.

---

## Tabla de permisos por rol

| Herramienta MCP       | admin / superadmin | dev | usuario | nuevo |
|-----------------------|--------------------|-----|---------|-------|
| `mi_perfil`           | ✓                  | ✓   | ✓       | ✗     |
| `listar_tareas`       | Todas              | Todas | Solo su empresa | ✗ |
| `obtener_tarea`       | Todas              | Todas | Solo su empresa | ✗ |
| `crear_tarea`         | ✓                  | ✓   | ✗       | ✗     |
| `actualizar_tarea`    | ✓                  | ✓   | ✗       | ✗     |
| `eliminar_tarea`      | ✓                  | ✗   | ✗       | ✗     |
| `cambiar_estado_tarea`| Todos los estados  | Solo PENDIENTE/PROGRESO/REVISIÓN/IMPEDIMENTOS | ✗ | ✗ |
| `registrar_horas`     | ✓                  | ✓   | Solo si es responsable (misma empresa) | ✗ |
| `asignar_tarea`       | ✓                  | ✓   | ✗       | ✗     |
| `listar_proyectos`    | Todos              | Todos | Solo su empresa | ✗ |
| `resumen_proyecto`    | Todos              | Todos | Solo su empresa | ✗ |
| `listar_usuarios`     | ✓                  | ✓   | ✗       | ✗     |

**Notas de restricción:**
- **COMPLETADOS**: solo `admin`/`superadmin` puede mover tareas a este estado desde el MCP.
- **eliminar_tarea**: exclusivo de `admin`/`superadmin`; las tareas facturadas no se pueden eliminar.
- **usuario**: todas las herramientas de lectura filtran automáticamente por la empresa del usuario; no puede crear, actualizar, eliminar ni cambiar estado.

---

## Archivos involucrados

| Archivo | Propósito |
|---------|-----------|
| `mcp_fofigest.py` | Servidor MCP distribuible. Se entrega a los usuarios. |
| `models/models.py` → `ApiKey` | Modelo de BD para almacenar API Keys (hash). |
| `app.py` → `require_api_key` | Decorador que valida el header `X-Fofigest-API-Key`. |
| `app.py` → `/api/mcp/*` | Endpoints REST protegidos por RBAC para las herramientas MCP. |
| `app.py` → `/api/auth/apikey` | CRUD de API Keys (requiere sesión web activa). |
| `app.py` → `/mis-api-keys` | Vista HTML para gestionar las claves. |
| `templates/mis_api_keys.html` | UI para generar y revocar claves. |

---

## Tabla de BD: `api_keys`

```sql
CREATE TABLE api_keys (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES usuarios(id),
    key_hash   VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 del token
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used  TIMESTAMP,
    is_active  BOOLEAN DEFAULT TRUE
);
```

---

## Endpoints REST de la API MCP

### Gestión de API Keys (requieren sesión web)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/mis-api-keys` | Vista HTML de gestión |
| POST | `/api/auth/apikey` | Crear nueva clave → retorna el token (una sola vez) |
| GET | `/api/auth/apikey` | Listar mis claves (sin mostrar el token) |
| DELETE | `/api/auth/apikey/<id>` | Revocar clave |

### Endpoints MCP (requieren header `X-Fofigest-API-Key`)

| Método | Ruta | Herramienta MCP |
|--------|------|-----------------|
| GET | `/api/mcp/me` | `mi_perfil` |
| GET | `/api/mcp/tareas` | `listar_tareas` |
| GET | `/api/mcp/tareas/<codigo>` | `obtener_tarea` |
| POST | `/api/mcp/tareas` | `crear_tarea` |
| PATCH | `/api/mcp/tareas/<codigo>` | `actualizar_tarea`, `asignar_tarea` |
| DELETE | `/api/mcp/tareas/<codigo>` | `eliminar_tarea` |
| PATCH | `/api/mcp/tareas/<codigo>/estado` | `cambiar_estado_tarea` |
| PATCH | `/api/mcp/tareas/<codigo>/horas` | `registrar_horas` |
| GET | `/api/mcp/proyectos` | `listar_proyectos` |
| GET | `/api/mcp/proyectos/<codigo>/resumen` | `resumen_proyecto` |
| GET | `/api/mcp/usuarios` | `listar_usuarios` |

---

## Cómo distribuir el MCP a los usuarios

### Paso 1 — El usuario genera su API Key
1. Inicia sesión en Fofigest.
2. Navega a `/mis-api-keys` (o busca "Mis API Keys" en el menú de perfil).
3. Dale un nombre descriptivo (ej: "Claude Desktop") y haz clic en **Generar**.
4. **Copia la clave inmediatamente** — no se puede ver de nuevo.

### Paso 2 — Crear el archivo de configuración
Guarda en `~/.fofigest_mcp.json`:
```json
{
  "server_url": "http://IP-O-DOMINIO-DEL-SERVIDOR:5000",
  "api_key": "fgt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

En Linux/Mac, protege el archivo:
```bash
chmod 600 ~/.fofigest_mcp.json
```

### Paso 3 — Instalar dependencias
```bash
pip install mcp httpx
```

### Paso 4 — Configurar el cliente MCP

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json` o equivalente):
```json
{
  "mcpServers": {
    "fofigest": {
      "command": "python",
      "args": ["/ruta/completa/a/mcp_fofigest.py"]
    }
  }
}
```

**VSCode** (`.vscode/mcp.json` o en settings globales):
```json
{
  "servers": {
    "fofigest": {
      "type": "stdio",
      "command": "python",
      "args": ["/ruta/completa/a/mcp_fofigest.py"]
    }
  }
}
```

---

## Ejemplos de uso con Claude

```
Usuario: "¿Cuántas tareas tiene el proyecto PRY-001 y cuál es su progreso?"
Claude: [llama resumen_proyecto(codigo_proyecto='PRY-001')]
→ Muestra total, distribución por estado, horas, fechas y equipo.

Usuario: "Crea una tarea de soporte para Empresa ABC en el proyecto PRY-002"
Claude: [llama crear_tarea(...)]
→ Crea la tarea y notifica al responsable.

Usuario: "Marca la tarea T-045 como completada"
Claude: [llama cambiar_estado_tarea(codigo_tarea='T-045', nuevo_estado='COMPLETADOS')]
→ Actualiza el estado y registra la trazabilidad.

Usuario: "Registra 2.5 horas en la tarea T-033"
Claude: [llama registrar_horas(codigo_tarea='T-033', horas=2.5)]
→ Suma las horas y muestra el progreso acumulado.
```

---

## Seguridad: qué NO puede hacer el MCP

- **No puede** acceder directamente a la base de datos.
- **No puede** ver contraseñas de usuarios ni tokens de sesión.
- **No puede** realizar acciones fuera del alcance del rol del usuario.
- **No puede** crear/modificar API Keys (solo la sesión web puede).
- **No puede** acceder a datos de empresas que no correspondan al rol del usuario.
- Las tareas facturadas o pagadas están protegidas contra modificación, igual que en la app web.

---

## Trazabilidad

Todas las operaciones de escritura del MCP quedan registradas en la tabla `trazabilidad_tarea`
con el correo y rol del usuario de la API Key, marcadas con `empresa_usuario` y la IP del cliente.
Esto es idéntico al comportamiento de la app web.

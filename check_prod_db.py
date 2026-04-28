"""
Diagnóstico de la BD de producción (Supabase).
Verifica tablas y columnas requeridas por el módulo de cobro.
"""
import psycopg2

URI = 'postgresql://postgres.wlvgmwuhfunnpddcgvzu:I0P2EdBGUabioCtA@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

TABLAS_REQUERIDAS = [
    'cuenta_cobro',
    'detalle_cuenta_cobro',
    'colilla_pago',
    'confirmacion_pago',
    'perfil_pago',
]

COLUMNAS_REQUERIDAS = {
    'tareas': ['facturada', 'cuenta_cobro_id'],
    'perfil_pago': ['firma_imagen'],
    'cuenta_cobro': ['numero_cuenta', 'usuario_id', 'empresa_pagadora', 'nit_pagadora',
                     'valor_total', 'mes', 'anio', 'estado'],
    'detalle_cuenta_cobro': ['cuenta_cobro_id', 'tarea_id', 'codigo_tarea',
                              'titulo_tarea', 'horas_dedicadas', 'precio_hora', 'subtotal'],
}

TIPOS_ENUM_REQUERIDOS = ['meses_cc', 'estado_cuenta', 'tipo_cuenta_banco']

conn = psycopg2.connect(URI)
cur = conn.cursor()

print("=" * 60)
print("DIAGNÓSTICO BD PRODUCCIÓN SUPABASE")
print("=" * 60)

# Tablas existentes
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
tablas_existentes = {r[0] for r in cur.fetchall()}
print("\n[TABLAS EN PRODUCCIÓN]")
for t in sorted(tablas_existentes):
    print(f"  ✓ {t}")

print("\n[TABLAS REQUERIDAS]")
falta_tabla = False
for tabla in TABLAS_REQUERIDAS:
    if tabla in tablas_existentes:
        print(f"  ✓ {tabla}")
    else:
        print(f"  ✗ FALTA: {tabla}")
        falta_tabla = True

print("\n[COLUMNAS REQUERIDAS]")
for tabla, cols in COLUMNAS_REQUERIDAS.items():
    if tabla not in tablas_existentes:
        print(f"  [SKIP] {tabla} no existe")
        continue
    cur.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND table_schema='public';",
        (tabla,)
    )
    cols_existentes = {r[0] for r in cur.fetchall()}
    for col in cols:
        if col in cols_existentes:
            print(f"  ✓ {tabla}.{col}")
        else:
            print(f"  ✗ FALTA: {tabla}.{col}")

print("\n[TIPOS ENUM]")
cur.execute("SELECT typname FROM pg_type WHERE typtype='e' ORDER BY typname;")
enums_existentes = {r[0] for r in cur.fetchall()}
for e in TIPOS_ENUM_REQUERIDOS:
    if e in enums_existentes:
        print(f"  ✓ {e}")
    else:
        print(f"  ✗ FALTA: {e}")

print("\n[TAREAS - muestra de estado facturada]")
if 'tareas' in tablas_existentes:
    cur.execute("SELECT COUNT(*) FROM tareas WHERE facturada IS NULL OR facturada = FALSE;")
    count = cur.fetchone()[0]
    print(f"  Tareas no facturadas disponibles: {count}")
else:
    print("  Tabla tareas no encontrada")

conn.close()
print("\n" + "=" * 60)

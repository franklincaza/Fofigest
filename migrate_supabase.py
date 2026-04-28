"""
Migración de producción (Supabase PostgreSQL).
Agrega la columna firma_imagen a perfil_pago.
"""
import psycopg2

URI = 'postgresql://postgres.wlvgmwuhfunnpddcgvzu:I0P2EdBGUabioCtA@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

conn = psycopg2.connect(URI)
conn.autocommit = False
cur = conn.cursor()

# Verificar columnas actuales
cur.execute(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name='perfil_pago' AND table_schema='public';"
)
cols = [r[0] for r in cur.fetchall()]
print(f"Columnas actuales en perfil_pago: {cols}")

if 'firma_imagen' in cols:
    print("La columna firma_imagen ya existe. Nada que hacer.")
else:
    cur.execute("ALTER TABLE perfil_pago ADD COLUMN firma_imagen TEXT;")
    conn.commit()
    print("✓ Columna firma_imagen agregada correctamente a perfil_pago (Supabase).")

# Verificar resultado
cur.execute(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name='perfil_pago' AND table_schema='public' ORDER BY ordinal_position;"
)
cols_final = [r[0] for r in cur.fetchall()]
print(f"Columnas finales en perfil_pago: {cols_final}")

conn.close()

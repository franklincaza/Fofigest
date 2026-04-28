"""
Script de migración: agrega la columna firma_imagen a perfil_pago.
Ejecutar una sola vez: python migrate_firma.py
"""
import sqlite3
import os

db_path = os.path.join('instance', 'Empresas.db')

if not os.path.exists(db_path):
    print(f"ERROR: No se encontró la base de datos en {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verificar tablas existentes
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [r[0] for r in cur.fetchall()]
print(f"Tablas encontradas: {tablas}")

if 'perfil_pago' not in tablas:
    print("La tabla perfil_pago no existe aún. Se creará al iniciar la app Flask.")
    conn.close()
    exit(0)

# Verificar si la columna ya existe
cur.execute("PRAGMA table_info(perfil_pago)")
columnas = [r[1] for r in cur.fetchall()]
print(f"Columnas en perfil_pago: {columnas}")

if 'firma_imagen' in columnas:
    print("La columna firma_imagen ya existe. Nada que hacer.")
else:
    cur.execute("ALTER TABLE perfil_pago ADD COLUMN firma_imagen TEXT")
    conn.commit()
    print("Columna firma_imagen agregada correctamente.")

conn.close()

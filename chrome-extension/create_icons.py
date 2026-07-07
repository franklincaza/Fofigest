"""
Genera los iconos de la extensión Chrome a partir del logo de Fofigest.
Ejecutar una sola vez desde la carpeta chrome-extension/:

    cd chrome-extension
    python create_icons.py
"""
import struct
import zlib
import os
import shutil

LOGO_PATH = os.path.join('..', 'static', 'img', 'logo_F-Photoroom.png')
ICONS_DIR = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(ICONS_DIR, exist_ok=True)

def make_solid_png(size, r=78, g=115, b=223):
    """Crea un PNG sólido (color Fofigest azul #4e73df) como fallback."""
    def chunk(tag, data):
        payload = tag + data
        return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    row  = bytes([0]) + bytes([r, g, b] * size)
    compressed = zlib.compress(row * size)

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', compressed)
            + chunk(b'IEND', b''))

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

for size in (16, 48, 128):
    dest = os.path.join(ICONS_DIR, f'icon{size}.png')

    if HAS_PIL and os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH).convert('RGBA')
            img = img.resize((size, size), Image.LANCZOS)
            img.save(dest)
            print(f'[OK] icon{size}.png — desde logo Fofigest (PIL)')
            continue
        except Exception as ex:
            print(f'[WARN] PIL falló: {ex}')

    # Fallback: PNG sólido azul Fofigest
    with open(dest, 'wb') as f:
        f.write(make_solid_png(size))
    print(f'[OK] icon{size}.png — color sólido #4e73df (sin PIL)')

print('\nIconos generados en:', ICONS_DIR)
print('Instala Pillow para iconos con el logo real:  pip install Pillow')

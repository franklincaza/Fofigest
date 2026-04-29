"""
generar_vapid.py — Genera las claves VAPID para push notifications.

Ejecución (una sola vez):
    python generar_vapid.py

Resultado:
  - Imprime VAPID_PUBLIC_KEY  (base64url) → pegar en config.py y en el meta tag del HTML
  - Imprime VAPID_PRIVATE_KEY (PEM)       → pegar en config.py como string

Dependencias: pywebpush (pip install pywebpush) o cryptography (ya instalado).
"""

import sys
import base64

def generar_con_cryptography():
    """Genera par de claves EC P-256 con la librería cryptography (ya instalada)."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization

    key = ec.generate_private_key(ec.SECP256R1())

    # Private key en formato PEM (string)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')

    # Public key en formato uncompressed point (65 bytes) → base64url
    public_bytes = key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    public_b64url = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

    return public_b64url, private_pem


def generar_con_pywebpush():
    """Genera par de claves usando py_vapid (viene con pywebpush)."""
    from py_vapid import Vapid
    v = Vapid()
    v.generate_keys()
    pub  = v.public_key.public_bytes(
        __import__('cryptography').hazmat.primitives.serialization.Encoding.X962,
        __import__('cryptography').hazmat.primitives.serialization.PublicFormat.UncompressedPoint,
    )
    public_b64url = base64.urlsafe_b64encode(pub).decode('utf-8').rstrip('=')

    from cryptography.hazmat.primitives import serialization
    private_pem = v.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')

    return public_b64url, private_pem


if __name__ == '__main__':
    try:
        public_b64url, private_pem = generar_con_cryptography()
        print("\n✅ Claves VAPID generadas exitosamente\n")
        print("═" * 60)
        print("VAPID_PUBLIC_KEY  (copia este valor):")
        print(f"  {public_b64url}")
        print()
        print("VAPID_PRIVATE_KEY  (copia este valor completo, incluyendo los guiones):")
        print(private_pem)
        print("═" * 60)
        print()
        print("📋 Pasos siguientes:")
        print("  1. Abre config.py")
        print('  2. Pega VAPID_PUBLIC_KEY  en  "VAPID_PUBLIC_KEY":  "<aquí>"')
        print('  3. Pega VAPID_PRIVATE_KEY en  "VAPID_PRIVATE_KEY": "<aquí>"')
        print("  4. Reinicia la aplicación Flask")
        print()
        print("  ⚠️  Guarda las claves de forma segura — si las pierdes")
        print("     tendrás que regenerarlas y todos los navegadores")
        print("     suscritos deberán volver a suscribirse.\n")

    except Exception as e:
        print(f"\n❌ Error generando claves: {e}")
        print("   Asegúrate de tener instalado: pip install pywebpush\n")
        sys.exit(1)

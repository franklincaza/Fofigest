config={
    "debug": False,
    "contraseña_google": "xxxx xxxx xxxx xxxx",   # Google App Password (16 chars)
    "EMAIL": "tu_correo@gmail.com",
    "host": "http://127.0.0.1:5000/",
    "version": "4.0.4",

    # ── Push Notifications (VAPID keys) ──────────────────────────────────────
    # Genera las claves ejecutando: python generar_vapid.py
    # Luego copia los valores aquí o carga desde variables de entorno.
    "VAPID_PUBLIC_KEY":  "TU_CLAVE_PUBLICA_VAPID",
    "VAPID_PRIVATE_KEY": "TU_CLAVE_PRIVADA_VAPID",
    "VAPID_EMAIL":       "mailto:tu_correo@gmail.com",
}

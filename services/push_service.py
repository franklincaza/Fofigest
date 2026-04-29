"""
push_service.py — Envío de push notifications via Web Push API (pywebpush).

Si pywebpush no está instalado las notificaciones push del navegador se desactivan
silenciosamente; las notificaciones internas (campana) siguen funcionando.

Instalación: pip install pywebpush

Generación de VAPID keys (ejecutar una sola vez):
    python generar_vapid.py
Y poner los valores en config.py o en variables de entorno:
    VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_EMAIL
"""

import os
import json
import logging

# ── Leer configuración ────────────────────────────────────────────────────────
try:
    import config as _cfg
    _c = _cfg.config
except Exception:
    _c = {}

VAPID_PUBLIC_KEY  = os.environ.get('VAPID_PUBLIC_KEY',  _c.get('VAPID_PUBLIC_KEY',  ''))
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', _c.get('VAPID_PRIVATE_KEY', ''))
VAPID_EMAIL       = os.environ.get('VAPID_EMAIL',       _c.get('VAPID_EMAIL', 'mailto:fofimaticsas@gmail.com'))

# ── Importar pywebpush (opcional) ─────────────────────────────────────────────
_pywebpush_ok = False
try:
    from pywebpush import webpush, WebPushException
    _pywebpush_ok = True
except ImportError:
    logging.warning(
        '[push_service] pywebpush no instalado — push browser desactivado. '
        'Instala con: pip install pywebpush  y luego ejecuta generar_vapid.py'
    )


# ── Funciones internas ────────────────────────────────────────────────────────

def _send_one(sub, title, body, url):
    """Envía push a una sola suscripción. Retorna True, False o 'expired'."""
    if not _pywebpush_ok or not VAPID_PRIVATE_KEY:
        return False
    try:
        payload = json.dumps({'title': title, 'body': body, 'url': url})
        webpush(
            subscription_info={
                'endpoint': sub.endpoint,
                'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
            },
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={'sub': VAPID_EMAIL},
        )
        return True
    except Exception as exc:
        logging.error(f'[push_service] _send_one: {exc}')
        resp = getattr(exc, 'response', None)
        if resp is not None and getattr(resp, 'status_code', 0) in (404, 410):
            return 'expired'
        return False


def _mark_expired(expired_ids):
    from models import models
    if not expired_ids:
        return
    try:
        models.PushSubscription.query.filter(
            models.PushSubscription.id.in_(expired_ids)
        ).update({'is_active': False}, synchronize_session=False)
        models.db.session.commit()
    except Exception as e:
        logging.error(f'[push_service] _mark_expired: {e}')


# ── API pública ───────────────────────────────────────────────────────────────

def send_to_user(user_id, title, body, url='/'):
    """Envía push a todas las suscripciones activas de un usuario."""
    from models import models
    try:
        subs = models.PushSubscription.query.filter_by(user_id=user_id, is_active=True).all()
        expired = [s.id for s in subs if _send_one(s, title, body, url) == 'expired']
        _mark_expired(expired)
    except Exception as e:
        logging.error(f'[push_service] send_to_user user_id={user_id}: {e}')


def send_to_all(title, body, url='/'):
    """Envía push a todos los usuarios con suscripciones activas."""
    from models import models
    try:
        subs = models.PushSubscription.query.filter_by(is_active=True).all()
        expired = [s.id for s in subs if _send_one(s, title, body, url) == 'expired']
        _mark_expired(expired)
    except Exception as e:
        logging.error(f'[push_service] send_to_all: {e}')

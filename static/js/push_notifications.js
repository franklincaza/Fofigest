/**
 * push_notifications.js
 * Registra el Service Worker y suscribe al usuario al servicio de push notifications.
 * Requiere: window.FOFIGEST_VAPID_PUBLIC_KEY definido antes de cargar este script.
 */
(function () {
    'use strict';

    // Solo activar para usuarios autenticados
    if (!localStorage.getItem('fofigest_session_token')) return;

    // Verificar soporte del navegador
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('[Push] Push no soportado en este navegador');
        return;
    }

    const metaVapid = document.querySelector('meta[name="vapid-public-key"]');
    const VAPID_PUBLIC_KEY = metaVapid ? metaVapid.getAttribute('content') : '';
    if (!VAPID_PUBLIC_KEY) {
        console.log('[Push] VAPID_PUBLIC_KEY no configurada — push desactivado');
        return;
    }

    // Si el usuario ya denegó, no volver a pedir
    if (Notification.permission === 'denied') return;

    function urlB64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; i++) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    function arrayBufferToBase64(buffer) {
        return btoa(String.fromCharCode(...new Uint8Array(buffer)));
    }

    function sendSubscriptionToServer(subscription) {
        const rawKey  = subscription.getKey('p256dh');
        const rawAuth = subscription.getKey('auth');
        return fetch('/api/push/subscribe', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                endpoint: subscription.endpoint,
                p256dh: rawKey  ? arrayBufferToBase64(rawKey)  : null,
                auth:   rawAuth ? arrayBufferToBase64(rawAuth) : null,
            }),
        });
    }

    async function subscribeToPush(registration) {
        try {
            // Verificar si ya existe suscripción activa
            let sub = await registration.pushManager.getSubscription();
            if (sub) {
                // Refrescar suscripción en el servidor (podría haber cambiado)
                await sendSubscriptionToServer(sub);
                return;
            }
            // Crear nueva suscripción
            sub = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlB64ToUint8Array(VAPID_PUBLIC_KEY),
            });
            await sendSubscriptionToServer(sub);
            console.log('[Push] Suscripción exitosa');
        } catch (err) {
            console.error('[Push] Error al suscribirse:', err);
        }
    }

    async function initPush() {
        const registration = await navigator.serviceWorker.ready;

        if (Notification.permission === 'granted') {
            await subscribeToPush(registration);
            return;
        }

        // Pedir permiso con diálogo amigable (SweetAlert2)
        if (window.Swal) {
            const result = await Swal.fire({
                title: 'Activar notificaciones',
                html: 'Recibe alertas cuando te asignen tareas o cuando haya mensajes del equipo.',
                icon: 'info',
                showCancelButton: true,
                confirmButtonText: '<i class="fas fa-bell me-1"></i> Activar',
                cancelButtonText: 'Ahora no',
                confirmButtonColor: '#4e73df',
                cancelButtonColor: '#858796',
            });
            if (!result.isConfirmed) return;
        }

        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            await subscribeToPush(registration);
        }
    }

    // Iniciar cuando el Service Worker esté listo (delay para no bloquear carga)
    window.addEventListener('load', function () {
        navigator.serviceWorker.ready.then(function () {
            setTimeout(initPush, 4000);
        });
    });

})();

// sw.js — Service Worker principal de Fofigest (PWA + Push Notifications)

const CACHE_NAME = 'fofigest-v2';

self.addEventListener('install', function (event) {
    self.skipWaiting();
    console.log('[SW] Instalado — version', CACHE_NAME);
});

self.addEventListener('activate', function (event) {
    event.waitUntil(clients.claim());
    console.log('[SW] Activado');
});

self.addEventListener('fetch', function (event) {
    // No interceptar requests de la API ni de terceros
    if (event.request.method !== 'GET') return;
    // Dejar pasar todo (sin estrategia de cache por ahora)
});

// ── PUSH NOTIFICATIONS ────────────────────────────────────────────────────────
self.addEventListener('push', function (event) {
    let data = { title: 'Fofigest', body: 'Tienes una notificación nueva', url: '/' };
    if (event.data) {
        try {
            data = JSON.parse(event.data.text());
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body || '',
        icon: '/static/img/logo_F-Photoroom.png',
        badge: '/static/img/logo_F-Photoroom.png',
        data: { url: data.url || '/' },
        vibrate: [200, 100, 200],
        requireInteraction: false,
        tag: 'fofigest-notif',   // agrupa notificaciones del mismo origen
        renotify: true,
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'Fofigest', options)
    );
});

// ── NOTIFICATION CLICK ────────────────────────────────────────────────────────
self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    const targetUrl = (event.notification.data && event.notification.data.url)
        ? event.notification.data.url
        : '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (windowClients) {
            // Intentar reusar una pestaña ya abierta
            for (let i = 0; i < windowClients.length; i++) {
                const client = windowClients[i];
                if ('focus' in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }
            // Si no hay pestaña abierta, abrir una nueva
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

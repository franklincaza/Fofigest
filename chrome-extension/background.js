// Fofigest Chrome Extension — Background Service Worker
// Gestiona alarmas y notificaciones Chrome.

const ALARM_DAILY   = 'fg_daily_reminder';
const ALARM_EXPIRY  = 'fg_check_expiry';

// ── Setup al instalar / iniciar ───────────────────────────────
chrome.runtime.onInstalled.addListener(setup);
chrome.runtime.onStartup.addListener(setup);

function setup() {
    setupAlarms();
    // Abrir el side panel al hacer clic en el ícono de la extensión
    if (chrome.sidePanel?.setPanelBehavior) {
        chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
    }
}

function setupAlarms() {
    // Recordatorio diario a las 8:00 AM
    chrome.alarms.get(ALARM_DAILY, alarm => {
        if (alarm) return;
        const now  = new Date();
        const fire = new Date();
        fire.setHours(8, 0, 0, 0);
        if (fire <= now) fire.setDate(fire.getDate() + 1);
        chrome.alarms.create(ALARM_DAILY, {
            delayInMinutes: (fire - now) / 60000,
            periodInMinutes: 24 * 60
        });
    });

    // Revisar tareas próximas a vencer cada 2 horas
    chrome.alarms.get(ALARM_EXPIRY, alarm => {
        if (!alarm) chrome.alarms.create(ALARM_EXPIRY, { periodInMinutes: 120 });
    });
}

// ── Disparador de alarmas ─────────────────────────────────────
chrome.alarms.onAlarm.addListener(alarm => {
    if (alarm.name === ALARM_DAILY)  showDailyReminder();
    if (alarm.name === ALARM_EXPIRY) checkExpiringTasks();
});

// ── Recordatorio diario ───────────────────────────────────────
function showDailyReminder() {
    chrome.notifications.create('fg_daily_' + Date.now(), {
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: 'Fofigest — Recordatorio diario',
        message: '¡Buenos días! Recuerda registrar las horas dedicadas a tus tareas de hoy.',
        buttons: [{ title: 'Abrir Fofigest' }],
        priority: 1
    });
}

// ── Revisión de tareas próximas a vencer ──────────────────────
async function checkExpiringTasks() {
    let tasks = null;

    // Intentar fetch directo al servidor (funciona sin pestaña abierta)
    try {
        const r = await fetch('http://127.0.0.1:5000/api/extension/tareas-proximas', {
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        });
        if (r.ok) {
            tasks = await r.json();
            chrome.storage.local.set({ cachedTareas: tasks, lastCacheTime: Date.now() });
        }
    } catch (_) {
        // Servidor offline — usar caché
    }

    // Fallback a caché de las últimas 4 horas
    if (!tasks) {
        const { cachedTareas, lastCacheTime } = await chrome.storage.local.get(['cachedTareas', 'lastCacheTime']);
        if (!cachedTareas || !lastCacheTime) return;
        if (Date.now() - lastCacheTime > 4 * 60 * 60 * 1000) return;
        tasks = cachedTareas;
    }

    if (!tasks || tasks.length === 0) return;

    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const en3 = new Date(hoy);
    en3.setDate(en3.getDate() + 3);

    const proximas = tasks.filter(t => {
        if (!t.fecha_fin || t.estado === 'COMPLETADOS') return false;
        const f = new Date(t.fecha_fin + 'T00:00:00');
        return f >= hoy && f <= en3;
    });

    if (proximas.length === 0) return;

    const msg = proximas.length === 1
        ? `"${proximas[0].titulo}" vence el ${proximas[0].fecha_fin}`
        : `${proximas.length} tareas vencen en los próximos 3 días`;

    const notifId = 'fg_expiry_' + hoy.toISOString().split('T')[0];
    chrome.notifications.create(notifId, {
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: 'Fofigest — Tareas próximas a vencer',
        message: msg,
        buttons: [{ title: 'Ver tareas' }],
        priority: 2
    });
}

// ── Clics en notificaciones ───────────────────────────────────
function openFofigest(path = '/tablero') {
    chrome.storage.sync.get(['serverUrl'], ({ serverUrl }) => {
        const base = serverUrl || 'http://127.0.0.1:5000';
        chrome.tabs.query({ url: [base + '/*'] }, tabs => {
            if (tabs.length > 0) {
                chrome.tabs.update(tabs[0].id, { active: true });
                chrome.windows.update(tabs[0].windowId, { focused: true });
            } else {
                chrome.tabs.create({ url: base + path });
            }
        });
    });
}

chrome.notifications.onButtonClicked.addListener(() => openFofigest('/tablero'));
chrome.notifications.onClicked.addListener(() => openFofigest('/tablero'));

// ── Mensajes desde popup y content script ────────────────────
// El service worker recibe los requests de API del popup y los ejecuta
// con credentials:'include', lo que envía las cookies de Flask
// sin restricciones SameSite (a diferencia de las páginas de extensión).
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'FOFIGEST_PAGE_READY') {
        chrome.storage.local.set({ fofigestTabId: sender.tab?.id });
        return false;
    }

    if (message.type === 'API_CALL') {
        proxifyApiCall(message)
            .then(sendResponse)
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true; // Mantiene el canal abierto para respuesta async
    }
});

const BASE = 'http://127.0.0.1:5000';

async function proxifyApiCall({ method = 'GET', path, body = null }) {
    const { fg_csrf_token } = await chrome.storage.local.get('fg_csrf_token');

    const opts = {
        method,
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    };

    if (body !== null && method !== 'GET') {
        opts.headers['Content-Type'] = 'application/json';
        if (fg_csrf_token) opts.headers['X-CSRFToken'] = fg_csrf_token;
        opts.body = JSON.stringify(body);
    }

    try {
        const r = await fetch(BASE + path, opts);

        // Redirect al login = sesión expirada
        if (r.redirected || r.status === 401) {
            return { ok: false, error: 'NOT_AUTHENTICATED', status: r.status };
        }
        if (!r.ok) {
            const d = await r.json().catch(() => ({}));
            return { ok: false, error: d.error || r.statusText, status: r.status };
        }
        const data = await r.json();
        return { ok: true, data };
    } catch (err) {
        return { ok: false, error: err.message };
    }
}

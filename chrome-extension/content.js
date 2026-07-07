// Fofigest Chrome Extension — Content Script
// Proxy de API: hace fetch same-origin desde la página de Fofigest
// para que popup.js acceda con las cookies de sesión del usuario.

(function () {
    'use strict';

    // El proxy API solo funciona en páginas Fofigest (mismo origen → cookies)
    if (!/^https?:\/\/(127\.0\.0\.1|localhost):5000/.test(location.origin)) return;

    // Si ya hay un listener activo de ESTA misma extensión en este contexto,
    // no registrar uno nuevo (previene doble respuesta en inyección doble).
    if (window.__fofigestListenerActive === chrome.runtime.id) return;
    window.__fofigestListenerActive = chrome.runtime.id;

    // Avisa al background que hay una página Fofigest activa
    try {
        chrome.runtime.sendMessage({ type: 'FOFIGEST_PAGE_READY', url: window.location.href });
    } catch (_) {}

    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
        if (message.type !== 'API_CALL') return false;

        const { method = 'GET', path, body } = message;
        const origin = window.location.origin;

        // credentials:'include' envía la cookie de sesión Flask (mismo origen).
        const opts = {
            method,
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        };

        if (body && method !== 'GET') {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }

        fetch(origin + path, opts)
            .then(r => {
                // Redirect al login = no autenticado
                if (r.redirected || r.status === 401) {
                    sendResponse({ ok: false, error: 'NOT_AUTHENTICATED', status: r.status });
                    return null;
                }
                if (!r.ok) {
                    return r.json()
                        .then(d => { sendResponse({ ok: false, error: d.error || r.statusText, status: r.status }); return null; })
                        .catch(() => { sendResponse({ ok: false, error: r.statusText, status: r.status }); return null; });
                }
                return r.json();
            })
            .then(data => { if (data !== null && data !== undefined) sendResponse({ ok: true, data }); })
            .catch(err => sendResponse({ ok: false, error: err.message }));

        return true; // Mantiene el canal abierto para respuesta async
    });
})();

/* ══════════════════════════════════════════════════════════════
   PANEL LATERAL — inyectado en páginas Fofigest
   Crea un FAB-tab en el borde izquierdo y un panel deslizante.
   El panel carga popup.html en un iframe con ?panel=1.
══════════════════════════════════════════════════════════════ */
(function injectPanel() {
    'use strict';
    if (document.getElementById('fg-panel-fab')) return;

    const W  = 420;   // ancho normal (px)
    const WX = 620;   // ancho expandido (px)
    let open     = false;
    let expanded = false;

    /* ── CSS ─────────────────────────────────────────────────── */
    const css = document.createElement('style');
    css.id    = 'fg-panel-css';
    css.textContent = `
        /* FAB — pestaña en borde derecho */
        #fg-panel-fab {
            all: unset;
            box-sizing: border-box;
            position: fixed;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            z-index: 2147483647;
            background: linear-gradient(160deg,#4e73df 0%,#224abe 100%);
            border-radius: 16px 0 0 16px;
            width: 42px;
            height: 68px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 3px;
            box-shadow: -4px 0 22px rgba(78,115,223,.55);
            transition:
                right .36s cubic-bezier(.32,.72,0,1),
                width .22s ease,
                background .18s ease;
        }
        #fg-panel-fab:hover {
            width: 50px;
            background: linear-gradient(160deg,#3d62d0 0%,#1a3fa8 100%);
            border-radius: 16px 0 0 16px;
        }
        #fg-panel-fab:focus-visible {
            outline: 3px solid rgba(255,255,255,.75);
            outline-offset: -3px;
        }
        /* Icono */
        #fg-panel-fab .fp-ico {
            width: 26px; height: 26px;
            border-radius: 6px;
            display: block;
            pointer-events: none;
            transition: transform .2s;
        }
        #fg-panel-fab:hover .fp-ico { transform: scale(1.1); }
        /* Etiqueta "FG" */
        #fg-panel-fab .fp-tag {
            font: 800 8px/1 system-ui,sans-serif;
            color: rgba(255,255,255,.6);
            letter-spacing: .1em;
            text-transform: uppercase;
            pointer-events: none;
        }
        /* Flecha (estado abierto) */
        #fg-panel-fab .fp-arr {
            display: none;
            pointer-events: none;
        }
        #fg-panel-fab .fp-arr svg { display: block; }

        /* FAB en estado abierto → pestaña de cierre */
        #fg-panel-fab.fp-open {
            right: ${W}px;
            width: 28px;
            border-radius: 10px 0 0 10px;
        }
        #fg-panel-fab.fp-open.fp-expanded { right: ${WX}px; }
        #fg-panel-fab.fp-open .fp-ico { display: none; }
        #fg-panel-fab.fp-open .fp-tag { display: none; }
        #fg-panel-fab.fp-open .fp-arr { display: block; }

        /* ── Panel ─────────────────────────────────────────── */
        #fg-panel-wrap {
            position: fixed;
            right: 0; top: 0; bottom: 0;
            width: ${W}px;
            z-index: 2147483640;
            display: flex;
            flex-direction: column;
            background: #f8f9fc;
            box-shadow: -6px 0 48px rgba(0,0,0,.22);
            transform: translateX(100%);
            transition:
                transform .36s cubic-bezier(.32,.72,0,1),
                width .36s cubic-bezier(.32,.72,0,1);
            overflow: hidden;
        }
        #fg-panel-wrap.fp-open { transform: translateX(0); }
        #fg-panel-wrap.fp-expanded { width: ${WX}px; }

        /* ── Cabecera del panel ─────────────────────────────── */
        #fg-panel-hdr {
            flex-shrink: 0;
            height: 52px;
            min-height: 52px;
            background: linear-gradient(135deg,#4e73df 0%,#224abe 100%);
            display: flex;
            align-items: center;
            padding: 0 8px 0 14px;
            gap: 10px;
            user-select: none;
        }
        #fg-ph-logo {
            width: 28px; height: 28px;
            border-radius: 6px;
            flex-shrink: 0;
            display: block;
        }
        #fg-ph-info { flex: 1; min-width: 0; }
        #fg-ph-title {
            font: 700 14.5px/1.1 system-ui,-apple-system,'Segoe UI',sans-serif;
            color: #fff;
            letter-spacing: .01em;
        }
        #fg-ph-sub {
            font: 400 10.5px/1 system-ui,sans-serif;
            color: rgba(255,255,255,.62);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        #fg-ph-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: rgba(255,255,255,.3);
            border: 1.5px solid rgba(255,255,255,.35);
            flex-shrink: 0;
            transition: background .3s;
        }
        #fg-ph-dot.online  { background: #1cc88a; border-color: rgba(28,200,138,.5); }
        #fg-ph-dot.offline { background: #e74a3b; border-color: rgba(231,74,59,.5);  }
        /* Botones de cabecera */
        .fp-hbtn {
            all: unset;
            box-sizing: border-box;
            background: rgba(255,255,255,.14);
            border-radius: 7px;
            color: rgba(255,255,255,.88);
            width: 30px; height: 30px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: background .15s;
        }
        .fp-hbtn:hover { background: rgba(255,255,255,.28); }
        .fp-hbtn:focus-visible {
            outline: 2px solid rgba(255,255,255,.65);
            outline-offset: 1px;
        }
        .fp-hbtn svg { display: block; pointer-events: none; }

        /* ── Iframe ─────────────────────────────────────────── */
        #fg-panel-frame {
            flex: 1;
            border: none;
            width: 100%;
            display: block;
            background: #f8f9fc;
        }
    `;
    document.head.appendChild(css);

    /* ── DOM ─────────────────────────────────────────────────── */
    const iconUrl = chrome.runtime.getURL('icons/icon48.png');

    // FAB
    const fab = document.createElement('button');
    fab.id = 'fg-panel-fab';
    fab.setAttribute('aria-label', 'Abrir panel Fofigest');
    fab.title = 'Fofigest';
    fab.innerHTML = `
        <img class="fp-ico" src="${iconUrl}" alt="">
        <span class="fp-tag">FG</span>
        <span class="fp-arr">
            <svg width="10" height="18" viewBox="0 0 10 18" fill="none">
                <path d="M2 2L8 9L2 16" stroke="rgba(255,255,255,.9)" stroke-width="2.2"
                      stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </span>`;

    // Panel
    const wrap = document.createElement('div');
    wrap.id = 'fg-panel-wrap';
    wrap.setAttribute('role', 'complementary');
    wrap.setAttribute('aria-label', 'Panel Fofigest');
    wrap.setAttribute('aria-hidden', 'true');

    // Cabecera
    const hdr = document.createElement('div');
    hdr.id = 'fg-panel-hdr';
    hdr.innerHTML = `
        <img id="fg-ph-logo" src="${iconUrl}" alt="Fofigest">
        <div id="fg-ph-info">
            <div id="fg-ph-title">Fofigest</div>
            <div id="fg-ph-sub"></div>
        </div>
        <span id="fg-ph-dot" title="Estado"></span>
        <button class="fp-hbtn" id="fp-btn-exp" aria-label="Expandir panel" title="Expandir / reducir">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 6V1h5M13 8v5H8M1 1l5 5M13 13l-5-5"
                      stroke="currentColor" stroke-width="1.7"
                      stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
        <button class="fp-hbtn" id="fp-btn-cls" aria-label="Cerrar panel" title="Cerrar panel">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M1 1l10 10M11 1L1 11"
                      stroke="currentColor" stroke-width="1.9"
                      stroke-linecap="round"/>
            </svg>
        </button>`;

    // Iframe
    const frame = document.createElement('iframe');
    frame.id  = 'fg-panel-frame';
    frame.src = chrome.runtime.getURL('popup/popup.html') + '?panel=1';
    frame.title = 'Panel de tareas Fofigest';

    wrap.appendChild(hdr);
    wrap.appendChild(frame);
    document.body.appendChild(fab);
    document.body.appendChild(wrap);

    /* ── Referencias rápidas ─────────────────────────────────── */
    const dot    = document.getElementById('fg-ph-dot');
    const sub    = document.getElementById('fg-ph-sub');
    const btnExp = document.getElementById('fp-btn-exp');
    const btnCls = document.getElementById('fp-btn-cls');

    /* ── Funciones de estado ─────────────────────────────────── */
    function setOpen(value) {
        open = value;
        wrap.classList.toggle('fp-open', open);
        wrap.setAttribute('aria-hidden', String(!open));
        fab.classList.toggle('fp-open', open);
        fab.setAttribute('aria-label', open ? 'Cerrar panel Fofigest' : 'Abrir panel Fofigest');
        fab.title = open ? 'Cerrar' : 'Fofigest';
        if (expanded) {
            wrap.classList.toggle('fp-expanded', open);
            fab.classList.toggle('fp-expanded', open);
        }
    }

    function toggleExpand() {
        expanded = !expanded;
        wrap.classList.toggle('fp-expanded', expanded);
        if (open) fab.classList.toggle('fp-expanded', expanded);
    }

    /* ── Listeners ───────────────────────────────────────────── */
    fab.addEventListener('click', () => setOpen(!open));
    btnCls.addEventListener('click', () => setOpen(false));
    btnExp.addEventListener('click', toggleExpand);

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && open) setOpen(false);
    });

    // Mensajes desde el iframe (popup.js)
    window.addEventListener('message', e => {
        if (!e.data || typeof e.data !== 'object') return;
        if (e.data.fg === 'close')  { setOpen(false); return; }
        if (e.data.fg === 'expand') { toggleExpand();  return; }
        if (e.data.fg === 'status') {
            if (e.data.authenticated) {
                dot.className = 'online';
                const u = e.data.user;
                const nombre = [u?.nombres, u?.apellidos].filter(Boolean).join(' ');
                sub.textContent = [nombre, u?.empresa].filter(Boolean).join(' · ');
            } else {
                dot.className = 'offline';
                sub.textContent = 'Sin sesión';
            }
        }
    });
})();

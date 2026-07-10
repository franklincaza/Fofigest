// Fofigest Chrome Extension — Popup Script

'use strict';

const BASE_URL = 'http://127.0.0.1:5000';

// Modo content.js panel: iframe con ?panel=1
const IS_PANEL = new URLSearchParams(location.search).has('panel');
// Modo Chrome Side Panel nativo: ?mode=sidepanel
const IS_SIDEPANEL = new URLSearchParams(location.search).get('mode') === 'sidepanel';

if (IS_PANEL)     document.documentElement.classList.add('fg-is-panel');
if (IS_SIDEPANEL) document.documentElement.classList.add('fg-is-sidepanel');

// ── Helpers DOM ───────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Estado global ─────────────────────────────────────────────
const state = {
    user: null,
    authenticated: false,
    fofigestTab: null,
    currentTab: 'timers',
    filterEstado: '',
    filterBusqueda: '',
    timers: {}
};

let timerInterval = null;

// ── Utilidades ────────────────────────────────────────────────
function formatTime(ms) {
    const s = Math.floor(ms / 1000);
    const h = String(Math.floor(s / 3600)).padStart(2, '0');
    const m = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    return `${h}:${m}:${sec}`;
}

function msToHours(ms) {
    return Math.round(ms / 36000) / 100;
}

function formatDate(str) {
    if (!str) return '—';
    const [y, m, d] = str.split('-');
    return `${d}/${m}/${y}`;
}

function estadoBadge(estado) {
    const map = {
        PENDIENTE:    ['secondary', 'Pendiente'],
        PROGRESO:     ['primary',   'En progreso'],
        'REVISIÓN':   ['warning',   'Revisión'],
        IMPEDIMENTOS: ['danger',    'Impedimentos'],
        COMPLETADOS:  ['success',   'Completados']
    };
    const [cls, label] = map[estado] || ['secondary', estado];
    return `<span class="badge badge-${cls}">${label}</span>`;
}

function isUrgent(fechaStr) {
    if (!fechaStr) return false;
    const fecha = new Date(fechaStr + 'T00:00:00');
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const diff = (fecha - hoy) / 86400000;
    return diff >= 0 && diff <= 3;
}

function escHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escAttr(str) {
    return String(str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ── Chrome storage (timers) ───────────────────────────────────
function contextValido() {
    try { return !!chrome.runtime?.id; } catch { return false; }
}

function syncTimerToPage(taskId, timer, action) {
    if (!state.fofigestTab) return;
    try {
        chrome.tabs.sendMessage(state.fofigestTab.id, {
            type: 'TIMER_SYNC',
            action,
            taskId,
            accumulated: timer?.accumulated || 0,
            startedAt:   timer?.startTime  || null
        });
    } catch {}
}

async function getTimers() {
    if (!contextValido()) return {};
    try {
        const { fg_timers } = await chrome.storage.local.get('fg_timers');
        return fg_timers || {};
    } catch {
        return {};
    }
}

async function saveTimers(timers) {
    if (!contextValido()) return;
    try {
        await chrome.storage.local.set({ fg_timers: timers });
    } catch {}
}

function getElapsed(timer) {
    if (!timer) return 0;
    const base = timer.accumulated || 0;
    if (timer.running && timer.startTime) return base + (Date.now() - timer.startTime);
    return base;
}

// ── API via content script (mismo origen → cookies funciona) ──
// El content script se inyecta en la pestaña de Fofigest y hace fetch
// con credentials:'include'. Al ser mismo origen, SameSite=Lax no bloquea.
function apiCall(method, path, body = null) {
    if (!state.fofigestTab) return Promise.resolve({ ok: false, error: 'NO_TAB' });
    return new Promise((resolve, reject) => {
        chrome.tabs.sendMessage(
            state.fofigestTab.id,
            { type: 'API_CALL', method, path, body },
            res => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else if (!res) {
                    reject(new Error('Sin respuesta del content script'));
                } else {
                    resolve(res);
                }
            }
        );
    });
}

// ── Buscar pestaña Fofigest abierta ───────────────────────────
async function findFofigestTab() {
    const tabs = await chrome.tabs.query({
        url: ['http://127.0.0.1:5000/*', 'http://localhost:5000/*']
    });
    return tabs.length > 0 ? tabs[0] : null;
}

// ── Leer usuario autenticado desde el meta tag del DOM ────────
async function readAuthFromPage(tabId) {
    try {
        const results = await chrome.scripting.executeScript({
            target: { tabId },
            func: () => {
                const meta = document.querySelector('meta[name="fg-current-user"]');
                if (!meta?.content) return null;
                try { return JSON.parse(meta.content); } catch { return null; }
            }
        });
        return results?.[0]?.result ?? null;
    } catch {
        return null;
    }
}

// ── Inyectar content script si no está activo ─────────────────
async function injectContentScript(tabId) {
    try {
        await chrome.scripting.executeScript({ target: { tabId }, files: ['content.js'] });
    } catch (_) {
        // Ya inyectado — el listener existente sirve
    }
}

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    $('btn-open-fofigest')?.addEventListener('click', () => {
        chrome.tabs.create({ url: BASE_URL });
    });
    $('btn-go-login')?.addEventListener('click', () => {
        chrome.tabs.create({ url: BASE_URL + '/' });
    });

    state.fofigestTab = await findFofigestTab();

    if (!state.fofigestTab) {
        showScreen('no-tab');
        return;
    }

    const user = await readAuthFromPage(state.fofigestTab.id);

    if (!user) {
        if (IS_PANEL) window.parent.postMessage({ fg: 'status', authenticated: false }, '*');
        showScreen('not-auth');
        return;
    }

    await injectContentScript(state.fofigestTab.id);

    state.user = user;
    state.authenticated = true;
    if (IS_PANEL) window.parent.postMessage({ fg: 'status', authenticated: true, user }, '*');
    showScreen('main');
    setupEventListeners();
    loadTimersTab();
});

// ── Pantallas ─────────────────────────────────────────────────
function showScreen(name) {
    $('state-no-tab').classList.toggle('hidden', name !== 'no-tab');
    $('state-not-auth').classList.toggle('hidden', name !== 'not-auth');
    $('state-main').classList.toggle('hidden', name !== 'main');

    const dot = $('status-dot');
    if (name === 'main') {
        dot.className = 'status-dot status-online';
        dot.title = 'Conectado a Fofigest';
        $('header-user').classList.remove('hidden');
        $('user-name').textContent = `${state.user.nombres} ${state.user.apellidos}`.trim();
        $('user-empresa').textContent = state.user.empresa || '';
    } else {
        dot.className = 'status-dot status-offline';
        dot.title = 'Sin conexión';
    }
}

// ── Event listeners ───────────────────────────────────────────
function setupEventListeners() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    $('btn-refresh-timers').addEventListener('click', () => loadTimersTab());
    $('btn-refresh-tablero')?.addEventListener('click', () => loadTableroTab());

    let debounce;
    $('filter-estado').addEventListener('change', () => {
        state.filterEstado = $('filter-estado').value;
        loadTasksTab();
    });
    $('filter-busqueda').addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
            state.filterBusqueda = $('filter-busqueda').value;
            loadTasksTab();
        }, 400);
    });

    $('form-new-task').addEventListener('submit', handleNewTask);
    setupEditModal();
}

// ── Cambio de tab ─────────────────────────────────────────────
function switchTab(tabName) {
    state.currentTab = tabName;
    clearTimerInterval();

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-panel').forEach(panel => {
        const isActive = panel.dataset.panel === tabName;
        panel.classList.toggle('hidden', !isActive);
        if (isActive) panel.style.display = '';
    });

    if      (tabName === 'timers')  loadTimersTab();
    else if (tabName === 'tablero') loadTableroTab();
    else if (tabName === 'tasks')   loadTasksTab();
    else if (tabName === 'new')     initNewForm();
}

// ══════════════════════════════════════════════════════════════
// TAB: CRONÓMETROS
// ══════════════════════════════════════════════════════════════

async function loadTimersTab() {
    state.timers = await getTimers();
    const list = $('timers-list');
    list.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';

    try {
        const res = await apiCall('GET', '/b/api/tareas?estado=PROGRESO');
        let tasks = res.ok ? (res.data || []) : [];

        const timerIds = Object.keys(state.timers).map(Number);
        const faltantes = timerIds.filter(id => !tasks.find(t => t.id === id));
        for (const id of faltantes) {
            const r = await apiCall('GET', `/tareas/${id}`);
            if (r.ok && r.data) tasks.unshift(r.data);
        }

        renderTimerCards(list, tasks);
        startTimerInterval();
        chrome.storage.local.set({ cachedTareas: tasks, lastCacheTime: Date.now() });
    } catch (err) {
        list.innerHTML = `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
}

function renderTimerCards(container, tasks) {
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-stopwatch"></i>
                <p>No hay tareas en progreso</p>
                <small>Usa el <strong>Tablero</strong> para mover tareas a "En Progreso"</small>
            </div>`;
        return;
    }

    container.innerHTML = tasks.map(task => {
        const timer    = state.timers[task.id];
        const elapsed  = getElapsed(timer);
        const running  = timer?.running || false;
        const hDed     = task.horas_dedicadas || 0;
        const hEst     = task.horas_estimadas || 0;
        const progreso = hEst > 0 ? Math.min(100, Math.round((hDed / hEst) * 100)) : 0;
        const hasSaved = elapsed > 0;

        return `
        <div class="timer-card" data-id="${task.id}">
            <div class="timer-card__header">
                ${estadoBadge(task.estado)}
                <span class="timer-card__empresa">${escHtml(task.empresa || '')}</span>
            </div>
            <div class="timer-card__title">${escHtml(task.titulo)}</div>
            <div class="timer-card__project">${escHtml(task.codigo_proyecto)}</div>
            <div class="progress-bar-wrap">
                <div class="progress-bar-fill" style="width:${progreso}%"></div>
            </div>
            <div class="timer-card__stats">
                <span>Dedicadas: <strong>${hDed}h</strong></span>
                <span>Estimadas: <strong>${hEst || '—'}h</strong></span>
                <span style="margin-left:auto;font-size:10px;color:#aaa">${progreso}%</span>
            </div>
            <div class="timer-card__controls">
                <div class="timer-display ${running ? 'running' : ''}" data-timer="${task.id}">
                    ${formatTime(elapsed)}
                </div>
                <div class="timer-btns">
                    <button class="btn-timer-toggle ${running ? 'active' : ''}"
                            data-id="${task.id}"
                            data-title="${escAttr(task.titulo)}"
                            data-empresa="${escAttr(task.empresa || '')}">
                        <i class="fas fa-${running ? 'pause' : 'play'}"></i>
                        ${running ? 'Pausar' : 'Iniciar'}
                    </button>
                    ${hasSaved ? `
                    <button class="btn-timer-save" data-id="${task.id}">
                        <i class="fas fa-save"></i> Guardar
                    </button>` : ''}
                    <button class="btn-card-edit btn-edit-task" data-id="${task.id}" title="Editar tarea">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
        </div>`;
    }).join('');

    container.querySelectorAll('.btn-timer-toggle').forEach(btn => {
        btn.addEventListener('click', () =>
            toggleTimer(btn.dataset.id, btn.dataset.title, btn.dataset.empresa));
    });
    container.querySelectorAll('.btn-timer-save').forEach(btn => {
        btn.addEventListener('click', () => saveTimer(btn.dataset.id));
    });
    container.querySelectorAll('.btn-edit-task').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.id));
    });
}

function startTimerInterval() {
    clearTimerInterval();
    timerInterval = setInterval(async () => {
        if (!contextValido()) { clearTimerInterval(); return; }
        if (state.currentTab !== 'timers') return;
        try {
            state.timers = await getTimers();
        } catch {
            return;
        }
        document.querySelectorAll('[data-timer]').forEach(el => {
            const timer = state.timers[el.dataset.timer];
            if (timer?.running) {
                el.textContent = formatTime(getElapsed(timer));
                el.classList.add('running');
            }
        });
    }, 1000);
}

function clearTimerInterval() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

async function toggleTimer(taskId, taskTitle, taskEmpresa) {
    const timers = await getTimers();
    const timer  = timers[taskId] || { accumulated: 0, running: false };

    if (timer.running) {
        timer.accumulated = getElapsed(timer);
        timer.running = false; timer.startTime = null;
    } else {
        timer.running = true; timer.startTime = Date.now();
        timer.taskTitle = taskTitle; timer.taskEmpresa = taskEmpresa;
    }

    timers[taskId] = timer;
    await saveTimers(timers);
    state.timers = timers;

    // Sincronizar estado del timer con la app (localStorage del tablero)
    syncTimerToPage(taskId, timer, timer.running ? 'start' : 'pause');

    const btn     = document.querySelector(`.btn-timer-toggle[data-id="${taskId}"]`);
    const display = document.querySelector(`[data-timer="${taskId}"]`);
    if (btn) {
        btn.innerHTML = `<i class="fas fa-${timer.running ? 'pause' : 'play'}"></i> ${timer.running ? 'Pausar' : 'Iniciar'}`;
        btn.classList.toggle('active', timer.running);
    }
    if (display) display.classList.toggle('running', timer.running);

    // Agregar botón guardar en la tarjeta de Cronómetros
    const card = document.querySelector(`.timer-card[data-id="${taskId}"]`);
    if (card && !card.querySelector('.btn-timer-save') && (timer.accumulated || 0) > 0) {
        const btnsDiv = card.querySelector('.timer-btns');
        const saveBtn = document.createElement('button');
        saveBtn.className  = 'btn-timer-save';
        saveBtn.dataset.id = taskId;
        saveBtn.innerHTML  = '<i class="fas fa-save"></i> Guardar';
        saveBtn.addEventListener('click', () => saveTimer(taskId));
        btnsDiv.insertBefore(saveBtn, btnsDiv.querySelector('.btn-card-edit'));
    }

    // Agregar botón guardar en la tarjeta del Tablero (mini-kanban)
    const tableroCard = document.querySelector(`.tablero-card[data-id="${taskId}"]`);
    if (tableroCard && !tableroCard.querySelector('.btn-tablero-save') && (timer.accumulated || 0) > 0) {
        const actDiv = tableroCard.querySelector('.tablero-card__actions');
        const saveBtn = document.createElement('button');
        saveBtn.className  = 'btn-tablero-save btn-card-timer';
        saveBtn.dataset.id = taskId;
        saveBtn.title = 'Guardar tiempo';
        saveBtn.innerHTML  = '<i class="fas fa-save"></i>';
        saveBtn.addEventListener('click', () => saveTimer(taskId));
        actDiv.insertBefore(saveBtn, actDiv.firstChild);
    }
}

async function saveTimer(taskId) {
    const timers = await getTimers();
    const timer  = timers[taskId];
    if (!timer) return;

    // Pausar si está corriendo antes de calcular el tiempo final
    if (timer.running && timer.startTime) {
        timer.accumulated = getElapsed(timer);
        timer.running = false;
        timer.startTime = null;
        timers[taskId] = timer;
        await saveTimers(timers);
        state.timers = timers;
    }

    const elapsed = timer.accumulated || 0;
    const horas   = msToHours(elapsed);

    if (horas <= 0) {
        showToast('Tiempo demasiado pequeño para guardar (mín. 18 seg)', 'warning');
        return;
    }

    const timeStr = formatTime(elapsed);
    const confirmado = window.confirm(
        `Guardar tiempo registrado\n\nTiempo acumulado: ${timeStr} = ${horas} h\n\n¿Agregar este tiempo a las horas dedicadas de la tarea?`
    );
    if (!confirmado) return;

    const btn   = document.querySelector(`.btn-timer-save[data-id="${taskId}"]`);
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; }

    try {
        const res = await apiCall('POST', '/api/extension/timer/save', { id: parseInt(taskId), horas });
        if (res.ok) {
            delete timers[taskId];
            await saveTimers(timers);
            state.timers = timers;
            syncTimerToPage(taskId, null, 'remove');
            showToast(`✅ ${formatTime(elapsed)} guardado`, 'success');
            setTimeout(loadTimersTab, 700);
        } else {
            showToast(`❌ ${res.error || 'Error al guardar'}`, 'danger');
            if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Guardar'; }
        }
    } catch (err) {
        showToast(`❌ ${err.message}`, 'danger');
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Guardar'; }
    }
}

// ══════════════════════════════════════════════════════════════
// TAB: TABLERO (Mini Kanban)
// ══════════════════════════════════════════════════════════════

const ESTADOS_KANBAN = [
    { key: 'PENDIENTE',    label: 'Pendiente',    cls: 'secondary' },
    { key: 'PROGRESO',     label: 'En progreso',  cls: 'primary'   },
    { key: 'REVISIÓN',     label: 'Revisión',     cls: 'warning'   },
    { key: 'IMPEDIMENTOS', label: 'Impedimentos', cls: 'danger'    },
    { key: 'COMPLETADOS',  label: 'Completados',  cls: 'success'   },
];

let tableroTasks = [];
let tableroEstadoActivo = 'PROGRESO';

async function loadTableroTab() {
    const list = $('tablero-list');
    list.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Cargando tablero...</div>';

    try {
        const res = await apiCall('GET', '/b/api/tareas');
        tableroTasks = res.ok ? (res.data || []) : [];
        renderTableroBoard();
    } catch (err) {
        list.innerHTML = `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
}

function renderTableroBoard() {
    const grupos = {};
    ESTADOS_KANBAN.forEach(e => { grupos[e.key] = []; });
    tableroTasks.forEach(t => {
        if (grupos[t.estado]) grupos[t.estado].push(t);
    });

    const pills = $('tablero-pills');
    pills.innerHTML = ESTADOS_KANBAN.map(e => `
        <button class="estado-pill ${e.key === tableroEstadoActivo ? 'active' : ''} pill-${e.cls}"
                data-estado="${e.key}">
            ${e.label} <span class="pill-count">${grupos[e.key].length}</span>
        </button>
    `).join('');

    pills.querySelectorAll('.estado-pill').forEach(btn => {
        btn.addEventListener('click', () => {
            tableroEstadoActivo = btn.dataset.estado;
            pills.querySelectorAll('.estado-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderTableroTasks($('tablero-list'), grupos[tableroEstadoActivo]);
        });
    });

    renderTableroTasks($('tablero-list'), grupos[tableroEstadoActivo]);
}

function renderTableroTasks(container, tasks) {
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Sin tareas en este estado</p>
            </div>`;
        return;
    }

    container.innerHTML = tasks.map(t => {
        const hDed    = t.horas_dedicadas || 0;
        const hEst    = t.horas_estimadas || 0;
        const prog    = hEst > 0 ? Math.min(100, Math.round((hDed / hEst) * 100)) : 0;
        const urgente = isUrgent(t.fecha_fin) && t.estado !== 'COMPLETADOS';
        const timer    = state.timers[t.id];
        const running  = timer?.running || false;
        const elapsed  = getElapsed(timer);
        const hasSaved = elapsed > 0;

        const opciones = ESTADOS_KANBAN
            .filter(e => e.key !== t.estado)
            .map(e => `<option value="${e.key}">${e.label}</option>`)
            .join('');

        return `
        <div class="tablero-card ${urgente ? 'urgent' : ''}" data-id="${t.id}">
            <div class="tablero-card__top">
                <div class="tablero-card__title">${escHtml(t.titulo)}</div>
                ${urgente ? '<span class="badge badge-warning" title="Vence pronto">⚠</span>' : ''}
            </div>
            <div class="tablero-card__meta">
                <span><i class="fas fa-building"></i> ${escHtml(t.empresa || '—')}</span>
                <span><i class="fas fa-user"></i> ${escHtml(t.responsable)}</span>
                ${t.fecha_fin ? `<span class="${urgente ? 'text-warning' : ''}">
                    <i class="fas fa-calendar-alt"></i> ${formatDate(t.fecha_fin)}
                </span>` : ''}
            </div>
            <div class="progress-bar-wrap">
                <div class="progress-bar-fill" style="width:${prog}%"></div>
            </div>
            <div class="tablero-card__footer">
                <span class="tablero-hours">${hDed}h / ${hEst || '?'}h</span>
                <div class="tablero-card__actions">
                    ${t.estado !== 'COMPLETADOS' ? `
                    <button class="btn-card-timer ${running ? 'btn-card-timer--active' : ''} btn-timer-add"
                            data-id="${t.id}"
                            data-title="${escAttr(t.titulo)}"
                            data-empresa="${escAttr(t.empresa || '')}"
                            title="${running ? 'Cronómetro corriendo' : 'Iniciar cronómetro'}">
                        <i class="fas fa-${running ? 'pause' : 'stopwatch'}"></i>
                    </button>` : ''}
                    ${hasSaved ? `
                    <button class="btn-card-timer btn-tablero-save" data-id="${t.id}" title="Guardar tiempo (${formatTime(elapsed)})">
                        <i class="fas fa-save"></i>
                    </button>` : ''}
                    <button class="btn-card-edit btn-edit-task" data-id="${t.id}" title="Editar tarea">
                        <i class="fas fa-edit"></i>
                    </button>
                    <select class="select-estado" data-id="${t.id}" title="Cambiar estado">
                        <option value="">Mover a...</option>
                        ${opciones}
                    </select>
                </div>
            </div>
        </div>`;
    }).join('');

    container.querySelectorAll('.btn-timer-add').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const timer = state.timers[id];
            if (timer?.running) {
                // Pausar desde el tablero
                await toggleTimer(id, btn.dataset.title, btn.dataset.empresa);
                btn.innerHTML = '<i class="fas fa-stopwatch"></i>';
                btn.classList.remove('btn-card-timer--active');
                showToast('⏸ Cronómetro pausado', 'info');
            } else {
                await startTimerFromTask(id, btn.dataset.title, btn.dataset.empresa);
                btn.innerHTML = '<i class="fas fa-pause"></i>';
                btn.classList.add('btn-card-timer--active');
                showToast('⏱ Cronómetro iniciado', 'info');
            }
        });
    });

    container.querySelectorAll('.btn-tablero-save').forEach(btn => {
        btn.addEventListener('click', () => saveTimer(btn.dataset.id));
    });

    container.querySelectorAll('.btn-edit-task').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.id));
    });

    container.querySelectorAll('.select-estado').forEach(sel => {
        sel.addEventListener('change', async () => {
            const nuevoEstado = sel.value;
            if (!nuevoEstado) return;
            sel.disabled = true;

            try {
                const res = await apiCall('PUT', `/tareas/${sel.dataset.id}/estado`, { estado: nuevoEstado });
                if (res.ok) {
                    showToast(`✅ Movida a ${nuevoEstado}`, 'success');
                    await loadTableroTab();
                } else {
                    showToast(`❌ ${res.error || 'Error'}`, 'danger');
                    sel.value = ''; sel.disabled = false;
                }
            } catch (err) {
                showToast(`❌ ${err.message}`, 'danger');
                sel.value = ''; sel.disabled = false;
            }
        });
    });
}

// ══════════════════════════════════════════════════════════════
// TAB: TAREAS
// ══════════════════════════════════════════════════════════════

async function loadTasksTab() {
    const list = document.querySelector('#panel-tasks .tasks-list');
    list.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';

    let path = '/b/api/tareas?';
    if (state.filterEstado)   path += `estado=${encodeURIComponent(state.filterEstado)}&`;
    if (state.filterBusqueda) path += `clave_busqueda=${encodeURIComponent(state.filterBusqueda)}&`;

    try {
        const res   = await apiCall('GET', path);
        const tasks = res.ok ? (res.data || []) : [];
        chrome.storage.local.set({ cachedTareas: tasks, lastCacheTime: Date.now() });
        renderTaskList(list, tasks);
    } catch (err) {
        list.innerHTML = `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
}

function renderTaskList(container, tasks) {
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle"></i>
                <p>No hay tareas con ese filtro</p>
            </div>`;
        return;
    }

    const shown = tasks.slice(0, 30);
    container.innerHTML = shown.map(t => {
        const urgente = isUrgent(t.fecha_fin) && t.estado !== 'COMPLETADOS';
        return `
        <div class="task-item ${urgente ? 'urgent' : ''}">
            <div class="task-item__header">
                ${estadoBadge(t.estado)}
                ${urgente ? '<span class="badge badge-warning">⚠ Vence pronto</span>' : ''}
            </div>
            <div class="task-item__title">${escHtml(t.titulo)}</div>
            <div class="task-item__meta">
                <span><i class="fas fa-building"></i> ${escHtml(t.empresa || '—')}</span>
                <span><i class="fas fa-calendar-alt"></i> ${formatDate(t.fecha_fin)}</span>
                <span><i class="fas fa-user"></i> ${escHtml(t.responsable)}</span>
            </div>
            <div class="task-item__actions">
                <a href="${BASE_URL}/tablero" target="_blank" class="btn-action btn-open">
                    <i class="fas fa-external-link-alt"></i> Tablero
                </a>
                <button class="btn-action btn-edit btn-edit-task" data-id="${t.id}">
                    <i class="fas fa-edit"></i> Editar
                </button>
                ${t.estado !== 'COMPLETADOS' ? `
                <button class="btn-action btn-timer-add"
                        data-id="${t.id}"
                        data-title="${escAttr(t.titulo)}"
                        data-empresa="${escAttr(t.empresa || '')}">
                    <i class="fas fa-stopwatch"></i> Cronómetro
                </button>` : ''}
            </div>
        </div>`;
    }).join('');

    if (tasks.length > 30) {
        container.innerHTML += `<div class="more-hint">+${tasks.length - 30} más — usa los filtros</div>`;
    }

    container.querySelectorAll('.btn-edit-task').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.id));
    });

    container.querySelectorAll('.btn-timer-add').forEach(btn => {
        btn.addEventListener('click', async () => {
            await startTimerFromTask(btn.dataset.id, btn.dataset.title, btn.dataset.empresa);
            showToast('⏱ Cronómetro iniciado', 'info');
            switchTab('timers');
        });
    });
}

async function startTimerFromTask(taskId, taskTitle, taskEmpresa) {
    const timers = await getTimers();
    if (timers[taskId]?.running) return;
    timers[taskId] = {
        running: true, startTime: Date.now(),
        accumulated: timers[taskId]?.accumulated || 0,
        taskTitle, taskEmpresa
    };
    await saveTimers(timers);
    state.timers = timers;
}

// ══════════════════════════════════════════════════════════════
// TAB: NUEVA TAREA
// ══════════════════════════════════════════════════════════════

function initNewForm() {
    const today = new Date().toISOString().split('T')[0];
    const tmrw  = new Date(Date.now() + 86400000).toISOString().split('T')[0];
    $('new-fecha-inicio').value = today;
    if (!$('new-fecha-fin').value) $('new-fecha-fin').value = tmrw;
    if (state.user) {
        if (!$('new-responsable').value)
            $('new-responsable').value = `${state.user.nombres} ${state.user.apellidos}`.trim();
        if (!$('new-empresa').value)
            $('new-empresa').value = state.user.empresa || '';
    }
}

async function handleNewTask(e) {
    e.preventDefault();
    const data = {
        titulo:          $('new-titulo').value.trim(),
        empresa:         $('new-empresa').value.trim(),
        codigo_proyecto: $('new-codigo-proyecto').value.trim(),
        responsable:     $('new-responsable').value.trim(),
        fecha_inicio:    $('new-fecha-inicio').value,
        fecha_fin:       $('new-fecha-fin').value || $('new-fecha-inicio').value,
        horas_estimadas: parseFloat($('new-horas').value) || 8,
        estado:          $('new-estado').value,
        tipo_consumo:    $('new-tipo').value,
        descripcion:     'Tarea creada desde extensión Chrome'
    };
    const btn = $('btn-create-task');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
    try {
        const res = await apiCall('POST', '/api/gantt/tarea', data);
        if (res.ok && res.data?.ok !== false) {
            showToast('✅ Tarea creada exitosamente', 'success');
            e.target.reset();
            initNewForm();
        } else {
            showToast(`❌ ${res.data?.error || res.error || 'Error al crear'}`, 'danger');
        }
    } catch (err) {
        showToast(`❌ ${err.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus"></i> Crear Tarea';
    }
}

// ══════════════════════════════════════════════════════════════
// MODAL: EDITAR TAREA
// ══════════════════════════════════════════════════════════════

let editTaskId = null;

function setupEditModal() {
    $('btn-modal-close').addEventListener('click', closeEditModal);
    $('btn-edit-cancel').addEventListener('click', closeEditModal);
    $('modal-edit').addEventListener('click', e => {
        if (e.target === $('modal-edit')) closeEditModal();
    });
    $('form-edit-task').addEventListener('submit', handleEditSubmit);
}

function openEditModal(taskId) {
    editTaskId = taskId;
    $('modal-edit').classList.remove('hidden');

    const btn = $('btn-edit-save');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';

    apiCall('GET', `/tareas/${taskId}`)
        .then(res => {
            if (res.ok && res.data) {
                populateEditForm(res.data);
            } else {
                closeEditModal();
                showToast('❌ No se pudo cargar la tarea', 'danger');
                return;
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-save"></i> Guardar cambios';
        })
        .catch(err => {
            closeEditModal();
            showToast(`❌ ${err.message}`, 'danger');
        });
}

function populateEditForm(task) {
    $('edit-titulo').value          = task.titulo || '';
    $('edit-empresa').value         = task.empresa || '';
    $('edit-codigo-proyecto').value = task.codigo_proyecto || '';
    $('edit-responsable').value     = task.responsable || '';
    $('edit-fecha-inicio').value    = task.fecha_inicio ? String(task.fecha_inicio).split('T')[0] : '';
    $('edit-fecha-fin').value       = task.fecha_fin   ? String(task.fecha_fin).split('T')[0]   : '';
    $('edit-horas').value           = task.horas_estimadas != null ? task.horas_estimadas : '';
    $('edit-estado').value          = task.estado      || 'PENDIENTE';
    $('edit-tipo').value            = task.tipo_consumo || 'Desarrollo';
}

function closeEditModal() {
    $('modal-edit').classList.add('hidden');
    editTaskId = null;
}

async function handleEditSubmit(e) {
    e.preventDefault();
    if (!editTaskId) return;

    const data = {
        titulo:          $('edit-titulo').value.trim(),
        empresa:         $('edit-empresa').value.trim(),
        codigo_proyecto: $('edit-codigo-proyecto').value.trim(),
        responsable:     $('edit-responsable').value.trim(),
        fecha_inicio:    $('edit-fecha-inicio').value,
        fecha_fin:       $('edit-fecha-fin').value || $('edit-fecha-inicio').value,
        horas_estimadas: parseFloat($('edit-horas').value) || 0,
        estado:          $('edit-estado').value,
        tipo_consumo:    $('edit-tipo').value,
    };

    const btn = $('btn-edit-save');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';

    try {
        const res = await apiCall('PUT', `/tareas/${editTaskId}`, data);
        if (res.ok) {
            showToast('✅ Tarea actualizada', 'success');
            closeEditModal();
            if      (state.currentTab === 'tasks')   loadTasksTab();
            else if (state.currentTab === 'tablero') loadTableroTab();
            else if (state.currentTab === 'timers')  loadTimersTab();
        } else {
            showToast(`❌ ${res.error || 'Error al guardar'}`, 'danger');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-save"></i> Guardar cambios';
        }
    } catch (err) {
        showToast(`❌ ${err.message}`, 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-save"></i> Guardar cambios';
    }
}

// ── Toast ──────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
    document.querySelectorAll('.toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('visible')));
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * notifications_ui.js
 * Campana de notificaciones en el navbar con polling cada 30s.
 * Controla el badge contador, el offcanvas con la lista y las acciones de leer.
 */
(function () {
    'use strict';

    const POLL_INTERVAL = 30000; // 30 segundos

    // ── Utilidades ────────────────────────────────────────────────────────────

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatRelativeTime(dateStr) {
        if (!dateStr) return '';
        // El servidor envía "YYYY-MM-DD HH:MM:SS" en UTC
        const date = new Date(dateStr.replace(' ', 'T') + 'Z');
        const diffSec = Math.floor((Date.now() - date.getTime()) / 1000);
        if (diffSec < 60)    return 'hace un momento';
        if (diffSec < 3600)  return `hace ${Math.floor(diffSec / 60)} min`;
        if (diffSec < 86400) return `hace ${Math.floor(diffSec / 3600)} h`;
        return `hace ${Math.floor(diffSec / 86400)} d`;
    }

    function typeIcon(type) {
        const map = {
            task_assigned:   'fas fa-tasks',
            task_updated:    'fas fa-edit',
            admin_broadcast: 'fas fa-bullhorn',
            file_link:       'fas fa-file-download',
        };
        return map[type] || 'fas fa-bell';
    }

    // ── Badge contador ────────────────────────────────────────────────────────

    function updateBadge(count) {
        const badge = document.getElementById('notif-badge');
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : String(count);
            badge.style.display = 'inline-flex';
        } else {
            badge.style.display = 'none';
        }
    }

    function fetchUnreadCount() {
        fetch('/api/notifications/unread-count', { credentials: 'include' })
            .then(function (r) { return r.ok ? r.json() : { count: 0 }; })
            .then(function (data) { updateBadge(data.count || 0); })
            .catch(function () {});
    }

    // ── Lista de notificaciones ───────────────────────────────────────────────

    function renderList(notifications) {
        const list = document.getElementById('notif-list');
        if (!list) return;

        if (!notifications || notifications.length === 0) {
            list.innerHTML =
                '<li class="notif-empty">' +
                '<i class="fas fa-bell-slash me-2 opacity-50"></i>' +
                'No tienes notificaciones</li>';
            return;
        }

        list.innerHTML = notifications.map(function (n) {
            const hasUrl = n.url && n.url !== 'None' && n.url !== '';
            return (
                '<li class="notif-item' + (n.is_read ? '' : ' unread') + '" ' +
                'data-id="' + n.id + '" ' +
                'onclick="fofiNotif.markRead(' + n.id + ', \'' + escapeHtml(n.url || '') + '\')">' +
                '<span class="notif-icon-wrap"><i class="' + typeIcon(n.type) + '"></i></span>' +
                '<div class="notif-body">' +
                '<div class="notif-title">' + escapeHtml(n.title) + '</div>' +
                '<div class="notif-msg">' + escapeHtml(n.message) + '</div>' +
                '<div class="notif-time">' + formatRelativeTime(n.created_at) + '</div>' +
                (hasUrl ? '<span class="notif-link-label badge bg-primary mt-1">' +
                    escapeHtml(n.url_label || 'Ver') + '</span>' : '') +
                '</div>' +
                '</li>'
            );
        }).join('');
    }

    function loadNotifications() {
        fetch('/api/notifications/list', { credentials: 'include' })
            .then(function (r) { return r.ok ? r.json() : []; })
            .then(function (data) {
                renderList(data);
                fetchUnreadCount();
            })
            .catch(function () {});
    }

    // ── Acciones públicas (expuestas en window.fofiNotif) ────────────────────

    window.fofiNotif = {
        markRead: function (id, url) {
            fetch('/api/notifications/' + id + '/read', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
            })
            .then(function () {
                const item = document.querySelector('.notif-item[data-id="' + id + '"]');
                if (item) item.classList.remove('unread');
                fetchUnreadCount();
                if (url && url !== 'None' && url !== '') {
                    window.location.href = url;
                }
            })
            .catch(function () {});
        },

        markAllRead: function () {
            fetch('/api/notifications/mark-all-read', {
                method: 'PUT',
                credentials: 'include',
            })
            .then(function () {
                document.querySelectorAll('.notif-item.unread')
                    .forEach(function (el) { el.classList.remove('unread'); });
                updateBadge(0);
            })
            .catch(function () {});
        },
    };

    // ── Inicialización ────────────────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', function () {
        // Cargar lista al abrir el offcanvas
        const offcanvas = document.getElementById('notifOffcanvas');
        if (offcanvas) {
            offcanvas.addEventListener('show.bs.offcanvas', function () {
                loadNotifications();
            });
        }

        // Polling del badge
        fetchUnreadCount();
        setInterval(fetchUnreadCount, POLL_INTERVAL);
    });

})();

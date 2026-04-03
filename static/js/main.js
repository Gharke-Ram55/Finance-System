// FinTrack — Zorvyn
// main.js — small, focused utility functions

(function () {
    'use strict';

    // ─── Live date in topbar ───
    function updateDate() {
        const el = document.getElementById('live-date');
        if (!el) return;
        const now = new Date();
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        el.textContent = now.toLocaleDateString('en-IN', options);
    }
    updateDate();

    // ─── Sidebar toggle (mobile) ───
    window.toggleSidebar = function () {
        const sb = document.getElementById('sidebar');
        if (sb) sb.classList.toggle('open');
    };

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
        const sb = document.getElementById('sidebar');
        if (!sb) return;
        if (sb.classList.contains('open') && !sb.contains(e.target)) {
            const toggle = document.querySelector('.sidebar-toggle');
            if (toggle && !toggle.contains(e.target)) {
                sb.classList.remove('open');
            }
        }
    });

    // ─── Auto-dismiss alerts after 4s ───
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (el) {
            el.style.transition = 'opacity 0.4s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 400);
        });
    }, 4000);

    // ─── Confirm dialogs for delete forms ───
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const msg = el.dataset.confirm || 'Are you sure?';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // ─── Category filter based on type selection ───
    const typeSelect = document.getElementById('id_transaction_type');
    if (typeSelect) {
        typeSelect.addEventListener('change', function () {
            // Could be extended to filter categories by type via AJAX
            // Keeping it simple for now; could fetch /api/categories/?type=income etc.
        });
    }

})();

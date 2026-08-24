/* Keyboard shortcuts. "/" focuses search; j and k move through the list of
 * items on a page; "?" shows what is available. Ignored while typing. */
(function () {
    'use strict';

    var ITEM_SELECTOR = [
        '.study-question-link', '.comparison-col a', '.suggest-item',
        'main a.d-flex', 'main .study-card-link', 'main li a[href^="/atlas/"]'
    ].join(',');

    function typing(target) {
        var tag = (target.tagName || '').toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
    }

    var index = -1;

    function items() {
        return Array.prototype.filter.call(
            document.querySelectorAll(ITEM_SELECTOR),
            function (el) { return el.offsetParent !== null; }
        );
    }

    function move(delta) {
        var list = items();
        if (!list.length) return;
        index = Math.max(0, Math.min(list.length - 1, index + delta));
        var el = list[index];
        el.focus({preventScroll: true});
        el.scrollIntoView({block: 'center', behavior: 'smooth'});
    }

    function showHelp() {
        var existing = document.getElementById('shortcuts-help');
        if (existing) { existing.remove(); return; }
        var box = document.createElement('div');
        box.id = 'shortcuts-help';
        box.className = 'shortcuts-help';
        box.setAttribute('role', 'dialog');
        box.setAttribute('aria-label', 'Keyboard shortcuts');
        box.innerHTML =
            '<strong>Keyboard shortcuts</strong>' +
            '<dl><dt>/</dt><dd>search</dd>' +
            '<dt>j / k</dt><dd>next / previous item</dd>' +
            '<dt>g then h</dt><dd>home</dd>' +
            '<dt>Esc</dt><dd>close</dd>' +
            '<dt>?</dt><dd>this help</dd></dl>';
        document.body.appendChild(box);
    }

    var awaitingG = false;

    document.addEventListener('keydown', function (e) {
        if (typing(e.target) || e.metaKey || e.ctrlKey || e.altKey) return;

        if (e.key === '/') {
            var search = document.querySelector('.navbar input[type="search"]');
            if (search) { e.preventDefault(); search.focus(); search.select(); }
        } else if (e.key === 'j') { e.preventDefault(); move(1); }
        else if (e.key === 'k') { e.preventDefault(); move(-1); }
        else if (e.key === '?') { e.preventDefault(); showHelp(); }
        else if (e.key === 'g') { awaitingG = true; setTimeout(function () { awaitingG = false; }, 900); return; }
        else if (e.key === 'h' && awaitingG) { window.location.href = '/'; }
        else if (e.key === 'Escape') {
            var help = document.getElementById('shortcuts-help');
            if (help) help.remove();
        }
        awaitingG = false;
    });
})();

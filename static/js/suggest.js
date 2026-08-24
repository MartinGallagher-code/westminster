/* Typeahead over everything: the standards' text, the Atlas layers, and the
 * ontology's positions. Readers previously had to know the Atlas existed
 * before they could search it.
 *
 * Progressive enhancement: without JS the box is still a search form. */
(function () {
    'use strict';

    var input = document.querySelector('.navbar input[type="search"], #navbar-search');
    if (!input || !window.fetch) return;

    var form = input.closest('form');
    var panel = document.createElement('div');
    panel.className = 'suggest-panel';
    panel.setAttribute('role', 'listbox');
    panel.hidden = true;
    (form || input.parentNode).appendChild(panel);

    var items = [];
    var active = -1;
    var lastQuery = '';
    var timer = null;
    var controller = null;

    function hide() {
        panel.hidden = true;
        active = -1;
        input.setAttribute('aria-expanded', 'false');
    }

    function render(data) {
        items = [];
        panel.innerHTML = '';
        (data.groups || []).forEach(function (group) {
            var heading = document.createElement('div');
            heading.className = 'suggest-group';
            heading.textContent = group.label;
            panel.appendChild(heading);
            group.items.forEach(function (item) {
                var link = document.createElement('a');
                link.className = 'suggest-item';
                link.href = item.url;
                link.setAttribute('role', 'option');
                link.innerHTML =
                    '<span class="suggest-name"></span><span class="suggest-detail"></span>';
                link.querySelector('.suggest-name').textContent = item.name;
                link.querySelector('.suggest-detail').textContent = item.detail || '';
                panel.appendChild(link);
                items.push(link);
            });
        });
        if (!items.length) {
            hide();
            return;
        }
        var all = document.createElement('a');
        all.className = 'suggest-all';
        all.href = data.search_url;
        all.textContent = 'See all results';
        panel.appendChild(all);
        items.push(all);

        panel.hidden = false;
        input.setAttribute('aria-expanded', 'true');
    }

    function highlight(index) {
        items.forEach(function (el) { el.classList.remove('is-active'); });
        if (index >= 0 && index < items.length) {
            items[index].classList.add('is-active');
            items[index].scrollIntoView({block: 'nearest'});
        }
        active = index;
    }

    function fetchSuggestions() {
        var query = input.value.trim();
        if (query.length < 2) { hide(); return; }
        if (query === lastQuery && !panel.hidden) return;
        lastQuery = query;
        if (controller) controller.abort();
        controller = new AbortController();
        fetch('/api/suggest/?q=' + encodeURIComponent(query), {signal: controller.signal})
            .then(function (r) { return r.ok ? r.json() : {groups: []}; })
            .then(render)
            .catch(function () { /* aborted or offline: leave the form alone */ });
    }

    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');

    input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(fetchSuggestions, 160);
    });

    input.addEventListener('keydown', function (e) {
        if (panel.hidden) return;
        if (e.key === 'ArrowDown') { e.preventDefault(); highlight(Math.min(active + 1, items.length - 1)); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(Math.max(active - 1, 0)); }
        else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); items[active].click(); }
        else if (e.key === 'Escape') { hide(); }
    });

    document.addEventListener('click', function (e) {
        if (!panel.contains(e.target) && e.target !== input) hide();
    });
})();

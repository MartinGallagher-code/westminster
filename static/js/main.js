document.addEventListener('DOMContentLoaded', function() {
    // ── Theme (light/dark) toggle ──
    var toggleBtn = document.getElementById('theme-toggle');
    var toggleIcon = document.getElementById('theme-toggle-icon');
    var toggleLabel = document.getElementById('theme-toggle-label');

    function updateToggleUI() {
        var current = document.documentElement.getAttribute('data-bs-theme');
        if (toggleIcon) {
            toggleIcon.className = current === 'dark'
                ? 'bi bi-sun-fill me-2'
                : 'bi bi-moon-stars-fill me-2';
        }
        if (toggleLabel) {
            toggleLabel.textContent = current === 'dark' ? 'Light mode' : 'Dark mode';
        }
    }

    if (toggleBtn) {
        updateToggleUI();
        toggleBtn.addEventListener('click', function() {
            var current = document.documentElement.getAttribute('data-bs-theme');
            var next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
            updateToggleUI();
        });
    }

    // ── Color scheme selector ──
    var SCHEME_COLORS = {
        classic: { primary: '#6B2737', accent: '#B8860B' },
        ocean:   { primary: '#1B4965', accent: '#2A9D8F' },
        forest:  { primary: '#2D5016', accent: '#C07D1A' },
        stone:   { primary: '#4A4440', accent: '#B5703C' },
        royal:   { primary: '#4A2060', accent: '#C8963C' }
    };

    function setColorScheme(scheme) {
        if (scheme === 'classic') {
            document.documentElement.removeAttribute('data-color-scheme');
        } else {
            document.documentElement.setAttribute('data-color-scheme', scheme);
        }
        localStorage.setItem('colorScheme', scheme);

        // Update active states in dropdown
        document.querySelectorAll('.scheme-option').forEach(function(btn) {
            btn.classList.toggle('active', btn.getAttribute('data-scheme') === scheme);
        });

        // Update brand shield SVG colors
        var shield = document.querySelector('.brand-shield');
        if (shield && SCHEME_COLORS[scheme]) {
            var paths = shield.querySelectorAll('path');
            if (paths[0]) {
                paths[0].setAttribute('fill', SCHEME_COLORS[scheme].primary);
                paths[0].setAttribute('stroke', SCHEME_COLORS[scheme].accent);
            }
            if (paths[1]) {
                paths[1].setAttribute('fill', SCHEME_COLORS[scheme].accent);
            }
        }
    }

    // Initialize color scheme from localStorage
    var savedScheme = localStorage.getItem('colorScheme') || 'classic';
    setColorScheme(savedScheme);

    // Bind scheme option buttons
    document.querySelectorAll('.scheme-option').forEach(function(btn) {
        btn.addEventListener('click', function() {
            setColorScheme(this.getAttribute('data-scheme'));
        });
    });


    // Persist active tab across question navigation
    var tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    if (tabButtons.length) {
        var savedTab = localStorage.getItem('activeTab');
        if (savedTab) {
            var target = document.querySelector('[data-bs-target="' + savedTab + '"]');
            if (target) {
                var tab = new bootstrap.Tab(target);
                tab.show();
            }
        }
        tabButtons.forEach(function(btn) {
            btn.addEventListener('shown.bs.tab', function() {
                localStorage.setItem('activeTab', btn.getAttribute('data-bs-target'));
                // Lazy-load commentary content
                var pane = document.querySelector(btn.getAttribute('data-bs-target'));
                if (pane && pane.dataset.lazyUrl && pane.dataset.loaded !== 'true') {
                    fetch(pane.dataset.lazyUrl)
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            pane.innerHTML = data.html;
                            pane.dataset.loaded = 'true';
                            if (window.initHighlightsForPane) {
                                window.initHighlightsForPane(pane);
                            }
                        });
                }
            });
        });
    }


    // ── Document tradition filter ──
    var DEFAULT_FILTERS = {westminster: true, three_forms_of_unity: false, other: false};

    function loadDocFilters() {
        try {
            var raw = localStorage.getItem('docFilters');
            if (raw) {
                var f = JSON.parse(raw);
                if (f.westminster || f.three_forms_of_unity || f.other) {
                    return f;
                }
            }
        } catch(e) {}
        return Object.assign({}, DEFAULT_FILTERS);
    }

    function saveDocFilters(filters) {
        localStorage.setItem('docFilters', JSON.stringify(filters));
    }

    function applyDocFilters(filters) {
        // Remove the FOUC-prevention style tag now that JS is in control
        var foucStyle = document.getElementById('tradition-filter-fouc');
        if (foucStyle) foucStyle.parentNode.removeChild(foucStyle);

        document.querySelectorAll('[data-tradition]').forEach(function(el) {
            var tradition = el.getAttribute('data-tradition');
            if (filters[tradition]) {
                el.classList.remove('doc-tradition-hidden');
            } else {
                el.classList.add('doc-tradition-hidden');
            }
        });

        document.querySelectorAll('.tradition-toggle').forEach(function(btn) {
            var tradition = btn.getAttribute('data-tradition');
            var check = btn.querySelector('.tradition-check');
            var active = !!filters[tradition];
            btn.classList.toggle('active', active);
            if (check) check.style.visibility = active ? 'visible' : 'hidden';
        });
    }

    var docFilters = loadDocFilters();
    applyDocFilters(docFilters);

    document.querySelectorAll('.tradition-toggle').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var tradition = this.getAttribute('data-tradition');
            var next = Object.assign({}, docFilters);
            next[tradition] = !next[tradition];
            // Enforce: at least one must remain active; default to westminster
            if (!next.westminster && !next.three_forms_of_unity && !next.other) {
                next.westminster = true;
            }
            docFilters = next;
            saveDocFilters(docFilters);
            applyDocFilters(docFilters);
        });
    });


    // Add Bootstrap classes to Django form inputs that don't have them
    var formInputs = document.querySelectorAll('form input[type="text"], form input[type="email"], form input[type="password"]');
    formInputs.forEach(function(input) {
        if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
        }
    });
});

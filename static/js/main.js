document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle
    var toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        function updateToggleIcon() {
            var current = document.documentElement.getAttribute('data-bs-theme');
            toggleBtn.innerHTML = current === 'dark'
                ? '<i class="bi bi-sun-fill"></i>'
                : '<i class="bi bi-moon-stars-fill"></i>';
        }
        updateToggleIcon();
        toggleBtn.addEventListener('click', function() {
            var current = document.documentElement.getAttribute('data-bs-theme');
            var next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
            updateToggleIcon();
        });
    }

    // Quick Jump form
    var form = document.getElementById('quick-jump-form');
    if (form) {
        var catSelect = document.getElementById('quick-jump-catechism');
        var numInput = document.getElementById('quick-jump-input');

        // Set initial max and update when catechism selection changes
        if (catSelect) {
            if (catSelect.options.length) {
                var initSelected = catSelect.options[catSelect.selectedIndex];
                numInput.max = initSelected.getAttribute('data-max') || 999;
            }
            catSelect.addEventListener('change', function() {
                var selected = catSelect.options[catSelect.selectedIndex];
                numInput.max = selected.getAttribute('data-max') || 999;
            });
        }

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var num = parseInt(numInput.value);
            var slug = catSelect ? catSelect.value : 'wsc';
            var selected = catSelect ? catSelect.options[catSelect.selectedIndex] : null;
            var max = selected ? parseInt(selected.getAttribute('data-max')) : 999;
            var docType = selected ? selected.getAttribute('data-doc-type') : 'catechism';
            var pathSegment = docType === 'confession' ? 'sections' : 'questions';
            if (num >= 1 && num <= max) {
                window.location.href = '/' + slug + '/' + pathSegment + '/' + num + '/';
            }
        });
    }

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

    // Topic accordion: expand + scroll when jump-to link clicked or URL has hash
    function openAccordionForHash(hash) {
        if (!hash) return;
        var item = document.querySelector(hash + '.accordion-item');
        if (!item) return;
        var collapse = item.querySelector('.accordion-collapse');
        if (collapse && !collapse.classList.contains('show')) {
            var bsCollapse = new bootstrap.Collapse(collapse, { toggle: true });
        }
        setTimeout(function() { item.scrollIntoView({ behavior: 'smooth' }); }, 150);
    }
    if (window.location.hash && document.getElementById('topic-accordion')) {
        openAccordionForHash(window.location.hash);
    }
    document.querySelectorAll('.topic-jump-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var hash = this.getAttribute('href');
            history.replaceState(null, '', hash);
            openAccordionForHash(hash);
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

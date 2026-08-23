document.addEventListener('DOMContentLoaded', function() {

    // ── 1. Document Selector (compare index page) ──

    var docCheckboxes = document.querySelectorAll('.doc-checkbox');
    var compareBtn = document.getElementById('compare-btn');
    var selectionCount = document.getElementById('selection-count');
    var selectAllBtn = document.getElementById('select-all-btn');
    var clearAllBtn = document.getElementById('clear-all-btn');

    function updateCompareButton() {
        var selected = [];
        docCheckboxes.forEach(function(cb) {
            if (cb.checked) selected.push(cb.value);
        });

        if (selected.length >= 2) {
            compareBtn.href = '/compare/custom/?docs=' + selected.join(',');
            compareBtn.setAttribute('aria-disabled', 'false');
            compareBtn.classList.remove('disabled');
            selectionCount.textContent = selected.length + ' documents selected';
        } else {
            compareBtn.href = '#';
            compareBtn.setAttribute('aria-disabled', 'true');
            compareBtn.classList.add('disabled');
            selectionCount.textContent = 'Select at least 2 documents';
        }
    }

    if (docCheckboxes.length) {
        docCheckboxes.forEach(function(cb) {
            cb.addEventListener('change', updateCompareButton);
        });

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', function() {
                docCheckboxes.forEach(function(cb) { cb.checked = true; });
                updateCompareButton();
            });
        }

        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', function() {
                docCheckboxes.forEach(function(cb) { cb.checked = false; });
                updateCompareButton();
            });
        }

        // Preset buttons select a curated group of documents, then let the
        // reader refine the selection before comparing.
        var presetBtns = document.querySelectorAll('.preset-btn');
        presetBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var slugs = (this.getAttribute('data-slugs') || '').split(',');
                docCheckboxes.forEach(function(cb) {
                    cb.checked = slugs.indexOf(cb.value) !== -1;
                });
                updateCompareButton();
            });
        });

        updateCompareButton();
    }

    // ── 2. Narrow-screen document switcher (theme detail pages) ──
    //
    // Below lg the comparison columns stack, so the documents are read in
    // sequence rather than side by side. These tabs show one at a time in
    // place. The classes are maintained at every width; the CSS media query
    // decides when they take effect, so resizing needs no JS.

    var docTabs = document.querySelectorAll('.comparison-doc-tabs .doc-tab');
    var tabbedColumns = document.getElementById('comparison-columns');

    if (docTabs.length && tabbedColumns) {
        var columns = tabbedColumns.querySelectorAll('.comparison-col');

        function showDocument(slug) {
            columns.forEach(function(col) {
                col.classList.toggle('is-active', col.getAttribute('data-doc') === slug);
            });
            docTabs.forEach(function(tab) {
                var active = tab.getAttribute('data-doc') === slug;
                tab.classList.toggle('is-active', active);
                tab.setAttribute('aria-pressed', active ? 'true' : 'false');
            });
        }

        tabbedColumns.classList.add('has-doc-tabs');
        showDocument(docTabs[0].getAttribute('data-doc'));

        docTabs.forEach(function(tab) {
            tab.addEventListener('click', function() {
                showDocument(this.getAttribute('data-doc'));
            });
        });
    }

    // ── 3. Column Toggle (theme detail pages) ──

    var colToggles = document.querySelectorAll('.col-toggle');
    var comparisonColumns = document.getElementById('comparison-columns');

    if (colToggles.length && comparisonColumns) {
        colToggles.forEach(function(toggle) {
            toggle.addEventListener('change', function() {
                var slug = this.value;
                var col = comparisonColumns.querySelector(
                    '.comparison-col[data-doc="' + slug + '"]'
                );
                if (col) {
                    col.style.display = this.checked ? '' : 'none';
                }

                // Recalculate column widths for visible columns
                var visibleCols = comparisonColumns.querySelectorAll(
                    '.comparison-col:not([style*="display: none"])'
                );
                var count = visibleCols.length;
                var colClass;
                if (count <= 1) colClass = 'col-lg-12';
                else if (count === 2) colClass = 'col-lg-6';
                else if (count === 3) colClass = 'col-lg-4';
                else colClass = 'col-lg-3';

                visibleCols.forEach(function(vc) {
                    vc.className = vc.className
                        .replace(/col-lg-\d+/g, '')
                        .replace(/\s+/g, ' ')
                        .trim();
                    vc.classList.add(colClass);
                });
            });
        });
    }
});

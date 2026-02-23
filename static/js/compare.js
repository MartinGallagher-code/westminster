document.addEventListener('DOMContentLoaded', function() {

    // ── 1. Document Selector (compare index page) ──

    var docCheckboxes = document.querySelectorAll('.doc-checkbox');
    var compareBtn = document.getElementById('compare-btn');
    var selectionCount = document.getElementById('selection-count');
    var presetBtns = document.querySelectorAll('.preset-btn');
    var selectAllBtn = document.getElementById('select-all-btn');
    var clearAllBtn = document.getElementById('clear-all-btn');

    var presetMap = window.PRESET_MAP || {};

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

        // Update preset button active states
        presetBtns.forEach(function(btn) {
            var preset = presetMap[btn.getAttribute('data-preset')];
            if (!preset) return;
            var allChecked = preset.catechisms.every(function(slug) {
                var cb = document.getElementById('doc-' + slug);
                return cb && cb.checked;
            });
            // Only mark active if exactly these are checked (no extras)
            var checkedCount = 0;
            docCheckboxes.forEach(function(cb) { if (cb.checked) checkedCount++; });
            btn.classList.toggle('active', allChecked && checkedCount === preset.catechisms.length);
        });
    }

    if (docCheckboxes.length) {
        docCheckboxes.forEach(function(cb) {
            cb.addEventListener('change', updateCompareButton);
        });

        presetBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var preset = presetMap[this.getAttribute('data-preset')];
                if (!preset) return;

                // Clear all first
                docCheckboxes.forEach(function(cb) { cb.checked = false; });

                // Check the preset's catechisms
                preset.catechisms.forEach(function(slug) {
                    var cb = document.getElementById('doc-' + slug);
                    if (cb) cb.checked = true;
                });

                updateCompareButton();
            });
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

        updateCompareButton();
    }

    // ── 2. Column Toggle (theme detail pages) ──

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

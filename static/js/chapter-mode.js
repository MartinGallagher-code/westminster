(function () {
    'use strict';

    var STORAGE_KEY = 'viewMode';
    var btnSection = document.getElementById('btn-section-mode');
    var btnChapter = document.getElementById('btn-chapter-mode');
    var sectionContent = document.getElementById('section-mode-content');
    var chapterContent = document.getElementById('chapter-mode-content');
    var hint = document.getElementById('chapter-mode-hint');
    var navCol = document.getElementById('nav-col');

    if (!btnSection || !btnChapter || !sectionContent || !chapterContent) return;

    function setMode(mode, skipScroll) {
        if (mode === 'chapter') {
            sectionContent.classList.add('d-none');
            chapterContent.classList.remove('d-none');
            btnChapter.classList.add('active');
            btnSection.classList.remove('active');
            if (hint) hint.classList.remove('d-none');
            // Hide the left sidebar in chapter mode since all content is visible
            if (navCol) navCol.classList.add('d-none');
            // Expand main col to full width
            var mainCol = document.getElementById('main-col');
            if (mainCol) {
                mainCol.classList.remove('col-lg-9');
                mainCol.classList.add('col-lg-12');
            }
            // Scroll active item into view
            if (!skipScroll) {
                var active = chapterContent.querySelector('.chapter-mode-active');
                if (active) {
                    active.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        } else {
            sectionContent.classList.remove('d-none');
            chapterContent.classList.add('d-none');
            btnSection.classList.add('active');
            btnChapter.classList.remove('active');
            if (hint) hint.classList.add('d-none');
            if (navCol) navCol.classList.remove('d-none');
            var mainCol = document.getElementById('main-col');
            if (mainCol) {
                mainCol.classList.remove('col-lg-12');
                mainCol.classList.add('col-lg-9');
            }
        }
        localStorage.setItem(STORAGE_KEY, mode);
    }

    btnSection.addEventListener('click', function () {
        setMode('section');
    });

    btnChapter.addEventListener('click', function () {
        setMode('chapter');
    });

    // Clicking a non-active chapter item navigates to that question (in chapter mode)
    var items = chapterContent.querySelectorAll('.chapter-mode-item');
    items.forEach(function (item) {
        item.addEventListener('click', function (e) {
            // Don't intercept clicks on links/buttons inside the item
            if (e.target.closest('a, button')) return;
            var url = item.getAttribute('data-question-url');
            if (url) {
                // Preserve chapter mode across navigation
                window.location.href = url;
            }
        });
    });

    // Restore saved mode on page load
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'chapter') {
        setMode('chapter', true);
    }
})();

(function () {
    'use strict';

    var STORAGE_KEY = 'viewMode';
    var btnSection = document.getElementById('btn-section-mode');
    var btnChapter = document.getElementById('btn-chapter-mode');
    var sectionContent = document.getElementById('section-mode-content');
    var chapterContent = document.getElementById('chapter-mode-content');
    var hint = document.getElementById('chapter-mode-hint');
    var navCol = document.getElementById('nav-col');
    var mainCol = document.getElementById('main-col');

    if (!btnSection || !btnChapter || !mainCol || !chapterContent) return;

    function setMode(mode, skipScroll) {
        if (mode === 'chapter') {
            // Hide section-mode main column, show chapter-mode column
            mainCol.classList.add('d-none');
            chapterContent.classList.remove('d-none');
            btnChapter.classList.add('active');
            btnSection.classList.remove('active');
            if (hint) hint.classList.remove('d-none');
            // Keep nav sidebar visible (it's the page tree)
            if (navCol) {
                navCol.classList.remove('d-none');
                navCol.classList.add('d-lg-block');
            }
            // Scroll active item into view
            if (!skipScroll) {
                var active = chapterContent.querySelector('.chapter-mode-active');
                if (active) {
                    active.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        } else {
            // Show section-mode main column, hide chapter-mode column
            mainCol.classList.remove('d-none');
            chapterContent.classList.add('d-none');
            btnSection.classList.add('active');
            btnChapter.classList.remove('active');
            if (hint) hint.classList.add('d-none');
            if (navCol) {
                navCol.classList.remove('d-none');
                navCol.classList.add('d-lg-block');
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

    // Clicking a chapter item switches to section mode on that question's page
    var items = chapterContent.querySelectorAll('.chapter-mode-item');
    items.forEach(function (item) {
        item.addEventListener('click', function () {
            var url = item.getAttribute('data-question-url');
            if (url) {
                // Force section mode for the destination page
                localStorage.setItem(STORAGE_KEY, 'section');
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

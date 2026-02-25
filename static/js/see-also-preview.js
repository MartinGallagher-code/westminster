(function () {
    'use strict';

    var mainCol = document.getElementById('main-col');
    var previewCol = document.getElementById('preview-col');
    if (!mainCol || !previewCol) return;

    var titleEl = document.getElementById('preview-title');
    var questionEl = document.getElementById('preview-question');
    var answerEl = document.getElementById('preview-answer');
    var linkEl = document.getElementById('preview-link');
    var closeBtn = document.getElementById('preview-close');

    var activePk = null;

    function openPanel(data) {
        // Build title label
        var label = data.abbreviation + ' ' + data.item_prefix + data.display_number;
        titleEl.textContent = label;

        // Question text
        if (data.is_confession) {
            questionEl.textContent = data.question_text;
        } else {
            questionEl.textContent = 'Q. ' + data.question_text;
        }

        // Answer text
        if (data.is_confession) {
            answerEl.textContent = data.answer_text;
        } else {
            answerEl.textContent = 'A. ' + data.answer_text;
        }

        linkEl.href = data.url;

        // Show the panel and shrink the main column
        mainCol.classList.remove('col-lg-9');
        mainCol.classList.add('col-lg-5');
        previewCol.classList.remove('d-none');

        // On small screens, scroll to the preview panel
        if (window.innerWidth < 992) {
            previewCol.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function closePanel() {
        previewCol.classList.add('d-none');
        mainCol.classList.remove('col-lg-5');
        mainCol.classList.add('col-lg-9');

        // Clear active link highlight
        var prev = document.querySelector('.see-also-link.active');
        if (prev) prev.classList.remove('active');
        activePk = null;
    }

    // Close button
    closeBtn.addEventListener('click', closePanel);

    // Delegate click on see-also links
    document.addEventListener('click', function (e) {
        var link = e.target.closest('.see-also-link');
        if (!link) return;

        e.preventDefault();
        var pk = link.dataset.previewPk;
        if (!pk) return;

        // If same link clicked again, toggle panel closed
        if (pk === activePk) {
            closePanel();
            return;
        }

        // Highlight active link
        var prev = document.querySelector('.see-also-link.active');
        if (prev) prev.classList.remove('active');
        link.classList.add('active');
        activePk = pk;

        // Show loading state
        titleEl.textContent = 'Loading\u2026';
        questionEl.textContent = '';
        answerEl.textContent = '';
        linkEl.href = link.href;

        // Show panel immediately so the user sees something
        mainCol.classList.remove('col-lg-9');
        mainCol.classList.add('col-lg-5');
        previewCol.classList.remove('d-none');

        fetch('/api/question/' + pk + '/preview/')
            .then(function (res) {
                if (!res.ok) throw new Error(res.status);
                return res.json();
            })
            .then(function (data) {
                // Only update if this is still the active request
                if (activePk === pk) {
                    openPanel(data);
                }
            })
            .catch(function () {
                if (activePk === pk) {
                    titleEl.textContent = 'Error';
                    questionEl.textContent = 'Could not load preview.';
                    answerEl.textContent = '';
                }
            });
    });
})();

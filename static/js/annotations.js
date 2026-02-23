document.addEventListener('DOMContentLoaded', function() {
    var config = window.COMMENT_CONFIG;
    if (!config) return;

    var annotationData = []; // all annotations for this question

    // ── 1. Load existing annotations ──
    function loadAnnotations() {
        fetch(config.listCreateUrl + '?question_id=' + config.questionId, {
            credentials: 'same-origin'
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            annotationData = data.comments || [];
            annotationData.forEach(function(c) {
                applyAnnotation(c);
            });
        });
    }

    loadAnnotations();

    // Expose for lazy-loaded commentary panes
    window.initAnnotationsForPane = function(pane) {
        annotationData.forEach(function(c) {
            if (c.content_type_tag === 'commentary' && c.commentary_id) {
                var container = pane.querySelector(
                    '[data-content-type="commentary"][data-commentary-id="' + c.commentary_id + '"]'
                );
                if (container) {
                    applyAnnotation(c, container);
                }
            }
        });
    };

    // ── 2. Apply annotation to the DOM ──
    function findContainer(commentObj) {
        if (commentObj.content_type_tag === 'commentary' && commentObj.commentary_id) {
            return document.querySelector(
                '[data-content-type="commentary"][data-commentary-id="' + commentObj.commentary_id + '"]'
            );
        }
        return document.querySelector(
            '[data-content-type="' + commentObj.content_type_tag + '"][data-question-id="' + config.questionId + '"]'
        );
    }

    function applyAnnotation(commentObj, container) {
        container = container || findContainer(commentObj);
        if (!container) return;

        var text = commentObj.selected_text;
        var occurrence = commentObj.occurrence_index;
        var fullText = container.textContent;

        var pos = -1;
        for (var i = 0; i <= occurrence; i++) {
            pos = fullText.indexOf(text, pos + 1);
            if (pos === -1) return;
        }

        wrapRange(container, pos, pos + text.length, commentObj.id);
    }

    function wrapRange(container, start, end, commentId) {
        var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
        var nodes = [];
        var node;
        while (node = walker.nextNode()) {
            // Skip text inside existing marks
            if (node.parentElement.closest('mark.user-annotation')) continue;
            nodes.push({ node: node, length: node.textContent.length });
        }

        var offset = 0;
        for (var i = 0; i < nodes.length; i++) {
            nodes[i].start = offset;
            offset += nodes[i].length;
        }

        for (var i = nodes.length - 1; i >= 0; i--) {
            var n = nodes[i];
            var nStart = n.start;
            var nEnd = nStart + n.length;
            if (nEnd <= start || nStart >= end) continue;

            var overlapStart = Math.max(start, nStart) - nStart;
            var overlapEnd = Math.min(end, nEnd) - nStart;

            var textNode = n.node;
            if (overlapEnd < textNode.textContent.length) {
                textNode.splitText(overlapEnd);
            }
            if (overlapStart > 0) {
                textNode = textNode.splitText(overlapStart);
            }

            var mark = document.createElement('mark');
            mark.className = 'user-annotation';
            mark.setAttribute('data-comment-id', commentId);
            textNode.parentNode.replaceChild(mark, textNode);
            mark.appendChild(textNode);
        }
    }

    // ── 3. Selection UI ──
    var annotateBtn = document.createElement('button');
    annotateBtn.textContent = 'Annotate';
    annotateBtn.className = 'btn btn-sm shadow';
    annotateBtn.style.cssText =
        'position:absolute;z-index:1055;display:none;' +
        'background-color:var(--wm-accent);color:#fff;border:none;font-size:0.8rem;';
    document.body.appendChild(annotateBtn);

    var pendingSelection = null;

    document.addEventListener('mouseup', function(e) {
        if (e.target.closest('.annotation-popover') || e.target === annotateBtn) return;

        var sel = window.getSelection();
        if (!sel || sel.isCollapsed || !sel.toString().trim()) {
            annotateBtn.style.display = 'none';
            return;
        }

        var anchorContainer = sel.anchorNode.parentElement.closest('[data-annotatable]');
        var focusContainer = sel.focusNode.parentElement.closest('[data-annotatable]');
        if (!anchorContainer || anchorContainer !== focusContainer) {
            annotateBtn.style.display = 'none';
            return;
        }

        var rect = sel.getRangeAt(0).getBoundingClientRect();
        var isCommentary = anchorContainer.getAttribute('data-content-type') === 'commentary';

        // Position next to the highlight button (if in commentary) or centered (if in Q/A)
        var leftOffset = isCommentary ? 45 : 0;
        annotateBtn.style.left = (rect.left + window.scrollX + rect.width / 2 - 35 + leftOffset) + 'px';
        annotateBtn.style.top = (rect.top + window.scrollY - 36) + 'px';
        annotateBtn.style.display = 'block';

        pendingSelection = {
            container: anchorContainer,
            text: sel.toString(),
            range: sel.getRangeAt(0).cloneRange()
        };
    });

    annotateBtn.onclick = function() {
        if (pendingSelection) {
            showCreateForm(pendingSelection.container, pendingSelection.text, pendingSelection.range);
        }
        annotateBtn.style.display = 'none';
    };

    document.addEventListener('mousedown', function(e) {
        if (e.target !== annotateBtn && !e.target.closest('.annotation-popover')) {
            annotateBtn.style.display = 'none';
        }
    });

    // ── 4. Create annotation popover ──
    var activePopover = null;

    function removeActivePopover() {
        if (activePopover) {
            activePopover.remove();
            activePopover = null;
        }
    }

    function showCreateForm(container, selectedText, range) {
        removeActivePopover();

        var popover = document.createElement('div');
        popover.className = 'annotation-popover shadow';

        var preview = selectedText.length > 50 ? selectedText.substring(0, 50) + '...' : selectedText;
        popover.innerHTML =
            '<div class="annotation-popover-header">' +
                '<small class="text-muted">"' + escapeHtml(preview) + '"</small>' +
            '</div>' +
            '<textarea class="form-control form-control-sm mb-2" rows="3" ' +
                'placeholder="Write your annotation..."></textarea>' +
            '<div class="d-flex justify-content-end gap-1">' +
                '<button class="btn btn-sm btn-outline-secondary annotation-cancel">Cancel</button>' +
                '<button class="btn btn-sm btn-primary annotation-save">Save</button>' +
            '</div>';

        var rect = range.getBoundingClientRect();
        popover.style.left = Math.max(8, rect.left + window.scrollX) + 'px';
        popover.style.top = (rect.bottom + window.scrollY + 8) + 'px';

        document.body.appendChild(popover);
        activePopover = popover;

        var textarea = popover.querySelector('textarea');
        textarea.focus();

        // Allow Ctrl+Enter / Cmd+Enter to save
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                popover.querySelector('.annotation-save').click();
            }
        });

        popover.querySelector('.annotation-cancel').onclick = function() {
            removeActivePopover();
            window.getSelection().removeAllRanges();
        };

        popover.querySelector('.annotation-save').onclick = function() {
            var commentText = textarea.value.trim();
            if (!commentText) return;
            saveAnnotation(container, selectedText, commentText);
            removeActivePopover();
        };

        // Close on outside click (deferred to avoid immediate close)
        setTimeout(function() {
            document.addEventListener('mousedown', closePopoverOnOutsideClick);
        }, 0);
    }

    function closePopoverOnOutsideClick(e) {
        if (activePopover && !activePopover.contains(e.target) && !e.target.closest('mark.user-annotation')) {
            removeActivePopover();
            document.removeEventListener('mousedown', closePopoverOnOutsideClick);
        }
    }

    // ── 5. Save annotation via AJAX ──
    function saveAnnotation(container, selectedText, commentText) {
        var contentType = container.getAttribute('data-content-type');
        var commentaryId = container.getAttribute('data-commentary-id') || null;

        // Calculate occurrence_index
        var fullText = container.textContent;
        var sel = window.getSelection();
        var occurrenceIndex = 0;

        if (sel && sel.rangeCount > 0) {
            var selRange = sel.getRangeAt(0);
            var preRange = document.createRange();
            preRange.setStart(container, 0);
            preRange.setEnd(selRange.startContainer, selRange.startOffset);
            var selStart = preRange.toString().length;

            var searchPos = 0;
            while (true) {
                var found = fullText.indexOf(selectedText, searchPos);
                if (found === -1 || found >= selStart) break;
                occurrenceIndex++;
                searchPos = found + 1;
            }
        }

        fetch(config.listCreateUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                question_id: config.questionId,
                content_type_tag: contentType,
                commentary_id: commentaryId ? parseInt(commentaryId) : null,
                selected_text: selectedText,
                occurrence_index: occurrenceIndex,
                comment_text: commentText
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.id) {
                var newComment = {
                    id: data.id,
                    content_type_tag: contentType,
                    commentary_id: commentaryId,
                    selected_text: selectedText,
                    occurrence_index: occurrenceIndex,
                    comment_text: commentText
                };
                annotationData.push(newComment);
                applyAnnotation(newComment);
            }
            window.getSelection().removeAllRanges();
        });
    }

    // ── 6. View/Edit/Delete on click ──
    document.addEventListener('click', function(e) {
        var mark = e.target.closest('mark.user-annotation');
        if (!mark) return;
        e.preventDefault();
        e.stopPropagation();
        showDetailPopover(mark);
    });

    function showDetailPopover(markEl) {
        removeActivePopover();

        var commentId = markEl.getAttribute('data-comment-id');
        var commentObj = null;
        for (var i = 0; i < annotationData.length; i++) {
            if (String(annotationData[i].id) === String(commentId)) {
                commentObj = annotationData[i];
                break;
            }
        }
        if (!commentObj) return;

        var popover = document.createElement('div');
        popover.className = 'annotation-popover shadow';
        renderDetailView(popover, commentObj);

        var rect = markEl.getBoundingClientRect();
        popover.style.left = Math.max(8, rect.left + window.scrollX) + 'px';
        popover.style.top = (rect.bottom + window.scrollY + 8) + 'px';

        document.body.appendChild(popover);
        activePopover = popover;

        setTimeout(function() {
            document.addEventListener('mousedown', closePopoverOnOutsideClick);
        }, 0);
    }

    function renderDetailView(popover, commentObj) {
        var preview = commentObj.selected_text;
        if (preview.length > 50) preview = preview.substring(0, 50) + '...';

        popover.innerHTML =
            '<div class="annotation-popover-header">' +
                '<small class="text-muted">"' + escapeHtml(preview) + '"</small>' +
            '</div>' +
            '<p class="mb-2" style="font-size:0.875rem;white-space:pre-wrap;">' + escapeHtml(commentObj.comment_text) + '</p>' +
            '<div class="d-flex justify-content-end gap-1">' +
                '<button class="btn btn-sm btn-outline-secondary annotation-edit"><i class="bi bi-pencil me-1"></i>Edit</button>' +
                '<button class="btn btn-sm btn-outline-danger annotation-delete"><i class="bi bi-trash me-1"></i>Delete</button>' +
            '</div>';

        popover.querySelector('.annotation-edit').onclick = function() {
            renderEditView(popover, commentObj);
        };

        popover.querySelector('.annotation-delete').onclick = function() {
            deleteAnnotation(commentObj.id);
            removeActivePopover();
        };
    }

    function renderEditView(popover, commentObj) {
        var preview = commentObj.selected_text;
        if (preview.length > 50) preview = preview.substring(0, 50) + '...';

        popover.innerHTML =
            '<div class="annotation-popover-header">' +
                '<small class="text-muted">"' + escapeHtml(preview) + '"</small>' +
            '</div>' +
            '<textarea class="form-control form-control-sm mb-2" rows="3"></textarea>' +
            '<div class="d-flex justify-content-end gap-1">' +
                '<button class="btn btn-sm btn-outline-secondary annotation-edit-cancel">Cancel</button>' +
                '<button class="btn btn-sm btn-primary annotation-edit-save">Save</button>' +
            '</div>';

        var textarea = popover.querySelector('textarea');
        textarea.value = commentObj.comment_text;
        textarea.focus();

        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                popover.querySelector('.annotation-edit-save').click();
            }
        });

        popover.querySelector('.annotation-edit-cancel').onclick = function() {
            renderDetailView(popover, commentObj);
        };

        popover.querySelector('.annotation-edit-save').onclick = function() {
            var newText = textarea.value.trim();
            if (!newText) return;
            updateAnnotation(commentObj.id, newText, function() {
                commentObj.comment_text = newText;
                renderDetailView(popover, commentObj);
            });
        };
    }

    // ── 7. Update annotation via AJAX ──
    function updateAnnotation(commentId, commentText, onSuccess) {
        var url = config.updateUrlTemplate.replace('{id}', commentId);
        fetch(url, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({ comment_text: commentText })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.updated && onSuccess) onSuccess();
        });
    }

    // ── 8. Delete annotation via AJAX ──
    function deleteAnnotation(commentId) {
        var url = config.deleteUrlTemplate.replace('{id}', commentId);
        fetch(url, {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: { 'X-CSRFToken': config.csrfToken }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.deleted) {
                // Unwrap all marks with this comment ID
                var marks = document.querySelectorAll('mark[data-comment-id="' + commentId + '"]');
                marks.forEach(function(m) {
                    var parent = m.parentNode;
                    while (m.firstChild) {
                        parent.insertBefore(m.firstChild, m);
                    }
                    parent.removeChild(m);
                    parent.normalize();
                });

                // Remove from local data
                annotationData = annotationData.filter(function(c) {
                    return String(c.id) !== String(commentId);
                });
            }
        });
    }

    // ── Utility ──
    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }
});

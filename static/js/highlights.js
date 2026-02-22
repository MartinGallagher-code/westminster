document.addEventListener('DOMContentLoaded', function() {
    var config = window.HIGHLIGHT_CONFIG;
    if (!config) return;

    var highlightData = {};

    // ── 1. Load existing highlights ──
    function initHighlightsForContainers(containers) {
        if (!containers.length) return;

        var ids = [];
        containers.forEach(function(el) {
            ids.push(el.getAttribute('data-commentary-id'));
        });

        var url = config.listCreateUrl + '?' + ids.map(function(id) {
            return 'commentary_id=' + id;
        }).join('&');

        fetch(url, { credentials: 'same-origin' })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                data.highlights.forEach(function(h) {
                    if (!highlightData[h.commentary_id]) {
                        highlightData[h.commentary_id] = [];
                    }
                    highlightData[h.commentary_id].push(h);
                });
                containers.forEach(function(el) {
                    var cid = el.getAttribute('data-commentary-id');
                    if (highlightData[cid]) {
                        highlightData[cid].forEach(function(h) {
                            applyHighlight(el, h);
                        });
                    }
                });
            });
    }

    // Init highlights for all commentary containers on the page
    var containers = document.querySelectorAll('.commentary-text[data-commentary-id]');
    initHighlightsForContainers(containers);

    // Expose function for lazy-loaded panes
    window.initHighlightsForPane = function(pane) {
        var paneContainers = pane.querySelectorAll('.commentary-text[data-commentary-id]');
        initHighlightsForContainers(paneContainers);
    };

    // ── 2. Apply a highlight to the DOM ──
    function applyHighlight(container, highlightObj) {
        var text = highlightObj.selected_text;
        var occurrence = highlightObj.occurrence_index;
        var fullText = container.textContent;

        var pos = -1;
        for (var i = 0; i <= occurrence; i++) {
            pos = fullText.indexOf(text, pos + 1);
            if (pos === -1) return;
        }

        wrapRange(container, pos, pos + text.length, highlightObj.id);
    }

    function wrapRange(container, start, end, highlightId) {
        var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
        var nodes = [];
        var node;
        while (node = walker.nextNode()) {
            nodes.push({ node: node, length: node.textContent.length });
        }

        var offset = 0;
        for (var i = 0; i < nodes.length; i++) {
            nodes[i].start = offset;
            offset += nodes[i].length;
        }

        // Process in reverse to avoid invalidating offsets
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
            mark.className = 'user-highlight';
            mark.setAttribute('data-highlight-id', highlightId);
            textNode.parentNode.replaceChild(mark, textNode);
            mark.appendChild(textNode);
        }
    }

    // ── 3. Selection UI ──
    var highlightBtn = document.createElement('button');
    highlightBtn.textContent = 'Highlight';
    highlightBtn.className = 'btn btn-warning btn-sm shadow';
    highlightBtn.style.cssText = 'position:absolute;z-index:1050;display:none;';
    document.body.appendChild(highlightBtn);

    document.addEventListener('mouseup', function(e) {
        // Don't interfere with the remove popover
        if (e.target.closest('.highlight-popover') || e.target === highlightBtn) return;

        var sel = window.getSelection();
        if (!sel || sel.isCollapsed || !sel.toString().trim()) {
            highlightBtn.style.display = 'none';
            return;
        }

        var anchorContainer = sel.anchorNode.parentElement.closest('.commentary-text[data-commentary-id]');
        var focusContainer = sel.focusNode.parentElement.closest('.commentary-text[data-commentary-id]');
        if (!anchorContainer || anchorContainer !== focusContainer) {
            highlightBtn.style.display = 'none';
            return;
        }

        var rect = sel.getRangeAt(0).getBoundingClientRect();
        highlightBtn.style.left = (rect.left + window.scrollX + rect.width / 2 - 40) + 'px';
        highlightBtn.style.top = (rect.top + window.scrollY - 36) + 'px';
        highlightBtn.style.display = 'block';

        highlightBtn.onclick = function() {
            saveHighlight(anchorContainer, sel.toString());
            highlightBtn.style.display = 'none';
        };
    });

    document.addEventListener('mousedown', function(e) {
        if (e.target !== highlightBtn) {
            highlightBtn.style.display = 'none';
        }
    });

    // ── 4. Save a new highlight ──
    function saveHighlight(container, selectedText) {
        var commentaryId = container.getAttribute('data-commentary-id');
        var fullText = container.textContent;

        // Calculate occurrence_index
        var selRange = window.getSelection().getRangeAt(0);
        var preRange = document.createRange();
        preRange.setStart(container, 0);
        preRange.setEnd(selRange.startContainer, selRange.startOffset);
        var selStart = preRange.toString().length;

        var occurrenceIndex = 0;
        var searchPos = 0;
        while (true) {
            var found = fullText.indexOf(selectedText, searchPos);
            if (found === -1 || found >= selStart) break;
            occurrenceIndex++;
            searchPos = found + 1;
        }

        fetch(config.listCreateUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                commentary_id: parseInt(commentaryId),
                selected_text: selectedText,
                occurrence_index: occurrenceIndex
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.id) {
                applyHighlight(container, {
                    id: data.id,
                    selected_text: selectedText,
                    occurrence_index: occurrenceIndex
                });
                if (!highlightData[commentaryId]) {
                    highlightData[commentaryId] = [];
                }
                highlightData[commentaryId].push({
                    id: data.id,
                    selected_text: selectedText,
                    occurrence_index: occurrenceIndex
                });
            }
            window.getSelection().removeAllRanges();
        });
    }

    // ── 5. Remove highlight on click ──
    var removePopover = null;

    document.addEventListener('click', function(e) {
        var mark = e.target.closest('mark.user-highlight');
        if (!mark) return;
        e.preventDefault();
        showRemovePopover(mark);
    });

    function showRemovePopover(markEl) {
        if (removePopover) {
            removePopover.remove();
            removePopover = null;
        }

        removePopover = document.createElement('div');
        removePopover.className = 'highlight-popover shadow-sm';
        removePopover.innerHTML = '<button class="btn btn-sm btn-outline-danger">Remove highlight</button>';
        removePopover.style.cssText = 'position:absolute;z-index:1050;background:#fff;border:1px solid #ddd;border-radius:4px;padding:4px 8px;';

        var rect = markEl.getBoundingClientRect();
        removePopover.style.left = (rect.left + window.scrollX) + 'px';
        removePopover.style.top = (rect.bottom + window.scrollY + 4) + 'px';
        document.body.appendChild(removePopover);

        removePopover.querySelector('button').onclick = function() {
            var highlightId = markEl.getAttribute('data-highlight-id');
            deleteHighlight(highlightId, markEl);
            removePopover.remove();
            removePopover = null;
        };

        setTimeout(function() {
            document.addEventListener('mousedown', closeRemovePopover);
        }, 0);
    }

    function closeRemovePopover(e) {
        if (removePopover && !removePopover.contains(e.target) && !e.target.closest('mark.user-highlight')) {
            removePopover.remove();
            removePopover = null;
            document.removeEventListener('mousedown', closeRemovePopover);
        }
    }

    // ── 6. Delete a highlight ──
    function deleteHighlight(highlightId, markEl) {
        var url = config.deleteUrlTemplate.replace('{id}', highlightId);

        fetch(url, {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: { 'X-CSRFToken': config.csrfToken }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.deleted) {
                // Unwrap all <mark> elements with this highlight ID
                var marks = document.querySelectorAll('mark[data-highlight-id="' + highlightId + '"]');
                marks.forEach(function(m) {
                    var parent = m.parentNode;
                    while (m.firstChild) {
                        parent.insertBefore(m.firstChild, m);
                    }
                    parent.removeChild(m);
                    parent.normalize();
                });
            }
        });
    }
});

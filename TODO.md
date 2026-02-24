# TODO — Next Steps

1. **Configurable comparison page** — Allow users to configure which documents to compare side-by-side on a topic. Consider pre-sets (e.g. "Westminster family", "Continental Reformed") and/or a custom selector for picking documents.

---

## Backlog: Apply Document Collection Filter Site-Wide

### Goal
Make the Westminster / Three Forms of Unity / Other document collection filter affect
**every** page, feature, and count on the site — not just the home page and navbar.

Currently the filter lives only in `localStorage` and hides/shows DOM elements via CSS.
To filter server-rendered content (search results, scripture counts, cross-references,
comparisons, See Also links, etc.) the **backend must also know** which traditions the
user has selected.

---

### Architecture: Cookie-Based Filter Propagation

Replace `localStorage`-only storage with a **dual cookie + localStorage** approach:

- When the user toggles the filter, write it to both `localStorage` (for instant CSS
  show/hide as today) **and** a `docFilters` **cookie** (sent automatically with every
  HTTP request).
- A Django utility `get_active_traditions(request)` reads the cookie and returns a list
  such as `['westminster', 'three_forms_of_unity']`. Falls back to `['westminster']`.
- Views pass that list into every ORM query that touches `Catechism` or `Question`.
- Pages that show server-rendered counts/results are marked `data-filter-sensitive` on
  `<body>` so that JS triggers a page reload whenever the filter changes.

---

### Tasks

#### Phase 1 — Infrastructure

- [ ] **1.1 Write filter to cookie on every change** (`static/js/main.js`)
  - In `saveDocFilters()`, also set `document.cookie = 'docFilters=<json>; path=/'`.
  - On page load, sync `localStorage` from the cookie so state is consistent.

- [ ] **1.2 Add `get_active_traditions(request)` utility** (`catechism/views.py` or
  `catechism/utils.py`)
  - Reads the `docFilters` cookie; falls back to `['westminster']` if absent/invalid.

- [ ] **1.3 Expose `active_traditions` in global template context**
  (`catechism/context_processors.py`)

- [ ] **1.4 Reload `data-filter-sensitive` pages when filter changes**
  (`static/js/main.js`)
  - After saving the cookie, check for `data-filter-sensitive` on the page and call
    `location.reload()` (with a short debounce).

---

#### Phase 2 — Home Page (`/`)

- [ ] **2.1 Filter "Question of the Day" server-side** (`HomeView`)
  - Random questions should only be drawn from documents in the active traditions:
    `Catechism.objects.filter(tradition__in=active_traditions)`.

- [ ] **2.2 Filter document count/headings**
  - Pass the filtered queryset to the template instead of relying on CSS hiding for
    any summary counts.

---

#### Phase 3 — Search (`/search/`)

- [ ] **3.1 Filter search queryset by active traditions** (`SearchView`)
  - Add `.filter(catechism__tradition__in=active_traditions)` to the `Question`
    queryset. Mark page `data-filter-sensitive`.

- [ ] **3.2 Update "X results across Y documents" summary** (`search_results.html`)

---

#### Phase 4 — Scripture Index & Book Pages

- [ ] **4.1 Filter citation counts in Scripture Index** (`ScriptureIndexView`)
  - Filter `ScriptureIndex` annotations by `question__catechism__tradition__in=...`.
  - Mark page `data-filter-sensitive`.

- [ ] **4.2 Filter citation list in Scripture Book view** (`ScriptureBookView`)
  - Filter entries shown to questions from active traditions.
  - Hide empty document groups in `scripture_book.html`.

---

#### Phase 5 — Compare Feature

- [ ] **5.1 Compare Index — hide sets with no active-tradition entries**
  (`CompareIndexView` + `compare_index.html`)
  - A set is relevant if at least one `ComparisonEntry` catechism is in active
    traditions.

- [ ] **5.2 Compare List — hide themes with no active-tradition entries**
  (`CompareSetView` + `compare_list.html`)

- [ ] **5.3 Compare Theme — filter columns to active traditions**
  (`CompareSetThemeView` + `compare_theme.html` + `compare.js`)
  - Only render columns for catechisms whose tradition is active. Update column
    headings/counts. Hide show/hide toggles for filtered-out columns. Mark
    `data-filter-sensitive`.

- [ ] **5.4 Custom Compare — only offer active-tradition documents**
  (`CustomCompareView` + `compare_custom.html`)
  - Restrict the selectable document list to active traditions. Hide presets that
    reference unavailable documents. Mark `data-filter-sensitive`.

- [ ] **5.5 Custom Compare Theme — intersect selection with active traditions**
  (`CustomCompareThemeView` + `compare_custom_theme.html`)
  - Only show columns for documents that are both user-selected AND in an active
    tradition.

---

#### Phase 6 — See Also / Cross-References (Question Detail)

- [ ] **6.1 Filter `StandardCrossReference` groups** (`QuestionDetailView`)
  - Only include target catechisms whose tradition is in `active_traditions`.
  - Remove empty group headers in `question_detail.html`.

- [ ] **6.2 Filter WSC ↔ WLC cross-reference link**
  - Only show the WLC cross-reference link if `westminster` is active.

- [ ] **6.3 Filter comparison-theme backlinks**
  - Only show themes that have at least one column from an active tradition.

- [ ] **6.4 Filter cross-reference hover preview API**
  (`/api/question/<pk>/preview/` + `see-also-preview.js`)
  - Read the `docFilters` cookie in the view (or accept `traditions` as a query
    param). Return 404 / empty if the target question's tradition is not active.
  - JS caller passes the current filter state as a query param.

---

#### Phase 7 — Navbar & Global UI

- [ ] **7.1 Navbar document count badge** (`navbar.html`)
  - If a "Documents (N)" badge exists, update its count via JS after
    `applyDocFilters()` to reflect only visible documents.

- [ ] **7.2 Out-of-filter document banner** (`question_detail.html`)
  - If a user navigates directly to a document outside their active filter, show a
    banner with an option to add that tradition to their filter.

---

#### Phase 8 — Testing

- [ ] **8.1 Unit tests for `get_active_traditions()`**
  - Cookie parsing, fallback to Westminster, multiple-tradition combinations.

- [ ] **8.2 View tests for filtered querysets**
  - Search, scripture, compare, cross-reference views return only filtered results.

- [ ] **8.3 Manual smoke test checklist**
  - Westminster only: home, search, scripture counts, compare columns, See Also
  - TFU only: same
  - Other only: only Inst/HOT visible everywhere
  - All three: everything shows
  - Changing filter on scripture/search/compare pages reloads with updated data
  - Cross-reference hover preview does not appear for filtered-out documents

---

### File Change Summary

| File | Changes needed |
|------|---------------|
| `static/js/main.js` | Write cookie on filter change; reload `data-filter-sensitive` pages |
| `static/js/see-also-preview.js` | Pass tradition filter as query param to preview API |
| `static/js/compare.js` | Operate toggle logic on active-tradition columns only |
| `catechism/views.py` | Add `get_active_traditions()`; filter all querysets |
| `catechism/context_processors.py` | Expose `active_traditions` globally |
| `templates/catechism/home.html` | Use server-filtered queryset for counts |
| `templates/catechism/search_results.html` | Show filtered result count |
| `templates/catechism/scripture_index.html` | Counts from filtered view |
| `templates/catechism/scripture_book.html` | Hide empty document groups |
| `templates/catechism/compare_index.html` | Hide sets with no active entries |
| `templates/catechism/compare_list.html` | Hide themes with no active entries |
| `templates/catechism/compare_theme.html` | Filter columns; update count text |
| `templates/catechism/compare_custom.html` | Only show active-tradition documents |
| `templates/catechism/compare_custom_theme.html` | Filter columns |
| `templates/catechism/question_detail.html` | Filter cross-refs, themes, WLC link |
| `catechism/tests/` | New and updated tests |

---

2. ~~**Simplify top-bar navigation** — Remove the individual document shortcut links from the top bar (too many). Replace with a drop-down menu that shows the full name of each document.~~ ✓

3. **Document landing pages** — On the main page for each document, add a description of the document, its history, historical context, authorship, date, etc.

4. ~~**Expand document name abbreviations** — Use full document names where it makes sense, rather than only showing abbreviations.~~ ✓

5. ~~**Missing scripture proof texts** — Some scripture references do not have the full Bible text attached. Audit and fill in the gaps.~~ ✓

6. ~~**SHC section formatting** — The Second Helvetic Confession has sections that start with all-caps text. These should be preceded by a line break and treated as the start of new sections.~~ ✓

7. ~~**Align section/question counts on document pages** — On the main page for each document, the number of sections or questions does not appear at a consistent distance, causing a staggered/ragged layout. Fix alignment.~~ ✓

8. ~~**Remove top-level "go to" functionality** — Remove the top-level "go to" feature for jumping to a document and number.~~ ✓

9. ~~**Rename "Compare All Three" button** — On the home page, the "Compare All Three" button no longer makes sense now that there are more than three documents. Rename it to something like "Compare Documents".~~ ✓

10. ~~**Update scripture index** — Ensure the scripture index includes all scripture references from all documents.~~ ✓

11. ~~**Full document names on search results** — On the search results page, use the full name of the document rather than its abbreviation.~~ ✓

12. ~~**Remove section symbol (§)** — Remove the "section" symbol wherever it is used on the site.~~ ✓

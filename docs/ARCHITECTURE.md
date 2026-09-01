# Architecture

How the project is put together, and why. For operational procedures — backups,
restores, health checks, monitoring — see [`OPERATIONS.md`](OPERATIONS.md).

## The shape of it

A Django 4.2 project with three apps, mounted in this order (`config/urls.py`):

| Mount | App | What it holds |
|---|---|---|
| `/accounts/` | `accounts` | Sign-in, and everything private to a reader: notes, highlights, inline comments, the memorisation deck, reading positions |
| `/atlas/` | `westminster_standards` | The Westminster Standards Atlas — the Assembly itself, its divines, disputes and schools |
| `/` | `catechism` | The confessional texts and everything built on them |

`catechism` is mounted last because its final route is a catch-all
(`<slug:catechism_slug>/`). Anything added at the root must be registered
*before* that route or it will be shadowed by it.

## The data model

Everything in `catechism/models.py` hangs off one table.

**`Catechism`** is a loaded document — the Confession, a catechism, the Book of
Church Order, a systematic theology. Despite the name it is not necessarily a
catechism; `document_type` and `is_prose_document` decide whether it is
presented as questions or as chapters and sections, and `item_name`,
`item_prefix` and `topic_name` supply the vocabulary the templates use
("Question 3" vs "Chapter III, Section 2"). Its `tradition` decides who can
see it at all — see *Collections* below.

**`Topic`** is a chapter or a thematic grouping; **`Question`** is one
question, section or chapter of a document. Both carry `BelongsToDocument`,
which is what lets one set of templates render fourteen documents of three
different shapes.

Around those:

- **Commentary.** `CommentarySource` (Fisher, Watson, Ridgley, Hodge, …) with
  `Commentary` rows attached to a `Question`. `FisherSubQuestion` exists
  because Fisher & Erskine's exposition is itself in question-and-answer form.
- **Scripture.** `Question.proof_texts` is a semicolon-separated display string
  as printed ("1 Cor. 10:31; Rom. 11:36"). `ScriptureIndex` is the parsed,
  queryable form — the inverse index, "what cites this passage". `BibleBook`
  backs the browse pages. `ScripturePassage` holds fetched verse text and is
  normally **empty**; see *Scripture proofs* below.
- **Cross-references.** `StandardCrossReference` is the general
  document-to-document form. `CrossReference` is the older WSC↔WLC-only table,
  still loaded by `load_crossrefs`.
- **Comparison.** `ComparisonSet` → `ComparisonTheme` → `ComparisonEntry`,
  where an entry is "this theme, in this document, spans questions N to M".
  Ranges rather than single questions, because documents fold and split each
  other's chapters.
- **Ontology.** `OntologyLocus`, `OntologyAttribute`, `DoctrineHead`, and the
  join tables `QuestionOntologyTag` and `QuestionDoctrineHead`. This is the
  Atlas's taxonomy mirrored into the database — see *The Atlas seam*.
- **`DataVersion`** records a hash per loader; see *Loading*.

## Loading

There are 42 management commands, and the order they run in matters. The
canonical sequence is `scripts/load_data.sh`, which both `build.sh` (deploy)
and the CI data-integrity job run — a check against a differently-loaded
database is not a check, so there is one script and not two.

The broad order is: source texts, then commentaries on them, then the things
derived from both (cross-references, the Scripture index, comparison
cross-references). Some loaders assume their subject is already present —
`load_standard_crossrefs` needs the Westminster Standards loaded and says so
rather than raising `KeyError`.

Each loader hashes its source files through `_helpers.data_is_current` and
skips when nothing has changed, so a deploy that touches no data does no work.
**A loader whose logic changes without its data changing will not re-run.**
Where that matters the loader includes the relevant module in its hash — as
`load_westminster_ontology` does with `heads_of_doctrine.py`.

External fetches are deliberately *not* in the sequence, because they call
upstream services: `fetch_scripture` and `fetch_watson` are run by hand.

## Scripture proofs

Worth understanding before touching a question page. `ScripturePassage` — the
verse text — is populated only by `fetch_scripture`, which is manual. A fully
loaded database therefore has **no verse text at all**, against roughly 4,700
distinct proof references.

So the reference itself is the load-bearing thing. `scripture_refs.py` parses
it and `scripture_urls()` resolves it to the Scripture index page for its book,
in bulk (one `BibleBook` fetch per page). Around 99% of the corpus resolves;
the rest render as plain text. `check_site_integrity` holds that floor.

The rule on the page: a reference is either a working link or plain text, never
something that looks interactive and is not.

## Collections (`tradition`)

Every document carries a `tradition`, and a reader chooses which collections
are active from the navigation bar. `get_active_traditions(request)` reads that
choice, and essentially every view filters by it.

This is the single most common source of "why does this 404 in production but
not in my tests". A document, comparison theme or doctrine page is only
reachable if its whole collection is active for that visitor — and crawlers
arrive cookie-less, with the defaults. `_comparison_themes_for_traditions` is
set-aware for exactly this reason: a theme whose own entries all happen to be
active is still unreachable if its comparison *set* references a collection
that is not.

A document with `tradition='other'` is invisible to every view.
`check_site_integrity` fails if such a document has questions, because that
state means content is loaded and unreachable.

## Caching

`cache_read_only_page` (`catechism/cache.py`) caches expensive read-only pages
in the database cache. Two things to know: it caches **anonymous GETs only**,
because a signed-in reader's page carries their notes and highlights; and the
key is built explicitly from path plus active collections rather than by
varying on `Cookie`, since every visitor carries a csrftoken and varying on it
would cache nothing useful.

`clear_cache` runs at the end of `build.sh`. In local development with
`DEBUG=True` the template engine still holds rendered pages in this cache, so
a template edit may not show until the cache is cleared.

## Search

`_search_questions` runs the query. On PostgreSQL this uses a stored `tsvector`
column with a GIN index; on SQLite it falls back to substring matching, so the
production search path is **not exercised by a default local run**. The
`postgres` CI job exists to cover it, and five tests skip without it.

A query that parses as a Scripture reference ("Rom 8:30") redirects to the
Scripture index instead of running a text search; `?text=1` opts back in.

Results are grouped by document. Unfiltered, each group shows a sample and
offers the rest behind its own document filter; filtered to one document, the
list paginates. Before that, every match rendered on one page — 633KB of HTML
for a common word.

## The Atlas seam

`westminster_standards` was ported in from another project and can still be
synced with it, which shapes a few things:

- **The Atlas owns the doctrine-head taxonomy.** `heads_of_doctrine.py` is the
  source of truth. `load_westminster_ontology` mirrors it into `DoctrineHead`
  and derives every question-to-head link from its coverage lists. Add or
  rename a head *there and nowhere else*; `data/westminster_ontology.json`
  holds only loci, attributes and per-question attribute tags.
- **Ported files stay syncable.** `entity_search.py` and `bridge.py` exist to
  keep site-specific behaviour out of the ported `views.py`.
- **URL generation is centralised** in `catechism/atlas.py`, backed by
  `WESTMINSTER_ATLAS_BASE_URL`, so the Atlas can move without a template edit.

`westminster_standards` keeps its content in Python modules (`personas.py`,
`cruxes.py`, `schools.py`, `works.py`) rather than in the database. They are
large; that is the upstream project's design, not an accident here.

## Testing

`pytest` for `catechism` and `accounts`; `westminster_standards` keeps a
Django-style `tests.py`. Three CI jobs, because the unit suite alone cannot
see everything:

1. **`test`** — flake8, a migration check, the suite with coverage, and
   `collectstatic` under the *production* storage (the manifest resolves every
   `url()` in the vendored CSS, so a dangling font reference fails in CI
   rather than on deploy).
2. **`data-integrity`** — loads the real corpus with `scripts/load_data.sh`,
   then runs `check_site_integrity`. The unit suite runs against factories, so
   defects that only appear in the loaded data survive it: doctrine-head chips
   linking to Atlas pages that did not exist, and `sitemap.xml` advertising
   URLs that 404, both survived a green suite.
3. **`postgres`** — the whole suite against PostgreSQL 16, for the search path
   above.

`check_site_integrity` is the one to reach for when something is wrong with the
*loaded site* rather than with the code: it checks that documents are
reachable, that the ontology matches the Atlas, that proof references resolve,
and that the links pages actually render — and the URLs in the sitemap — all
return 200.

## Conventions worth knowing

- **No external assets.** Bootstrap, its icons and both typefaces are vendored
  under `static/vendor/` and served from this origin. A test enforces it. The
  site must render with `cdn.jsdelivr.net` and Google Fonts unreachable, and
  must not disclose a visitor's IP to either.
- **`{# ... #}` must open and close on one line.** Django renders a multi-line
  one verbatim into the page. It has happened twice;
  `test_template_comments.py` now reads every template to prevent a third.
  Use `{% comment %}` for anything longer.
- **Record user-visible changes in `CHANGELOG.md`**, and future work in
  `TODO.md` (`TODO_PCA_BCO.md` for BCO specifics).

# Westminster Standards Atlas

A Django app, mounted at **`/atlas/`** in Study Reformed (`config/urls.py`),
that catalogues the Westminster confessional landscape through a structured
ontology and exposes it as a browseable atlas of the Confession (1646), the
Larger and Shorter Catechisms (1647), and their two service-books (1645).

Where Study Reformed presents the *texts* — with proofs, commentary and
cross-references — the Atlas presents the *world around them*: the Assembly
that wrote them, the positions it debated and rejected, the parties inside it,
and the traditions that received and revised its work.

## Origin, and what that means for edits

This app was ported from the TimeSpaceMatterObserver project
(ontologicalatlas.com), where it was mounted at `/westminster_standards/`
alongside a sister app at `/puritans/`. Neither of those exists here. The data
layer is unchanged from upstream, so the app can still be synced with it, and
two conventions follow from that:

- **Site-specific behaviour is kept out of the ported `views.py`.**
  `bridge.py` redirects the Confession-chapter and catechism-question full-text
  pages to Study Reformed's own pages; `entity_search.py` exposes the
  persona/crux/school/head layers to the site-wide search. Both exist so
  `views.py` stays close to upstream.
- **The design tokens are bridged, not rewritten.** Templates extend Study
  Reformed's site `base.html`, and
  `static/westminster_standards/atlas-theme.css` maps this app's tokens onto
  the site theme.

This app is also the **single source of truth for the heads of doctrine**.
Study Reformed's `load_westminster_ontology` mirrors `heads_of_doctrine.py`
into its database and derives every question-to-head link from the coverage
lists here — so add or rename a head in that file and nowhere else.
`data/westminster_ontology.json` holds only loci, attributes and hand-authored
per-question attribute tags.

## The 8-locus Westminster ontology

| # | Locus | Attributes |
|---|---|---|
| I    | **Scripture** | sufficiency · canon · authority · interpretation · necessity |
| II   | **God & Decree** | Trinity · order of decrees · extent of atonement · reprobation · pactum salutis |
| III  | **Covenant** | number · Mosaic · children · testamental continuity |
| IV   | **Christology** | natures · offices · states & descent · active-obedience imputation |
| V    | **Soteriology** | effectual calling · justification · faith · perseverance · assurance |
| VI   | **Law & Sanctification** | three uses · tripartite division · Sabbath · good works |
| VII  | **Ecclesiology & Worship** | polity · sacramental efficacy · regulative principle · censures & synods |
| VIII | **Civil & Last Things** | magistrate · oaths & marriage · intermediate state · final judgment |

35 attributes in total. For each, every value is listed — the contested
alternatives the Assembly debated, the rejected Roman/Arminian/Socinian/
Antinomian positions, and post-Assembly developments. One value per attribute
is marked as the **WCF baseline**, the position the Standards themselves take;
the mapping lives in `data.WESTMINSTER_BASELINE_ATTRS` and is validated at
import time.

## What each layer holds

| File | Contents |
|---|---|
| `data.py` | The 8-locus ontology and `WESTMINSTER_BASELINE_ATTRS` (35 attributes) |
| `heads_of_doctrine.py` | 39 heads of doctrine, each tagged with the `attribute_keys` it bears on. Every WCF section and catechism question is covered. |
| `personas.py` | 181 Westminster divines, with bios drawn from the historical record where material exists |
| `cruxes.py` | 30 cruxes — background, parties, outcome, confessional language, legacy |
| `schools.py` | 16 Assembly parties and receiving traditions, each with a full 35-attribute profile |
| `works.py` | 6 works: the Standards themselves, by chapter or Q&A |
| `locus_mapping.py` | Chapter / question / section → locus assignments |
| `questions.py` | Attribute labels and dimension mapping. `QUESTIONS` itself is empty. |
| `controversies.py`, `cases.py` | Empty. Kept for the upstream shape. |

The layers are pure Python rather than database tables — that is the upstream
project's design. `cruxes.py` and `personas.py` are large files for that
reason.

## How the text is tagged

Every WCF section and every catechism question maps to one or more heads of
doctrine, and every head carries the ontology `attribute_keys` it bears on —
full keys of the form `locus_attr`, e.g. `god_decree_extent_of_atonement`.

A section's ontology tags are therefore *derived*: the union of the
`attribute_keys` of the heads covering it
(`attributes_for_wcf_section`, `attributes_for_catechism_question`). Pages
render these as locus-tinted chips linking to the Westminster baseline value
for each attribute.

Heads treating doctrines the ontology does not adjudicate as a *contested*
axis (creation, providence, adoption, the doctrine of God's essence) are mapped
to the nearest representative attribute within their locus, so every section
receives at least one tag. These nearest-fit associations are flagged
*representative* (`_REPRESENTATIVE_ATTRS` in `heads_of_doctrine.py`) and render
with a dashed border and a trailing **≈**, distinct from *core* tags marking a
genuinely contested axis. The same attribute can be core under one head and
representative under another — `order_of_decrees` is core for the eternal
decree (WCF III) but representative for providence (WCF V) — and a section's
tag shows as core whenever any covering head treats it so.

## Routes

All under `/atlas/`; see `urls.py` for the full list.

```
/atlas/                                   home
/atlas/ontology/                          the full eight-locus grid
/atlas/dimension/<dim>/                   locus detail
/atlas/dimension/<dim>/<attr>/<val>/      value detail
/atlas/personas/  /atlas/personas/<slug>/
/atlas/cruxes/    /atlas/cruxes/<slug>/
/atlas/schools/   /atlas/schools/<slug>/
/atlas/heads/     /atlas/heads/<slug>/
/atlas/works/     /atlas/works/<slug>/
/atlas/search/
```

`check_site_integrity` fetches every Atlas page and every doctrine-head chip,
so a route that stops resolving fails CI rather than the live site.

## Adding content

**A persona.** Append a dict to `PERSONAS` in `personas.py` with `slug`,
`name`, `dates`, `role`, `tagline`, `bio`, and `attrs` — inheriting from
`WESTMINSTER_BASELINE_ATTRS` and overriding only on points of departure.
Goodwin overrides `ecclesiology_worship_polity` to
`Independent-Congregational`; Calamy overrides
`god_decree_extent_of_atonement` to `Hypothetical-Universal`.

**A school.** An Assembly party or a receiving tradition, with a complete
35-attribute `attrs` profile (baseline plus overrides) and a `description`.

**A head of doctrine.** Here and nowhere else — see the note above. The heads
module is part of `load_westminster_ontology`'s hash, so editing it re-triggers
the loader on the next deploy.

## Licence and attribution

The ontology and structured data are original to this project.

The Westminster Standards texts are public domain (1646–1647), as are the 1788
American revisions. The standard modern critical edition is the *Westminster
Confession of Faith: Edinburgh Edition* (Free Presbyterian Publications), with
the Larger and Shorter Catechisms in the same edition.

# Westminster Standards Atlas

> **Integration note.** This app was ported from the
> TimeSpaceMatterObserver project (ontologicalatlas.com) into **Study
> Reformed**, where it is mounted at **`/atlas/`** (see `config/urls.py`).
> Its templates extend Study Reformed's site `base.html` and its design
> tokens are bridged to the site theme in
> `static/westminster_standards/atlas-theme.css`. The Confession-chapter
> and catechism-question full-text pages redirect to Study Reformed's own
> pages via `bridge.py`. Sections below that describe the tsmo mount,
> `/puritans/`, or `core/` describe the app's origin and may not apply
> here. The data layer is unchanged, so it can still be synced with the
> upstream app.
>
> This app is also the **single source of truth for the heads of doctrine**:
> Study Reformed's `load_westminster_ontology` mirrors
> `heads_of_doctrine.py` into its database and derives every
> question-to-head link from the coverage lists here, so add or rename a
> head in this file and nowhere else. `entity_search.py` exposes the
> persona/crux/school/head layers to the site-wide search without touching
> `views.py`.

A Django app — mounted at `/atlas/` in Study Reformed (originally at
`/westminster_standards/` in the TimeSpaceMatterObserver project) — that
catalogues the Westminster confessional landscape through a structured
ontology and exposes it as a browseable atlas of the Confession (1646),
the Larger and Shorter Catechisms (1647), and their two service-books
(1645).

Sister app to `/puritans/`. Where the Puritan atlas maps the wider
seventeenth-century Reformed-Puritan tradition (190 personas, 500 works,
18 schools), this atlas maps the *confessional consensus* the
Westminster Assembly produced, the contested positions inside that
consensus, and its reception and revision history.

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

35 attributes total — matching the shape of `puritans/data.py` so the
downstream machinery (value-detail page, dimension intersections,
entity placement) can be reused.

For each attribute, every value is listed (the contested alternatives
the Assembly debated, the rejected Roman/Arminian/Socinian/Antinomian
positions, and any post-Assembly developments). One value per
attribute is marked as the **WCF baseline** — the position the
Standards themselves take. The full mapping lives in
`westminster_standards.data.WESTMINSTER_BASELINE_ATTRS` and is
validated at import time.

## Differences from the Puritan ontology

The Puritan ontology maps a *tradition* (190 figures across two
centuries, multiple competing schools). The Westminster ontology
maps a *confessional consensus* (one document, one Assembly, one
hammered-out doctrinal position) plus its surrounding alternatives.
Three concrete differences:

1. The loci are organised by the internal shape of the Standards
   themselves — Scripture first (WCF I), then God and decree
   (II–V), covenant and Christ (VII–VIII), the *ordo salutis*
   (X–XVIII), law and sanctification (XIX–XXII), polity and worship
   (XXV–XXXI, plus XXI), civil and last things (XXIII–XXIV, XXXII–XXXIII).
2. The contested positions inside each attribute are read off the
   *Assembly debates* — supra/infra, particular vs hypothetical-
   universal atonement, jure divino presbyterianism vs Independency
   vs Erastianism, strict vs moderate regulative principle, papal
   Antichrist vs reserved, *custos utriusque tabulae* vs disestablishment.
3. The default `attrs` for a confessionally Westminster persona/work
   is the `WESTMINSTER_BASELINE_ATTRS` dict; departures from the
   Standards are marked as overrides on individual attributes.

## Layer files

| File | Status | Description |
|---|---|---|
| `data.py` | populated | The 8-locus ontology and the `WESTMINSTER_BASELINE_ATTRS` map. |
| `personas.py` | stubbed | Westminster divines (Twisse, Calamy, Rutherford, Gillespie, Goodwin, Nye, Selden, …). |
| `works.py` | stubbed | The Standards themselves (WCF, LC, SC, DPW, FPCG) with full text by chapter or Q&A. |
| `schools.py` | stubbed | The Assembly parties (English Presbyterians, Scots, Dissenting Brethren, Erastians, Hypothetical Universalists) and the receiving traditions (1689 Particular Baptists, Savoy 1658, 1788 American revision, the Marrow controversy, the 1843 Disruption, etc.). |
| `questions.py` | stubbed | The contested questions debated at the Assembly. |
| `controversies.py` | stubbed | The Grand Debate, the Calamy-Rutherford atonement debate, the Erastian controversy, the active-obedience vote, the 1788 revision, etc. |
| `cases.py` | stubbed | Key Assembly votes and post-Assembly reception cases. |
| `heads_of_doctrine.py` | populated | ~39 systematic-theology heads (every WCF section and every catechism question maps to at least one), each tagged with the ontology `attribute_keys` it bears on. |
| `locus_mapping.py` | populated | Chapter/question/section → locus assignments. |

## Tagging the text with the ontology

Every WCF section and every catechism question is mapped to one or more
*heads of doctrine* (`heads_of_doctrine.py`), and every head carries the
ontology **`attribute_keys`** it bears on — full keys of the form
`locus_attr`, e.g. `god_decree_extent_of_atonement`.

A work-section's ontology tags are therefore *derived*: they are the union
of the `attribute_keys` of the heads that cover that section
(`attributes_for_wcf_section`, `attributes_for_catechism_question`). The
WCF chapter, catechism-question, and directory-work section pages render
these as locus-tinted chips that link to the Westminster baseline value for
each attribute. Heads treating doctrines the ontology does not adjudicate
as a *contested* axis (creation, providence, adoption, the doctrine of
God's essence, …) are mapped to the nearest representative attribute within
their locus, so every section of every work receives at least one tag.

These nearest-fit associations are flagged *representative* (the
`_REPRESENTATIVE_ATTRS` set in `heads_of_doctrine.py`) and render with a
dashed border and a trailing **≈**, distinct from *core* tags that mark a
genuinely contested axis. The same attribute can be core under one head and
representative under another — e.g. `order_of_decrees` is core for the
eternal decree (WCF III) but representative for providence (WCF V) — and a
section's tag is shown as core whenever any covering head treats it so.

## URLs

The app is mounted at `/westminster_standards/` from `tsmo/urls.py`.

```
/westminster_standards/                                  home
/westminster_standards/ontology/                         the full eight-locus grid
/westminster_standards/dimension/<dim>/                  locus detail
/westminster_standards/dimension/<dim>/<attr>/<val>/     value detail
```

## Adding content

### Adding a persona

Append a dict to `PERSONAS` in `personas.py` with: `slug`, `name`,
`dates`, `role`, `tagline`, `bio`, `attrs` (inheriting from
`WESTMINSTER_BASELINE_ATTRS` and overriding only on points of
departure — e.g. Goodwin would override `ecclesiology_worship_polity`
to `Independent-Congregational`; Calamy would override
`god_decree_extent_of_atonement` to `Hypothetical-Universal`).

### Adding a work

For the Standards themselves, supply the full text broken into
chapters (WCF), questions (LC/SC), or sections (DPW/FPCG). For other
works (Owen's *Death of Death*, Rutherford's *Lex Rex*, Gillespie's
*Aaron's Rod Blossoming*, Calamy's atonement defences) follow the
same shape as `puritans/works.py`.

### Adding a school

A school is an Assembly party or a receiving tradition. Each school
has a complete 35-attribute `attrs` profile (inheriting from baseline
with overrides) and a `description`.

## Extracting to its own repo

To extract `westminster_standards/` as a standalone reusable Django
app: same recipe as `puritans/` — the app is fully self-contained
except for being mounted in `tsmo/urls.py`, the data is pure-Python
(no models), and templates extend `westminster_standards/base.html`.

## License & attribution

Ontology and structured data: original.

Westminster Standards text (to be added): public-domain (1646–1647);
the standard modern critical edition is the *Westminster Confession of
Faith: Edinburgh Edition* (Free Presbyterian Publications) and the
*Westminster Larger Catechism* and *Shorter Catechism* in the same
edition. The 1788 American revisions are also public-domain.

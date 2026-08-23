# Operations

Runbook for the deployed site. Everything here has been rehearsed except where
it says otherwise.

## Health check

`GET /health/` opens a database connection and runs `SELECT 1`, returning
`{"status": "ok"}` or a `503`. It is cheap enough to poll and it fails when the
database is gone, which is the failure that matters.

Point an external uptime monitor at `https://studyreformed.com/health/`:

- **Interval:** 1–5 minutes.
- **Alert on:** two consecutive failures, or any non-200.
- **Do not** point the monitor at `/`, which is served from the page cache and
  can return 200 while the database is unreachable.

> Provisioning the monitor is a manual step — it needs an account on whichever
> service you use (Render, UptimeRobot, Better Stack, Healthchecks.io). Nothing
> in this repository sets it up.

## Backups

**Check what the current database plan actually gives you.** `render.yaml`
provisions the database on Render's free plan. Historically that plan has had
neither automated backups nor point-in-time recovery, and free databases have
had a fixed lifetime after which they are removed. Confirm the present policy
in the Render dashboard; if there are no automated backups, the manual dump
below is the only backup, and it needs a schedule.

### Take a backup

```bash
# DATABASE_URL is the external connection string from the Render dashboard.
pg_dump -Fc -f "westminster-$(date +%Y-%m-%d).dump" "$DATABASE_URL"
```

Custom format (`-Fc`) rather than plain SQL: it restores selectively and
compresses. A full dump of the loaded corpus is a couple of hundred kilobytes,
so keeping many of them costs nothing.

Store dumps somewhere that is not Render.

## Restore, and rehearsing it

A backup nobody has restored is a hypothesis. Rehearse this on a scratch
database on a schedule — quarterly is enough for a site whose content changes
on deploy.

```bash
createdb westminster_restored
pg_restore -d westminster_restored westminster-2026-08-23.dump

DATABASE_URL=postgres://user:pass@host:5432/westminster_restored \
  ./scripts/verify_restore.sh
```

`scripts/verify_restore.sh` checks the three things a successful-looking
`pg_restore` can still get wrong:

1. **The schema matches the code** — `migrate --check` fails if the dump
   predates a migration.
2. **The data is all there** — row counts per model, printed so you can compare
   them against production.
3. **The pages render** — `check_site_integrity` walks the sitemap, the Atlas,
   and the ontology relationships against the restored data.

The last one is the point. A restore that reports success can still be missing
a loader's output: a rehearsal of this procedure caught exactly that — every
document and question present, every ontology row absent, so every doctrine
chip on the site would have been blank.

### Restoring into production

1. Put the service in maintenance (or accept the downtime; this is a reading
   site).
2. Restore into a **new** database, never over the live one.
3. Run `scripts/verify_restore.sh` against it.
4. Point `DATABASE_URL` at the restored database and redeploy.
5. Re-run the loaders (`./scripts/load_data.sh`) if the dump predates a content
   change. They are idempotent and skip unchanged sources.

## Rebuilding content without a restore

Every dataset is in the repository, so the content can be rebuilt from an empty
database:

```bash
python manage.py migrate
python manage.py createcachetable
./scripts/load_data.sh
python manage.py check_site_integrity
```

Only user-generated data — accounts, notes, highlights, annotations,
memorisation decks — is irreplaceable. That is what the backups are *for*;
everything else is reproducible.

## Monitoring

| What | Where | Notes |
|---|---|---|
| Errors | Sentry | Set `SENTRY_DSN`; unset disables it. `send_default_pii` is off, so notes and highlights never leave the server. |
| Uptime | External monitor | `/health/`, as above. |
| Data integrity | CI (`data-integrity` job) | Loads the real corpus and runs `check_site_integrity` on every pull request. |
| Search backend | CI (`postgres` job) | The production search path is Postgres-only; this job is the only thing that exercises it. |

Run `python manage.py check_site_integrity` from a shell on the deployed
instance after any manual data change.

## Verifying the text

`python manage.py check_transcription` compares the loaded Westminster text
against the Atlas app's independently sourced copy of the same documents.
Two transcriptions agreeing is evidence; where they disagree, the divergence is
either an error in one or a genuine edition difference, and both want an
editor's eye.

```bash
python manage.py check_transcription                 # all three documents
python manage.py check_transcription --document wcf --summary
```

`--summary` groups the findings by the differing words, which turns dozens of
sections into a handful of decisions. On the current corpus the Larger
Catechism agrees everywhere, the Shorter differs in one place, and the
Confession differs in 59 sections — overwhelmingly British against American
orthography (*honour/honor*, *pretence/pretense*, *endeavouring/endeavoring*)
and roman against arabic numerals in the canon list, with a small number of
real textual variants underneath.

**This is not a check against a critical edition.** It compares two
public-domain transcriptions the project already holds. Collating against a
modern critical print edition — the Free Presbyterian Publications text, or the
OPC's — remains editorial work that needs the book in hand; the command accepts
any reference with the same shape, so that collation can reuse it.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | yes | `config.settings.production` |
| `SECRET_KEY` | yes | Session and CSRF signing |
| `DATABASE_URL` | yes | Postgres connection string |
| `ALLOWED_HOSTS` | yes | Comma-separated |
| `SENTRY_DSN` | no | Error monitoring; unset disables it |
| `SENTRY_TRACES_SAMPLE_RATE` | no | Defaults to `0.05` |
| `PAGE_CACHE_SECONDS` | no | Anonymous page cache; defaults to `3600` in production |
| `GOOGLE_ANALYTICS_ID` | no | Analytics |

"""Development settings pointed at Postgres, for the CI Postgres job.

The production search uses a stored tsvector column and a GIN index that
SQLite has no equivalent for, so that code path is only ever exercised against
Postgres. This module exists so CI can run the whole suite there.
"""

import dj_database_url

from .development import *  # noqa: F401,F403

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://westminster:westminster@localhost:5432/westminster',
        conn_max_age=0,
    ),
}

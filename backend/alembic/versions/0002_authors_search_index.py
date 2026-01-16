"""authors search index

Revision ID: 80582064d30b
Revises: 0001
Create Date: 2026-01-15 17:28:25.079197

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.add_column(
        "authors", sa.Column("search_vector", sa.dialects.postgresql.TSVECTOR)
    )

    op.execute("""
    UPDATE authors
    SET search_vector =
        to_tsvector(
            'russian',
            last_name || ' ' || first_name || ' ' || coalesce(middle_name, '')
        )
    """)

    op.execute("""
    CREATE INDEX idx_authors_search
    ON authors USING GIN(search_vector)
    """)

    op.execute("""
    CREATE FUNCTION authors_search_vector_trigger() RETURNS trigger AS $$
    BEGIN
      NEW.search_vector :=
        to_tsvector(
          'russian',
          NEW.last_name || ' ' || NEW.first_name || ' ' || coalesce(NEW.middle_name, '')
        );
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql
    """)

    op.execute("""
    CREATE TRIGGER authors_search_vector_update
    BEFORE INSERT OR UPDATE
    ON authors
    FOR EACH ROW
    EXECUTE FUNCTION authors_search_vector_trigger()
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS authors_search_vector_update ON authors")
    op.execute("DROP FUNCTION IF EXISTS authors_search_vector_trigger")
    op.execute("DROP INDEX IF EXISTS idx_authors_search")
    op.drop_column("authors", "search_vector")

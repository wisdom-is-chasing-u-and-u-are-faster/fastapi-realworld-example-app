"""add user_article_bookmarks table

Revision ID: a1b2c3d4e5f6
Revises: fdf8821871d7
Create Date: 2025-01-01 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "fdf8821871d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_article_bookmarks",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "article_id",
            sa.Integer,
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_user_article_bookmarks",
        "user_article_bookmarks",
        ["user_id", "article_id"],
    )


def downgrade() -> None:
    op.drop_table("user_article_bookmarks")

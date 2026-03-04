"""002_roles_users_sessions

Revision ID: 002_roles_users_sessions
Revises: 001_extensions_and_base_enums
Create Date: 2026-03-04 17:55:00

"""

from collections.abc import Sequence

import bcrypt
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_roles_users_sessions"
down_revision: str | None = "001_extensions_and_base_enums"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ROLE_NAMES = ("BD", "Admin", "SuperAdmin", "SupplyChain")
SEED_USERNAME = "admin"
SEED_EMAIL = "admin@ems.local"
SEED_PASSWORD = "admin"


def _seed_password_hash() -> str:
    return bcrypt.hashpw(SEED_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id", name="pk_user_roles"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
    )

    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token_hash", name="uq_sessions_refresh_token_hash"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)

    roles_table = sa.table("roles", sa.column("name", sa.String()))
    op.bulk_insert(roles_table, [{"name": role_name} for role_name in ROLE_NAMES])

    password_hash = _seed_password_hash()
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO users (id, email, username, password_hash, is_active)
            VALUES (gen_random_uuid(), :email, :username, :password_hash, true)
            ON CONFLICT (username) DO NOTHING
            """
        ),
        {
            "email": SEED_EMAIL,
            "username": SEED_USERNAME,
            "password_hash": password_hash,
        },
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO user_roles (user_id, role_id)
            SELECT u.id, r.id
            FROM users u
            JOIN roles r ON r.name = 'SuperAdmin'
            WHERE u.username = :username
            ON CONFLICT (user_id, role_id) DO NOTHING
            """
        ),
        {"username": SEED_USERNAME},
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")

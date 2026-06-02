"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("email", sa.String(320)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("photo_url", sa.String(1024)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "user_health_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gender", sa.String(32)),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("height_cm", sa.Float()),
        sa.Column("weight_kg", sa.Float()),
        sa.Column("bmi", sa.Float()),
        sa.Column("activity_level", sa.String(64)),
        sa.Column("fitness_goal", sa.String(128)),
        sa.Column("daily_step_goal", sa.Integer()),
        sa.Column("water_goal_ml", sa.Integer()),
        sa.Column("sleep_goal_minutes", sa.Integer()),
        sa.Column("target_weight_kg", sa.Float()),
        sa.Column("baseline_hr", sa.Integer()),
        sa.Column("baseline_hrv", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_health_profiles_user_id", "user_health_profiles", ["user_id"], unique=True)

    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_type", sa.String(64), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("serial_number", sa.String(255), nullable=False),
        sa.Column("firmware_version", sa.String(64)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "serial_number", name="uq_user_device_serial"),
    )
    for column in ("user_id", "device_type", "model", "serial_number", "is_active"):
        op.create_index(f"ix_devices_{column}", "devices", [column])

    _sensor_table("heart_rate_readings", sa.Column("bpm", sa.Integer(), nullable=False), "uq_hr_device_time")
    _sensor_table("hrv_readings", sa.Column("rmssd_ms", sa.Float(), nullable=False), "uq_hrv_device_time")
    _sensor_table("spo2_readings", sa.Column("percentage", sa.Float(), nullable=False), "uq_spo2_device_time")
    _sensor_table("stress_readings", sa.Column("score", sa.Integer(), nullable=False), "uq_stress_device_time")
    _sensor_table("skin_temperature_readings", sa.Column("celsius", sa.Float(), nullable=False), "uq_temp_device_time")

    op.create_table(
        "activity_readings",
        *_sensor_columns(),
        sa.Column("steps", sa.Integer()),
        sa.Column("calories_kcal", sa.Float()),
        sa.Column("distance_meters", sa.Float()),
        sa.Column("active_minutes", sa.Integer()),
        sa.UniqueConstraint("device_id", "recorded_at", name="uq_activity_device_time"),
    )
    _indexes("activity_readings")

    op.create_table(
        "sleep_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer()),
        sa.Column("stages", postgresql.JSONB()),
        sa.Column("source_payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sleep_sessions_user_id", "sleep_sessions", ["user_id"])
    op.create_index("ix_sleep_sessions_device_id", "sleep_sessions", ["device_id"])
    op.create_index("ix_sleep_sessions_started_at", "sleep_sessions", ["started_at"])
    op.create_index("ix_sleep_sessions_ended_at", "sleep_sessions", ["ended_at"])

    op.create_table(
        "workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("workout_type", sa.String(128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("duration_minutes", sa.Integer()),
        sa.Column("calories_kcal", sa.Float()),
        sa.Column("avg_heart_rate", sa.Integer()),
        sa.Column("max_heart_rate", sa.Integer()),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("source_payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_workouts_user_id", "workouts", ["user_id"])
    op.create_index("ix_workouts_device_id", "workouts", ["device_id"])
    op.create_index("ix_workouts_workout_type", "workouts", ["workout_type"])
    op.create_index("ix_workouts_started_at", "workouts", ["started_at"])

    op.create_table(
        "user_goals_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal_type", sa.String(64), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="in_progress"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "goal_type", "period_start", name="uq_goal_period"),
    )
    op.create_index("ix_user_goals_progress_user_id", "user_goals_progress", ["user_id"])
    op.create_index("ix_user_goals_progress_goal_type", "user_goals_progress", ["goal_type"])
    op.create_index("ix_user_goals_progress_period_start", "user_goals_progress", ["period_start"])

    op.create_table(
        "ai_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("suggestion_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("model_provider", sa.String(64)),
        sa.Column("model_name", sa.String(128)),
        sa.Column("input_hash", sa.String(128), nullable=False),
        sa.Column("evidence", postgresql.JSONB()),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_suggestions_user_id", "ai_suggestions", ["user_id"])
    op.create_index("ix_ai_suggestions_suggestion_type", "ai_suggestions", ["suggestion_type"])
    op.create_index("ix_ai_suggestions_input_hash", "ai_suggestions", ["input_hash"])
    op.create_index("ix_ai_suggestions_expires_at", "ai_suggestions", ["expires_at"])

    for table in (
        "heart_rate_readings",
        "hrv_readings",
        "spo2_readings",
        "stress_readings",
        "skin_temperature_readings",
    ):
        op.execute(
            f"SELECT create_hypertable('{table}', 'recorded_at', if_not_exists => TRUE, migrate_data => TRUE)"
        )


def downgrade() -> None:
    for table in (
        "ai_suggestions",
        "user_goals_progress",
        "workouts",
        "sleep_sessions",
        "activity_readings",
        "skin_temperature_readings",
        "stress_readings",
        "spo2_readings",
        "hrv_readings",
        "heart_rate_readings",
        "devices",
        "user_health_profiles",
        "users",
    ):
        op.drop_table(table)


def _sensor_columns():
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    ]


def _sensor_table(name: str, value_column: sa.Column, unique_name: str) -> None:
    op.create_table(name, *_sensor_columns(), value_column, sa.UniqueConstraint("device_id", "recorded_at", name=unique_name))
    _indexes(name)


def _indexes(table: str) -> None:
    op.create_index(f"ix_{table}_user_id", table, ["user_id"])
    op.create_index(f"ix_{table}_device_id", table, ["device_id"])
    op.create_index(f"ix_{table}_recorded_at", table, ["recorded_at"])


import asyncio
import io
import json

import httpx
import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, select, func, MetaData, Table
from sqlalchemy.orm import Session

from app import manage
from app.config import settings
from app.db import Base, Lesson, Budget, Family, LearningRecord, seed
from app.providers import ProviderUnavailable


def test_isolated_v3_schema_matches_models_and_seed_is_idempotent(tmp_path):
    url = 'sqlite:///' + (tmp_path / 'v3-migration.db').as_posix()
    command.upgrade(manage.migration_config(url), 'head')
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            assert set(Base.metadata.tables) == {'families', 'lessons', 'learning_records', 'usage_logs', 'budget'}
            assert set(Base.metadata.tables) <= set(inspect(connection).get_table_names())
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        with Session(engine) as db:
            seed(db)
            db.get(Budget, 1).reserved_usd = 0.75
            db.commit()
            seed(db)
            assert db.scalar(select(func.count()).select_from(Lesson)) == 30
            assert db.get(Budget, 1).reserved_usd == 0.75
    finally:
        engine.dispose()


def test_postgres_v3_sql_compiles_without_connection():
    config = manage.migration_config('postgresql+psycopg://unused:unused@localhost/unused')
    output = io.StringIO()
    config.output_buffer = output
    command.upgrade(config, 'head', sql=True)
    sql = output.getvalue()
    assert 'CREATE TABLE families' in sql
    assert 'CREATE TABLE lessons' in sql
    assert 'CREATE TABLE learners' not in sql
    assert 'ADD COLUMN voice_enabled BOOLEAN DEFAULT false NOT NULL' in sql
    assert "ADD COLUMN narrations JSON DEFAULT '{}' NOT NULL" in sql
    assert 'COMMIT;' in sql


def test_voice_migration_preserves_existing_progress_and_defaults_off(tmp_path):
    url = 'sqlite:///' + (tmp_path / 'upgrade-v2-to-v3.db').as_posix()
    config = manage.migration_config(url)
    command.upgrade(config, '0001_family_initial')
    engine = create_engine(url)
    try:
        old = MetaData()
        families = Table('families', old, autoload_with=engine)
        records = Table('learning_records', old, autoload_with=engine)
        with engine.begin() as conn:
            conn.execute(families.insert().values(id='existing', token_hash='hash', csrf='csrf', created_at=1,
                         pin_hash='old-hash', nickname='River', age_band='6-8', ai_enabled=False,
                         session_minutes=15, started_at=0, break_until=0, parent_hash='', parent_expires=0))
            conn.execute(records.insert().values(id='existing:m68-01', family_id='existing', lesson_id='m68-01',
                         position=4, answers={'q4': [{'choice': 0, 'correct': True}]}, hints={},
                         completed=True, transfer_independent=True))
        command.upgrade(config, 'head')
        with Session(engine) as db:
            assert db.get(Family, 'existing').voice_enabled is False
            record = db.get(LearningRecord, 'existing:m68-01')
            assert record.narrations == {}
            assert record.completed and record.transfer_independent
            assert record.answers == {'q4': [{'choice': 0, 'correct': True}]}
    finally:
        engine.dispose()


def test_preflight_only_reads_catalog_without_secret_output(monkeypatch):
    monkeypatch.setattr(settings, 'nebius_api_key', 'private-v2-test-key')
    monkeypatch.setattr(settings, 'enable_paid_operations', False)
    requests = []

    def respond(request):
        requests.append((request.method, request.url.path))
        return httpx.Response(200, json={'data': [{'id': settings.nebius_model}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(manage.httpx, 'AsyncClient', lambda **kwargs: client)
    report = asyncio.run(manage.preflight())
    assert report['ok']
    assert requests == [('GET', '/v1/models')]
    assert report['inference_requests'] == 0
    assert 'private-v2-test-key' not in json.dumps(report)


def test_live_check_rejects_before_provider_access_without_budget(monkeypatch):
    monkeypatch.setattr(settings, 'enable_paid_operations', False)
    monkeypatch.setattr(settings, 'paid_budget_usd', 5)

    async def unexpected_preflight():
        raise AssertionError('Preflight should not run before live permission check')

    monkeypatch.setattr(manage, 'preflight', unexpected_preflight)
    with pytest.raises(ProviderUnavailable, match='explicitly authorized'):
        asyncio.run(manage.live_check())

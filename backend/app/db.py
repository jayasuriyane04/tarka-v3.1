import json
import time
from sqlalchemy import create_engine, String, Integer, Boolean, JSON, Float, Text, false
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings, ROOT


class Base(DeclarativeBase):
    pass


class Family(Base):
    __tablename__ = 'families'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    pin_hash: Mapped[str] = mapped_column(String(200), default='')
    nickname: Mapped[str] = mapped_column(String(20), default='Learner')
    age_band: Mapped[str] = mapped_column(String(10), default='6-8')
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    session_minutes: Mapped[int] = mapped_column(Integer, default=15)
    started_at: Mapped[float] = mapped_column(Float, default=0)
    break_until: Mapped[float] = mapped_column(Float, default=0)
    parent_hash: Mapped[str] = mapped_column(String(64), default='')
    parent_expires: Mapped[float] = mapped_column(Float, default=0)


class Lesson(Base):
    __tablename__ = 'lessons'
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)


class LearningRecord(Base):
    __tablename__ = 'learning_records'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    family_id: Mapped[str] = mapped_column(String(36), index=True)
    lesson_id: Mapped[str] = mapped_column(String(30))
    position: Mapped[int] = mapped_column(Integer, default=0)
    # Only choices, checked results and authored hint identifiers; no child free text.
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    hints: Mapped[dict] = mapped_column(JSON, default=dict)
    # Aggregate narration requests per question, including pre-answer assistance.
    # These record permission to speak, not proof the learner heard audio.
    narrations: Mapped[dict] = mapped_column(JSON, default=dict, server_default='{}')
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    transfer_independent: Mapped[bool] = mapped_column(Boolean, default=False)


class Usage(Base):
    __tablename__ = 'usage_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(String(36), index=True)
    provider: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(150), default='')
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    reserved_usd: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class Budget(Base):
    __tablename__ = 'budget'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reserved_usd: Mapped[float] = mapped_column(Float, default=0)


def make_engine(url):
    args = {'connect_args': {'check_same_thread': False, 'timeout': 20}} if url.startswith('sqlite') else {}
    return create_engine(url, **args)


engine = make_engine(settings.database_url)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def seed(db):
    for lesson in json.loads((ROOT / 'backend/content/lessons.json').read_text(encoding='utf-8')):
        previous = db.get(Lesson, lesson['id'])
        if previous:
            previous.data = lesson
        else:
            db.add(Lesson(id=lesson['id'], data=lesson))
    if db.get(Budget, 1) is None:
        db.add(Budget(id=1, reserved_usd=0))
    db.commit()

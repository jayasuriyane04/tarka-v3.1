from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ProfileIn(Strict):
    nickname: str = Field(default='Learner', min_length=1, max_length=20, pattern=r'^[\w \-]+$')
    age_band: Literal['6-8', '9-11', '12-15']
    ai_enabled: bool = False
    voice_enabled: bool = False
    session_minutes: Literal[10, 15, 20] = 15


class SetupIn(ProfileIn):
    pin: str = Field(pattern=r'^\d{6}$')
    adult_confirmed: Literal[True]


class UnlockIn(Strict):
    pin: str = Field(pattern=r'^\d{6}$')


class LessonIn(Strict):
    lesson_id: str = Field(min_length=1, max_length=30)


class AnswerIn(LessonIn):
    choice: int = Field(ge=0, le=3)


class NarrationIn(LessonIn):
    segment: Literal['lesson', 'question', 'hint', 'feedback']
    hint_level: int | None = Field(default=None, ge=1, le=3)


class NarrationOut(Strict):
    text: str = Field(min_length=1, max_length=12000)
    label: str
    source: Literal['lesson', 'nebius']
    question_id: str


class DeleteIn(Strict):
    confirm: Literal[True]
    current_password: str | None = Field(default=None, min_length=1, max_length=128, repr=False)


class RegisterIn(Strict):
    username: str = Field(min_length=3, max_length=32, pattern=r'^[A-Za-z0-9_]+$')
    password: str = Field(min_length=15, max_length=128, repr=False)
    adult_confirmed: Literal[True]
    existing_pin: str | None = Field(default=None, pattern=r'^\d{6}$', repr=False)


class LoginIn(Strict):
    username: str = Field(min_length=3, max_length=32, pattern=r'^[A-Za-z0-9_]+$')
    password: str = Field(min_length=1, max_length=128, repr=False)


class PasswordIn(Strict):
    current_password: str = Field(min_length=1, max_length=128, repr=False)
    new_password: str = Field(min_length=15, max_length=128, repr=False)


class HintSelection(Strict):
    hint_id: Literal['step_hint', 'look_again', 'worked_example']

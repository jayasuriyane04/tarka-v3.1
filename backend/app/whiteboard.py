"""Bounded, authored maths boards. Authorization happens before any content leaves.

The tutor can select an already-delivered hint; neither providers nor learners may
submit executable markup, coordinates, equations, or arbitrary board instructions.
"""
import json
import time
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from pydantic import Field, model_validator

from .config import ROOT
from .schemas import Strict, LessonIn


class Counters(Strict):
    kind: Literal['counters']
    groups: list[Annotated[int, Field(ge=0, le=20)]] = Field(min_length=1, max_length=8)
    caption: str = Field(min_length=1, max_length=300)


class FractionVisual(Strict):
    kind: Literal['fraction']
    numerator: int = Field(ge=0, le=20)
    denominator: int = Field(ge=1, le=20)
    caption: str = Field(min_length=1, max_length=300)

    @model_validator(mode='after')
    def proper_fraction(self):
        if self.numerator > self.denominator:
            raise ValueError('The fraction diagram must fit one whole.')
        return self


class NumberLine(Strict):
    kind: Literal['number_line']
    start: float = Field(ge=-100, le=1000)
    end: float = Field(ge=-100, le=1000)
    marks: list[float] = Field(min_length=2, max_length=12)
    caption: str = Field(min_length=1, max_length=300)

    @model_validator(mode='after')
    def bounded_marks(self):
        if self.start >= self.end or any(not self.start <= point <= self.end for point in self.marks):
            raise ValueError('Number-line marks must be inside its ordered bounds.')
        return self


class Rectangle(Strict):
    kind: Literal['rectangle']
    length: int = Field(ge=1, le=20)
    width: int = Field(ge=1, le=20)
    caption: str = Field(min_length=1, max_length=300)


Visual = Annotated[Counters | FractionVisual | NumberLine | Rectangle, Field(discriminator='kind')]


class BoardStep(Strict):
    title: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=1800)
    equation: str | None = Field(default=None, max_length=200)
    visual: Visual | None = None


class AuthoredBoard(Strict):
    example_prompt: str = Field(min_length=1, max_length=500)
    steps: list[BoardStep] = Field(min_length=2, max_length=6)
    arithmetic_checks: list[str] = Field(min_length=1, max_length=10)


class WhiteboardIn(LessonIn):
    segment: Literal['lesson', 'hint', 'feedback']
    hint_level: int | None = Field(default=None, ge=1, le=3)

    @model_validator(mode='after')
    def hint_only(self):
        if (self.segment == 'hint') != (self.hint_level is not None):
            raise ValueError('Supply a hint level only for a delivered hint.')
        return self


class WhiteboardOut(Strict):
    title: str = Field(min_length=1, max_length=150)
    source: Literal['lesson', 'nebius']
    question_id: str = Field(min_length=1, max_length=60)
    steps: list[BoardStep] = Field(min_length=1, max_length=6)


@lru_cache(maxsize=1)
def authored_boards():
    payload = json.loads((ROOT / 'backend/content/whiteboards.json').read_text(encoding='utf-8'))
    return {key: AuthoredBoard.model_validate(value) for key, value in payload.items()}


def register_whiteboard(app, *, context, ready_to_learn, lesson_data, record_for, feedback_for):
    @app.post('/api/whiteboard', response_model=WhiteboardOut)
    def whiteboard(body: WhiteboardIn, ctx=Depends(context)):
        db, family = ctx
        ready_to_learn(db, family)
        lesson = lesson_data(db, family, body.lesson_id)
        if lesson['subject'] != 'maths':
            raise HTTPException(404, 'Whiteboards are available in maths lessons.')
        record = record_for(db, family, body.lesson_id)
        if record.completed and body.segment != 'feedback':
            raise HTTPException(409, 'This lesson is finished. You can revisit its checked feedback.')
        question = lesson['questions'][-1] if record.completed else lesson['questions'][record.position]
        attempts = record.answers.get(question['id'], [])
        answered = bool(attempts and attempts[-1]['correct'])
        source = 'lesson'
        if body.segment == 'lesson':
            if question['kind'] == 'transfer':
                raise HTTPException(409, 'Earlier worked examples are closed during this new challenge.')
            board = authored_boards().get(lesson['id'])
            if not board or board.example_prompt != lesson['worked_example']['prompt']:
                raise HTTPException(503, 'This teaching board is being checked. The written lesson is available.')
            title, steps = 'Worked example: ' + lesson['title'], board.steps
        elif body.segment == 'hint':
            hint = next((item for item in record.hints.get(question['id'], []) if item['level'] == body.hint_level), None)
            if hint is None:
                raise HTTPException(409, 'Ask for that hint first, then open it on the board.')
            source = hint['source']
            title = f'Hint {hint["level"]} for this question'
            steps = [BoardStep(title='Notice this', text=hint['message']),
                     BoardStep(title='Your thinking turn', text='Use your own marks below. Then return to the question and try your next step.')]
        else:
            checked = feedback_for(question, attempts)
            if checked is None:
                raise HTTPException(409, 'Check an answer before opening its feedback board.')
            title = 'Checked answer feedback'
            steps = [BoardStep(title='What the answer check found', text=checked['message'])]
            if checked['correct']:
                steps.append(BoardStep(title='Why it works', text=checked['explanation']))
            else:
                steps.append(BoardStep(title='Try another approach', text='Read the question once more. You can ask for a hint, or use your drawing space to show what you know.'))
        result = WhiteboardOut(title=title, source=source, question_id=question['id'], steps=steps)
        previous = record.narrations.get(question['id'], {})
        segments = dict(previous.get('segments', {}))
        key = 'whiteboard:' + body.segment
        segments[key] = segments.get(key, 0) + 1
        # A shared assistance flag protects transfer scoring. Separate counters
        # preserve the meaning of V3's existing read-aloud statistics.
        assistance = not answered and body.segment in {'lesson', 'hint', 'feedback'}
        record.narrations = {**record.narrations, question['id']: {
            **previous, 'requests': previous.get('requests', 0),
            'whiteboard_requests': previous.get('whiteboard_requests', 0) + 1,
            'whiteboard_assistance': bool(previous.get('whiteboard_assistance') or assistance),
            'assistance': bool(previous.get('assistance') or assistance),
            'segments': segments, 'last_requested_at': time.time(),
        }}
        db.commit()
        return result

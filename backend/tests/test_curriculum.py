"""Deterministic educational-content checks; no model or provider calls."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('tarka_v3_curriculum_validation', ROOT / 'evaluation/validate_curriculum.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


@pytest.fixture
def lessons():
    return json.loads((ROOT / 'backend/content/lessons.json').read_text(encoding='utf-8'))


def test_all_lessons_have_valid_answers_evidence_and_balanced_positions(lessons):
    result = validation.validate(lessons)
    assert result['lessons'] == 30
    assert result['questions'] == 120
    assert result['practice_questions'] == 90
    assert result['transfer_questions'] == 30
    assert result['exact_arithmetic_answer_checks'] == 60
    assert result['reading_evidence_source_checks'] == 60
    assert result['self_contained_reading_transfers'] == 15
    assert result['correct_answer_position_counts'] == {0:30, 1:30, 2:30, 3:30}
    assert result['human_review_completed'] is False
    assert result['network_calls'] == 0


def test_original_v2_lessons_are_preserved_exactly(lessons):
    original_path = ROOT.parent / 'tarka-v2/backend/content/lessons.json'
    if not original_path.exists():
        pytest.skip('Sibling V2 checkout is not included in a standalone V3 deployment.')
    original = json.loads(original_path.read_text(encoding='utf-8'))
    assert len(original) == 18
    assert lessons[:18] == original
    assert len(lessons[18:]) == 12
    assert {lesson['skill'] for lesson in lessons[:18]}.isdisjoint(
        {lesson['skill'] for lesson in lessons[18:]}
    )


def test_every_new_lesson_has_a_distinct_skill(lessons):
    new_lessons = lessons[18:]
    assert len({lesson['skill'] for lesson in new_lessons}) == 12


def test_mean_rejects_an_empty_dataset():
    with pytest.raises(ValueError, match='at least one value'):
        validation.arithmetic_answer({'operation': 'mean', 'values': []})


def test_incorrect_math_answer_key_is_detected(lessons):
    question = lessons[0]['questions'][0]
    question['answer_index'] = (question['answer_index'] + 1) % 4
    with pytest.raises(ValueError, match='keyed arithmetic answer is wrong'):
        validation.validate(lessons)


def test_equivalent_numeric_distractor_is_detected(lessons):
    question = lessons[0]['questions'][0]
    distractor_index = (question['answer_index'] + 1) % 4
    question['options'][distractor_index] = question['options'][question['answer_index']] + '.0'
    with pytest.raises(ValueError, match='multiple numerically correct options'):
        validation.validate(lessons)


def test_missing_evidence_quote_is_detected(lessons):
    reading = next(lesson for lesson in lessons if lesson['subject'] == 'reading')
    reading['questions'][0]['evidence'] = 'A detail that is not in this passage.'
    with pytest.raises(ValueError, match='evidence is absent'):
        validation.validate(lessons)


def test_transfer_never_depends_on_an_unexposed_passage_field(lessons):
    reading = next(lesson for lesson in lessons if lesson['subject'] == 'reading')
    transfer = reading['questions'][-1]
    transfer['passage'] = transfer['prompt']
    transfer['prompt'] = 'Which action shows that Oli kept trying?'
    with pytest.raises(ValueError, match='evidence is absent'):
        validation.validate(lessons)


def test_repeated_choice_text_is_detected(lessons):
    question = lessons[0]['questions'][0]
    question['options'][1] = question['options'][0]
    with pytest.raises(ValueError, match='duplicate choice text'):
        validation.validate(lessons)


def test_missing_transfer_question_is_detected(lessons):
    lessons[0]['questions'][-1]['kind'] = 'practice'
    with pytest.raises(ValueError, match='three practice questions'):
        validation.validate(lessons)


@pytest.mark.parametrize(('metadata','expected'), [
    ({'operation':'add','operands':[9,4]}, '13'),
    ({'operation':'add','operands':['0.4','0.35']}, '3/4'),
    ({'operation':'subtract','left':15,'right':6}, '9'),
    ({'operation':'mean','values':[0,4,8]}, '4'),
    ({'operation':'mean','values':[2,3,6,7]}, '9/2'),
    ({'operation':'multiply','operands':[4,3]}, '12'),
    ({'operation':'fraction','operator':'equivalent','left':'6/15'}, '2/5'),
    ({'operation':'fraction','operator':'add','left':'1/3','right':'1/6'}, '1/2'),
    ({'operation':'fraction','operator':'subtract','left':'3/4','right':'1/8'}, '5/8'),
    ({'operation':'fraction','operator':'multiply','left':'2/3','right':'3/5'}, '2/5'),
    ({'operation':'equation','coefficient':'1/4','offset':'2','rhs':'5'}, '12'),
    ({'operation':'ratio','known_base':4,'unknown_base':28,'known_value':7}, '49'),
])
def test_exact_oracles_cover_fractional_and_proportional_calculations(metadata, expected):
    assert validation.arithmetic_answer(metadata) == validation.Fraction(expected)

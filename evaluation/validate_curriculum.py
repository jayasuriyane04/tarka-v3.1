"""Offline content validation for Tarka v3. No network, models or user-code execution."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / 'backend/content/lessons.json'


def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def arithmetic_answer(check: dict) -> Fraction:
    """Derive the exact numeric answer from simple authored metadata, not answer_index."""
    operation = check['operation']
    if operation == 'add':
        return sum((Fraction(str(x)) for x in check['operands']), Fraction(0))
    if operation == 'subtract':
        return Fraction(str(check['left'])) - Fraction(str(check['right']))
    if operation == 'mean':
        values = check['values']
        require(isinstance(values, list) and len(values) > 0, 'A mean needs at least one value.')
        return sum((Fraction(str(value)) for value in values), Fraction(0)) / len(values)
    if operation == 'multiply':
        result = Fraction(1)
        for value in check['operands']:
            result *= Fraction(str(value))
        return result
    if operation == 'fraction':
        left = Fraction(check['left'])
        if check['operator'] == 'equivalent':
            return left
        right = Fraction(check['right'])
        if check['operator'] == 'add':
            return left + right
        if check['operator'] == 'subtract':
            return left - right
        if check['operator'] == 'multiply':
            return left * right
    if operation == 'equation':
        coefficient = Fraction(check['coefficient'])
        require(coefficient != 0, 'Equation coefficient cannot be zero.')
        return (Fraction(check['rhs']) - Fraction(check['offset'])) / coefficient
    if operation == 'ratio':
        known_base = Fraction(str(check['known_base']))
        require(known_base > 0, 'Known ratio base must be positive.')
        return Fraction(str(check['unknown_base'])) * Fraction(str(check['known_value'])) / known_base
    raise ValueError(f'Unsupported arithmetic operation: {check}')


def validate(lessons: list[dict] | None = None) -> dict:
    lessons = lessons if lessons is not None else json.loads(CONTENT_PATH.read_text(encoding='utf-8'))
    require(isinstance(lessons, list) and len(lessons) == 30, 'Exactly thirty lessons are required.')
    lesson_fields = {'id','title','subject','age_band','skill','summary','explanation','worked_example','visual','questions','encouragement'}
    question_fields = {'id','kind','prompt','options','answer_index','explanation','hints'}
    distribution = Counter()
    answer_positions = Counter()
    seen_lessons, seen_questions, seen_passages = set(), set(), set()
    maths_checked = reading_checked = transfer_checked = 0
    for lesson in lessons:
        lesson_id = lesson.get('id', '<missing>')
        require(lesson_fields <= lesson.keys(), f'{lesson_id}: missing lesson fields.')
        require(lesson_id not in seen_lessons, f'{lesson_id}: duplicate lesson ID.')
        seen_lessons.add(lesson_id)
        require(lesson['subject'] in {'maths','reading'}, f'{lesson_id}: unsupported subject.')
        require(lesson['age_band'] in {'6-8','9-11','12-15'}, f'{lesson_id}: unsupported age band.')
        distribution[(lesson['age_band'], lesson['subject'])] += 1
        for field in ('title','skill','summary','explanation','encouragement'):
            require(isinstance(lesson[field], str) and lesson[field].strip(), f'{lesson_id}: empty {field}.')
        example = lesson['worked_example']
        require(isinstance(example, dict) and set(example) == {'prompt','explanation'}, f'{lesson_id}: invalid worked example.')
        require(all(isinstance(x, str) and x.strip() for x in example.values()), f'{lesson_id}: blank example text.')
        visual = lesson['visual']
        require(visual['kind'] in {'counters','fraction','number_line','reading'}, f'{lesson_id}: unsupported visual kind.')
        require(isinstance(visual.get('caption'), str) and visual['caption'], f'{lesson_id}: missing visual caption.')
        if visual['kind'] == 'counters':
            require(1 <= len(visual['groups']) <= 6 and all(type(x) is int and 0 < x <= 20 for x in visual['groups']), f'{lesson_id}: invalid counter groups.')
        elif visual['kind'] == 'fraction':
            require(type(visual['numerator']) is int and type(visual['denominator']) is int and 0 <= visual['numerator'] <= visual['denominator'] <= 16 and visual['denominator'] > 0, f'{lesson_id}: invalid fraction visual.')
        elif visual['kind'] == 'number_line':
            require(visual['start'] < visual['end'] and visual['step'] > 0 and (visual['end'] - visual['start']) % visual['step'] == 0, f'{lesson_id}: invalid number line.')
        else:
            require(isinstance(visual.get('focus'), str) and visual['focus'], f'{lesson_id}: missing reading visual focus.')
        questions = lesson['questions']
        require(len(questions) == 4, f'{lesson_id}: each lesson needs four questions.')
        require([q['kind'] for q in questions] == ['practice','practice','practice','transfer'], f'{lesson_id}: use three practice questions followed by one transfer.')
        if lesson['subject'] == 'reading':
            passage = lesson.get('passage')
            require(isinstance(passage, str) and passage.strip(), f'{lesson_id}: reading lesson needs a passage.')
            require(passage not in seen_passages, f'{lesson_id}: repeated practice passage.')
            seen_passages.add(passage)
            if lesson['age_band'] == '6-8':
                require(len(passage.split()) <= 90, f'{lesson_id}: youngest passage exceeds the short-passage limit.')
        for question in questions:
            question_id = question.get('id', '<missing>')
            require(question_fields <= question.keys(), f'{question_id}: missing question fields.')
            require(question_id not in seen_questions, f'{question_id}: duplicate question ID.')
            seen_questions.add(question_id)
            require(question_id.startswith(lesson_id + '-'), f'{question_id}: ID does not match lesson.')
            for field in ('prompt','explanation'):
                require(isinstance(question[field], str) and question[field].strip(), f'{question_id}: missing {field}.')
            options = question['options']
            require(isinstance(options, list) and len(options) == 4 and all(isinstance(x, str) and x.strip() for x in options), f'{question_id}: need four nonempty options.')
            require(len({x.strip().casefold() for x in options}) == 4, f'{question_id}: duplicate choice text.')
            require(type(question['answer_index']) is int and 0 <= question['answer_index'] <= 3, f'{question_id}: invalid answer index.')
            answer_positions[question['answer_index']] += 1
            hints = question['hints']
            require(isinstance(hints, list) and len(hints) == 3 and all(isinstance(x, str) and x.strip() for x in hints), f'{question_id}: exactly three nonempty hints required.')
            require(len(set(hints)) == 3, f'{question_id}: repeated hint.')
            if lesson['age_band'] == '6-8':
                require(len(question['prompt'].split()) <= 45, f'{question_id}: youngest prompt too long.')
                require(all(len(option.split()) <= 14 for option in options), f'{question_id}: youngest choice too long.')
                require(all(len(hint.split()) <= 30 for hint in hints), f'{question_id}: youngest hint too long.')
            if lesson['subject'] == 'maths':
                require('check' in question, f'{question_id}: maths check metadata is required.')
                expected = arithmetic_answer(question['check'])
                values = [Fraction(option) for option in options]
                require(values[question['answer_index']] == expected, f'{question_id}: keyed arithmetic answer is wrong.')
                require(sum(value == expected for value in values) == 1, f'{question_id}: multiple numerically correct options.')
                maths_checked += 1
            else:
                evidence = question.get('evidence')
                require(isinstance(evidence, str) and evidence.strip(), f'{question_id}: reading evidence is required.')
                source = question['prompt'] if question['kind'] == 'transfer' else lesson['passage']
                require(evidence in source, f'{question_id}: evidence is absent from its own source text.')
                if question['kind'] == 'transfer':
                    require(question['prompt'].startswith('Read: '), f'{question_id}: transfer text must be self-contained in the public prompt.')
                    require(lesson['passage'] not in question['prompt'], f'{question_id}: transfer must use a different short text.')
                    transfer_checked += 1
                reading_checked += 1
    require(all(distribution[(band, subject)] == 5 for band in ('6-8','9-11','12-15') for subject in ('maths','reading')), 'Need five lessons per subject per band.')
    require(len(answer_positions) == 4 and max(answer_positions.values()) - min(answer_positions.values()) <= 2, 'Correct choice positions should be balanced.')
    return {
        'status':'passed', 'lessons':len(lessons), 'questions':len(seen_questions),
        'practice_questions':sum(q['kind'] == 'practice' for lesson in lessons for q in lesson['questions']),
        'transfer_questions':sum(q['kind'] == 'transfer' for lesson in lessons for q in lesson['questions']),
        'exact_arithmetic_answer_checks':maths_checked, 'reading_evidence_source_checks':reading_checked,
        'self_contained_reading_transfers':transfer_checked,
        'correct_answer_position_counts':dict(sorted(answer_positions.items())),
        'distribution':{f'{band}/{subject}':count for (band,subject), count in sorted(distribution.items())},
        'dataset_sha256':hashlib.sha256(json.dumps(lessons, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        'network_calls':0, 'human_review_completed':False, 'model_evaluation':'not_run',
        'limitations':[
            'Arithmetic is checked from authored metadata; this does not independently parse or prove every natural-language explanation.',
            'Reading evidence checks verify quoted source text, not semantic correctness, reading-level calibration or clinical/educational assessment validity.',
            'No independent teacher review, child study, learning-gain claim or paid model inference has been performed.',
            'Age bands are navigation choices for foundation practice, not a diagnosis or a certified curriculum alignment.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/reports/curriculum-validation.json')
    args = parser.parse_args()
    report = {'created_at':datetime.now(timezone.utc).isoformat(), **validate()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

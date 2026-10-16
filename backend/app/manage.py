"""V3 maintenance: isolated migrations, safe catalog reads and gated synthetic AI checks."""
import argparse
import asyncio
import json
import math
import sys

import httpx
from alembic import command
from alembic.config import Config

from .config import ROOT, settings
from .db import Family, SessionLocal, seed
from .providers import ProviderUnavailable, bounded_json, cards_for, safe_base, select_hint


def migration_config(database_url=None):
    config = Config(str(ROOT / 'backend' / 'alembic.ini'))
    config.attributes['database_url'] = database_url or settings.database_url
    return config


async def preflight():
    """Read only the account model catalog; never request generation."""
    checks = []
    try:
        settings.validate_deployment()
        checks.append({'name': 'application_configuration', 'ok': True})
    except ValueError:
        checks.append({'name': 'application_configuration', 'ok': False,
                       'action': 'Check secret/cookies/database, prices, authorized budget and session/output settings.'})
    try:
        if not settings.nebius_api_key:
            raise ProviderUnavailable('Set NEBIUS_API_KEY locally in the v3 root .env file. Authored lessons remain available without AI.')
        base = safe_base()
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            result = await bounded_json(client, 'GET', base + '/models',
                                        headers={'Authorization': f'Bearer {settings.nebius_api_key}'})
        available = {item.get('id') for item in result.get('data', [])}
        if settings.nebius_model not in available:
            raise ProviderUnavailable('The selected model is not available to this account. Choose an account-visible NVIDIA model and matching prices.')
        checks.append({'name': 'nebius_model_access', 'ok': True, 'model': settings.nebius_model})
    except ProviderUnavailable as error:
        checks.append({'name': 'nebius_model_access', 'ok': False, 'action': str(error)})
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        checks.append({'name': 'nebius_model_access', 'ok': False,
                       'action': 'Could not read the model catalog. Check endpoint, key, account access, network and provider status.'})
    return {'ok': all(item['ok'] for item in checks), 'mode': 'read_only',
            'inference_requests': 0, 'checks': checks,
            'note': 'Catalog reads may consume API quota. No child data or generation request was sent. Account access is not proof of live hint quality.'}


async def live_check():
    """One synthetic adult-operated selector check through the normal budget gate."""
    if not settings.enable_paid_operations or not math.isfinite(settings.paid_budget_usd) or settings.paid_budget_usd <= 0:
        raise ProviderUnavailable('Live checks require paid operations enabled and a positive spending ceiling explicitly authorized by the operator.')
    report = await preflight()
    if not report['ok']:
        return {'ok': False, 'mode': 'synthetic_live_smoke', 'preflight': report,
                'action': 'Resolve the preflight failures before making a paid inference request.'}
    lessons = json.loads((ROOT / 'backend' / 'content' / 'lessons.json').read_text(encoding='utf-8'))
    lesson, level = lessons[0], 1
    question = lesson['questions'][0]
    # This in-memory profile is not a child record and never enters the provider payload.
    synthetic = Family(id='operator-v3-live-check', ai_enabled=True, age_band=lesson['age_band'])
    with SessionLocal() as db:
        selected = await select_hint(db, synthetic, lesson, question, level, [])
    allowed = cards_for(lesson, question, level)
    return {'ok': selected in allowed, 'mode': 'synthetic_live_smoke',
            'model': settings.nebius_model, 'selected_hint_id': selected,
            'authored_text_only': selected in allowed,
            'note': 'A synthetic opt-in profile was used and the shared budget ledger reserved the request. No child participated. This does not verify browser controls, educational quality, provider retention or the full lesson library.'}


def main():
    parser = argparse.ArgumentParser(description='Tarka v3 database and AI checks')
    parser.add_argument('command', choices=['upgrade', 'seed', 'preflight', 'live-check', 'schema-sql'])
    args = parser.parse_args()
    try:
        if args.command == 'upgrade':
            settings.validate_deployment()
            command.upgrade(migration_config(), 'head')
            print('V3 database migrations applied.')
        elif args.command == 'seed':
            settings.validate_deployment()
            with SessionLocal() as db:
                seed(db)
            print('V3 original lessons seeded idempotently.')
        elif args.command == 'schema-sql':
            command.upgrade(migration_config('postgresql+psycopg://offline:offline@localhost/offline'), 'head', sql=True)
        else:
            report = asyncio.run(preflight() if args.command == 'preflight' else live_check())
            print(json.dumps(report, indent=2))
            return 0 if report['ok'] else 1
        return 0
    except ProviderUnavailable as error:
        print(json.dumps({'ok': False, 'action': str(error)}))
        return 1
    except Exception as error:
        # Connection/HTTP exception messages can reveal secret-bearing URLs.
        print(json.dumps({'ok': False, 'error_type': type(error).__name__,
                          'action': 'Check v3 configuration and database connectivity. Apply migrations and seed before live checks; keep secrets out of shared logs.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())

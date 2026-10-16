# Dependency and license inventory

Original Tarka v3 code and authored lessons use Apache License 2.0. Third-party packages retain their own licenses. V3 does not bundle model weights, Monaco Editor or a code-execution server.

The frontend lockfile and `backend/requirements.lock.txt` record resolved packages for repeat installation. This direct-dependency inventory is not a complete transitive software bill of materials or a legal compliance assessment.

| Component | Role | Upstream license |
|---|---|---|
| React / React DOM | Browser interface | MIT |
| TypeScript | Type checking | Apache-2.0 |
| Vite / React plugin | Development and production build | MIT |
| Vitest | Frontend tests | MIT |
| React type definitions | TypeScript definitions | MIT |
| FastAPI | HTTP API | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| SQLAlchemy | Database access | MIT |
| Alembic | Database migrations | MIT |
| psycopg / psycopg-binary | PostgreSQL driver | LGPL-3.0-or-later and bundled notices |
| HTTPX | Provider requests | BSD-3-Clause |
| pydantic-settings | Validated configuration | MIT |
| pytest | Backend tests | MIT |
| Python | Runtime | PSF license and accompanying notices |
| Node.js | Frontend build runtime | MIT and bundled component notices |
| PostgreSQL | Persistent database | PostgreSQL License |
| Debian-based container images | Base operating system | Multiple component licenses |

Check installed dependency metadata and retain required license/notices when distributing a package or image. Review bundled binary notices as well as top-level Python/JavaScript licenses. Keep the inventory aligned with actual manifests and repeat tests after dependency changes.

NVIDIA Nemotron is called remotely through Nebius Token Factory. Its exact model license and the service's billing, data-processing and retention terms must be checked for the model/account used. Tarka's Apache license does not replace those terms. UNICEF guidance is a cited design reference, not a software dependency or endorsement.

Upstream references: [React](https://github.com/facebook/react), [FastAPI](https://github.com/fastapi/fastapi/blob/master/LICENSE), [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/blob/main/LICENSE), [Psycopg](https://www.psycopg.org/license/), [PostgreSQL](https://www.postgresql.org/about/licence/) and [Nebius model catalog](https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference).

## V3 speech dependency

V3 adds no TTS package or model weights. Browser Web Speech (`speechSynthesis`, `SpeechSynthesisUtterance`) uses the selected installed voice, restricted to browser-reported local English voices. Voice assets belong to the operating system/voice vendor and are not redistributed in this source archive. Browser support and voice availability are runtime capabilities, not guarantees. See the [SpeechSynthesis API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) and [localService](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/localService) reference.

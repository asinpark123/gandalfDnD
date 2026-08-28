# GandalfDnD

GandalfDnD is a persistent solo D&D engine with an AI dungeon-master boundary. Phase 0 proves the
smallest trustworthy loop: campaign state enters the model as data, the model returns typed
proposals, application code validates those proposals, dice are rolled by code, and the accepted
result is committed to PostgreSQL with an append-only event trail.

## Phase 0 scope

- FastAPI API with health, campaigns, one character, locations, turns, and player-visible events
- PostgreSQL as the canonical source of truth through SQLAlchemy 2 and Alembic
- HP, inventory, and current-location state changes with pre-commit validation
- auditable application dice rolls, including internally logged hidden rolls
- provider-neutral DM interface
- deterministic offline provider for development and repeatable tests
- OpenAI Responses provider with Pydantic structured output

Not included yet: RAG/pgvector, the spoiler-safe Guide, combat, a web UI, Redis, Celery, or a
permanent application VM.

## Local setup

Python 3.11 or newer is required. From the repository:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Gandalf reaches PostgreSQL through a local-only SSH tunnel:

```bash
ssh -N -L 5433:127.0.0.1:5432 postgresvm
```

Keep that terminal open. In another terminal:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn app.api:app --reload
```

The API is then available at `http://127.0.0.1:8000`; interactive API documentation is at
`http://127.0.0.1:8000/docs`.

## Model provider

The safe default is `GANDALF_LLM_PROVIDER=deterministic`, which performs no external calls. To use
the OpenAI adapter, set these only in the ignored `.env` file:

```text
GANDALF_LLM_PROVIDER=openai
GANDALF_OPENAI_API_KEY=...
GANDALF_OPENAI_MODEL=gpt-5.4
```

The adapter uses the Responses API's Pydantic parsing path. Its output is never written directly to
canonical state: all proposed changes pass through `StateChangeValidator` first.

## API surface

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Confirm the API can reach its configured database |
| `POST` | `/campaigns` | Create a campaign and starting location |
| `POST` | `/campaigns/{id}/character` | Add the Phase 0 solo character |
| `GET` | `/campaigns/{id}/state` | Read canonical campaign, character, and location state |
| `POST` | `/campaigns/{id}/turns` | Process and persist one player action |
| `GET` | `/campaigns/{id}/events` | Read the ordered player-visible event trail |

## Verification

Tests are hard-guarded to a database whose name begins with `gandalfdnd_test`.

```bash
source .venv/bin/activate
ruff check .
ruff format --check .
pytest
```

The integration test recreates only Phase 0 rows inside the dedicated test database. It never
targets the development database or any pre-existing service database.

## Design constraints

- PostgreSQL state wins over model prose.
- Campaign events are immutable after insertion.
- Every model output is typed and validated before commit.
- Dice outcomes come from `DiceService`, never model invention.
- The development and test credentials are separate and ignored by Git.
- Clawvis is outside GandalfDnD's Phase 0 topology and must remain untouched.

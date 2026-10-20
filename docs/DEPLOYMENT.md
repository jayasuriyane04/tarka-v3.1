# Deploying the v3 prototype

This guide prepares a local or controlled trial deployment. It is not a claim that the image, PostgreSQL, live AI or child-facing browser flow has been verified. `STATUS.md` records actual results.

## Keep V1, V2 and V3 separate

Run commands from `outputs/tarka-v3`. Use v3's database, cookie namespace and ports: 8003 for the API/built app and 5175 for frontend development. Do not point V3 migrations at a V1 or V2 database or reuse their session cookies/secrets. Create a fresh V3 database; the package contains no child profiles.

Use the native setup in [README.md](../README.md). `backend/requirements.lock.txt` and `frontend/package-lock.json` are the repeatable installation records. Do not regenerate them casually before a demo; retest dependency changes.

## Local configuration

Copy `.env.example` to `.env` in the v3 root. Keep it out of Git and screenshots. No Judge0 configuration is needed; this application does not run child code.

Keep `ENABLE_PAID_OPERATIONS=false` and `PAID_BUDGET_USD=0` during local authored-lesson testing. Household AI choices should default to false independently of these operator flags.

The default database is SQLite for preview. Apply migrations and seed content using the maintenance commands from the README. Missing AI access must leave the authored learning path usable, with no invented model responses.

## Optional NVIDIA/Nebius hint selection

1. Create or use your Nebius Token Factory account and check billing/credits.
2. Store the API key in `NEBIUS_API_KEY` on the server.
3. Confirm the exact account-visible NVIDIA model and endpoint. The initial values are:

   ```text
   NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
   NEBIUS_MODEL=nvidia/Nemotron-3_5-Lightning
   ```

4. Verify current prices before using the sample input/output rates as cost estimates.
5. Obtain an explicit operator spending ceiling before any paid request. Set `ENABLE_PAID_OPERATIONS=true` and `PAID_BUDGET_USD` to the authorized ceiling.
6. Test using an adult-owned dummy profile. Opt that household into AI through the parent gate.
7. Verify that the response is a valid current-question hint ID and that the browser shows the matching authored text, not model-generated prose.
8. Turn the opt-in off and confirm that further hint interactions make no inference requests.

From `backend` using the project Python environment, `python -m app.manage preflight` reads the account model catalog without making a generation request. These reads may consume API quota. Once spending is explicitly authorized, `python -m app.manage live-check` performs one synthetic hint-selection interaction through the normal budget ledger; a bounded retry can make a second generation request. It uses an in-memory dummy household with AI enabled, not a real child profile, so it does not validate the browser's parent gate. Do not run the live check before authorization.

Inspect request payloads without exposing credentials. They must not contain the nickname, PIN, cookies or unrelated child history. Record model ID, endpoint, dated observations and usage totals. Do not invite children into a live AI trial just to validate account setup.

The operator budget and household choice solve different problems. A configured key does not mean a parent has opted in. A parent opting in does not authorize the operator to exceed an agreed spend ceiling.

Provider references: [Nebius quickstart](https://docs.tokenfactory.nebius.com/quickstart), [NVIDIA model catalog](https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference), [structured output](https://docs.tokenfactory.nebius.com/ai-models-inference/json), and [billing](https://docs.tokenfactory.nebius.com/other-capabilities/billing-new). Public documentation does not establish availability or response behavior in a specific account.

Public documentation rechecked on 2026-10-13: the quickstart uses `https://api.tokenfactory.nebius.com/v1/`; the official Nemotron page lists `nvidia/Nemotron-3_5-Lightning` and input/output prices of $0.06/$0.24 per million tokens. These are sample rates, not a verified account invoice. No account catalog or real inference has been checked for v3.

## PostgreSQL container setup

Install Docker with Compose. Set a strong `POSTGRES_PASSWORD` and randomly generated `SESSION_SECRET` in `.env`. A generated hexadecimal database password avoids connection-URL escaping errors in the supplied Compose file.

From the v3 project root:

```text
docker compose up --build -d
docker compose logs -f app
```

Compose starts PostgreSQL 16, waits for its health check and runs the application migration/seed commands. The unprivileged application container serves the built frontend at `http://127.0.0.1:8003`. Its database persists in the separate `tarka_v3_postgres` named volume. `python -m app.manage schema-sql` compiles PostgreSQL migration SQL without connecting to a database; compilation is not a live PostgreSQL deployment test.

Database ports are not published. The app binds to host loopback, which is appropriate for a local test or a reverse proxy on the same VM. `docker compose down` preserves the volume. Do not add `-v` unless you intend to erase that database and have considered backups and retained data.

Run one application process/worker initially. The single-instance setup avoids races in process-local controls; verify the actual locking design before adding replicas. Move migrations to one release task before introducing multiple instances.

## Before a shared or public trial

1. Have the curriculum independently reviewed for correctness, reading level, difficulty and accessibility across all three age bands.
2. Establish the appropriate permissions and review for the proposed child trial. The built-in acknowledgement and PIN do not do this for you.
3. Determine data retention, deletion, backup access and provider-processing details; communicate these to participating adults in plain language.
4. Configure PostgreSQL, runtime secret storage, HTTPS and secure cookies.
5. Set `APP_ENV=production`, `COOKIE_SECURE=true`, a random `SESSION_SECRET`, the production database URL and exact HTTPS `ALLOWED_ORIGINS`.
6. Add per-public-IP request limits and TLS termination at the host/reverse proxy. Do not expose development servers.
7. Use a fresh adult-owned test household to verify PIN limits, authorization expiry, session ownership, export, deletion, AI opt-in and enforced breaks.
8. Inspect the browser on desktop and a narrow viewport, using keyboard controls and a screen reader where possible.
9. Test a backup/restore process and clarify that deleting live work does not automatically delete every backup or exported copy.
10. Record unresolved limitations. Keep paid inference disabled if live validation or data-flow review is incomplete.

No release should describe the prototype as certified safe, legally compliant or educationally proven on the strength of automated tests alone.

## Operational handover

Assign an adult operator to monitor service failures, budget, incorrect content reports and deletion requests. Keep credentials and child data out of ordinary logs. Retain a previous application image and compatible database backup before releases.

If model behavior, spend or data handling is unexpected, disable paid operations and household AI access while investigating. Authored practice should remain available. Do not reset the spending ledger to bypass the approved ceiling.

A public URL, successful container build, live inference check and completed child study must each be recorded separately; none follows automatically from the presence of this deployment recipe.

## V3 voice deployment check

No speech key or paid voice provider is needed. The frontend uses installed browser-reported local English voices only. Test the actual target browser and device: voice enumeration may arrive asynchronously, unsupported/no-local-voice states must preserve text learning, and speech must stop on navigation and breaks. A server-side browser smoke test without local voices does not verify audible output. Parent opt-in and narration logs persist in the V3 database through migration 0002.

## Account and whiteboard upgrade (2026-10-19)

Stop the running app and back up its V3 database, rebuild the frontend, then run the normal launcher. Migration 0003 adds account/session/throttle tables without replacing learner records. Legacy profiles can link to an account with their existing PIN; do not create a fresh database when preserving V3 work. Read [account and board operations](ACCOUNTS-AND-WHITEBOARD.md) for session lifetimes, proxy settings, scrypt memory requirements and recovery limits. Validate signup, sign-in, sign-out-all, password changes, old-cookie rejection and owned progress in the deployed environment. No SMTP/API key is required for local parent accounts or authored whiteboards.

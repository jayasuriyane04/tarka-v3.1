# Tarka V3 implementation plan

1. Done: copy V2 source, tests, curriculum, configuration and documentation; preserve V2 and save a hash manifest. Exclude credentials, child data and installed/build caches.
2. Done: preserve V2 capabilities, isolate V3 cookies/database/ports, and add parent-controlled spoken teaching with visible transcripts, pace/voice choice and stop/pause controls.
3. Done: preserve the original 18 lessons and add 12 original maths/reading lessons across three age bands (30 lessons / 120 questions).
4. Done for local scope: 181 backend tests, 39 frontend tests, curriculum validation, SQLite migrations, production build and actual browser journeys pass. Browser review fixes included in the final build. See STATUS.md for test boundaries.
5. Done: update setup/deployment/parent/demo documentation, record measured evidence and screenshots, and prepare the clean source/build archive.
6. Externally pending: account model preflight/live inference under an authorized ceiling; real PostgreSQL/container/hosting validation; human listening/accessibility, educator and supervised student review; hackathon scope check and user-recorded video.

No paid operations without authorization. Browser speech is labelled device speech, not NVIDIA-generated audio. Live Nebius remains separately gated by credentials and budget. Neither a build nor mocked tests establish live provider quality or educational effectiveness.

"""Read-only comparison with the original V2 checkout, when available."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'V2-BASELINE.json').read_text(encoding='utf-8'))
source = (ROOT / manifest['source']).resolve()
report = {'created_at': datetime.now(timezone.utc).isoformat(), 'source': manifest['source']}
if not source.is_dir():
    report.update(status='skipped', reason='The standalone package does not include the sibling V2 checkout.')
else:
    mismatches = []
    for entry in manifest['copied_files']:
        path = source / entry['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            mismatches.append(entry['path'])
    original = json.loads((source / 'backend/content/lessons.json').read_text(encoding='utf-8'))
    current = json.loads((ROOT / 'backend/content/lessons.json').read_text(encoding='utf-8'))
    preserved = len(original) == 18 and current[:18] == original
    report.update(status='passed' if not mismatches and preserved else 'failed',
                  source_files_checked=len(manifest['copied_files']), changed_source_files=mismatches,
                  original_lesson_objects_preserved=preserved, original_lessons=len(original),
                  additional_lessons=len(current) - len(original))
target = ROOT / 'evaluation/reports/v2-preservation.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(1 if report['status'] == 'failed' else 0)

# Start the built app in this terminal. No browser launch or paid AI configuration.
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$localPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$workspacePython = Join-Path $projectRoot '..\..\work\tarka-venv\Scripts\python.exe'
if (Test-Path -LiteralPath $localPython) {
    $pythonPath = (Resolve-Path -LiteralPath $localPython).Path
} elseif (Test-Path -LiteralPath $workspacePython) {
    $pythonPath = (Resolve-Path -LiteralPath $workspacePython).Path
} else {
    throw 'Create the project .venv and install backend/requirements.lock.txt as described in README.md first.'
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'frontend\dist\index.html'))) {
    throw 'Build the frontend first: cd frontend; npm ci; npm run build.'
}
Push-Location (Join-Path $projectRoot 'backend')
try {
    & $pythonPath -m app.manage upgrade
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    & $pythonPath -m app.manage seed
    if ($LASTEXITCODE -ne 0) { throw 'Lesson seeding failed.' }
    Write-Host 'Open http://127.0.0.1:8003 in your browser. Press Ctrl+C here to stop.'
    & $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8003
    if ($LASTEXITCODE -ne 0) { throw 'The app stopped. Check the preceding server message.' }
} finally {
    Pop-Location
}

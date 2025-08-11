# Build Trigger

This file triggers the GitHub Actions workflow for Windows installer builds.

**Build ID**: `alpha-build-$(date +%Y%m%d-%H%M%S)`
**Branch**: `feature/tauri-implementation-20250809`
**Target**: Windows MSI + NSIS EXE
**Timestamp**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Expected Outputs:
- `Hearthlink-1.3.0-alpha-{timestamp}-x86_64-pc-windows-msvc.msi`
- `Hearthlink-1.3.0-alpha-{timestamp}-x86_64-pc-windows-msvc.exe`
- `build-info.json` with metadata

## Workflow Status:
Ready to trigger via GitHub Actions manual dispatch or PR to main.
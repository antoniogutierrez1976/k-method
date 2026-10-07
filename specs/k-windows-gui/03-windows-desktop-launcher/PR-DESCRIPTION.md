# Pull Request: feat(gui) - Phase 3: Windows Desktop Launcher & PowerShell Integration

- **Closes:** #k-windows-gui (Phase 3)
- **Governed-By:** [[ADR-004-antigravity-gui-and-embedded-skills]]
- **Verified-By:** `python scripts/verify-all.py` (63 unit tests passing, OKF graph clean)

---

## 1. Summary of Changes

### Windows Desktop Launcher
- Created [launch.py](file:///d:/dev/k-method/scripts/harness/gui/launch.py):
  - Dynamic TCP port allocation (`find_available_port`) to prevent bind conflicts.
  - Automatic default browser launch targeting local host `http://127.0.0.1:{port}`.
  - Localhost binding security enforcement (`127.0.0.1` by default).
  - Health check polling utility (`verify_server_health`).
  - Graceful shutdown on Ctrl+C / KeyboardInterrupt.

### PowerShell Launcher Script
- Created [run-gui.ps1](file:///d:/dev/k-method/run-gui.ps1) in repository root:
  - Enforces UTF-8 console encoding on Windows.
  - Supports `-Port`, `-HostAddress`, and `-NoBrowser` switches.

### Documentation
- Updated [README.md](file:///d:/dev/k-method/README.md) with GUI launcher usage instructions.

---

## 2. Acceptance Criteria Verification

- [x] **AC-Sec-1:** Default localhost binding `127.0.0.1` (`test_AC_Sec_1_localhost_binding_default`).
- [x] **AC-1:** Port auto-resolution on busy ports (`test_AC_1_port_auto_resolution`).
- [x] **AC-2:** Python launcher CLI parameter parsing (`test_AC_2_launch_cli_args`).
- [x] **AC-3:** PowerShell launcher contract and parameters (`test_AC_3_powershell_launcher_contract`).
- [x] **AC-4:** Server lifecycle health check verification (`test_AC_4_healthcheck_verification`).
- [x] **AC-5:** Documentation updated in README.md (`test_AC_5_documentation_updated`).

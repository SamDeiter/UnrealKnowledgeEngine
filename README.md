# Unreal Knowledge Engine (UKE) v4.1 POC

Proof-of-concept for the Unreal Knowledge Engine, demonstrating Learning Objects (LOs), Trust Gate validation, automated docs-as-tests capture, and deterministic learning paths.

## Prerequisites

- **Python 3.11+**
- **Unreal Engine 5** (Source build or Launcher version) - Required for `capture` and full `heal` verification.
- **Dependencies**: `rich`, `pydantic`, `PyYAML`, `pillow` (Install via `pip install .`)

## Installation

```bash
pip install -e .
```

## CLI Commands

The `uke` CLI is the main entrypoint.

### 1. Initialization

Creates the folder structure and sample `context.json`.

```bash
uke init
```

### 2. Gate (Validation)

Validates LO schema and evidence integrity.

```bash
uke gate --engine <UE_ENGINE_PATH>
```

Outputs: `out/gate_report.json`, `out/status.json`

### 3. Capture (Docs-as-Tests)

Runs the integration test for a specific LO in Unreal Engine, capturing screenshots and layout data.

```bash
uke capture --engine <UE_ENGINE_PATH> --lo staticmesh.collision.simple
```

Outputs: `out/images/staticmesh.collision.simple/` (step_01.png, step_01.layout.json, step_01.final.png)

### 4. Auto-Heal

Checks for cosmetic drift using normalized hashing.

```bash
uke heal --engine <UE_ENGINE_PATH> --from-sha <OLD> --to-sha <NEW>
```

Outputs: Audit logs in `out/audit/`

### 5. Plan

Generates a deterministic learning path based on context.

```bash
uke plan --context context.json
```

Outputs: `out/path/path.json`, `out/path/path.md`

### 6. Site Generation

Generates a static markdown site for the LOs.

```bash
uke site
```

Outputs: `out/site/`

## Repo Structure

- **knowledge/**: LO definitions (YAML) and assets.
- **tools/**: Python implementations for gate, capture, heal, plan, cli.
- **out/**: Generated artifacts (ignored by git).
- **tests/**: Unit tests.

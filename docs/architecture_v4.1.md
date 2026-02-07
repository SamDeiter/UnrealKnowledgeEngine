# Unreal Knowledge Engine: Architecture v4.1

This document supersedes v4.0 and incorporates the v4.0 updates plus additional changes required for **safe autonomous updates**, **reliable test-based docs**, and **operable CI at engine velocity**. The major refinement in v4.1 is: *automation is allowed only when risk is bounded and observable*.

---

## 1. System Philosophy: The Exception-Gated Autonomous Knowledge Graph

We do not author documentation pages; we **compile and continuously validate** a graph of Learning Objects (LOs).

### Core Axioms

* **Immutable Truth**: Every factual claim is backed by code evidence (SHA + structural identity).
* **Docs are Tests**: Every *task* LO has an executable validation (integration test) when feasible.
* **Management by Exception**: Mechanical drift is auto-healed; semantic drift is flagged with risk.
* **Context-Aware**: Learning paths are generated using *user/project context* as constraints.
* **Auditability**: Every auto-merge is attributable, reproducible, and reversible.

---

## 2. Learning Object (LO) Schema (v4.1)

v4.1 keeps v4.0 schema changes and adds the missing fields required to support autonomous operation: explicit requirements, validation contracts, and lifecycle states.

```yaml
id: staticmesh.collision.simple
schema_version: 4.1

type: task   # concept | task | reference | troubleshooting

title: "Setting Simple Collision"
version: 1.1.0

scope:
  editor: true
  runtime: false

# NEW: explicit dependency constraints for context-aware planning
requirements:
  engine_version: ">=5.3 <5.7"
  plugins_required: []
  plugins_incompatible: []
  settings_required:
    - key: "/Script/Engine.PhysicsSettings.bEnableEnhancedDeterminism"
      equals: false

volatility:
  level: High
  decay_rate: 0.1

prereqs:
  - staticmesh.import.basics

maintenance_policy:
  auto_merge_line_shifts: true
  auto_merge_cosmetic: true
  auto_merge_safe_renames: true  # NEW (bounded by symbol_id + signature equivalence)
  max_auto_merge_risk: low       # NEW: low | medium | high

outcomes:
  - "Can enable simple collision in the Static Mesh Editor"

failure_modes:
  - condition: "Actor falls through floor"
    check: "Collision Complexity != UseComplexAsSimple"
    remediation:
      - staticmesh.collision.troubleshoot

evidence:
  - context: "Primary API"
    symbol: UStaticMesh::SetCollisionComplexity
    symbol_id: "c:@S@UStaticMesh@F@SetCollisionComplexity#..."   # clang USR
    file: Engine/Source/.../StaticMesh.h
    ast_node: FunctionDecl
    snippet_hash: "sha256:7f9a2d..."   # normalized hash
    commit: "5e4c9a2"

# NEW: validation is a first-class contract
validation:
  kind: editor_integration_test  # none | compile | unit | editor_integration_test
  script: "capture_collision_settings.py"
  asserts:
    - "mesh.CollisionComplexity == complex_as_simple"
  artifacts:
    images:
      - id: step_01
        anchors: [CollisionComplexityRow]

# NEW: lifecycle state separates stale docs from broken engine behavior
lifecycle:
  status: verified   # verified | stale | needs_review | invalid | quarantined
  last_verified_sha: "5e4c9a2"
  last_verified_at: "2026-02-07"

trust:
  trust_score: 0.85
  risk_level: low     # low | medium | high
```

### Notes on new fields

* **requirements** enables deterministic filtering using context.
* **validation** makes "docs-as-tests" machine enforceable.
* **lifecycle.status** adds `quarantined` for flaky tests or unsafe drift.
* **risk_level** is computed by the pipeline and must not be author-edited.

---

## 3. Docs-as-Tests Pipeline (v4.1)

### 3.1 Test Hermeticity (New)

Docs-as-tests only works if tests are repeatable.

Rules for capture/validation scripts:

* Run inside a dedicated **TutorialCaptureProject** with fixed assets.
* Set deterministic editor layout/window size (reset layout step).
* Disable nondeterministic influences when possible (auto-save prompts, popups).
* No network calls.
* Tests must define **setup**, **assert**, **capture**, **teardown**.

If a test is flaky > N runs, LO becomes `quarantined` until fixed.

### 3.2 Validation Outcome Mapping (Refined)

* **Assertion fails** → `invalid` (engine regression or unsupported behavior)
* **Assertion passes, capture fails** → `needs_review` (pipeline/tooling issue)
* **Assertion passes, anchor lost** → `stale` + `image_needs_review`

This prevents generating screenshots for broken features.

---

## 4. Green Lane Freshness Pipeline (Exception-Gated)

### Phase 1: Drift Detection & Classification

Inputs: Previous SHA vs Current SHA

Detection layers:

1. **Symbol identity** (symbol_id/USR) existence
2. **AST signature** comparison (params, return type, metadata)
3. **Normalized snippet hash**

Classification outputs:

* `mechanical` (line shifts, whitespace)
* `cosmetic` (comment-only)
* `safe_rename` (identifier rename with symbol_id stable and signature stable)
* `compatible_api_change` (new optional param/defaulted, overload added)
* `breaking_change` (param reorder/remove, type change, removed symbol)
* `behavioral_change` (implementation semantics; detected via heuristics or asserts)

Output: `impact_report.json` containing per-symbol events + severity.

### Phase 2: Evidence Re-Hashing + Re-Anchoring

For each evidence entry:

* Locate by symbol_id
* Re-extract canonical snippet
* Normalize + hash

Rules:

* Hash match → auto-heal line ranges + commit
* Hash mismatch with stable symbol_id → mark `needs_review` and generate proposal
* Symbol missing → mark `invalid` and open red-lane task

### Phase 3: Agent Semantic Analysis (Proposal)

The agent reads:

* old snippet vs new snippet
* AST signature diff
* any validation failures

Agent produces:

* PR with changes
* a **risk classification** (low/medium/high)
* the exact **reasoning artifacts** (diff excerpts, impacted LO IDs)

### Phase 4: Auto-Merge vs Human Review (New Policy)

**Green Lane auto-merge** requires all of:

* maintenance_policy permits it
* classification is `mechanical` or `cosmetic` or `safe_rename`
* LO validation passes (if validation.kind != none)
* risk_level == low
* no decrease in trust_score below threshold

**Red Lane** (human review) triggers when:

* breaking/behavioral/compatible_api_change
* validation fails
* anchor lost fallback reached
* risk_level medium/high

### 4.1 Audit Log + Rollback (New)

All merges (including auto) must write:

* `out/audit/<date>/<sha>.json`

  * change classification
  * impacted LOs
  * before/after hashes
  * test results

Auto-merges must be reversible via one command (`revert_auto_merge <audit_id>`).

---

## 5. UI Anchoring & Retargeting (v4.1)

v4.1 keeps v4.0's cascade but formalizes the anchor contract and reduces OCR reliance.

### 5.1 Anchor Contract (New)

Anchors are not pixels; they are **semantic targets**.

Primary anchors:

* Property row name (Details panel)
* Widget path/ID (Slate)

Fallback anchors:

* Category/section anchors
* OCR *only as a last resort* and never used for auto-merge decisions

### 5.2 Retargeting Cascade (Refined)

1. **Exact property anchor**: `GetWidgetBounds("CollisionComplexity")`
2. **Category anchor**: `GetWidgetBoundsCategory("Collision")` + scroll to best match
3. **Panel snapshot**: capture the full Details panel and mark `image_needs_review`

Renderer behavior:

* If (1) or (2) resolves → draw overlay
* If (3) → draw "anchor missing" badge and include remediation hint

### 5.3 Layout Determinism (New)

Capture runtime must enforce:

* fixed window size
* fixed DPI scaling policy (documented)
* reset editor layout before capture

This is required to keep anchors stable.

---

## 6. Context-Aware Path Planner (v4.1)

### 6.1 Context Acquisition

Users run a small script to produce context JSON:

```json
{
  "engine_version": "5.6.0",
  "plugins": ["Nanite", "Chaos"],
  "rendering": "Lumen",
  "platform": "Windows",
  "project_settings": {
    "DefaultPhysicsScene": "Chaos",
    "bUseAsyncScene": false
  }
}
```

Privacy policy:

* Context must not include file paths or proprietary project names by default.
* Context is optional; planner must still work without it.

### 6.2 Deterministic Planning Rules

Planner steps:

1. Filter by engine_version range
2. Filter by requirements (plugins/settings)
3. Filter by lifecycle.status (prefer verified; avoid quarantined/invalid)
4. Prefer higher trust_score
5. Topologically sort prereqs
6. Structure by LO type:

   * concept → task → troubleshooting

### 6.3 LLM Role Split (Strict)

* LLM may classify user goal into tags and select relevant *seed* concepts.
* Deterministic planner selects the actual LO set.
* LLM may narrate and adapt tone, but cannot add steps not present in selected LOs.

---

## 7. Operational Guardrails (v4.1)

### 7.1 Trust Gate (Expanded)

An LO can be in the **Verified Graph** only if:

* Schema valid
* Evidence resolvable at target SHA
* Hash check passes or is reviewed
* Validation passes (if required)
* Image anchors resolve or are explicitly marked stale

### 7.2 Quarantine Lane (New)

If tests are flaky or anchors intermittently fail:

* status → `quarantined`
* excluded from beginner paths
* visible only with warnings in advanced/troubleshooting contexts

### 7.3 Safety Constraints for Beginners (Refined)

High-volatility nodes:

* allowed only if trust_score above threshold and accompanied by a warning
* otherwise require prerequisite concept nodes that explain volatility (UI drift)

---

## 8. Metrics (v4.1)

v4.1 adds two missing metrics: *flakiness* and *rollback frequency*.

* **Auto-Merge Rate**: % of LO updates merged without human intervention (target > 60%)
* **Capture Pass Rate**: % of scripts that pass assertions + capture (target > 95%)
* **Anchor Hit Rate**: % of captures where anchor resolved (target > 90%)
* **Drift Latency**: time from engine commit → LO updated (target < 4 hours)
* **Flake Rate**: % of runs producing inconsistent results (target < 2%)
* **Rollback Rate**: auto-merges reverted per week (target: near 0; investigate spikes)

---

## 9. Revised POC Execution Plan (v4.1)

### Step 1: Vertical Slice – Docs-as-Tests Capture

* Implement TutorialCapture plugin (GetWidgetBounds + focus/scroll helpers)
* Write one capture script for Static Mesh collision
* Include assertions that fail on engine regression
* Produce: screenshot + layout manifest + overlay render

### Step 2: Green Lane – Normalizer + Auto-Heal

* Implement normalizer (strip comments/whitespace)
* Implement re-anchoring by symbol_id
* Mock git ops or apply to a sandbox repo
* Produce: an auto-commit for line drift and cosmetic updates

### Step 3: Deterministic Planner – Minimal Graph

Create 3 LOs:

* `staticmesh.collision.concept` (concept)
* `staticmesh.collision.simple` (task)
* `staticmesh.collision.troubleshoot` (troubleshooting)

Implement planner that:

* filters by context
* orders by concept → task → troubleshooting
* emits per-step reasoning

Success criteria:

> A beginner on Windows using Chaos/Lumen receives a deterministic, verified collision learning path with screenshots that are only generated if the engine assertions pass.

---

## Final Statement

v4.1 enables autonomy without losing correctness:

* **Auto-merge is allowed**, but only when bounded by identity, tests, and audit.
* **Docs rot becomes test failure**, not a surprise.
* **The graph stays trustworthy**, even at engine speed.

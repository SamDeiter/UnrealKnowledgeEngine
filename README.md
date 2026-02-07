# Unreal Knowledge Engine

An exception-gated autonomous knowledge graph for Unreal Engine 5 documentation.

The system compiles and continuously validates a graph of **Learning Objects (LOs)** backed by code evidence, executable tests, and deterministic path planning.

## Architecture

See [Architecture v4.1](docs/architecture_v4.1.md) for the full system design.

### Core Principles

- **Immutable Truth** — Every claim is backed by code evidence (SHA + structural identity)
- **Docs are Tests** — Task LOs have executable validation when feasible
- **Management by Exception** — Mechanical drift is auto-healed; semantic drift is flagged
- **Context-Aware** — Learning paths use user/project context as constraints
- **Auditable** — Every auto-merge is attributable, reproducible, and reversible

## Project Structure

```
UnrealKnowledgeEngine/
├── docs/
│   └── architecture_v4.1.md   # System architecture document
├── README.md
└── .gitignore
```

## License

Private — All rights reserved.

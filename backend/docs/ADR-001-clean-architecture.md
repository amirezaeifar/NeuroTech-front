# ADR-001: Pragmatic Clean Architecture for Phase 1

**Status:** Accepted  
**Date:** 2026-07-26  
**Deciders:** NeuroTech engineering

## Context

Phase 1 needs a Flask delivery layer, authentication workflows, SQLAlchemy persistence, Redis OTP, and PyJWT without coupling business rules to those technologies. It must also establish models for later business phases without prematurely exposing their APIs.

## Decision

Use four dependency layers:

1. `interfaces/http` translates Flask requests and responses.
2. `domain/services` owns authentication and OTP workflows.
3. `domain/repositories`, `domain/ports`, and `domain/unit_of_work.py` define framework-neutral boundaries.
4. `infrastructure` implements those boundaries with SQLAlchemy, Redis, Werkzeug, PyJWT, and Fernet.

`app/main.py` is the only composition root. SQLAlchemy entities remain in `domain/entities` as a documented pragmatic compromise; services interact with them only through repository ports and never create sessions.

## Options Considered

| Option | Assessment |
|---|---|
| Flask extensions and global model access | Lower initial code volume, but hides dependencies and makes transaction, token, and OTP behavior difficult to test safely. |
| Fully persistence-ignorant domain objects plus separate ORM mappings | Strongest isolation, but excessive mapping duplication for Phase 1's 87-table foundation. |
| Selected: ports, services, Unit of Work, and domain-hosted ORM entities | Preserves testable workflow and adapter boundaries while keeping the schema maintainable. |

## Consequences

- Controllers contain no ORM queries or transaction calls.
- Services can be tested with fake repositories and ports.
- Refresh rotation and OTP atomicity can change adapters without changing HTTP code.
- Alembic imports one complete metadata graph.
- Domain entities remain dependent on SQLAlchemy; this is the explicit compromise to revisit only if persistence requirements materially diverge.
- Product, academy, event, partner, trade, commerce, content, and administration workflows remain deferred even though their schema foundations exist.

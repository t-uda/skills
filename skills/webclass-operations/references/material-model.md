# Applicable Attribute Model

Reuse a suitable canonical source or compact task-local record across design, generation, application, and verification. No mandatory format or second database is required. Keep operator state outside instructor-facing prose unless that prose needs it.

## Discover before fixing values

Inspect controls for relevant object types and conditional branches. Record attribute scope, meaning, applicability/dependencies, allowed values, and import/UI support. Mark incomplete discovery. Familiar settings and export columns are examples, not an exhaustive schema.

| Level | Minimum information |
| --- | --- |
| Object/version | Target identity/type, owner/scope, content source/version and decision status, observed operational state, preservation constraints. |
| Definition | Attribute scope, meaning, applicability/dependencies, allowed values, available transfer routes. |
| Decision | Observed value with source/time; intended value or preservation of a specified snapshot; governing requirement; resolved, unknown, or not applicable. |
| Application/check | Changed/preserved fields, import/UI sequence, intermediate exposure, expected result, saved readback, rendering/behavior checks, discrepancies and untested scope. |

Share provenance at snapshot level where appropriate. Preserve means retain a known value, not skip discovery. Not applicable requires checking applicability; it is distinct from unknown. Observed defaults and prior policy never automatically become intended requirements.

For creation, copying, or migration, cover the complete applicable configuration, including attributes absent from exports. For bounded revision, check affected attributes/dependencies and enough preserved state to detect collateral changes. Refresh and reconcile concurrent changes before overwrite.

## Shared ownership and return path

The content workflow updates semantic requirements and version acceptance; the WebClass operator updates discovered definitions, observations, control mappings, application, and verification. The intervention workflow updates action authority/access/attention in existing task state, not educational policy. One agent can perform all roles by loading the relevant skill when its responsibility is needed; a handoff ceremony is unnecessary.

If a semantic requirement has no faithful platform representation, record the exact mismatch and supported alternatives. Return the affected decision to the content workflow, resolve it under existing delegation or a reserved human decision, then update the shared model/version and regenerate only affected derivatives and mappings. Keep unrelated accepted portions stable. Do not treat a technical limitation as permission to change the educational requirement.

Plan transitions as well as final values: verify actual staging controls, account for exposure/attempt/grading after each import/save, apply required UI-only settings, reopen and compare, then release when authorized. Record what was and was not checked; do not substitute local source equality for delivery verification.

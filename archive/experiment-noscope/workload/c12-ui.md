# Toy workload card 12 — ui skeleton notes

TOY-OK

## Scope

Single-owner card. Writes only `workload/c12-ui.md`.

## Content

This card records the UI skeleton notes for the toy workload experiment.
The toy experiment workload renders each card as a fixed UI skeleton slot
with a title, a content block and a notes block; card writers fill the
slots in the markdown skeleton below rather than hand-writing each view.

## UI skeleton template

Every card uses the following skeleton:

```markdown
# Toy workload card <NN> — <slug> notes

TOY-OK

## Scope

Single-owner card. Writes only `workload/c<NN>-<slug>.md`.

## Content

<Card content specific to the card's topic>

## Notes

<Card-specific notes, kept concise and data-only>
```

## Conventions

- Card title uses the `Toy workload card <NN> — <slug> notes` form.
- The acceptance marker is `TOY-OK` and sits on line 3, before the `##`
  sections.
- The checker (`workload/check.py`) verifies only the presence of the
  `TOY-OK` marker; the skeleton above is the contract for downstream UI
  consumers of the toy experiment.

## Notes

- All timestamps are UTC.
- This card is card 12, slug `ui`; it writes no file other than
  `workload/c12-ui.md`.
- Card 12 is part of the 20-card toy workload described in
  `docs/phase0-verification-2026-11-11.md`.
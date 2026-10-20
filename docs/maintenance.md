# Maintain the canonical documentation

Znbu owns the product design and backlog. Matomeru owns the implementation. The outline and todo indexes group the same concepts so a design and its remaining work are adjacent.

## Put each change in one place

- Add current behavior and its limits to the matching document under `outline/`.
- Add unfinished acceptance criteria to the matching document under `todo/`. Keep existing `B-nn` identifiers.
- Keep plans and research linked from the affected todo item until their unfinished scope is resolved. A plan file is not a second backlog.
- Keep an idea that applies beyond Matomeru in the ecosystem backlog. Do not drop it because its implementation belongs elsewhere.
- Link related concepts instead of repeating their requirements.

## Move finished work into the outline

1. Compare every acceptance criterion with implementation evidence. A checked box, a plan, or the presence of a package does not establish completion.
2. Record the implemented behavior in its outline document, with its item identifier and evidence. Distinguish recorded verification from a check performed during the current change.
3. If only part is implemented, leave only the remaining acceptance criteria in the active todo item and link to the implemented portion.
4. Keep work awaiting another session's verification open. Record its owner and scope without treating it as shipped.
5. Mark replaced designs as superseded and link their replacements. Do not describe removed code as current behavior.
6. Update the indexes and the source map after moving a section.

## Preserve source material

The source map records each inspected document, its preserved location, and its canonical destinations. Files under `sources/` are historical inputs, not alternate instructions or live backlogs. They retain original wording, including old paths, statuses, and contradictory proposals. The concept documents resolve those differences or name the unresolved decision.

Original notes in the hub and ima directories remain untouched. Documentation owned by another implementation session remains untouched. Refresh the source map when those inputs change rather than overwriting that session's work.

## Check a documentation change

Run the repository's documentation checker against a snapshot on vps2. It checks preserved-source hashes, canonical links and anchors, backlog identities, and references to unfinished plans. Review the source map as well: a valid link does not prove that a requirement was faithfully consolidated.

The consolidation does not implement backlog features or re-run historical application acceptance suites. New implementation claims require their own evidence.

## Consolidation verification

The final combined snapshot passed `python3 scripts/check-docs.py --root .` on vps2: 38 preserved sources, 31 canonical Markdown files, 9 plans, 102 item dispositions, zero errors and zero pending mappings. Five unresolved references remain only in immutable historical inputs: three out-of-scope Now documents, an old rail-image name, and a missing old orchestrator report.

Five throwaway negative cases also passed: changed preserved bytes, a broken canonical anchor, an unfinished plan without a todo link, a missing original B disposition, and a source without a canonical destination each failed the checker as expected. Log: `/root/proj/redeck-astra-verification/runs/run.3J60y6D2/verification.log`. External URLs and application runtime behavior were not checked by this documentation pass.

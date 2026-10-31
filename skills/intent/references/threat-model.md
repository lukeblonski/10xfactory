# Threat model

Add `**Model zagrożenia.**` to the block when the change checks or blocks something: a validation script, a hook, a lock, a gate in a workflow, a permission rule, a test that guards a behaviour. Other changes have no threat model.

## What it says

Two short lists in one paragraph or as bullets:

- **Chroni przed:** the mistakes the check exists to catch. By default, an accidental mistake of a person or an agent doing ordinary work: a typo, a forgotten file, a wrong path, a case difference in a file name, a link instead of a file.
- **Nie chroni przed:** what is deliberately out of scope. By default, a deliberate attempt to get around the check, i.e. one that takes conscious effort such as defeating another lock first.

Change the default only when the draft or the human says so (e.g. a payment check that must resist a hostile user).

## Why it matters

Reviews judge the change against this model. A finding inside it is fixed; a finding outside it is recorded as a known limit (in the limitation register in `context/foundation/limitations.md`) instead of being patched. This keeps review rounds from turning into an arms race over ever more exotic bypasses.

## Example

```markdown
**Model zagrożenia.**
- Chroni przed: przypadkową literówką w odwołaniu do skilla, którą agent zrobi przy zwykłej edycji.
- Nie chroni przed: celowym ukryciem odwołania, np. sklejeniem nazwy w czasie działania.
```

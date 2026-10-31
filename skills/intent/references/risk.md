# Risk level

Two levels only: `Wysokie` and `Niskie`. Drafts sometimes say "Średnie"; that level does not exist here, so decide between the two with the conditions below.

## High

The change is high risk when at least one condition holds:

1. it migrates or deletes data;
2. it touches logging in, payments or permissions (who may see or do what);
3. it adds an external service or a new dependency (a package, an API, a hosted tool);
4. it changes a public API: an interface other programs or people call (an HTTP endpoint, a published library function, a CLI used outside the repo, a file format others read);
5. it carries a product decision that neither the intent nor the product principles support.

When you are unsure whether a condition holds, the risk is high.

## Low

Every other change. Low risk still needs a reason: name what makes it safe (e.g. "only reads existing data", "changes one internal function covered by tests").

## The sentence

One sentence after the level, naming the condition that decided it or saying none holds:

- `**Ryzyko.** Wysokie. Zmiana dotyka uprawnień: decyduje, kto widzi rezerwacje innych osób.`
- `**Ryzyko.** Niskie. Zmiana dodaje widok, który tylko czyta istniejące rezerwacje, i nie dotyka danych, logowania, zależności ani publicznego API.`

A draft that already states a risk is checked against these conditions like any other. When the draft says low but a condition holds, the level becomes high; interactive, tell the human why; unattended, record the change as an escalation.

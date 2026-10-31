# Criteria: worse and better

Each example gives the original, why it is not accepted, and a rewording that can be checked.

## A new channel of evidence (stage 3 of the factory, V5 point 5)

- **Worse:** "Every criterion has an entry in the review report that refers to the run report."
- **Why:** it invents a new kind of evidence (a review entry pointing at a run report) while the problem was only "a criterion is not done without evidence". Review rounds 3 and 4 of that stage looped over how the new entry should look.
- **Better:** "Before archiving, the newest verifier report in `runs/` has a MET verdict with evidence for every criterion."
  - Sprawdzenie: polecenie `python3 skills/10x-impl-review/scripts/validate_change.py <change-id> --rules 5`

## A mechanism instead of an effect (stage 3 of the factory, V7)

- **Worse:** "Every problem the script finds becomes a review finding."
- **Why:** it prescribes how problems travel (into review findings) instead of what must happen. It led to an escalation in round 2 and a third loop around a repair command nobody needed.
- **Better:** "When the script exits with a code other than 0, the skill stops and shows the script's output."
  - Sprawdzenie: weryfikator — reads the skill's step that runs the script and confirms it stops on a non-zero exit and prints the output.

## An impression

- **Worse:** "Interfejs jest intuicyjny."
- **Why:** only a person can judge it, and the factory does not test by hand.
- **Better:** reword to the effect that made the author call it intuitive, e.g. "R4. Przycisk rezerwacji jest widoczny przy każdym wolnym biurku na liście." or "Anulowanie rezerwacji zajmuje najwyżej 2 kliknięcia od strony „Moje rezerwacje”."
  - Sprawdzenie: polecenie `npm test` (a test that renders the list and asserts the button, or counts the steps)

## A number of steps

- **Worse:** "Rezerwacja jest szybka."
- **Why:** "szybka" has no threshold.
- **Better:** "Rezerwacja biurka z listy wolnych biurek wymaga najwyżej 3 kroków: wybór dnia, wybór biurka, potwierdzenie."
  - Sprawdzenie: weryfikator — runs the end-to-end test of the booking flow and counts the steps in it.

## Several results in one

- **Worse:** "Formularz waliduje dane i wysyła mail z potwierdzeniem."
- **Why:** two results that can pass and fail separately.
- **Better:** two criteria: "Formularz z pustym polem e-mail pokazuje błąd i nie wysyła danych." and "Po poprawnym wysłaniu formularza kolejka maili ma jedną wiadomość z potwierdzeniem."

# Zmiany w skillach 10x — etap-6-poprawki: pozycja roadmapy kończy się tam, gdzie łańcuch i tak staje

- **Zakres:** gałąź `etap-6-poprawki` od `5bbf20a` (`master` przed zmianą) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only master...HEAD -- 'skills/10x-*'`. Sekcje dostają skille `10x-*` z tej listy.
- **Poza skillami:** kolejność zapisu stanu autopilota przy wznowieniu, programy testów w kroku planu testów, instalacja zabezpieczeń przez autopilota przed krokiem `zabezpieczenia`, zabezpieczenia bez szybkiej kontroli po edycji i pomiar według celu wersji (`scripts/autopilot.py`, `scripts/pomiar.py`, `skills/guardrails/`, `skills/retro/`, dokumenty startu i sesji). Ich kod jest publikowany wprost, więc nie mają tu sekcji.
- **Źródło:** polecenie człowieka 2026-11-03 (poprawki po budowie modu context-insight, etap 6); decyzja D-467 o celu fabryki w `context/foundation/decisions-archive.md`.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-roadmap

- **Co zmienić:**
  - Pozycja roadmapy to jedna zmiana. Obejmuje wszystkie historie użytkownika aż do najbliższego miejsca, w którym budowa i tak musi stanąć, a każda z tych historii jest fazą planu tej zmiany. Krok 6b opisuje to zamiast reguły, że pozycja to zwykle jedna historia.
  - Akapit o granulacji pozycji nie każe już wyrównywać ich wielkości ani dzielić dużych. Zamiast wyzwalaczy podziału ma cztery powody granicy: człowiek ma coś zobaczyć albo zaakceptować, potrzebny jest warunek z zewnątrz (konto, dostęp, zgoda dostawcy), następna historia wymaga zgody człowieka (płatna usługa, upublicznienie, wysyłka danych) albo niesie osobne duże ryzyko. Linia ryzyka pozycji nazywa powód, który ją kończy. Sama wielkość nie jest powodem.
  - Punkt samooceny o granulacji odrzuca roadmapę, gdy granica nie ma powodu albo gdy powód zatrzymania wypada w środku pozycji. Liczba historii w pozycji nie jest błędem.
  - Zasady ogólne (punkt o granulacji i punkt o przerwaniu zapisu) mówią to samo. Opis powiązania z `/10x-plan` mówi, że jedna pozycja daje jedną zmianę z fazami, a nie kilka zmian. Przykładowe wiersze tabeli przeglądu mają po dwie historie w pozycji.
  - Zakaz cięcia warstwami (osobna pozycja na dane, osobna na interfejs) zostaje.
- **Dlaczego:** każda pozycja to pełny łańcuch zmiany z własnym narzutem: plan, przegląd planu, implementacja, przegląd kodu, archiwum. Roadmapa modu context-insight miała 12 pozycji. Pierwsza (F-01) kosztowała 66 min i 27,99 USD. Pozostałe 10 pozycji zbudowane razem jako jedna zmiana (`pierwsza-wersja`) kosztowało 161 min i 75,36 USD. Człowiek szacował budowę tych 10 pozycji po kawałku na 250–300 USD (ok. 10 razy koszt F-01). Granica pozycji ma więc sens tylko tam, gdzie łańcuch i tak się zatrzymuje.
- **Zależności:** brak własnych plików. Reguła opiera się na polach, które skill już ma: blokerach zewnętrznych, warunkach zewnętrznych w wymaganiach wstępnych, niewiadomych blokujących i linii ryzyka.
- **Jak sprawdzić:** `grep -n 'boundary trigger' skills/10x-roadmap/SKILL.md` pokazuje krok 6b, punkt samooceny i zasady ogólne; `grep -nE 'one US-NN|oversized' skills/10x-roadmap/SKILL.md` nic nie znajduje.

# Zmiany w skillach 10x — poprawka P14 z retrospektywy wdrozenie: status w roadmapie aplikacji z wdrożeniem

- **Źródło:** propozycja P14 retrospektywy `context/changes/wdrozenie/` (dowód: interwencje `I-7` i `I-8` w `change.md` zmiany).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** w kroku zamykania pozycji roadmapy (część „Move and stamp”) sprawdzić, czy `CLAUDE.md` w repo ma sekcję `## Wdrożenie`. Jeśli ma, skill nie zmienia statusu pozycji ani w tabeli `## At a glance`, ani w bloku pozycji; nadal dopisuje wpis w `## Done` i podbija datę `updated`. Potwierdzenie na końcu mówi wtedy, że status czeka na wynik wdrożenia. Punkt „Co czytam” wymienia `CLAUDE.md`, czytany tylko pod kątem tej sekcji.
- **Dlaczego:** w aplikacji z wdrożeniem status `done` ma się pojawić dopiero po udanym wdrożeniu, a ustawia go autopilot. Skill ustawiał go wcześniej, więc autopilot musiał osobnym commitem przywracać poprzedni status (`hold_status`). Gdy skill przestanie ustawiać status, ten mechanizm da się usunąć bez ryzyka, że `done` pojawi się przed wdrożeniem.
- **Zależności:** krok `wynik-wdrozenia` w `scripts/autopilot.py`, który ustawia `done` po udanym wdrożeniu. Bez autopilota pozycja w aplikacji z `## Wdrożenie` zostaje z dawnym statusem i człowiek zmienia go sam.
- **Jak sprawdzić:** `grep -n 'Wdrożenie' skills/10x-archive/SKILL.md` pokazuje warunek w kroku zamykania roadmapy, w „Co czytam” i w potwierdzeniu. Po archiwizacji w repo z `## Wdrożenie` w `CLAUDE.md` commit archiwum nie zmienia linii `Status` pozycji w `context/foundation/roadmap.md`, a w repo bez tej sekcji zmienia ją na `done` jak dotąd.

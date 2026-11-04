# Polityka triage'u uwag z review

Treść tej polityki to decyzja człowieka. Agent jej nie zmienia. Propozycję zmiany reguły zapisuje w Notes zmiany.

## Kolejność

Agent triage stosuje reguły w tej kolejności: bramka, zapętlenie, waga. Pierwsza pasująca reguła rozstrzyga.

## Bramka

Poprawka uwagi CRITICAL albo WARNING, która trafia na bramkę z sekcji „Kiedy pytać człowieka” w `CLAUDE.md`, idzie do człowieka (ESCALATE, reguła `bramka <n>` z numerem bramki). Poprawka w zakresie zgody z góry z `change.md` (ścieżki, płatne przebiegi) na tę bramkę nie trafia. Innego powodu pytania człowieka ta polityka nie ma.

## Zapętlenie

Reguła `zapętlenie` działa od rundy 2: ten sam mechanizm wraca z powiązanymi uwagami (wobec `## Decyzje triage` wcześniejszych raportów tej serii) albo poprawka z poprzedniej rundy wprowadziła błąd. Agent nie łata wtedy dalej tego fragmentu.

- Reguła obejmuje tylko uwagi do naprawy (CRITICAL albo WARNING). Uwaga OBSERVATION w zapętlonym fragmencie dostaje `AUTO-SKIP (OBSERVATION)`.
- Przepisanie (`AUTO-FIX (zapętlenie)`): raport dostaje akapit „Dlaczego to się powtarza”. Poprawki fragmentu są cofane do stanu sprzed pierwszej łaty, czyli sprzed commitu z ` · commit <sha>` w `## Decyzje triage`: treść fragmentu bierze się z `git show <sha>^:<plik>` i zastępuje tylko ten fragment. Poprawki innych uwag w tych samych plikach zostają; cały plik wolno przywrócić tylko, gdy ten commit zmienił go wyłącznie dla uwag objętych zapętleniem. Potem fragment jest pisany od nowa, prościej, bez tej przyczyny. To jedna próba, bez człowieka.
- Twarde zatrzymanie (`AUTO-LIMIT (zapętlenie)`): gdy następna runda dalej ma w tym fragmencie uwagę do naprawy albo zapętlenie wypada w rundzie 3. Funkcja zostaje wyłączona (kod) albo wycięta z zakresu (plan, do „What We're NOT Doing”), a każda objęta uwaga dostaje wpis w rejestrze z warunkiem powrotu. Człowiek dostaje pytanie tylko, gdy wyłączenie łamie kryterium akceptacji (`bramka 1`).

## Waga

- `CRITICAL` — łamie kryterium akceptacji, test nie przechodzi, gubi dane albo jest dziurą w zabezpieczeniu w ramach modelu zagrożenia zmiany.
- `WARNING` — prawdziwy błąd w sytuacji, która zdarza się przy zwykłej pracy, bez złamanego kryterium.
- `OBSERVATION` — styl, nazwy, opis, przypadek hipotetyczny.

Reguły wagi:

- CRITICAL jest zawsze naprawiana (FIX, reguła `CRITICAL`).
- WARNING jest naprawiana w rundach 1–2 (FIX, reguła `WARNING`), a w rundzie 3 idzie do rejestru (LIMIT, reguła `WARNING, runda 3`).
- OBSERVATION jest pomijana jedną linią w raporcie (SKIP, reguła `OBSERVATION`), bez poprawki i bez rejestru.

Gdy zmiana nie opisuje modelu zagrożenia, przyjmij „przypadkowy błąd agenta, nie celowe obejście” i zapisz to założenie.

## Wpis w rejestrze

LIMIT nie ma poprawki. Uwaga dostaje wpis w rejestrze ograniczeń w `context/foundation/limitations.md`, z jednym zdaniem uzasadnienia i polem „Kiedy wrócić” (warunek, przy którym ograniczenie staje się ważne).

## Łączenie uwag

Uwagi o tym samym miejscu, np. błąd i brakujący test tuż przy nim, triage łączy w jedną poprawkę z jedną decyzją (D-012). Decyzję dostaje uwaga główna, a uwaga dołączona przejmuje ją bez osobnego rozstrzygania. Połączone uwagi mają jeden commit poprawki i najwyżej jedną eskalację.

## Wybór między opcjami A i B

Wybierz opcję zgodną z intencją i „Czego nie robimy”. Przy remisie wybierz mniejszą zmianę. Zalecenie ⭐ jest wskazówką, nie rozstrzygnięciem. Gdy jedna opcja łamie intencję, a druga „Czego nie robimy”, nie wybieraj: uwaga idzie do człowieka (bramka 1).

## Kto decyduje

Triage robi subagent w świeżym kontekście. Nie pisał kodu ani raportu. Czyta tylko raport, `change.md`, `plan.md`, `lessons.md`, politykę, diff zmiany i sekcję „Kiedy pytać człowieka” z `CLAUDE.md` fabryki (z `docs/zgoda-czlowieka.md` obok, gdy ocenia bramkę 2).

## Ponowne review

Po poprawkach uwag CRITICAL albo WARNING albo po przepisaniu przy zapętleniu kolejne review robi subagent w świeżym kontekście, gdy runda jest niższa niż 3. Obejmuje tylko commit z poprawkami i zapisuje następny numerowany raport. Rundy liczą się w całej zmianie: numer rundy to liczba raportów tego przeglądu w `reviews/` zmiany plus jeden, także gdy przegląd uruchamia człowiek albo autopilot. Rundy 4 nie ma. W rundzie 3 poprawki uwag CRITICAL sprawdzają polecenia, bez ponownego review.

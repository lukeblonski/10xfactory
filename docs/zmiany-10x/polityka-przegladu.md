# Zmiany w skillach 10x — polityka-przegladu: prostsza polityka triage'u z jedną skalą wagi

- **Źródło:** zmiana `polityka-przegladu` (etap 3 naprawy fabryki, decyzje człowieka 2026-11-02, D-446 i D-447 w `context/foundation/decisions.md`).
- **Cel zmiany:** triage przeglądu pyta człowieka tylko z bramek zapisanych w `CLAUDE.md`, zapętlenie kończy się jednym przepisaniem fragmentu albo twardym zatrzymaniem bez człowieka, a waga uwagi ma sprawdzalne definicje i sama wyznacza decyzję.

**Wspólne zależności:**
- `CLAUDE.md` z sekcją „Kiedy pytać człowieka” (lista bramek). W repo aplikacji agent triage'u bierze `<fabryka>/CLAUDE.md`, gdy prośba nazywa `<fabryka>`, a inaczej `CLAUDE.md` z katalogu głównego projektu.
- Plik polityki `references/triage-policy.md`, ten sam w obu skillach przeglądu (oryginał w `10x-impl-review`, kopia w `10x-plan-review`; `scripts/check_refs.py` pilnuje, żeby były identyczne).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:**
  - Polityka triage'u ma trzy reguły w stałej kolejności. Bramka: poprawka, która trafia na bramkę z `CLAUDE.md`, idzie do człowieka, chyba że mieści się w zgodzie z góry z `change.md`. Zapętlenie: od drugiej rundy, gdy ten sam mechanizm wraca albo poprawka z poprzedniej rundy coś zepsuła, raport dostaje akapit o przyczynie, fragment wraca do stanu sprzed pierwszej łaty i jest pisany od nowa; gdy to nie pomoże albo zapętlenie wypada w trzeciej rundzie, funkcja jest wyłączana i trafia do rejestru ograniczeń z warunkiem powrotu. Waga: uwaga krytyczna jest zawsze naprawiana, ostrzeżenie w rundach 1–2 naprawiane, a w rundzie 3 zapisywane w rejestrze, obserwacja pomijana jedną linią. Znikają dawne reguły eskalacji, napraw, ograniczeń i pominięć oraz sekcja o pytaniu o podejście.
  - Pole wagi w formacie uwagi dostaje trzy definicje (po polsku, te same co w polityce). Pole wpływu znika razem z tabelą, liniami w przykładach raportu, w szablonie zapisu i w pytaniach ręcznego triage'u. Liczbę opcji poprawki wyznacza waga: obserwacja dostaje jedną linię poprawki, uwaga krytyczna i ostrzeżenie blok z mocną stroną, kosztem, pewnością i ślepym punktem. Przykład uwagi o stylu nazw ma wagę obserwacji.
  - Przed uruchomieniem agenta triage'u sesja szuka sekcji „Kiedy pytać człowieka” w `CLAUDE.md`; gdy jej nie ma, zatrzymuje przegląd z nazwą pliku. Agent dostaje tę sekcję i `docs/zgoda-czlowieka.md` jako wejścia. Odpowiedź agenta ma linię decyzji na uwagę i najwyżej jeden blok zapętlenia (przyczyna, przepisanie albo twarde zatrzymanie), bez bloku pytania o podejście.
  - Zapis decyzji traci dwie siatki korekt i wpisy zamykane wspólnie przez recenzenta i autora. Linia w `## Decyzje triage` nie ma już pola wpływu. Ograniczenie bez warunku powrotu dostaje warunek „zmiana dotyka pliku z miejsca uwagi”. Dopisanie lekcji do `lessons.md` zostaje tylko na prośbę człowieka w ręcznym triage'u.
  - Krok poprawek traci drugiego agenta (autora) i zatrzymanie na pytaniu o podejście. Zamiast tego wykonuje przepisanie zapętlonego fragmentu albo jego wyłączenie. Ponowne review idzie po poprawce uwagi krytycznej albo ostrzeżenia albo po przepisaniu, gdy runda jest niższa niż 3. Czwarta runda tylko wypisuje, że limit trzech rund jest osiągnięty.
- **Dlaczego:** polityka powtarzała bramki z `CLAUDE.md` innymi słowami, wysyłała człowiekowi każdą uwagę o dużym wpływie, a zapętlenia uruchamiały dwóch agentów i często kończyły się pytaniem do człowieka. Waga nie miała definicji, a wpływ był drugą skalą na wyczucie. Przeglądy były prawie połową kosztu zmiany.
- **Zależności:** `CLAUDE.md` z sekcją „Kiedy pytać człowieka”; `references/triage-policy.md`.
- **Jak sprawdzić:** `grep -niw impact skills/10x-impl-review/SKILL.md` nic nie znajduje; `python3 scripts/check_refs.py` kończy się kodem 0, więc polityka i sekcja triage'u są identyczne w obu skillach; `python3 -m unittest discover -s scripts -p 'test_evallib.py'` przechodzi, więc prompt recenzenta i prompt triage'u dają się wyciąć z nowego pliku.

## 10x-plan-review

- **Co zmienić:** to samo co w `10x-impl-review`: ta sama polityka, ta sama sekcja triage'u i zapisu decyzji, definicje wagi w formacie uwagi, bez pola wpływu, bez pytania o podejście i bez agenta autora. Twarde zatrzymanie w planie wycina funkcję z zakresu (do listy tego, czego plan nie robi). Przykład niejasnego kroku planu ma wagę ostrzeżenia, więc dostaje pełny blok opcji. W opisie ślepych punktów planu słowo o wpływie na koszt zastępuje „zużycie zasobów i koszt”.
- **Dlaczego:** jak wyżej; przegląd planu ma tę samą politykę co przegląd kodu.
- **Zależności:** jak w `10x-impl-review`.
- **Jak sprawdzić:** `cmp skills/10x-impl-review/references/triage-policy.md skills/10x-plan-review/references/triage-policy.md` kończy się kodem 0; `grep -nE 'Approach question|pytani[ae] o podejście' skills/10x-plan-review/SKILL.md` nic nie znajduje.

## 10x-impl-review-ci

- **Co zmienić:** w opisie pola wagi w `references/impl-review-instructions.md` zamiast „jak źle, gdy zignorować” wpisać te same trzy definicje wagi co w polityce triage'u. Pole wpływu, jego gramatyka i waga dla brakującego testu zostają.
- **Dlaczego:** recenzja w CI ma oceniać wagę tak samo jak przegląd w sesji; triage'u w CI nie ma, więc pole wpływu zostaje bez zmian.
- **Zależności:** brak; plik nie odsyła do polityki triage'u.
- **Jak sprawdzić:** `grep -n 'przypadek hipotetyczny' skills/10x-impl-review-ci/references/impl-review-instructions.md` pokazuje definicję obserwacji.

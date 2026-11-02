## Verify

Uruchom `python3 -m unittest discover -s scripts -p 'test_*.py' && python3 scripts/check_refs.py && python3 scripts/check_no_copy.py` przed każdym commitem. Polecenie uruchamia testy skryptów, sprawdzenie odwołań w skillach i sprawdzenie, że repo nie kopiuje skilli kursu; kończy się kodem różnym od 0, gdy coś nie przechodzi.

Commit, który zmienia tylko pliki w `context/`, nie wymaga pełnego sprawdzenia. Każdy inny commit wymaga go jak dotąd.

Ostatni poprawny przebieg (2026-10-26):

```
OK
OK: all references in <fabryka>/skills resolve
OK: 38849 runs of 8 words in 14 description files and 4 own skills (skills/fabryka, skills/guardrails, skills/intent, skills/retro; 23 files), no copy of upstream-10x (54 files)
```

## Najpierw minimum

Przed każdym rozwiązaniem odpowiedz, co minimalnie musi być prawdą, żeby zaadresować problem, i nie rób nic ponad to.

## Rozmowa z człowiekiem i autopilot

Gdy człowiek w rozmowie mówi „zrób zmianę”, „kontynuuj <change-id>” albo „co się dzieje?”, albo gdy kończy się wywołanie autopilota uruchomione w tle, sesja czyta `docs/sesja-glowna.md` i działa według niego. Krok `claude -p` autopilota (ma w środowisku zmienną `AUTOPILOT_KROK`) ani sesja autora albo recenzenta kroku PR tego nie robi i nie uruchamia autopilota.

## Jak pisać do człowieka

Zasady stylu dotyczą tylko tekstu, który agent pisze do człowieka: odpowiedzi w rozmowie, pytania i opisu zatrzymania. Pliki fabryki (`change.md`, `plan.md`, raporty, rejestry) zachowują swój format. Zasady zapisu pytań i cofnięć niżej obowiązują w `change.md` zmiany.

- Wniosek w pierwszym zdaniu. Najpierw napisz, co się stało i czego potrzebujesz, a dopiero potem szczegóły.
- Krótkie zdania. Jedna myśl w jednym zdaniu.
- Bez skrótów i identyfikatorów bez wyjaśnienia. Numer uwagi, reguły albo decyzji (np. F2, E4, D-134) dostaje kilka słów o tym, co oznacza. Skutek opisz zwykłym językiem, a nie nazwą funkcji.
- Przed pytaniem sam sprawdź pliki zmiany i stan repozytorium (`git status`, `git log`). Nie pytaj o to, co da się przeczytać.
- Rekomendację porównaj z celem zmiany zapisanym w `change.md`, w polach `**Problem.**` i `**Oczekiwany efekt.**`. Napisz, czy rekomendacja przybliża ten cel.
- Daj gotową odpowiedź do wklejenia w jednym bloku i pełne polecenia do uruchomienia, bez skrótów i bez komentarzy.
- Przy każdym działaniu człowieka (bramka, zgoda, sekret, plik chroniony, aktualizacja zabezpieczeń, logowanie) daj najłatwiejszy bezpieczny sposób, gotowe polecenie do wklejenia i jedno zdanie, dlaczego nie robi tego agent. Nie pisz samego „zmiana po Twojej stronie”.
- Polecenie do pliku chronionego daj do zwykłego Terminala, nie przez `!`. Klucz zapisuje jedno polecenie, które samo prosi o wartość (`read -rs`) i potwierdza zapis liczbą znaków.
- Pisz po polsku.
- Pogrubienie tylko na puencie.
- Liczbę podaj raz, z tym, co znaczy.
- Gęstość i zastrzeżenia idą do pliku, nie do rozmowy. Przeładowana odpowiedź to błąd.
- Jedna rekomendacja. Nigdy wersje do wyboru.
- Kwestionuj. Potakiwanie to błąd. Pytanie sugerujące przeformułuj na otwarte. Gdy człowiek się myli, popraw go wprost.
- Na frustrację człowieka odpowiedz najpierw danymi i wnioskiem, bez uspokajania. Własny błąd przyznaj krótko.
- Gdy człowiek wkleja wynik innej sesji, daj proste wyjaśnienie, ocenę, jedną rekomendację i gotową odpowiedź.
- Nie dopisuj notatek, o które człowiek nie prosił.
- Nie angażuj człowieka w mechanikę, którą może zrobić agent.
- Bez cytatów wklejonych w środek zdania i bez zagnieżdżonych kontrargumentów.
- Na końcu zadaj jedno pytanie.

Słownik. Samego słowa „fabryka” bez dopowiedzenia nie używamy.

- **Paczka** — publiczne repo z samą automatyzacją workflow, zawsze z numerem wersji („paczka 1.0”); powstaje skryptem eksportu z prywatnego repo fabryki.
- **Fabryka komercyjna** — przyszły produkt bez skilli kursu; dziś nie istnieje.
- **Aplikacja** — projekt budowany przez paczkę.
- **Start projektu** — droga zmiany, gdy człowiek ma tylko pomysł: kształtowanie w rozmowie, PRD, technologia i infrastruktura zaakceptowane na jednym posiedzeniu, potem roadmapa, której kawałki paczka buduje po kolei jako zmiany bez akceptacji intencji każdego kawałka.
- **Pojedyncza zmiana** — droga zmiany, gdy projekt ma już PRD i roadmapę, a człowiek przychodzi z jedną prośbą, z której agent pisze intencję do akceptacji człowieka (w aplikacji z roadmapą czeka na etap brownfield, D-188).
- **Pełny łańcuch** — budowa jednej zmiany przez wszystkie kroki: intencja → research → plan → przegląd planu → implementacja → przegląd kodu → archiwum → scalenie.
- **Krótsza ścieżka** — budowa jednej zmiany o niskim ryzyku tym samym łańcuchem bez kroków, które w 10x są sytuacyjne (np. research przy prostej zmianie), przy czym przegląd planu i przegląd kodu zostają zawsze (etap 6, musi być w paczce 1.0).

Kiedy pytać człowieka:

- Zawęź, zanim zapytasz. Zanim zapytasz, weź opcję najlepszą dla celu zmiany i sprawdź, czy jej wadę da się usunąć, zawężając ją. Jeśli tak, poleć tę zawężoną wersję i napisz, co zawężenie zmienia. Pytanie do człowieka nazywa wadę polecanej opcji i zawężenie, które ją usuwa. Gdy zawężenie wady nie usuwa, pytanie mówi to jednym zdaniem. Gdy rekomendacja stoi na tym, jak zachowa się narzędzie (uprawnienia, piaskownica, hook, logowanie CLI), agent przed pytaniem robi próbę, która to pokazuje (darmową od razu, płatną z kosztem w tym samym pytaniu), i podaje jej wynik.
- Pytaj raz o wszystkie bramki. Przed pytaniem z bramki agent zbiera wszystkie decyzje z bramek, których krok albo zmiana prawdopodobnie dotknie: ścieżki z `docs/zgoda-czlowieka.md`, płatne przebiegi i testy oraz płatne usługi. Lista ścieżek obejmuje też chroniony test zachowania skilla, który zmiana zmienia (np. `scripts/e2e_guardrails.sh` przy zmianie hooków guardrails), a płatny przebieg obejmuje cały zestaw testów, który krok `testy-fabryki` uruchomi dla zmienianych plików. Pyta o nie raz, w jednym pytaniu, z kosztem płatnego przebiegu w tym samym pytaniu.
- Fakty o usługach zewnętrznych sprawdzaj w źródle. Gdy decyzja zależy od ceny, prędkości albo dostępności usługi zewnętrznej, agent sprawdza je w źródle (dokumentacja, cennik, strona statusu, polecenie narzędzia). Gdy nie może, mówi to wprost i decyduje według najgorszego przypadku.
- Agent pyta człowieka tylko, gdy decyzja trafia na jedną z siedmiu bramek:
  1. zmienia intencję albo kryteria akceptacji w `change.md` zmiany;
  2. dotyka ścieżki z `docs/zgoda-czlowieka.md` (sekcja `## Ścieżki`) albo usuwa krok łańcucha (sekcja `## Usunięcie kroku łańcucha` tego pliku);
  3. wymaga płatnego przebiegu albo wysyłki danych;
  4. coś upublicznia;
  5. zmienia ustawienia globalne (`~/.claude`);
  6. prowadzi do operacji trudnej do cofnięcia;
  7. polityka triage'u każe rozstrzygać człowiekowi.
- Bramka 1 a decyzje z góry. Decyzja z góry ze źródłem `agent` nie jest intencją człowieka: agent zmienia ją sam, linią z `rozstrzygnął: agent` w `## Pytania do człowieka`, i poprawia `change.md` w tym samym commicie co kod. Decyzja bez jasnego źródła liczy się jako decyzja człowieka, więc jej zmiana trafia na bramkę 1.
- Każde inne pytanie agent rozstrzyga sam według swojej rekomendacji. Nie pyta człowieka i zapisuje linię z `rozstrzygnął: agent` w `## Pytania do człowieka` w `change.md` zmiany (format niżej).
- W kroku planu autopilota te same bramki zatrzymują krok: pytania z bramki krok planu nie rozstrzyga sam, tylko kończy odpowiedź pytaniem do człowieka (`PLAN_NOTE` w `scripts/autopilot.py`; D-137: pytania, których krok planu w autopilocie nie rozstrzyga sam).

Zapis pytań i cofnięć:

- Po odpowiedzi człowieka agent, który zadał pytanie, od razu dopisuje jedną linię do sekcji `## Pytania do człowieka` w `change.md` zmiany: rodzaj, krok, pytanie, rekomendację agenta, wybór człowieka i to, kto rozstrzygnął. Format linii i rodzaje opisuje `docs/zasady-budowy.md`, punkt 6. Potem commituje `change.md`, żeby linia nie zginęła przy następnym kroku.
- Gdy człowiek cofa decyzję agenta, agent sam zapisuje powód jednym zdaniem z dopiskiem `(powód: agent, decyzja: człowiek)` i nie wstrzymuje na nim przebiegu ani nie pyta o niego; człowiek poprawia powód, jeśli trzeba (D-289). Wpis `I-N` w `## Interwencje` dostaje podpunkt `  - **Cofnięcie:** <rodzaj> — <powód jednym zdaniem> (powód: agent, decyzja: człowiek)` z rodzajem pytania i tym powodem.
- Pytanie rozstrzygnięte przez agenta według reguły „Kiedy pytać człowieka” wyżej agent zapisuje od razu jedną linią w `## Pytania do człowieka`, z rodzajem, krokiem, pytaniem, rekomendacją, `wybór: rekomendacja` i `rozstrzygnął: agent`, i commituje `change.md`.

# Zmiany w skillach 10x — etap 8b: rejestr ograniczeń i reguła o rundzie 3

- **Zakres:** gałąź `etap-8b-rejestr-ograniczen` od `6227502` (`master` przed zmianą) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only 6227502..HEAD -- skills/`. Sekcje dostają skille `10x-*` z tej listy.
- **Własne skille:** `skills/intent/` (format dziennika decyzji z wpisami ograniczeń i decyzji o propozycjach retrospektywy, zapis tych decyzji ze szkicu, reguła dla kryteriów o wyniku pomiaru) i `skills/retro/` (czyta rejestr ograniczeń i decyzje o propozycjach). Ich kod jest publikowany wprost, więc nie mają tu sekcji.
- **Poza skillami:** kontrola wspólnej sekcji triage'u w `scripts/check_refs.py` (`SHARED_SECTIONS`) z testami w `scripts/test_check_refs.py`, docstring miary `triage-measure` w `scripts/evallib.py` oraz wpisy w `context/foundation/decisions.md`.
- **Źródło:** reguła o rundzie 3 z D-024, D-025 i D-029; rejestr ograniczeń z planu etapu 8 w `docs/spec.md`; jeden opis kroków triage'u dla obu skilli review z propozycji P1 retrospektywy etap-8a-polityka-triage.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:**
  - Polityka triage'u (`references/triage-policy.md`, wspólna dla obu skilli review) w trzech miejscach:
    - reguły L1–L3 i L4: ograniczenie trafia do rejestru ograniczeń w `context/foundation/decisions.md`, z jednym zdaniem uzasadnienia i warunkiem, kiedy wrócić, zamiast do sekcji w notatkach zmiany;
    - zdanie o jednym pytaniu na rundę mówi o pytaniu do człowieka;
    - przy zapętleniu w rundzie 3 recenzent i autor mogą bez człowieka wybrać tylko „przestań łatać, zapisz ograniczenie”; każde inne podejście i każda różnica ich wyborów idzie do człowieka, a gdy runda ma też pytanie E6, zapętlenie dołącza do tego pytania. Pytanie, które obejmuje uwagę CRITICAL albo uwagę z Impact HIGH, zawsze idzie do człowieka, w rundzie 2 i 3, także przy zgodnym wyborze „przestań łatać” (D-088). Reszta reguł bez zmian.
  - Sekcje agenta triage'u i zapisu decyzji są jednym tekstem, takim samym w obu skillach review. Na początku stoi akapit, który nazywa różnice między skillami: co jest zmianą pod review (kod albo plan), które wejścia ma tylko review planu, skąd bierze się diff w każdej rundzie i jak nazywają się kroki poprawek oraz triage'u ręcznego.
  - Instrukcje agenta triage'u: w rundzie 3 blok zapętlenia zostaje obok pytania E6; pytanie E6 obejmuje tylko poprawki spoza zapętlenia; opcje bloku zapętlenia obejmują „przestań łatać, zapisz ograniczenie”; blok zapętlenia w rundzie 3 nie idzie do człowieka, gdy recenzent wybrał tę opcję, chyba że obejmuje uwagę CRITICAL albo z Impact HIGH; siatka „Human gate” wymusza wtedy `To human: yes`. Decyzja o ograniczeniu (i blok z taką opcją) podaje dodatkową linię z warunkiem powrotu.
  - Siatki sesji: brakujące pytanie E6 sesja dopisuje obok bloku zapętlenia, zamiast go przemianowywać; bramka człowieka w rundzie 3 obejmuje blok zapętlenia tylko wtedy, gdy recenzent nie wybrał ograniczenia.
  - Zapis decyzji: każde ograniczenie dostaje wpis w rejestrze — decyzja polityki, ograniczenie przyjęte przez człowieka w triage'u ręcznym (przyjęcie ryzyka albo odpowiedź „przestań łatać” na pytanie o podejście) i zapętlenie zamknięte zgodnie przez recenzenta i autora w rundzie 2 albo 3. Linia decyzji w notatkach zmiany dostaje numer wpisu. Decyzja ograniczenia bez warunku powrotu nie dostaje wpisu: idzie do człowieka jako eskalacja poza polityką. Sekcja ograniczeń w notatkach zmiany nie jest już pisana. Człowiek dostaje w rundzie najwyżej jedno pytanie: przy zapętleniu i E6 w rundzie 3 to jeden wpis.
  - Krok poprawek: najpierw blok zapętlenia, potem pytanie E6. Zgodny wybór ograniczenia przez recenzenta i autora daje decyzje ograniczenia i wpisy rejestru, bez poprawki i bez ponownego review z tego powodu. Commit dokumentów triage'u, który bierze plik lekcji, bierze też dziennik decyzji, gdy się zmienił.
  - „Co czytam”: dziennik decyzji tylko do dopisania wpisu ograniczenia.
- **Dlaczego:** ograniczenia leżały w notatkach zmian i nikt do nich nie wracał, gdy zaczynały mieć znaczenie; trzy zapętlenia z historii (hooki w etapie 2, etap 3, izolacja Codexa w 5a) skończyły się decyzją „przestań łatać, zapisz ograniczenie”, więc tę jedną decyzję można zostawić recenzentowi i autorowi (D-024, D-025, D-029). Dwie kopie kroków triage'u wymagały każdej poprawki w dwóch plikach (retrospektywa 8a, P1).
- **Zależności:** format wpisu ograniczenia w dzienniku decyzji (pola i kolejność jak w `skills/intent/references/principles-and-decisions.md`; pole `Zmiana:` to zmiana, która pisze wpis, bo warunek startu review commituje dziennik tylko z wpisami tej zmiany). Test `triage` z testów fabryki: prompt powstaje z sekcji `SKILL.md` między nagłówkami `### Triage sub-agent` i `### Recording the decisions` (nagłówków nie wolno zmienić), a parser odpowiedzi ignoruje nową linię z warunkiem powrotu. Kontrola `SHARED_SECTIONS` w `scripts/check_refs.py` pilnuje, że obie sekcje są takie same w obu skillach.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0; `diff <(awk '/^### Triage sub-agent/{f=1} f&&/^##+ /&&!/^### (Triage sub-agent|Recording the decisions)/{exit} f' skills/10x-impl-review/SKILL.md) <(awk '/^### Triage sub-agent/{f=1} f&&/^##+ /&&!/^### (Triage sub-agent|Recording the decisions)/{exit} f' skills/10x-plan-review/SKILL.md)` nic nie zwraca; `git diff 6227502..HEAD -- skills/10x-impl-review/references/triage-policy.md skills/10x-plan-review/references/triage-policy.md | grep -E '^[-+]- \*\*(E[1-6]|N[1-4]|L[1-3])\.'` nic nie zwraca; `grep -n 'Znane ograniczenia\|znanych ograniczeń\|round 3 has no E4 block' skills/10x-impl-review/SKILL.md skills/10x-plan-review/SKILL.md skills/10x-impl-review/references/triage-policy.md` nic nie zwraca.

## 10x-plan-review

- **Co zmienić:**
  - Polityka triage'u (ta sama kopia co w `10x-impl-review`) w tych samych trzech miejscach.
  - Sekcje agenta triage'u i zapisu decyzji: ten sam wspólny tekst co w `10x-impl-review`, z akapitem różnic na początku. W review planu zmianą pod review jest plan, wejściem jest też skrót planu, a diff istnieje tylko od rundy 2 i obejmuje plan oraz jego skrót.
  - Krok poprawek planu: ta sama kolejność co w `10x-impl-review` (najpierw blok zapętlenia, potem pytanie E6), ten sam zapis zgodnego wyboru ograniczenia i ta sama reguła commitu dziennika decyzji razem z dokumentami triage'u.
  - Triage ręczny: przyjęcie ryzyka i odpowiedź „przestań łatać” na pytanie o podejście dają wpis w rejestrze ograniczeń.
  - „Co czytam”: dziennik decyzji tylko do dopisania wpisu ograniczenia.
- **Dlaczego:** te same powody co w `10x-impl-review`; review planu dotąd przy przyjęciu ryzyka nie zapisywało ograniczenia nigdzie poza raportem.
- **Zależności:** te same co w `10x-impl-review`: format wpisu dziennika, kotwice sekcji testu `triage`, kontrola `SHARED_SECTIONS`.
- **Jak sprawdzić:** `diff skills/10x-impl-review/references/triage-policy.md skills/10x-plan-review/references/triage-policy.md` nic nie zwraca; `python3 -m unittest scripts.test_evallib scripts.test_eval_triage` przechodzi (prompt testu `triage` powstaje z obu skilli); polecenia z sekcji `10x-impl-review`.

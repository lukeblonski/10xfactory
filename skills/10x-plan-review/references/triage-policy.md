# Polityka triage'u uwag z review

Treść tej polityki to decyzja człowieka. Agent jej nie zmienia. Propozycję zmiany reguły zapisuje w Notes zmiany.

## Kolejność

Agent triage najpierw sprawdza bramkę, potem przy każdej uwadze zadaje pytania z sekcji „Pytania przy każdej uwadze”. Pierwsza pasująca reguła rozstrzyga.

## Bramka

Poprawka uwagi CRITICAL albo WARNING, która trafia na bramkę z sekcji „Kiedy pytać człowieka” w `CLAUDE.md`, idzie do człowieka (ESCALATE, reguła `bramka <n>` z numerem bramki). Poprawka w zakresie zgody z góry z `change.md` (ścieżki, płatne przebiegi) na tę bramkę nie trafia. Innego powodu pytania człowieka ta polityka nie ma.

## Pytania przy każdej uwadze

Przy każdej uwadze agent triage odpowiada na dwa pytania:

1. Czy to się zdarzy przy normalnym używaniu? Dowodem jest scenariusz człowieka, kryterium akceptacji albo zwykła ścieżka opisana w `change.md`.
2. Czy to atak z „Chroni przed”? Dowodem jest model zagrożenia w `change.md`.

Odpowiedzi dają jeden z trzech wyników:

- FIX z regułą `normalne używanie`: prawdziwy błąd albo złamane kryterium akceptacji, które zdarzą się przy normalnym używaniu. FIX z regułą `Chroni przed`: atak wymieniony w „Chroni przed”.
- LIMIT z regułą `przypadek szczególny`: przypadek szczególny albo wymyślony, którego nie ma w „Chroni przed”. Uwaga dostaje wpis w rejestrze z polem „Kiedy wrócić” i nie dostaje poprawki.
- SKIP z regułą `styl`: styl, nazwy, opis. Uwaga dostaje jedną linię w raporcie, bez poprawki i bez rejestru.

Waga nadana przez recenzenta nie zmienia wyniku tych pytań. Uwaga oznaczona jako CRITICAL, która dotyczy tylko przypadku wymyślonego spoza „Chroni przed”, idzie do rejestru.

## Waga

- `CRITICAL` — łamie kryterium akceptacji, test nie przechodzi, gubi dane albo jest dziurą w zabezpieczeniu w ramach modelu zagrożenia zmiany.
- `WARNING` — prawdziwy błąd w sytuacji, która zdarza się przy zwykłej pracy, bez złamanego kryterium.
- `OBSERVATION` — styl, nazwy, opis, przypadek hipotetyczny.

Waga opisuje uwagę i ustala kolejność w raporcie. O wyniku triage'u decydują pytania z poprzedniej sekcji.

Gdy zmiana nie opisuje modelu zagrożenia, przyjmij „przypadkowy błąd agenta, nie celowe obejście” i zapisz to założenie.

## Znany rodzaj błędu

Uwaga o znanym rodzaju błędu (np. wstrzyknięcie SQL, brak kontroli dostępu, niebezpieczna deserializacja) ma w raporcie źródło sposobu naprawy: OWASP Cheat Sheet Series, wpis CWE albo dokumentację narzędzia, podane nazwą i identyfikatorem, z jednym zdaniem o sposobie naprawy. Gdy taka uwaga dostaje FIX, naprawa idzie tym sposobem. Uwaga bez źródła idzie zwykłą drogą pytań, bez osobnej kontroli.

## Wpis w rejestrze

LIMIT nie ma poprawki. Uwaga dostaje wpis w rejestrze ograniczeń w `context/foundation/limitations.md`, z jednym zdaniem uzasadnienia i polem „Kiedy wrócić” (warunek, przy którym ograniczenie staje się ważne).

## Łączenie uwag

Uwagi o tym samym miejscu, np. błąd i brakujący test tuż przy nim, triage łączy w jedną poprawkę z jedną decyzją (D-012). Decyzję dostaje uwaga główna, a uwaga dołączona przejmuje ją bez osobnego rozstrzygania. Połączone uwagi mają jeden commit poprawki i najwyżej jedną eskalację.

## Wybór między opcjami A i B

Wybierz opcję zgodną z intencją i „Czego nie robimy”. Przy remisie wybierz mniejszą zmianę. Zalecenie ⭐ jest wskazówką, nie rozstrzygnięciem. Gdy jedna opcja łamie intencję, a druga „Czego nie robimy”, nie wybieraj: uwaga idzie do człowieka (bramka 1).

## Kto decyduje

Triage robi subagent w świeżym kontekście. Nie pisał kodu ani raportu. Czyta tylko raport, `change.md`, `plan.md`, `lessons.md`, politykę, diff zmiany i sekcję „Kiedy pytać człowieka” z `CLAUDE.md` fabryki (z `docs/zgoda-czlowieka.md` obok, gdy ocenia bramkę 2).

## Sprawdzenie zamknięcia

Po poprawkach przegląd kończy jedno sprawdzenie zamknięcia. Robi je subagent w świeżym kontekście, który nie pisał ani poprawek, ani raportu. Dostaje listę uwag z FIX i przy każdej zapisuje „załatwione” albo „niezałatwione” z dowodem. Uruchamia testy i sprawdza kryteria akceptacji, które dostarczają przeglądane fazy. Przy uwadze ze źródłem sprawdza, czy poprawka użyła sposobu ze źródła. Spraw spoza listy nie zgłasza.

Uwaga „niezałatwiona” dostaje jedną próbę naprawy. Po niej nowy subagent w świeżym kontekście sprawdza tylko te uwagi. Uwaga dalej niezałatwiona idzie do człowieka (ESCALATE, reguła `niezałatwione`) z dowodami ze sprawdzenia zamknięcia. Drugiego przeglądu nie ma.

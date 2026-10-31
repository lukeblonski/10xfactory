# Polityka triage'u uwag z review

Treść tej polityki to decyzja człowieka. Agent jej nie zmienia. Propozycję zmiany reguły zapisuje w Notes zmiany.

## Kolejność

Agent triage stosuje reguły w tej kolejności. Pierwsza pasująca reguła rozstrzyga.

## Eskalacja do człowieka (E)

- **E1.** Poprawka zmienia intencję, „Czego nie robimy” albo decyzję z góry zmiany.
- **E2.** Poprawka dotyczy kryteriów review, tej polityki, testów zachowania skilli, ustawień globalnych (`~/.claude`) albo upublicznienia czegokolwiek.
- **E3.** Poprawki nie da się łatwo cofnąć: usuwa dane, przepisuje historię git albo zmienia coś poza repo zmiany i jej projektem testowym.
- **E4.** Zapętlenie. Druga runda z rzędu znajduje nową formę tego samego problemu w tym samym mechanizmie albo poprawka z poprzedniej rundy wprowadziła regresję. Agent nie łata wtedy zapętlonego mechanizmu ani regresji. Uwagi w tym mechanizmie, regresje i każda poprawka, która dotyka plików zapętlonego mechanizmu, idą do jednego pytania o podejście na rundę (sekcja „Pytanie o podejście”). Pozostałe uwagi rozstrzyga normalnie.
- **E5.** Impact HIGH.
- **E6.** Trzecia runda review tej samej zmiany nadal ma uwagę CRITICAL albo WARNING do poprawy. Agent rozstrzyga wtedy uwagi tej rundy dalszymi regułami: poprawki są stosowane i sprawdzane poleceniami, ale ponownego review już nie ma. Runda daje jedno pytanie o podejście do człowieka.

## Napraw (N)

- **N1.** Uwaga CRITICAL.
- **N2.** Uwaga, przez którą nie jest spełnione kryterium akceptacji albo reguła z `lessons.md`.
- **N3.** Uwaga, która podważa cel zabezpieczenia (skryptu sprawdzającego, blokady) w ramach przyjętego modelu zagrożenia.

## Zapisz jako ograniczenie (L)

Bez poprawki. Wpis w rejestrze ograniczeń w `context/foundation/limitations.md`, z jednym zdaniem uzasadnienia i polem „Kiedy wrócić” (warunek, przy którym ograniczenie staje się ważne).

- **L1.** Uwaga dotyczy celowego obejścia albo przypadku spoza modelu zagrożenia. Gdy zmiana nie opisuje modelu zagrożenia, przyjmij „przypadkowy błąd agenta, nie celowe obejście” i zapisz to założenie. Obejście jest celowe tylko wtedy, gdy wymaga świadomego wysiłku, np. obejścia innej blokady. Formy, na które agent trafia przy zwykłej pracy (wielkość liter w nazwach plików, dowiązania), to przypadkowy błąd.
- **L2.** Problem dziś nie występuje, bo brakuje warunku, który by go wywołał, a poprawka nie jest trywialna.
- **L3.** Poprawka zmieniłaby działanie narzędzia spoza celu zmiany. Luka trafia wtedy dodatkowo do `lessons.md` jako reguła dla przyszłej zmiany.

## Napraw drobne (N4)

- **N4.** Pozostałe uwagi z Impact LOW, gdy poprawka mieści się w plikach tej zmiany.

## Pozostałe (L4)

- **L4.** Wszystko, czego nie objęła żadna reguła, zapisz jako ograniczenie w rejestrze (jak L1–L3) z adnotacją „poza polityką”. Retrospektywa sprawdzi, czy brakuje reguły.

## Pytanie o podejście

- Runda, w której pasuje E4 albo E6, daje człowiekowi najwyżej jedno pytanie o podejście. Uwagi tej rundy nie dostają osobnych wpisów do człowieka z reguł E4 ani E6.
- Pytanie wymienia objęte uwagi, co najmniej jedno inne podejście z zaletą i kosztem oraz wybór recenzenta.
- Zmiana podejścia zastępuje zapętlony mechanizm innym. Kolejna łata tego samego mechanizmu nie jest zmianą podejścia.
- Przy E4 recenzentem jest agent triage'u. Autorem jest drugi świeży agent: dostaje pytanie i opcje bez wyboru recenzenta i wybiera sam.
- Gdy recenzent i autor wybiorą to samo, nowe podejście jest stosowane jako poprawka objętych uwag bez pytania człowieka, a sprawdza je kolejna runda review.
- Człowiek dostaje pytanie, gdy recenzent i autor wybrali inaczej, gdy zmiana podejścia zmienia intencję albo kryteria akceptacji, gdy wymaga płatnego przebiegu albo wysyłki danych i gdy zapętlenie wypada w rundzie 3, poza wyjątkiem z następnego punktu. Przy E6 dostaje je zawsze.
- Pytanie, które obejmuje uwagę CRITICAL albo uwagę z Impact HIGH, człowiek dostaje zawsze, w rundzie 2 i 3, także gdy recenzent i autor wybrali to samo, również „przestań łatać, zapisz ograniczenie”. Zapętlenie na takiej uwadze znaczy, że modele sobie z nią nie radzą, więc decyduje człowiek.
- Przy zapętleniu w rundzie 3 recenzent i autor mogą bez człowieka wybrać tylko „przestań łatać, zapisz ograniczenie”, i tylko gdy pytanie nie obejmuje uwagi CRITICAL ani uwagi z Impact HIGH. Uwagi zapętlenia dostają wtedy wpisy w rejestrze ograniczeń, a ponownego review nie ma. Każde inne podejście, które dodaje kod, i każda różnica wyborów recenzenta i autora idą do człowieka. Gdy runda ma też pytanie E6, uwagi zapętlenia, które idą do człowieka, dołączają do niego.

## Łączenie uwag

Uwagi o tym samym miejscu, np. błąd i brakujący test tuż przy nim, triage łączy w jedną poprawkę z jedną decyzją (D-012). Decyzję dostaje uwaga główna, a uwaga dołączona przejmuje ją bez osobnego rozstrzygania. Połączone uwagi mają jeden commit poprawki i najwyżej jedną eskalację.

## Wybór między opcjami A i B

Wybierz opcję zgodną z intencją i „Czego nie robimy”. Przy remisie wybierz mniejszą zmianę. Zalecenie ⭐ jest wskazówką, nie rozstrzygnięciem. Gdy jedna opcja łamie intencję, a druga „Czego nie robimy”, nie wybieraj, tylko eskaluj jak E1.

## Kto decyduje

Triage robi subagent w świeżym kontekście. Nie pisał kodu ani raportu. Czyta tylko raport, `change.md`, `plan.md`, `lessons.md`, politykę i diff zmiany.

## Ponowne review

Po poprawkach uwagi CRITICAL albo WARNING kolejne review robi subagent w świeżym kontekście. Obejmuje tylko commit z poprawkami i zapisuje następny numerowany raport. Liczba rund jest ograniczona regułą E6. Review nie zaczyna rundy 4.

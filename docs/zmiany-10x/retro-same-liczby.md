# Zmiany w skillach 10x — retro-same-liczby: archiwum bez retrospektywy

- **Źródło:** zmiana `retro-same-liczby` (decyzje człowieka 2026-11-04, D-492 i D-493 w `context/foundation/decisions.md`).
- **Cel zmiany:** po każdej zmianie zostają tylko jej liczby ze `scripts/pomiar.py`, liczone bez agenta. Retrospektywa jednej zmiany znika razem z drogą jej propozycji. Wnioski i poprawki fabryki powstają tylko z ręcznej analizy w poprzek zmian, którą obserwator robi z człowiekiem, i wchodzą jako zwykłe zmiany po decyzji człowieka.

**Wspólne zależności:**
- `scripts/pomiar.py` z kolumną Interwencje i `scripts/autopilot.py`, który na końcu przebiegu wypisuje linię `liczby zmiany <id>: …` z wierszem tej zmiany.
- `docs/zasady-budowy.md`, punkt 9 („Wnioski z analizy w poprzek zmian”).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** archiwum nie uruchamia już retrospektywy przed przeniesieniem folderu. Znika cała sekcja tego kroku (sprawdzenie, czy plik wyniku już jest, migawka stanu repo, wywołanie skilla, sprawdzenie nowych plików i osobny commit wyniku), wzmianka o tym pliku w części o tym, co skill czyta, linia o retrospektywie w potwierdzeniu i punkt o propozycjach w liście tego, czego skill nie robi. Z `allowed-tools` znika narzędzie `Skill`, którego używało tylko to wywołanie. Reszta archiwum (weryfikator, `validate_change.py`, przeniesienie, zamknięcie pozycji roadmapy) zostaje bez zmian, więc skill wraca do kształtu bliższego oryginałowi kursu.
- **Dlaczego:** retrospektywa patrzyła na jedną zmianę i proponowała drobne reguły z jednym plikiem docelowym. Przez 32 retrospektywy i 160 propozycji nie znalazła dużej przyczyny powtarzających się rund przeglądu; znalazła ją dopiero analiza w poprzek 40 zmian. Ocena skutku poprawek nie rozróżniała poprawek wprowadzonych razem. Liczby zmiany liczy skrypt, bez agenta.
- **Zależności:** linia `liczby zmiany` na końcu przebiegu autopilota zastępuje listę propozycji; test łańcucha (`scripts/eval_chain.sh`, przypadek `chain-traces`) wymaga tej linii zamiast pliku retrospektywy.
- **Jak sprawdzić:** `grep -niE 'retro' skills/10x-archive/SKILL.md` nic nie znajduje; po archiwum zmiany jej folder w `context/archive/` nie ma pliku retrospektywy, a ostatnie wywołanie autopilota wypisuje linię zaczynającą się od `liczby zmiany`.

## 10x-plan-review

- **Co zmienić:** dwa miejsca, które odsyłały do retrospektywy, odsyłają do analizy w poprzek zmian: opis pola „Kiedy wrócić” wpisu w rejestrze ograniczeń (kto rozpozna warunek powrotu w śladach zmiany) i domyślna wartość pola „Możliwa reguła” we wpisie interwencji. Nic innego się nie zmienia.
- **Dlaczego:** retrospektywa jednej zmiany już nie istnieje; warunki powrotu z rejestru i reguły interwencji sprawdza teraz analiza w poprzek zmian.
- **Zależności:** `scripts/check_refs.py` porównuje wspólną część obu skilli przeglądu, więc zmiana jest identyczna w `10x-impl-review`.
- **Jak sprawdzić:** `grep -niE 'retrospe' skills/10x-plan-review/SKILL.md` nic nie znajduje; `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-impl-review

- **Co zmienić:** to samo co w `10x-plan-review`, w tych samych dwóch miejscach i tym samym brzmieniem.
- **Dlaczego:** jak wyżej.
- **Zależności:** jak w `10x-plan-review`.
- **Jak sprawdzić:** `grep -niE 'retrospe' skills/10x-impl-review/SKILL.md` nic nie znajduje; `python3 scripts/check_refs.py` kończy się kodem 0.

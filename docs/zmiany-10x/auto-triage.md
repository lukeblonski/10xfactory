# Zmiany w skillach 10x — auto-triage: automatyczny triage uwag z review

- **Zakres:** gałąź `auto-triage` od `d7dfb09` (prompt zmiany na `master`) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only d7dfb09 auto-triage -- 'skills/10x-*'`. Wynik: `10x-impl-review` i `10x-plan-review`.
- **Cel zmiany:** po review uwagi rozstrzyga osobny agent według spisanej polityki, bez pytania człowieka. Człowiek dostaje pytanie tylko w przypadkach z listy eskalacji, a ręczny triage zostaje jako wyjście awaryjne.

**Wspólne zależności:**
- Plik polityki `references/triage-policy.md` z repo fabryka. Ten sam plik leży w obu skillach. Oryginał jest w `10x-impl-review`, a kopia w `10x-plan-review`.
- `scripts/check_refs.py` i `scripts/test_check_refs.py` z repo fabryka. Skrypt pilnuje, żeby obie kopie polityki były identyczne bajt po bajcie, tak jak kopie `progress-format.md`.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:**
  - Na początku dodać krótki punkt „Co czytam”. Zawsze: plan, `change.md`, `lessons.md` i diff zakresu review. Tylko w razie potrzeby: zapisany raport, raport bieżącej rundy przy zapisie decyzji AUTO, politykę (czyta ją wyłącznie agent triage'u) i raport poprzedniej rundy (czyta go wyłącznie agent ponownego review). Nigdy: archiwum zmian ani polityki w głównej sesji.
  - Do listy dozwolonych narzędzi w nagłówku dopisać edycję i zapis plików, bo poprawki mają przechodzić bez pytania o uprawnienia.
  - Raport nigdy nie nadpisuje poprzedniego. Kolejne raporty tej samej serii dostają numer: bez numeru, potem `-2`, `-3`. Raport fazy ma osobną serię. Numer pliku nie jest numerem rundy. Review uruchomione przez człowieka to zawsze runda 1. Rundą drugą i dalszą jest tylko raport ponownego review poprawek. Ma w nagłówku linię `Round` ze wskazaniem poprzedniego raportu, a w zakresie sam commit z poprawkami. Triage bierze numer rundy z tej linii.
  - Przed zapisem raportu pierwszej rundy zrobić osobny commit folderu zmiany, jeśli coś w nim jest nowe albo zmienione. Potem sprawdzić, czy drzewo robocze jest czyste. Wynik decyduje o kroku poprawek.
  - Pytanie „co dalej” po zapisaniu raportu zastąpić krokiem automatycznego triage'u. Sesja uruchamia jednego świeżego subagenta. Podaje mu tylko ścieżki: raport, `change.md`, plan, `lessons.md`, politykę, polecenie diffu i numer rundy. Subagent stosuje reguły po kolei, nic nie zapisuje i zwraca dla każdej uwagi jedną linię `AUTO-FIX`, `AUTO-LIMIT` albo `AUTO-ESCALATE` z regułą i powodem. Przy eskalacji dodaje opcje i rekomendację, a przy zapętleniu co najmniej jedno inne podejście. Gdy w rundzie zadziała reguła limitu rund, każda poprawka tej rundy zamienia się w eskalację. Przy regule zapętlenia eskalują tylko uwagi w zapętlonym mechanizmie, regresje i poprawki jego plików.
  - Sesja przepisuje decyzje bez oceniania ich na nowo:
    - do pola `Decision` w raporcie;
    - do sekcji `## Decyzje triage` w `change.md`, z tytułem, oceną i miejscem uwagi. Każdy wpis trafia na koniec swojej sekcji, nie na koniec pliku;
    - ograniczenia do `### Znane ograniczenia` w Notes;
    - eskalacje do `## Wymaga Twojej decyzji`.

    Reguła L3 dodatkowo dopisuje wpis w `lessons.md`.
  - Dodać krok poprawek:
    - przy brudnym drzewie na starcie niczego nie poprawia. Każda poprawka tej rundy zamienia się w eskalację, a commit obejmuje tylko raport;
    - przy limicie rund niczego nie poprawia, a w trzeciej rundzie każda poprawka zamienia się w eskalację, także drobna. Przy zapętleniu poprawia resztę i kończy bez ponownego review;
    - w przeciwnym razie wprowadza poprawki AUTO-FIX i uruchamia automatyczne kryteria planu. Blokuje tylko kryterium, które przed poprawkami przechodziło, a po nich nie. Wtedy cofa poprawki tej rundy, zamienia ich decyzje w eskalacje, żeby ręczny triage je zobaczył, i się zatrzymuje;
    - po zielonych kryteriach robi dwa commity z nazwanymi plikami: najpierw poprawki, potem dokumenty.

    Gdy poprawiono choć jedną uwagę CRITICAL albo WARNING, świeży subagent robi review samego commitu poprawek. Ocenia tylko zmienione fragmenty, bez porównania z całym planem i bez zmiany statusu w `change.md`, ale z zakresem faz i listą tego, czego zmiana nie robi, robi to bez własnych subagentów, wskazuje regresje i powtórzenia z poprzedniej rundy i zapisuje kolejny raport bez triage'u. Potem znów idzie triage. Czwartej rundy nie ma nigdy, nawet gdy triage przeoczy limit. Na końcu skill wypisuje podsumowanie rund i to, co czeka na człowieka, razem z komendą ręcznego triage'u.
  - Ręczny triage (wywołanie z zapisanym raportem) bierze uwagi bez decyzji i eskalacje, a potem pyta, czy przejrzeć pozostałe decyzje AUTO. Pytanie o uwagę pokazuje decyzję AUTO. Decyzja człowieka inna niż AUTO dostaje dopisek z poprzednią wartością. Rozstrzygnięta eskalacja znika z listy. Na koniec sesji powstaje jeden wpis w `## Interwencje` w `change.md`: co się zmieniło, dlaczego, co zrobiłaby fabryka i jaka reguła mogłaby to zastąpić.
- **Dlaczego:** triage wymagał decyzji człowieka przy każdej uwadze, choć w trzech zmianach ponad 70 decyzji szło według tych samych reguł. Bez tego fabryka nie pracuje bez nadzoru, a samo zalecenie recenzenta bywało sprzeczne z intencją.
- **Zależności:** `references/triage-policy.md` w folderze skilla. Narzędzie do uruchamiania subagentów. Brak innych skilli fabryki.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0, a po dopisaniu znaku do jednej kopii polityki kodem 1. Po review zmiany w `change.md` jest sekcja `## Decyzje triage`, a każde pole `Decision` zaczyna się od `AUTO-`. `/10x-impl-review <raport>` prowadzi przez pytania i zapisuje zmianę decyzji w `## Interwencje`.

## 10x-plan-review

- **Co zmienić:**
  - Dodać punkt „Co czytam” jak wyżej. Zawsze czyta plan, `plan-brief.md`, `change.md`, `lessons.md` i format Progress. Plik powierzchni kontraktowych tylko wtedy, gdy istnieje.
  - Do nagłówka dodać tę samą listę dozwolonych narzędzi co w `10x-impl-review`, bo skill poprawia plan i robi commity bez nadzoru.
  - Warunek startu jak wyżej, z commitem folderu zmiany.
  - Raport zapisywać zawsze, przed triage'em, pod kolejnym numerem serii, i nie pytać o sposób dalszej pracy. Odesłanie przy wznowieniu ma prowadzić do kroku ręcznego triage'u, bo dziś wskazuje zły numer kroku.
  - Dodać ten sam automatyczny triage co w `10x-impl-review`. W pierwszej rundzie zmianą do oceny jest sam plan, a w kolejnych diff planu z commitu poprawek. Poprawki to zmiany w planie, a w briefie tylko tam, gdzie przestał się z planem zgadzać. Gdy poprawka dodaje kryterium, dopisuje też jego wiersz w Progress pod kolejnym wolnym numerem. Gdy zmienia znaczenie istniejącego kryterium, dodaje notkę w fazie i nie zmienia tytułu w Progress. Stanu istniejących wierszy nie zmienia. Zamiast automatycznych kryteriów po poprawkach sprawdzana jest spójność sekcji Progress z fazami, z tą samą zasadą blokady i cofania. Commity, ponowne review i podsumowanie działają jak wyżej.
  - Następna komenda wynika z werdyktu ostatniej rundy. Dopóki w `change.md` czekają eskalacje, następną komendą jest ręczny triage ostatniego raportu.
  - Ręczny triage jak w `10x-impl-review`, z dotychczasowymi opcjami tego skilla.
- **Dlaczego:** ten sam powód co wyżej. Uwagi do planu rozstrzygał dotąd człowiek albo agent bez spisanych reguł.
- **Zależności:** jak w `10x-impl-review`.
- **Jak sprawdzić:** po review planu jest raport z polami `AUTO-` i sekcja `## Decyzje triage` w `change.md`. Przy eskalacji skill podaje `/10x-plan-review <raport>` zamiast komendy implementacji.

# Zmiany w skillach 10x — poprawka P1 z retrospektywy etap-8d-retro-pr: odwołanie do pliku z późniejszej fazy

- **Źródło:** propozycja P1 retrospektywy `context/changes/etap-8d-retro-pr/` (dowód: uwaga `F1` z przeglądu planu i odchylenie `PC1` w planie).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-plan

- **Co zmienić:** w sekcji o kryteriach sukcesu faz, zaraz po akapicie o kryteriach unieważnianych przez późniejszą fazę, dopisać regułę w drugą stronę. Faza nie umieszcza ścieżki pliku, który powstaje dopiero w późniejszej fazie, w miejscu czytanym przez sprawdzenie istnienia pliku (np. lista sprawdzana przez `ls` albo odwołanie `scripts/…` w `skills/` sprawdzane przez `scripts/check_refs.py`). Takie odwołanie dodaje dopiero faza, w której plik powstaje.
- **Dlaczego:** w etapie 8d lista ścieżek z fazy 2 wymieniała dwa skrypty tworzone dopiero w fazie 3, przez co kryterium fazy 2 nie mogło przejść (krytyczna uwaga z przeglądu planu). Z tego samego powodu plik z fazy 2 odwołujący się do skryptu z fazy 3 wymagał decyzji człowieka w trakcie implementacji. Dotychczasowy akapit opisywał tylko odwrotny kierunek.
- **Zależności:** brak własnych plików. Przykład w regule wymienia `scripts/check_refs.py` fabryki; w repo bez tego skryptu reguła dotyczy innych sprawdzeń istnienia.
- **Jak sprawdzić:** `awk '/^## Success Criteria Guidelines/,/^## Common Patterns/' skills/10x-plan/SKILL.md | grep -n 'check_refs.py'` pokazuje nowy akapit, a `python3 scripts/check_refs.py` przechodzi.

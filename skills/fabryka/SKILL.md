---
name: fabryka
description: >
  Start projektu aplikacji fabryką w pustym folderze: przygotowanie repo ze znacznikiem .fabryka,
  pytania-bramki, kształtowanie /10x-shape w rozmowie, kroki bez rozmowy w trybie startu autopilota, posiedzenie akceptacji
  PRD, technologii i infrastruktury i lista końcowa z roadmapą. Prowadzi według instrukcji startu
  fabryki, bez pytania „fabryką czy zwyczajnie?”. W folderze z kodem bez znacznika tylko odpowiada,
  że przejęcie istniejącego projektu przyjdzie w osobnej zmianie. Trigger phrases: "/fabryka",
  "zacznij projekt fabryką", "start projektu fabryką".
argument-hint: "[opis aplikacji]"
---

# fabryka — start projektu aplikacji fabryką

`/fabryka [opis aplikacji]` to wejście do startu projektu wprost, bez pytania, które w pustym folderze zadaje hook startu sesji. Cała treść startu jest w jednej instrukcji fabryki, `<fabryka>/docs/start-projektu.md`; to polecenie wybiera tylko, od którego miejsca tej instrukcji sesja zaczyna, albo odmawia. `<fabryka>` to folder fabryki, którego pełną ścieżkę podaje hook startu sesji.

## Co czytam

- **Zawsze:** listę plików bieżącego folderu (`ls -A`), nic więcej przed wyborem przypadku.
- **Tylko w przypadku pustego folderu albo folderu ze znacznikiem:** `<fabryka>/docs/start-projektu.md` w całości; w folderze ze znacznikiem także `context/foundation/start.md` (czy ma sekcję `## Lista końcowa`), a po starcie `<fabryka>/docs/sesja-glowna.md`.
- **Nigdy:** plików w folderze z kodem bez znacznika (tam polecenie tylko odpowiada) ani `context/archive/` repo fabryki.

## Trzy przypadki

Sesja ustala przypadek z listy plików bieżącego folderu:

1. **Pusty folder** (lista ma najwyżej `.git` i `.DS_Store`): start według `<fabryka>/docs/start-projektu.md`, od sekcji „Przygotowanie folderu”. Pytania „fabryką czy zwyczajnie?” nie ma, bo człowiek wybrał już, wpisując to polecenie. Opis aplikacji z argumentu, gdy jest, to początek opisu właściciela.
2. **Pliki bez `.fabryka`**: sesja odpowiada jednym krótkim akapitem, że przejęcie istniejącego projektu przez fabrykę przyjdzie w osobnej zmianie, a do tego czasu ten folder zostaje zwykłym projektem Claude Code. Nie tworzy, nie zmienia i nie usuwa żadnego pliku, nie uruchamia `git` ani autopilota.
3. **Folder ze znacznikiem `.fabryka`**: gdy `context/foundation/start.md` nie ma sekcji `## Lista końcowa`, sesja prowadzi start dalej według `<fabryka>/docs/start-projektu.md`, od miejsca, które pokazują `start.md` i plik stanu `.autopilot-local/start-projektu/stan.json`. Gdy start ma już listę końcową, sesja działa według `<fabryka>/docs/sesja-glowna.md`.

Krok `claude -p` autopilota (zmienna `AUTOPILOT_KROK` w środowisku) nie wykonuje tego polecenia i nie uruchamia autopilota.

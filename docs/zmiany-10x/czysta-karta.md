# Zmiany w skillach 10x — czysta karta (etap 3 naprawy)

- **Źródło:** decyzja człowieka 2026-11-03 o czystej karcie reguł z retrospektyw (wpis w `context/foundation/decisions.md`).

## 10x-plan

- **Co zmienić:** w sekcji o kryteriach sukcesu usuń dwa akapity dopisane po retrospektywach: o kryterium, które późniejsza faza celowo unieważnia, i o ścieżce pliku, który powstaje dopiero w późniejszej fazie. Akapit o tym, czego nie stawiać jako wiersza ręcznego, zostaje.
- **Dlaczego:** czysta karta reguł z retrospektyw; zostają tylko zabezpieczenia i zasady człowieka.
- **Zależności:** brak.
- **Jak sprawdzić:** sekcja o kryteriach sukcesu nie mówi o późniejszych fazach.

## 10x-plan-review i 10x-impl-review

- **Co zmienić:** warunek startu przeglądu commituje tylko folder zmiany. Część o wpisach tej zmiany w `context/foundation/` znika.
- **Dlaczego:** czysta karta reguł z retrospektyw.
- **Zależności:** brak.
- **Jak sprawdzić:** warunek startu w obu skillach nie wymienia `context/foundation/`.

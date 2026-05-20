# Przeglad bezpieczenstwa aplikacji BudgetBuddy - stan na 2026-05-20

## 1. Osoba odpowiedzialna

Oskar Wojcicki - Security Engineer

## 2. Cel przegladu

Celem przegladu bylo sprawdzenie, czy obecna wersja aplikacji posiada podstawowe zabezpieczenia odpowiednie dla lokalnie uruchamianego systemu webowego rozwijanego w ramach projektu zespolowego oraz jakie ryzyka nalezy jeszcze uwzglednic przed finalizacja projektu.

## 3. Zakres sprawdzenia

W ramach przegladu przeanalizowano:

- sposob przechowywania hasel,
- obsluge sesji uzytkownika,
- walidacje danych formularzy,
- dostep do danych tylko w zakresie zalogowanego uzytkownika,
- bezpieczenstwo operacji na transakcjach,
- sposob prezentowania danych wpisywanych przez uzytkownika,
- naglowki odpowiedzi HTTP istotne dla bezpieczenstwa.

## 4. Zabezpieczenia obecne w aplikacji

Na obecnym etapie aplikacja wykorzystuje:

- haszowanie hasel przy pomocy `SHA-256`,
- mechanizm sesji oparty o identyfikator sesji i `HttpOnly cookie`,
- walidacje loginu i hasla przy rejestracji,
- walidacje danych budzetu i transakcji,
- ograniczenie dostepu do panelu tylko dla zalogowanego uzytkownika,
- ograniczenie edycji i usuwania transakcji tylko do danych nalezacych do aktualnego uzytkownika.

## 5. Zabezpieczenia dopracowane w tym etapie

W tym etapie dodatkowo wdrozono:

- escapowanie danych wyswietlanych w interfejsie, aby ograniczyc ryzyko wstrzykniecia kodu HTML lub JavaScript przez pola takie jak login, komunikaty i nazwy transakcji,
- dodanie `SameSite=Lax` do ciasteczka sesji,
- dodanie naglowka `X-Content-Type-Options: nosniff`,
- dodanie naglowka `X-Frame-Options: DENY`,
- dodanie naglowka `Referrer-Policy: same-origin`,
- dodanie polityki `Content-Security-Policy` ograniczajacej ladowanie zasobow do zaufanych zrodel,
- dodanie naglowkow `Cache-Control: no-store` oraz `Pragma: no-cache` dla odpowiedzi HTML.

## 6. Ryzyka ograniczone przez obecne zmiany

Wdrozone zmiany ograniczaja przede wszystkim:

- ryzyko wyswietlenia niebezpiecznego kodu pochodzacego z danych uzytkownika,
- ryzyko osadzenia aplikacji w obcej ramce,
- ryzyko niepozadanego zgadywania typu odpowiedzi przez przegladarke,
- ryzyko przechowywania wrazliwych danych panelu w pamieci podrecznej przegladarki,
- czesc ryzyk zwiazanych z przesylaniem ciasteczka sesji przy prostych przejsciach miedzy stronami.

## 7. Ograniczenia obecnej wersji bezpieczenstwa

Nalezy zaznaczyc, ze obecna wersja aplikacji nadal posiada ograniczenia typowe dla prostego lokalnego projektu:

- aplikacja nie korzysta jeszcze z HTTPS,
- nie wdrozono osobnych tokenow CSRF,
- mechanizm sesji jest prosty i przechowywany w pamieci procesu,
- hasla sa haszowane poprawnie, ale bez bardziej rozbudowanego podejscia z soleniem i dedykowanym algorytmem typu `bcrypt`,
- aplikacja nadal dziala na SQLite, a nie na docelowej bazie serwerowej.

## 8. Wnioski

Aktualny poziom bezpieczenstwa nalezy ocenic jako odpowiedni dla lokalnej, studenckiej wersji rozwijanej aplikacji, jednak nie jako poziom produkcyjny.

Najwazniejsze mocne strony obecnego stanu:

- poprawna izolacja danych pomiedzy uzytkownikami,
- rosnaca kontrola nad walidacja danych,
- swiadome wdrazanie podstawowych naglowkow bezpieczenstwa,
- stopniowe porzadkowanie sposobu obslugi sesji i prezentacji danych.

## 9. Co należy przed finalem projektu

Przed zakonczeniem projektu warto jeszcze:

- wykonac formalny przeglad scenariuszy testowych pod katem bezpieczenstwa,
- sprawdzic recznie, czy nie da sie edytowac lub usuwac cudzych transakcji po zmianie parametrow,
- utrzymac walidacje i izolacje danych przy kazdej kolejnej funkcji,
- opisac w dokumentacji, jakie elementy nalezaloby wdrozyc w wersji profesjonalnej systemu.

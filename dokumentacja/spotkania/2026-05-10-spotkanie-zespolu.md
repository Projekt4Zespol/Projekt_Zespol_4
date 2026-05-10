# Spotkanie zespolu - 2026-05-10

## 1. Informacje podstawowe

- Data spotkania: 2026-05-10
- Forma spotkania: spotkanie kontrolne i korygujace
- Prowadzaca spotkanie: Justyna Turowska

## 2. Uczestnicy

- Justyna Turowska
- Damian Wasiewicz
- Oskar Wojcicki
- Aniela Wrobel

## 3. Cel spotkania

Celem spotkania bylo uczciwe podsumowanie sytuacji projektowej po dniach 2026-05-08 i 2026-05-09, w ktorych zespol nie wykonal nowych prac implementacyjnych ani dokumentacyjnych, oraz ustalenie planu nadrobienia opoznienia.

## 4. Stan projektu przed spotkaniem

Na dzien 2026-05-10 projekt posiada:

- uporzadkowana dokumentacje organizacyjna,
- fundament backendu aplikacji,
- lokalna baze danych,
- podstawowy interfejs uzytkownika,
- podsumowanie etapu do 2026-05-07.

## 5. Uczciwe podsumowanie dni 2026-05-08 i 2026-05-09

Zespol stwierdzil, ze w dniach 2026-05-08 oraz 2026-05-09 nie zostaly wykonane nowe zadania projektowe. Nie pojawily sie:

- nowe commity,
- nowe elementy dokumentacji,
- nowe poprawki backendu,
- nowe poprawki frontendu,
- nowe testy.

## 6. Wplyw braku postepu

Brak prac w dwoch kolejnych dniach spowodowal:

- opoznienie wobec planu ustalonego 2026-05-07,
- brak realizacji doprecyzowanych zadan dla poszczegolnych osob,
- koniecznosc przesuniecia czesci planu na kolejne dni,
- ryzyko kumulacji zadan w kolejnych etapach.

## 7. Wnioski ze spotkania

1. Zbyt ogolny plan kolejnych zadan nie wystarczyl, aby utrzymac ciaglosc pracy.
2. Kazdy kolejny etap musi byc opisany nie tylko zadaniami, ale rowniez konkretnym wynikiem do oddania.
3. Po kazdym spotkaniu powinien powstac przynajmniej jeden commit statusowy lub techniczny tego samego dnia.
4. Opoznienie z 8 i 9 maja nalezy nadrobic w sposob kontrolowany, bez laczenia zbyt wielu odpowiedzialnosci w jednym commicie.

## 8. Decyzje podjete na spotkaniu

1. Dni 2026-05-08 i 2026-05-09 zostaja w dokumentacji oznaczone jako dni bez postepu.
2. Dzien 2026-05-10 ma rozpoczac etap nadrobienia opoznienia.
3. Do 2026-05-13 kazdy czlonek zespolu ma wykonac konkretny zakres prac przypisany do swojej roli.
4. Kolejne spotkanie kontrolne zostaje utrzymane na 2026-05-13.

## 9. Szczegolowy plan naprawczy do 2026-05-13

### 9.1 Damian Wasiewicz - Backend Developer / QA Engineer

Do wykonania:

- dopracowanie komunikatow backendowych po:
  - rejestracji,
  - logowaniu,
  - zapisaniu budzetu,
  - dodaniu transakcji,
- uporzadkowanie walidacji danych w formularzach,
- sprawdzenie calego przeplywu aplikacji w testach recznych.

### 9.2 Oskar Wojcicki - Frontend Developer / Security Engineer

Do wykonania:

- poprawa czytelnosci strony glownej,
- poprawa wygladu formularza rejestracji,
- poprawa wygladu formularza logowania,
- poprawa czytelnosci panelu uzytkownika,
- sprawdzenie, czy widoki wymagajace logowania sa poprawnie zabezpieczone.

### 9.3 Aniela Wrobel - DBA / Dokumentalista

Do wykonania:

- doprecyzowanie dokumentacyjnego opisu tabel,
- doprecyzowanie relacji miedzy danymi,
- kontrola spojnosci aktualnej bazy z logika backendu,
- uzupelnienie dokumentacji technicznej o stan warstwy danych po odbudowie projektu.

### 9.4 Justyna Turowska - Project Manager / Analityk systemowy

Do wykonania:

- aktualizacja statusu projektu po opoznieniu,
- przygotowanie bardziej szczegolowego planu kolejnych dni,
- wskazanie, ktore wymagania `Must` sa juz realnie gotowe,
- wskazanie, ktore elementy nadal sa na poziomie podstawowym.

## 10. Oczekiwany rezultat na 2026-05-13

Do kolejnego spotkania projekt ma:

- odzyskac regularnosc pracy,
- posiadac bardziej dopracowany backend podstawowych funkcji,
- posiadac czytelniejszy frontend podstawowych funkcji,
- posiadac bardziej szczegolowo opisana warstwe danych,
- posiadac dokumentacje, ktora wprost pokazuje opoznienie i sposob jego nadrobienia.

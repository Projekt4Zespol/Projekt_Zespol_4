# Spotkanie zespolu - 2026-05-07

## 1. Informacje podstawowe

- Data spotkania: 2026-05-07
- Forma spotkania: spotkanie kontrolne po pierwszym etapie odbudowy projektu
- Prowadzaca spotkanie: Justyna Turowska

## 2. Uczestnicy

- Justyna Turowska
- Damian Wasiewicz
- Oskar Wojcicki
- Aniela Wrobel

## 3. Cel spotkania

Celem spotkania bylo podsumowanie prac wykonanych po reorganizacji projektu oraz ustalenie bardzo konkretnego zakresu prac do kolejnego etapu, tak aby kazdy czlonek zespolu wiedzial, jakie elementy systemu ma rozwijac do dnia 2026-05-10.

## 4. Stan projektu na dzien spotkania

Na dzien 2026-05-07 projekt posiada:

- dzialajacy fundament backendu,
- lokalna baze danych,
- podstawowy interfejs z obsluga:
  - rejestracji,
  - logowania,
  - wylogowania,
  - ustawiania budzetu,
  - dodawania transakcji,
- uporzadkowana dokumentacje organizacyjna.

## 5. Zakres wykonany od 2026-05-04 do 2026-05-07

### 5.1 Czesci organizacyjne

- opisano reorganizacje projektu,
- opisano role zespolowe,
- opisano zasady pracy i commitowania,
- przygotowano plan sprintu kontrolnego.

### 5.2 Czesci techniczne

- wykonano techniczny reset poprzedniej implementacji,
- odtworzono backend podstawowych funkcji,
- utworzono baze danych SQLite,
- dodano podstawowe widoki i stylowanie frontendowe.

## 6. Wnioski po przegladzie aktualnej wersji

Zespol uznal, ze projekt odzyskal stabilny punkt wyjscia, ale obecna wersja nadal ma charakter podstawowy. Aplikacja dziala, lecz wymaga dalszego dopracowania, aby kolejny etap nie ograniczal sie jedynie do utrzymania obecnego stanu, ale przyniosl widoczny rozwoj funkcjonalny.

## 7. Problemy i ograniczenia

- obecny panel uzytkownika jest jeszcze prosty i wymaga doprecyzowania warstwy obslugi danych,
- lista transakcji prezentuje dane, ale nie pozwala jeszcze na zarzadzanie wpisami,
- dokumentacja statusowa musi zawierac wiecej szczegolow funkcjonalnych,
- kolejne zadania musza byc bardziej konkretne, aby uniknac zbyt ogolnego raportowania postepu.

## 8. Decyzje podjete na spotkaniu

1. Do kolejnego spotkania maja zostac przygotowane konkretne elementy rozwojowe aplikacji, a nie tylko ogolne poprawki.
2. W dokumentacji statusowej nalezy wskazywac:
   - jakie przyciski zostana dodane,
   - jakie formularze zostana rozszerzone,
   - jakie widoki beda zmieniane,
   - kto odpowiada za dana funkcje.
3. Kazdy czlonek zespolu ma do 2026-05-10 jasno przypisany zestaw zadan.

## 9. Szczegolowy plan do 2026-05-10

### 9.1 Damian Wasiewicz - Backend Developer / QA Engineer

Damian ma przygotowac:

- walidacje dla formularza rejestracji:
  - minimalna dlugosc loginu,
  - minimalna dlugosc hasla,
  - blokade duplikatu loginu,
- walidacje dla formularza dodawania transakcji:
  - sprawdzenie poprawnosci kwoty,
  - sprawdzenie poprawnosci daty,
  - sprawdzenie poprawnosci typu transakcji,
- uporzadkowanie komunikatow zwracanych po:
  - rejestracji,
  - logowaniu,
  - zapisie budzetu,
  - dodaniu transakcji,
- test reczny calego przeplywu:
  - rejestracja,
  - logowanie,
  - ustawienie budzetu,
  - dodanie transakcji,
  - wylogowanie.

### 9.2 Oskar Wojcicki - Frontend Developer / Security Engineer

Oskar ma przygotowac:

- bardziej czytelny przycisk `Zaloz konto` na stronie glownej,
- bardziej czytelny przycisk `Zaloguj sie` na stronie glownej,
- uporzadkowanie formularza rejestracji:
  - lepszy uklad pol,
  - bardziej czytelny przycisk `Zarejestruj`,
- uporzadkowanie formularza logowania:
  - lepszy uklad pol,
  - bardziej czytelny przycisk `Zaloguj`,
- dopracowanie panelu uzytkownika:
  - lepszy wyglad sekcji budzetu,
  - lepszy wyglad formularza dodawania transakcji,
  - lepsza czytelnosc listy transakcji,
- przeglad bezpieczenstwa podstawowych widokow:
  - sprawdzenie, czy panel wymaga logowania,
  - sprawdzenie, czy wylogowanie usuwa dostep do panelu,
  - sprawdzenie, czy uzytkownik nie powinien widziec cudzych danych.

### 9.3 Aniela Wrobel - DBA / Dokumentalista

Aniela ma przygotowac:

- kontrole poprawnosci aktualnej struktury bazy danych,
- opis tabel:
  - users,
  - budgets,
  - transactions,
- opis relacji pomiedzy tabelami,
- aktualizacje dokumentacji technicznej o:
  - stan bazy,
  - cel tabel,
  - znaczenie warstwy danych dla backendu.

### 9.4 Justyna Turowska - Project Manager / Analityk systemowy

Justyna ma przygotowac:

- bardziej szczegolowy opis statusu projektu,
- bardziej szczegolowy plan na kolejny etap,
- kontrole zgodnosci funkcji z wymaganiami `Must`,
- liste elementow, ktore sa juz gotowe,
- liste elementow, ktore nadal wymagaja rozwoju.

## 10. Oczekiwany rezultat na 2026-05-10

Do kolejnego spotkania zespol oczekuje, ze projekt bedzie posiadal:

- bardziej dopracowane formularze,
- bardziej dopracowane komunikaty systemowe,
- stabilniejszy przeplyw uzytkownika,
- bardziej szczegolowo opisana baze danych,
- bardziej profesjonalna dokumentacje statusowa.

## 11. Nastepne spotkanie

- Data: 2026-05-10
- Cel: ocena, czy wykonane zostaly konkretne zadania przypisane kazdej osobie oraz czy projekt jest gotowy do wejscia w kolejny etap rozwojowy.

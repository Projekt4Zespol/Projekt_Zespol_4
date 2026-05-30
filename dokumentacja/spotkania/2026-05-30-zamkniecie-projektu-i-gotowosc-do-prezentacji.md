# Zamkniecie projektu i gotowosc do prezentacji - stan na 2026-05-30

## 1. Informacje podstawowe

- Data spotkania: 2026-05-30
- Forma spotkania: spotkanie zamykajace etap developerski
- Prowadzaca spotkanie: Justyna Turowska

## 2. Uczestnicy

- Justyna Turowska
- Damian Wasiewicz
- Oskar Wojcicki
- Aniela Wrobel

## 3. Cel spotkania

Celem spotkania bylo formalne zamkniecie prac nad projektem BudgetBuddy, potwierdzenie gotowosci aplikacji do prezentacji oraz spisanie finalnego zakresu funkcji, stanu technicznego i wnioskow koncowych.

## 4. Podsumowanie koncowego etapu prac

### 4.1 Backend i logika aplikacji - Damian Wasiewicz

W finalnym etapie wykonano i domknieto:
;[]
- podzial panelu na tematyczne widoki:
  - przeglad,
  - budzet,
  - transakcje,
  - raporty,
- raport miesieczny oparty na danych transakcyjnych,
- raport roczny oparty na danych transakcyjnych,
- eksport danych do plikow `CSV`:
  - transakcje,
  - historia budzetu,
  - podsumowanie finansowe,
- automatyczne uruchamianie najnowszej wersji aplikacji po wpisaniu `python app.py`,
- utrzymanie zgodnosci backendu z testami automatycznymi.

### 4.2 Frontend i warstwa prezentacyjna - Oskar Wojcicki

W finalnym etapie wykonano:

- powiekszenie i dopracowanie logotypu aplikacji,
- dodanie tematycznych zakladek / podstron wewnatrz panelu,
- zwiekszenie odstepow pomiedzy sekcjami,
- poprawienie czytelnosci kart i raportow,
- dopracowanie finalnego wygladu dashboardu,
- zmiane prezentacji wykresu kategorii na bardziej pokazowy wykres kolowy z legenda.

### 4.3 Warstwa danych i dokumentacja techniczna - Aniela Wrobel

W finalnym etapie potwierdzono i udokumentowano:

- finalny opis architektury i warstwy danych,
- przygotowanie tabeli `budget_history`,
- wdrozenie historii zmian budzetu,
- opis gotowosci modelu danych do eksportu i raportowania,
- opis stanu obecnego oraz kierunkow dalszej rozbudowy po oddaniu projektu.

### 4.4 Organizacja projektu i finalna kontrola - Justyna Turowska

W finalnym etapie wykonano:

- domkniecie harmonogramu zgodnie z terminem 2026-05-30,
- kontrola, aby ostatnie zmiany byly konkretne i uzasadnione,
- potwierdzenie gotowosci projektu do prezentacji,
- przygotowanie finalnego dokumentu zamykajacego etap realizacji.

## 5. Finalny zakres funkcji aplikacji

Na moment zamkniecia projektu aplikacja BudgetBuddy posiada:

- rejestracje uzytkownika,
- logowanie i wylogowanie,
- ustawianie budzetu miesiecznego,
- historie zmian budzetu,
- dodawanie transakcji,
- edycje transakcji,
- usuwanie transakcji,
- filtrowanie transakcji po kategorii i typie,
- sortowanie transakcji,
- dashboard z podsumowaniami finansowymi,
- sekcje analityczne,
- wykres udzialu kategorii w wydatkach,
- raport miesieczny,
- raport roczny,
- eksport danych do `CSV`,
- podstawowe zabezpieczenia i testy automatyczne.

## 6. Ocena gotowosci projektu

Zespol uznal, ze projekt jest gotowy do pokazania na prezentacji, poniewaz:

- aplikacja posiada wyraznie wiecej niz podstawowe MVP,
- najwazniejsze scenariusze dzialania sa zaimplementowane i przetestowane,
- interfejs zostal dopracowany pod odbior wizualny,
- dokumentacja techniczna i organizacyjna zostala domknieta,
- ostatnie dni przyniosly funkcje realnie zwiekszajace wartosc projektu:
  - historia budzetu,
  - eksport danych,
  - raporty okresowe,
  - podstrony panelu,
  - finalna wersja prezentacyjna dashboardu.

## 7. Ostateczne wnioski zespolu

1. Projekt zostal skutecznie uporzadkowany po poczatkowych problemach organizacyjnych.
2. Podzial odpowiedzialnosci pomiedzy role techniczne i organizacyjne zaczal dzialac realnie i byl widoczny w koncowej fazie prac.
3. Ostatni etap rozwoju znacząco podniosl jakosc projektu pod wzgledem funkcjonalnym i wizualnym.
4. Finalna wersja jest wystarczajaco rozbudowana, aby dobrze wypasc na prezentacji i pokazac logiczny rozwoj systemu.

## 8. Decyzje koncowe

1. Dnia 2026-05-30 development zostaje zamkniety.
2. Dopuszczalne sa juz tylko drobne czynnosci techniczne zwiazane z uruchomieniem aplikacji lub przygotowaniem pokazu.
3. Wszelkie dalsze rozbudowy nalezy traktowac jako etap po oddaniu projektu.

## 9. Zakres prezentacji

Na prezentacji nalezy pokazac przede wszystkim:

- strone startowa aplikacji,
- logowanie i przejscie do panelu,
- zakladki panelu,
- ustawienie i historie budzetu,
- dodawanie i edycje transakcji,
- filtrowanie listy transakcji,
- wykres i sekcje analityczne,
- raport miesieczny i raport roczny,
- eksport danych do `CSV`.

## 10. Stan koncowy

Na dzien 2026-05-30 projekt BudgetBuddy zostaje uznany za zakonczony na poziomie zespolowego projektu studenckiego i gotowy do finalnej prezentacji. :)

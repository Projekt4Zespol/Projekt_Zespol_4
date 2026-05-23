# Spotkanie zespolu, podsumowanie postepow oraz plan do 2026-05-25

## 1. Informacje podstawowe

- Data spotkania: 2026-05-22
- Forma spotkania: spotkanie kontrolne i planujace finalizacje projektu
- Prowadzaca spotkanie: Justyna Turowska

## 2. Uczestnicy

- Justyna Turowska
- Damian Wasiewicz
- Oskar Wojcicki
- Aniela Wrobel

## 3. Cel spotkania

Celem spotkania bylo podsumowanie etapu, w ktorym projekt zostal rozszerzony o funkcje zarzadzania transakcjami, analityke dashboardu, formalny przeglad bezpieczenstwa oraz etap QA, a takze ustalenie, jak doprowadzic projekt do finalnej wersji do dnia 2026-05-30 przy zachowaniu realnego harmonogramu.

## 4. Podsumowanie postepow od 2026-05-19 do 2026-05-22

### 4.1 Backend i logika aplikacji - Damian Wasiewicz

W obecnym etapie wykonano:

- dodanie mozliwosci edycji transakcji,
- utrzymanie funkcji usuwania transakcji,
- dalsza rozbudowe dashboardu o bardziej efektowne sekcje analityczne,
- utrzymanie dzialajacego filtrowania i sortowania transakcji,
- przygotowanie aplikacji pod bardziej dojrzala prezentacje danych finansowych.

### 4.2 Frontend i bezpieczenstwo - Oskar Wojcicki

W obecnym etapie wykonano:

- formalny przeglad bezpieczenstwa aplikacji,
- dodanie podstawowych naglowkow bezpieczenstwa HTTP,
- dopracowanie ochrony prezentowanych danych przez escapowanie tekstu,
- utrzymanie spojnosci wizualnej dashboardu po kolejnych rozbudowach funkcjonalnych.

### 4.3 QA i testowanie - Damian Wasiewicz

W obecnym etapie wykonano:

- przygotowanie formalnych scenariuszy testowych,
- dodanie testow automatycznych dla najwazniejszych funkcji aplikacji,
- uruchomienie testow obejmujacych:
  - rejestracje i logowanie,
  - zapis budzetu,
  - dodawanie transakcji,
  - filtrowanie i sortowanie,
  - edycje i usuwanie transakcji,
  - weryfikacje, ze uzytkownik nie usuwa cudzych wpisow.

### 4.4 Warstwa danych i dokumentacja techniczna - Aniela Wrobel

W obecnym etapie utrzymano:

- opis struktury danych i relacji,
- zgodnosc opisu bazy z aktualnym stanem aplikacji,
- gotowosc do dalszego rozbudowania dokumentacji technicznej pod final projektu.


### 4.5 Organizacja projektu - Justyna Turowska

W obecnym etapie wykonano:

- utrzymanie regularnych podsumowan i planow,
- doprecyzowanie terminu koncowego projektu na 2026-05-30,
- ustalenie, ze 2026-05-31 bedzie dniem prezentacji, a nie dalszego developmentu,
- przejscie od ogolnych planow do bardzo konkretnego etapu finalizacji.

## 5. Ocena aktualnego stanu projektu

Zespol uznal, ze projekt osiagnal dobry poziom rozwoju funkcjonalnego jak na obecny etap i nie jest juz jedynie prostym MVP.

Najwazniejsze atuty aktualnej wersji:

- aplikacja obsluguje juz podstawowe operacje finansowe,
- uzytkownik moze dodawac, edytowac i usuwac transakcje,
- dashboard zawiera podsumowania oraz elementy analityczne,
- wdrozone zostaly pierwsze formalne etapy bezpieczenstwa i testowania,
- projekt jest coraz lepiej przygotowany do pokazania na prezentacji.

## 6. Ryzyka i obszary wymagajace dopracowania

Na obecnym etapie nadal nalezy uwzglednic:

- brak eksportu danych, ktory moglby byc atrakcyjnym dodatkiem w finalnej wersji,
- brak bardziej formalnego dopiecia dokumentacji technicznej calego systemu,
- koniecznosc utrzymania stabilnosci aplikacji przy kolejnych rozbudowach,
- potrzebe finalnego dopracowania warstwy prezentacyjnej przed 2026-05-30.

## 7. Wnioski ze spotkania

1. Projekt rozwija sie szybciej i dojrzalej niz na poczatku reorganizacji.
2. Funkcje `Security` i `QA` zostaly wreszcie formalnie wydzielone i od teraz beda traktowane jako realne etapy projektu.
3. Ostatnia faza projektu musi laczyc:
   - domykanie funkcjonalnosci,
   - dopracowanie wizualne,
   - przygotowanie dokumentacji,
   - stabilizacje przed prezentacja.


## 8. Decyzje podjete na spotkaniu

1. Termin zamkniecia projektu zostaje potwierdzony na 2026-05-30.
2. Dzien 2026-05-31 zostaje przeznaczony na prezentacje gotowego projektu.
3. Do konca projektu nalezy jeszcze dopracowac:
   - dokumentacje techniczna i architekture danych,
   - ostatnie elementy wizualne dashboardu,
   - ewentualna funkcje eksportu danych lub dodatkowego raportowania,
   - koncowa kontrole stabilnosci i spojnosci systemu.

## 9. Plan do 2026-05-25

### 9.1 Damian Wasiewicz

Do wykonania:

- dalsze domykanie logiki aplikacji,
- rozwazenie funkcji eksportu danych lub kolejnego przydatnego rozszerzenia uzytkowego,
- utrzymanie zgodnosci zmian z testami automatycznymi.

### 9.2 Oskar Wojcicki

Do wykonania:

- dalsze dopracowanie dashboardu i prezentacji listy transakcji,
- poprawienie sposobu prezentacji akcji przy transakcjach,
- przygotowanie aplikacji do finalnego etapu pokazowego.

### 9.3 Aniela Wrobel

Do wykonania:

- przygotowanie rozbudowanego dokumentu technicznego warstwy danych,
- opis, jakie elementy modelu danych nalezaloby zmienic w wersji bardziej profesjonalnej,
- przygotowanie materialu do dokumentacji koncowej dotyczacego bazy danych, relacji i ograniczen obecnej architektury.

### 9.4 Justyna Turowska

Do wykonania:

- kontrola postepu wobec twardego terminu 2026-05-30,
- uporzadkowanie finalnego harmonogramu,
- przygotowanie dokumentu podsumowujacego ostatni etap przed zamknieciem projektu.

## 10. Plan finalizacji do 2026-05-30

### Etap 1 - 2026-05-23 do 2026-05-25

- dalsza rozbudowa funkcjonalna,
- dokumentacja warstwy danych,
- dopracowanie dashboardu.

### Etap 2 - 2026-05-26 do 2026-05-28

- dokumentacja techniczna i projektowa,
- poprawki po testach i przegladzie bezpieczenstwa,
- dopracowanie finalnego wygladu aplikacji.

### Etap 3 - 2026-05-29 do 2026-05-30

- zamkniecie developmentu,
- finalna kontrola jakosci,
- sprawdzenie gotowosci projektu do prezentacji.

## 11. Oczekiwany rezultat na 2026-05-25

Do kolejnego spotkania projekt powinien:

- byc jeszcze lepiej domkniety funkcjonalnie,
- miec mocniejszy wkład Anieli w dokumentacje techniczna i warstwe danych,
- byc blizej finalnej wersji prezentacyjnej,
- utrzymywac stabilnosc mimo szybkiego rozwoju.

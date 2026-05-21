# Scenariusze testowe i etap QA - stan na 2026-05-21

## 1. Osoba odpowiedzialna

Damian Wasiewicz - QA Engineer

## 2. Cel etapu

Celem etapu bylo formalne wydzielenie obszaru testowania w projekcie BudgetBuddy oraz przygotowanie realnych scenariuszy testowych obejmujacych glowne funkcje aplikacji.

## 3. Zakres objety testami

W obecnym etapie przetestowano lub objęto scenariuszami:

- rejestracje uzytkownika,
- logowanie uzytkownika,
- ustawianie budzetu,
- dodawanie transakcji,
- filtrowanie transakcji,
- sortowanie transakcji,
- edycje transakcji,
- usuwanie transakcji,
- ograniczenie dostepu do danych tak, aby uzytkownik nie mogl usuwac cudzych wpisow.

## 4. Przygotowane scenariusze testowe

### Scenariusz 1

Rejestracja, logowanie, ustawienie budzetu i dodanie pierwszej transakcji.

Oczekiwany rezultat:

- konto zostaje utworzone,
- logowanie konczy sie powodzeniem,
- budzet zapisuje sie poprawnie,
- transakcja pojawia sie na panelu.

### Scenariusz 2

Filtrowanie i sortowanie listy transakcji.

Oczekiwany rezultat:

- po wybraniu kategorii i typu uzytkownik widzi tylko pasujace wpisy,
- lista odpowiada wybranemu sposobowi sortowania.

### Scenariusz 3

Edycja i usuwanie transakcji oraz weryfikacja, czy inny uzytkownik nie moze usunac cudzej transakcji.

Oczekiwany rezultat:

- wlasciciel moze zaktualizowac swoj wpis,
- wlasciciel moze usunac swoj wpis,
- inny uzytkownik nie moze usunac obcej transakcji.

## 5. Forma realizacji

W ramach etapu przygotowano automatyczne testy w Pythonie uruchamiane lokalnie na tymczasowej bazie danych, bez ingerencji w glowna baze projektu.

## 6. Znaczenie dla projektu

Etap QA ma duze znaczenie, poniewaz:

- porzadkuje podejscie do testowania,
- potwierdza dzialanie najwazniejszych funkcji,
- zmniejsza ryzyko regresji przy dalszej rozbudowie systemu,
- wzmacnia wiarygodnosc projektu przed finalna prezentacja.

## 7. Wnioski

Na obecnym etapie aplikacja posiada juz wystarczajaco duzo funkcji, aby testowanie bylo osobnym i dobrze uzasadnionym obszarem pracy. Dalsze zmiany powinny byc nadal sprawdzane w sposob uporzadkowany, szczegolnie przy rozwoju dashboardu, analityki, eksportu danych i kolejnych operacji na transakcjach.

# Gotowosc warstwy danych do finalizacji i eksportu - stan na 2026-05-26

## 1. Osoba odpowiedzialna

Aniela Wrobel - DBA, Dokumentalista

## 2. Cel opracowania

Celem dokumentu jest ocena, czy obecna warstwa danych aplikacji BudgetBuddy jest gotowa do:

- koncowej fazy projektu,
- obslugi obecnych funkcji aplikacji,
- przygotowania eksportu danych,
- dalszego opisania w finalnej dokumentacji technicznej.

Dokument stanowi praktyczne dopelnienie poprzedniego opracowania o rozwoju modelu danych i skupia sie na tym, co zostalo juz osiagniete oraz co jeszcze nalezy dopilnowac przed oddaniem projektu.

## 3. Aktualny stan danych w projekcie

Na dzien 26.05.2026 aplikacja korzysta z lokalnej bazy `SQLite`, w ktorej wykorzystywane sa trzy glowne obszary danych:

- dane uzytkownikow,
- dane budzetowe,
- dane transakcyjne.

Obecny model pozwala na poprawna obsluge:

- rejestracji uzytkownika,
- logowania i identyfikacji wlasciciela danych,
- ustawienia miesiecznego limitu budzetowego,
- dodawania transakcji,
- edycji transakcji,
- usuwania transakcji,
- filtrowania i sortowania historii operacji,
- prezentowania podsumowan i analityki w dashboardzie.

Z punktu widzenia warstwy danych oznacza to, ze obecna struktura jest wystarczajaca dla finalnej wersji projektu studenckiego, ale jednoczesnie widoczne sa juz miejsca, w ktorych system moglby zostac rozbudowany po oddaniu projektu.

## 4. Ocena gotowosci tabel do finalnej wersji

### 4.1 Tabela `users`

Tabela `users` jest gotowa do finalnej wersji projektu, poniewaz:

- przechowuje podstawowe dane identyfikacyjne uzytkownika,
- pozwala przypisac rekordy budzetowe i transakcyjne do konkretnego wlasciciela,
- wspiera izolacje danych pomiedzy kontami.

Na obecnym etapie nie ma potrzeby rozbudowy tej tabeli o dodatkowe dane profilowe, poniewaz nie sa one wymagane przez glowne zalozenia projektu.

### 4.2 Tabela `budgets`

Tabela `budgets` jest wystarczajaca dla obecnej wersji systemu, poniewaz:

- przechowuje aktualny miesieczny limit budzetowy,
- laczy limit bezposrednio z uzytkownikiem,
- pozwala budowac podsumowania w dashboardzie.

Ograniczeniem pozostaje brak historii zmian budzetu. Do finalnej wersji oddawanej w ramach projektu nie jest to krytyczne, ale zostaje wskazane jako naturalny kierunek rozwoju.

### 4.3 Tabela `transactions`

Tabela `transactions` jest najwazniejszym elementem warstwy danych i na obecnym etapie wspiera juz wszystkie kluczowe funkcje biznesowe aplikacji:

- zapis tytulu operacji,
- zapis kwoty,
- zapis kategorii,
- zapis typu transakcji,
- zapis daty transakcji,
- przypisanie wpisu do wlasciciela,
- dalsza analize danych w dashboardzie.

Tabela jest rowniez wystarczajaca do przygotowania eksportu danych, poniewaz zawiera wszystkie podstawowe informacje potrzebne do stworzenia zestawienia historii finansowej.

## 5. Gotowosc pod eksport danych

### 5.1 Co juz wspiera eksport

Obecny model danych pozwala przygotowac eksport transakcji bez koniecznosci przebudowy bazy. Do eksportu mozna wykorzystac nastepujace pola:

- identyfikator transakcji,
- nazwe transakcji,
- typ transakcji,
- kategorie,
- kwote,
- date transakcji,
- date utworzenia wpisu.

W praktyce oznacza to, ze eksport do prostego formatu, np. `CSV`, jest mozliwy do wdrozenia na obecnym modelu danych.

### 5.2 Proponowany zakres eksportu

Najbardziej uzasadniony eksport w obecnej wersji projektu powinien obejmowac:

- liste transakcji uzytkownika,
- aktualny limit budzetowy,
- podstawowe podsumowanie finansowe.

Przykladowy logiczny uklad eksportu transakcji:

| Pole | Znaczenie |
| --- | --- |
| `title` | nazwa operacji |
| `transaction_type` | przychod lub wydatek |
| `category` | przypisana kategoria |
| `amount` | kwota |
| `transaction_date` | data operacji |
| `created_at` | data zapisu w systemie |

### 5.3 Ograniczenia eksportu

Obecny model danych nie przechowuje:

- historii zmian budzetu,
- wersjonowania rekordow,
- dodatkowych metadanych eksportowych,
- bardziej szczegolowych statusow transakcji.

Nie blokuje to jednak prostego i przydatnego eksportu danych w wersji finalnej projektu.

## 6. Gotowosc pod koncowa dokumentacje techniczna

Na ten moment warstwa danych jest wystarczajaco ustabilizowana, aby mozna bylo przygotowac finalna czesc dokumentacji obejmujaca:

- opis tabel,
- opis relacji,
- opis przechowywanych pol,
- opis roli kluczy i integralnosci danych,
- ograniczenia obecnej wersji,
- plan przejscia do bardziej profesjonalnej architektury.

Oznacza to, ze Aniela moze w kolejnych dniach skupic sie nie tylko na samym opisie struktury, ale rowniez na przygotowaniu dojrzalej, koncowej wersji dokumentacji technicznej.

## 7. Elementy wymagajace dopilnowania przed 30.05

Przed zamknieciem projektu nalezy dopilnowac nastepujacych kwestii:

- zgodnosci opisu modelu danych z aktualnym stanem aplikacji,
- zgodnosci dokumentacji z funkcjami takimi jak edycja i usuwanie transakcji,
- dopisania informacji o gotowosci modelu danych pod eksport,
- opisania ograniczen wynikajacych z wykorzystania `SQLite`,
- opisania planu przejscia na `PostgreSQL` jako rozwiazania docelowego.

## 8. Wnioski

Na dzien 26.05.2026 warstwa danych aplikacji BudgetBuddy jest gotowa do obslugi finalnej wersji projektu studenckiego i wspiera wszystkie najwazniejsze funkcje wdrozone w aplikacji.

Najwazniejsze wnioski sa nastepujace:

- obecny model danych jest wystarczajacy dla finalnej wersji oddawanej 30.05,
- baza danych wspiera nie tylko podstawowe funkcje, ale takze rozbudowany dashboard, analityke i zarzadzanie transakcjami,
- model danych mozna wykorzystac do prostego eksportu informacji bez koniecznosci przebudowy tabel,
- najwazniejszym zadaniem na dalszym etapie jest teraz dopracowanie finalnej dokumentacji technicznej oraz opisanie kierunku rozwoju do bardziej profesjonalnej wersji systemu.

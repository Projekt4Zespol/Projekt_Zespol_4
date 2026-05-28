# Finalna dokumentacja warstwy danych i architektury - stan na 2026-05-28

## 1. Osoba odpowiedzialna

Aniela Wrobel - DBA, Dokumentalista

## 2. Cel dokumentu

Celem dokumentu jest przygotowanie koncowego opisu technicznego warstwy danych oraz architektury aplikacji BudgetBuddy przed zamknieciem projektu dnia 30.05.2026.

Dokument porzadkuje:

- wykorzystywane technologie,
- podzial odpowiedzialnosci miedzy warstwami aplikacji,
- strukture bazy danych,
- sposob obslugi kluczowych funkcji,
- ograniczenia obecnej wersji,
- kierunki dalszej rozbudowy po oddaniu projektu.

## 3. Architektura obecnej wersji aplikacji

### 3.1 Model techniczny

Aplikacja BudgetBuddy zostala zrealizowana jako lekka aplikacja webowa uruchamiana lokalnie, bez wykorzystania zewnetrznego frameworka backendowego.

Obecna architektura sklada sie z nastepujacych warstw:

- warstwa logiki aplikacyjnej w `Python`,
- warstwa prezentacji generowana po stronie serwera,
- lokalna baza danych `SQLite`,
- statyczna warstwa stylow `CSS`.

### 3.2 Wykorzystane technologie

W projekcie wykorzystano:

- `Python` - glowny jezyk implementacji,
- `http.server` - obsluga prostego serwera HTTP,
- `sqlite3` - lokalna obsluga bazy danych,
- `HTML` generowany dynamicznie po stronie aplikacji,
- `CSS` - wyglad interfejsu,
- `unittest` - automatyczne testy funkcjonalne.

### 3.3 Uzasadnienie obecnej architektury

Na potrzeby projektu zespolowego przyjeto architekture prosta, mozliwa do szybkiego uruchomienia i rozwoju przez zespol pracujacy na jednym repozytorium.

Zalety takiego rozwiazania:

- szybkie wdrozenie wersji dzialajacej,
- niska zlozonosc srodowiska,
- latwe lokalne uruchamianie,
- czytelny podzial odpowiedzialnosci pomiedzy backend, baze danych, frontend i dokumentacje.

Ograniczenia:

- brak warstwy API rozdzielonej od widokow,
- brak frameworka klasy produkcyjnej,
- brak serwerowej bazy danych,
- ograniczona skalowalnosc i modularnosc.

## 4. Warstwa danych

### 4.1 Ogolna rola bazy danych

Warstwa danych odpowiada za:

- przechowywanie kont uzytkownikow,
- przechowywanie aktualnego limitu budzetowego,
- przechowywanie historii transakcji,
- wspieranie dashboardu i sekcji analitycznej,
- obsluge filtrowania, sortowania, edycji i usuwania transakcji.

### 4.2 Glówne encje

W obecnej wersji systemu wykorzystywane sa cztery podstawowe encje:

- `users`
- `budgets`
- `transactions`
- `budget_history`

### 4.3 Tabela `users`

Tabela `users` przechowuje informacje potrzebne do uwierzytelnienia oraz identyfikacji wlasciciela danych.

Najwazniejsze pola:

- `id` - klucz glowny,
- `username` - unikalna nazwa uzytkownika,
- `password_hash` - zahaszowane haslo,
- `created_at` - data utworzenia konta.

Rola w systemie:

- pozwala rozdzielic dane pomiedzy uzytkownikami,
- stanowi punkt odniesienia dla budzetow i transakcji,
- wspiera bezpieczna izolacje danych.

### 4.4 Tabela `budgets`

Tabela `budgets` przechowuje aktualny miesieczny limit budzetowy przypisany do konkretnego uzytkownika.

Najwazniejsze pola:

- `id` - klucz glowny,
- `user_id` - klucz obcy do tabeli `users`,
- `monthly_limit` - aktualna wartosc budzetu,
- `updated_at` - data ostatniej aktualizacji.

Rola w systemie:

- przechowuje wartosc limitu do dashboardu i analityki,
- pozwala obliczac stopien wykorzystania budzetu,
- stanowi podstawe do wyliczania pozostalego limitu.

### 4.5 Tabela `transactions`

Tabela `transactions` przechowuje operacje finansowe uzytkownika.

Najwazniejsze pola:

- `id` - klucz glowny,
- `user_id` - klucz obcy do tabeli `users`,
- `title` - nazwa transakcji,
- `amount` - wartosc operacji,
- `category` - kategoria przypisana do operacji,
- `transaction_type` - typ operacji (`income` lub `expense`),
- `transaction_date` - data operacji,
- `created_at` - data zapisu w systemie.

Rola w systemie:

- wspiera rejestrowanie przychodow i wydatkow,
- wspiera analityke dashboardu,
- wspiera operacje filtrowania i sortowania,
- wspiera edycje i usuwanie wpisow,
- stanowi podstawe do przygotowania eksportu danych.

### 4.6 Tabela `budget_history`

Tabela `budget_history` przechowuje historie zmian limitu budzetowego uzytkownika.

Najwazniejsze pola:

- `id` - klucz glowny,
- `user_id` - klucz obcy do tabeli `users`,
- `previous_limit` - poprzednia wartosc limitu,
- `new_limit` - nowa wartosc limitu,
- `changed_at` - data zapisania zmiany.

Rola w systemie:

- zapisuje kolejne zmiany budzetu miesiecznego,
- pozwala pokazac historie limitu w panelu,
- przygotowuje system pod eksport danych budzetowych,
- stanowi baze pod miesieczne i roczne raporty budzetowe.

## 5. Relacje miedzy danymi

Aktualny model relacji:

- jeden uzytkownik moze miec jeden aktywny rekord budzetowy,
- jeden uzytkownik moze miec wiele rekordow historii budzetu,
- jeden uzytkownik moze miec wiele transakcji,
- kazda transakcja nalezy do jednego uzytkownika.

Opis logiczny:

- `users` 1 --- 1 `budgets`
- `users` 1 --- n `budget_history`
- `users` 1 --- n `transactions`

Relacje te pozwalaja zachowac prostote modelu przy jednoczesnym wsparciu wszystkich funkcji wymaganych w projekcie.

## 6. Jak model danych wspiera aktualne funkcje aplikacji

### 6.1 Rejestracja i logowanie

Model danych wspiera rejestracje i logowanie poprzez:

- zapis unikalnego konta w tabeli `users`,
- bezpieczne przechowywanie hasha hasla,
- przypisanie wszystkich pozostalych danych do konkretnego uzytkownika.

### 6.2 Ustawianie budzetu

Budzet miesieczny jest przechowywany oddzielnie, co upraszcza:

- aktualizacje limitu,
- obliczenia dashboardu,
- prezentacje pozostalego budzetu.

Od obecnego etapu aplikacja zapisuje takze historie zmian budzetu w tabeli `budget_history`, dzieki czemu mozliwe jest odtworzenie poprzednich wartosci limitu.

### 6.3 Dodawanie, edycja i usuwanie transakcji

Tabela `transactions` zostala zaprojektowana tak, aby wspierac caly cykl pracy na wpisach:

- dodanie nowej pozycji,
- odczyt historii,
- edycje istniejacego wpisu,
- usuniecie wybranego wpisu.

### 6.4 Filtrowanie i sortowanie

Model danych pozwala filtrowac i sortowac transakcje po:

- kategorii,
- typie,
- dacie,
- kwocie.

### 6.5 Dashboard i analityka

Dane przechowywane w tabelach pozwalaja obliczac:

- sume przychodow,
- sume wydatkow,
- saldo,
- pozostaly limit budzetowy,
- strukture wydatkow wedlug kategorii,
- podstawowe wskazniki prezentowane w dashboardzie.

## 7. Bezpieczenstwo i integralnosc danych

Na obecnym etapie warstwa danych wspiera bezpieczenstwo systemu poprzez:

- przypisanie wszystkich rekordow do wlasciciela,
- ograniczenie operacji na danych do aktualnie zalogowanego uzytkownika,
- wykorzystanie hashowania hasel,
- podstawowa walidacje danych po stronie backendu.

Integralnosc danych zapewniaja:

- klucze glowne,
- klucze obce,
- logiczne powiazania pomiedzy tabelami,
- ograniczenie jednego aktywnego budzetu na uzytkownika.

## 8. Gotowosc do eksportu danych

Obecny model danych pozwala wdrozyc prosty eksport, w szczegolnosci:

- liste transakcji do `CSV`,
- zestawienie aktualnego budzetu,
- historie zmian budzetu,
- podstawowe dane do raportu koncowego.

Jest to mozliwe bez przebudowy tabel, poniewaz kluczowe informacje znajduja sie juz w strukturze `transactions` i `budgets`.

## 9. Ograniczenia obecnej architektury i warstwy danych

Mimo ze obecna wersja jest wystarczajaca do oddania projektu, nalezy odnotowac ograniczenia:

- brak osobnej tabeli kategorii,
- brak warstwy API,
- brak wykorzystania `PostgreSQL`,
- brak rozbudowanego modelu raportowania okresowego,
- ograniczona modularnosc wynikajaca z prostej architektury aplikacji.

## 10. Kierunki dalszej rozbudowy po oddaniu projektu

Po oddaniu projektu najbardziej uzasadnione kierunki rozwoju to:

- przejscie z `SQLite` na `PostgreSQL`,
- wydzielenie warstwy API,
- dodanie osobnej tabeli kategorii,
- rozbudowa eksportu danych,
- przygotowanie raportow miesiecznych i rocznych,
- dalsze uszczelnienie bezpieczenstwa i testow.

## 11. Wnioski koncowe

Na dzien 28.05.2026 warstwa danych oraz obecna architektura aplikacji BudgetBuddy sa wystarczajace do finalnego oddania projektu dnia 30.05.2026.

Najwazniejsze wnioski:

- obecna struktura danych wspiera wszystkie kluczowe funkcje wdrozone w aplikacji,
- architektura jest prosta, ale spojna i obronialna na potrzeby projektu zespolowego,
- model danych nadaje sie do opisania w dokumentacji koncowej bez koniecznosci dalszej przebudowy,
- projekt posiada czytelne kierunki dalszego rozwoju do wersji bardziej profesjonalnej.

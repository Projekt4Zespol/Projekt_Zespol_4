# Opis warstwy danych aplikacji BudgetBuddy - stan na 2026-05-13

## 1. Osoba odpowiedzialna

Aniela Wrobel - DBA

## 2. Cel dokumentu

Celem dokumentu jest techniczne opisanie obecnej warstwy danych aplikacji BudgetBuddy tak, aby zespol mial jasna podstawe do dalszego rozwoju backendu, dokumentacji oraz kolejnych sprintow.

## 3. Obecnie wykorzystywana technologia

Na aktualnym etapie projekt wykorzystuje lokalna baze danych SQLite zapisywana w pliku `budgetbuddy.db`.

Wybor tej technologii na obecnym etapie wynika z potrzeby szybkiego uruchomienia pierwszej dzialajacej wersji aplikacji oraz prostego testowania funkcji backendowych bez dodatkowej konfiguracji serwera bazodanowego.

## 4. Tabele wykorzystywane w projekcie

W obecnej wersji systemu wykorzystywane sa trzy glowne tabele:

- `users`
- `budgets`
- `transactions`

## 5. Opis tabel

### 5.1 Tabela `users`

Tabela `users` przechowuje dane potrzebne do identyfikacji i logowania uzytkownikow.

Pola:

- `id` - klucz glowny, identyfikator uzytkownika, typ `INTEGER`, wartosc nadawana automatycznie,
- `username` - nazwa uzytkownika, typ `TEXT`, pole wymagane, wartosc unikalna,
- `password_hash` - zahaszowane haslo uzytkownika, typ `TEXT`, pole wymagane,
- `created_at` - data utworzenia konta, typ `TEXT`, pole wymagane.

Rola tabeli:

- przechowywanie kont uzytkownikow,
- zapewnienie mozliwosci logowania,
- powiazanie uzytkownika z budzetem i transakcjami.

### 5.2 Tabela `budgets`

Tabela `budgets` przechowuje informacje o ustawionym limicie miesiecznym dla danego uzytkownika.

Pola:

- `id` - klucz glowny, identyfikator wpisu budzetowego, typ `INTEGER`, wartosc nadawana automatycznie,
- `user_id` - klucz obcy wskazujacy uzytkownika z tabeli `users`, typ `INTEGER`, pole wymagane, wartosc unikalna,
- `monthly_limit` - limit miesieczny ustawiony przez uzytkownika, typ `REAL`, pole wymagane,
- `updated_at` - data ostatniej aktualizacji budzetu, typ `TEXT`, pole wymagane.

Rola tabeli:

- przechowywanie aktualnego budzetu przypisanego do konkretnego uzytkownika,
- zapewnienie relacji jeden uzytkownik - jeden aktualny limit budzetowy.

### 5.3 Tabela `transactions`

Tabela `transactions` przechowuje informacje o operacjach finansowych dodanych przez uzytkownika.

Pola:

- `id` - klucz glowny, identyfikator transakcji, typ `INTEGER`, wartosc nadawana automatycznie,
- `user_id` - klucz obcy wskazujacy uzytkownika z tabeli `users`, typ `INTEGER`, pole wymagane,
- `title` - nazwa transakcji, typ `TEXT`, pole wymagane,
- `amount` - kwota transakcji, typ `REAL`, pole wymagane,
- `category` - kategoria transakcji, typ `TEXT`, pole wymagane,
- `transaction_type` - typ transakcji, typ `TEXT`, pole wymagane,
- `transaction_date` - data transakcji, typ `TEXT`, pole wymagane,
- `created_at` - data dodania wpisu do systemu, typ `TEXT`, pole wymagane.

Rola tabeli:

- przechowywanie historii przychodow i wydatkow uzytkownika,
- dostarczanie danych do podsumowan na panelu uzytkownika,
- umozliwienie dalszej rozbudowy o filtrowanie, edycje i raportowanie.

## 6. Relacje pomiedzy tabelami

Obecne relacje w systemie sa nastepujace:

- `users` -> `budgets`
- `users` -> `transactions`

Opis relacji:

- jeden uzytkownik moze miec jeden aktualny wpis budzetowy,
- jeden uzytkownik moze miec wiele transakcji,
- kazdy wpis budzetowy musi nalezec do jednego konkretnego uzytkownika,
- kazda transakcja musi nalezec do jednego konkretnego uzytkownika.

## 7. Zasady integralnosci danych

W obecnej wersji systemu zachowane sa nastepujace zasady:

- kazdy uzytkownik posiada unikalny login,
- tabela `budgets` pozwala tylko na jeden aktualny budzet dla jednego uzytkownika,
- transakcje i budzety sa laczone z kontem uzytkownika przez `user_id`,
- dane wymagane przez aplikacje sa oznaczone jako `NOT NULL`.

## 8. Wsparcie logiki aplikacji przez warstwe danych

Obecna struktura danych wspiera nastepujace funkcje:

- rejestracje uzytkownika,
- logowanie uzytkownika,
- ustawienie lub aktualizacje limitu budzetowego,
- dodawanie transakcji,
- pobieranie historii transakcji dla zalogowanego uzytkownika,
- wyliczanie podstawowych podsumowan na panelu.

## 9. Ograniczenia obecnej wersji warstwy danych

Na tym etapie warstwa danych posiada jeszcze ograniczenia, ktore beda rozwijane w kolejnych sprintach:

- brak osobnej tabeli kategorii,
- brak tabeli historii zmian budzetu,
- brak relacji przygotowanych pod rozbudowany system raportowania,
- brak mechanizmu migracji charakterystycznego dla bardziej rozbudowanych frameworkow,
- wykorzystanie SQLite zamiast docelowej bazy PostgreSQL.

## 10. Kierunek dalszego rozwoju

W kolejnych etapach zalecane jest:

- przygotowanie bardziej formalnego modelu danych,
- wydzielenie kategorii do osobnej tabeli,
- przygotowanie struktury pod edycje i usuwanie transakcji,
- rozwazenie przejscia na PostgreSQL zgodnie z pierwotnymi zalozeniami projektu,
- dopracowanie dokumentacji technicznej o diagram relacji i dokladniejszy opis przeplywu danych.

## 11. Znaczenie dokumentu dla kolejnych sprintow

Dokument porzadkuje obecny stan warstwy danych i stanowi punkt odniesienia dla:

- dalszej rozbudowy backendu,
- przygotowania kolejnych zmian bazodanowych,
- dokumentacji projektowej,
- kontroli zgodnosci implementacji z zalozeniami systemu.

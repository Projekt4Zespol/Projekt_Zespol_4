# Podsumowanie etapu 2026-05-04 do 2026-05-07 oraz szczegolowy plan do 2026-05-10

## 1. Charakter etapu

Etap od 2026-05-04 do 2026-05-07 mial charakter reorganizacyjny i odbudowujacy. Jego zadaniem bylo uporzadkowanie projektu oraz przywrocenie wersji aplikacji, ktora mogla zostac dalej rozwijana zgodnie z odpowiedzialnosciami zespolowymi.

## 2. Co zostalo wykonane

### 2.1 Dokumentacja i organizacja

Wykonano:

- dokument reorganizacji projektu,
- dokument rol zespolowych,
- dokument zasad pracy,
- dokument planu sprintu kontrolnego,
- dokument spotkania z dnia 2026-05-04.

### 2.2 Backend

Przygotowano:

- obsluge rejestracji uzytkownika,
- obsluge logowania i wylogowania,
- obsluge ustawiania budzetu,
- obsluge dodawania transakcji,
- prosty panel uzytkownika.

### 2.3 Baza danych

Przygotowano:

- lokalna baze SQLite,
- tabele dla:
  - users,
  - budgets,
  - transactions,
- podstawowy opis stanu warstwy danych.

### 2.4 Frontend

Przygotowano:

- podstawowy widok strony glownej,
- formularz rejestracji,
- formularz logowania,
- panel uzytkownika,
- podstawowe stylowanie aplikacji.

## 3. Co dokladnie ma zostac rozwinięte do 2026-05-10

### 3.1 Zakres backendowy - Damian

Do realizacji:

- dodanie bardziej precyzyjnych komunikatow po akcjach systemowych,
- dopracowanie walidacji formularza rejestracji,
- dopracowanie walidacji formularza transakcji,
- sprawdzenie poprawnosci przeplywu logowania i wylogowania,
- sprawdzenie poprawnosci zapisu budzetu.

### 3.2 Zakres frontendowy - Oskar

Do realizacji:

- poprawa ukladu strony glownej,
- poprawa przyciskow:
  - `Zaloz konto`,
  - `Zaloguj sie`,
- poprawa wygladu formularza rejestracji,
- poprawa wygladu formularza logowania,
- poprawa wygladu formularza dodawania transakcji,
- poprawa czytelnosci listy transakcji,
- uporzadkowanie sekcji panelu uzytkownika.

### 3.3 Zakres bazodanowy - Aniela

Do realizacji:

- doprecyzowanie opisu tabel,
- doprecyzowanie opisu relacji,
- kontrola spojnosci aktualnej bazy z backendem,
- dopisanie dokumentacyjnego znaczenia kazdej tabeli.

### 3.4 Zakres organizacyjny - Justyna

Do realizacji:

- wskazanie, ktore wymagania `Must` sa juz odtworzone,
- wskazanie, ktore elementy sa jeszcze zbyt podstawowe,
- przygotowanie precyzyjniejszego opisu zakresu na nastepny etap,
- przygotowanie kolejnego raportu statusowego bez ogolnikow.

## 4. Oczekiwany rezultat kolejnego etapu

Do 2026-05-10 projekt powinien zostac doprowadzony do stanu, w ktorym:

- podstawowe formularze beda bardziej czytelne i spojne,
- komunikaty systemowe beda bardziej zrozumiale,
- warstwa danych bedzie lepiej opisana,
- status projektu bedzie opisywany bardziej konkretnie,
- kazda osoba bedzie miala wyraznie widoczny postep w swoim obszarze.

## 5. Znaczenie etapu do 2026-05-10

Kolejny etap nie ma jeszcze charakteru duzego rozwoju funkcjonalnego, ale ma bardzo duze znaczenie dla jakosci projektu. To wlasnie teraz projekt przechodzi od samego uporzadkowania do bardziej dojrzalego sposobu rozwijania funkcji, dokumentowania postepu oraz kontrolowania jakosci pracy zespolowej.

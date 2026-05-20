import hashlib
import html
import os
import secrets
import sqlite3
import urllib.parse
from datetime import datetime
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


KATALOG_GLOWNY = Path(__file__).resolve().parent
SCIEZKA_BAZY = KATALOG_GLOWNY / "budgetbuddy.db"
KATALOG_STATYCZNY = KATALOG_GLOWNY / "static"
DOZWOLONE_KATEGORIE = {"Jedzenie", "Transport", "Rachunki", "Rozrywka", "Inne"}
DOZWOLONE_SORTOWANIA = {
    "najnowsze": "transaction_date DESC, id DESC",
    "najstarsze": "transaction_date ASC, id ASC",
    "kwota_rosnaco": "amount ASC, id DESC",
    "kwota_malejaco": "amount DESC, id DESC",
}
sesje: dict[str, int] = {}


def bezpieczny_tekst(wartosc: object) -> str:
    return html.escape(str(wartosc), quote=True)


def polaczenie_z_baza() -> sqlite3.Connection:
    polaczenie = sqlite3.connect(SCIEZKA_BAZY)
    polaczenie.row_factory = sqlite3.Row
    return polaczenie


def przygotuj_baze() -> None:
    with polaczenie_z_baza() as polaczenie:
        polaczenie.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        polaczenie.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        polaczenie.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        polaczenie.commit()


def haszuj_haslo(haslo: str) -> str:
    return hashlib.sha256(haslo.encode("utf-8")).hexdigest()


def poprawny_login(login: str) -> bool:
    return 3 <= len(login) <= 32


def poprawne_haslo(haslo: str) -> bool:
    return 4 <= len(haslo) <= 64


def zbuduj_lacze_z_komunikatem(sciezka: str, komunikat: str) -> str:
    return f"{sciezka}?{urllib.parse.urlencode({'message': komunikat})}"


def pobierz_komunikat(sciezka: str) -> str:
    zapytanie = urllib.parse.urlparse(sciezka).query
    parametry = urllib.parse.parse_qs(zapytanie)
    return parametry.get("message", [""])[0]


def zbuduj_opcje_kategorii(wybrana_kategoria: str = "") -> str:
    opcje = ['<option value="">Wszystkie kategorie</option>']
    for kategoria in sorted(DOZWOLONE_KATEGORIE):
        zaznaczenie = " selected" if kategoria == wybrana_kategoria else ""
        opcje.append(f'<option value="{kategoria}"{zaznaczenie}>{kategoria}</option>')
    return "".join(opcje)


def zbuduj_opcje_kategorii_formularza(wybrana_kategoria: str) -> str:
    opcje = []
    for kategoria in sorted(DOZWOLONE_KATEGORIE):
        zaznaczenie = " selected" if kategoria == wybrana_kategoria else ""
        opcje.append(f'<option value="{kategoria}"{zaznaczenie}>{kategoria}</option>')
    return "".join(opcje)


def zbuduj_formularz_transakcji(edytowana_transakcja: sqlite3.Row | None = None) -> str:
    czy_edycja = edytowana_transakcja is not None
    tytul = "Edytuj transakcje" if czy_edycja else "Dodaj transakcje"
    opis = (
        "Zmien dane wybranej transakcji i zapisz poprawiona wersje wpisu."
        if czy_edycja
        else "Dodaj przychod lub wydatek, aby zaktualizowac swoja historie finansowa."
    )
    akcja = "/transaction/update" if czy_edycja else "/transaction"
    etykieta_przycisku = "Zapisz zmiany" if czy_edycja else "Dodaj transakcje"
    nazwa = html.escape(str(edytowana_transakcja["title"])) if czy_edycja else ""
    kwota = f'{float(edytowana_transakcja["amount"]):.2f}' if czy_edycja else ""
    kategoria = str(edytowana_transakcja["category"]) if czy_edycja else "Jedzenie"
    typ = str(edytowana_transakcja["transaction_type"]) if czy_edycja else "expense"
    data_transakcji = (
        str(edytowana_transakcja["transaction_date"])
        if czy_edycja
        else datetime.now().strftime("%Y-%m-%d")
    )
    zaznacz_wydatek = " selected" if typ == "expense" else ""
    zaznacz_przychod = " selected" if typ == "income" else ""
    pole_id = (
        f'<input type="hidden" name="transaction_id" value="{edytowana_transakcja["id"]}">'
        if czy_edycja
        else ""
    )
    link_anuluj = (
        '<a class="przycisk przycisk-jasny" href="/dashboard">Anuluj edycje</a>'
        if czy_edycja
        else ""
    )

    return f"""
    <article class="karta">
        <h2>{tytul}</h2>
        <p class="opis-sekcji">{opis}</p>
        <form method="post" action="{akcja}">
            {pole_id}
            <label>Nazwa
                <input type="text" name="title" required maxlength="80" placeholder="np. Zakupy spozywcze" value="{nazwa}">
            </label>
            <label>Kwota
                <input type="number" step="0.01" min="0.01" name="amount" required placeholder="0.00" value="{kwota}">
            </label>
            <label>Kategoria
                <select name="category">
                    {zbuduj_opcje_kategorii_formularza(kategoria)}
                </select>
            </label>
            <label>Typ
                <select name="transaction_type">
                    <option value="expense"{zaznacz_wydatek}>Wydatek</option>
                    <option value="income"{zaznacz_przychod}>Przychod</option>
                </select>
            </label>
            <label>Data
                <input type="date" name="transaction_date" value="{data_transakcji}" required>
            </label>
            <div class="przyciski">
                <button class="przycisk" type="submit">{etykieta_przycisku}</button>
                {link_anuluj}
            </div>
        </form>
    </article>
    """


def zbuduj_sekcje_analityczna(limit: float, suma_wydatkow: float, suma_przychodow: float, transakcje: list[sqlite3.Row]) -> str:
    wydatki_kategorii: dict[str, float] = {}
    liczba_wydatkow = 0
    liczba_przychodow = 0
    for transakcja in transakcje:
        if transakcja["transaction_type"] == "expense":
            liczba_wydatkow += 1
            kategoria = str(transakcja["category"])
            wydatki_kategorii[kategoria] = wydatki_kategorii.get(kategoria, 0.0) + float(transakcja["amount"])
        elif transakcja["transaction_type"] == "income":
            liczba_przychodow += 1

    wykorzystanie_budzetu = 0.0
    if limit > 0:
        wykorzystanie_budzetu = min((suma_wydatkow / limit) * 100, 100.0)

    pasek_klasa = "postep-neutralny"
    if wykorzystanie_budzetu >= 90:
        pasek_klasa = "postep-alert"
    elif wykorzystanie_budzetu >= 65:
        pasek_klasa = "postep-ostrzegawczy"
    elif wykorzystanie_budzetu > 0:
        pasek_klasa = "postep-dobry"

    laczna_kwota_wydatkow = sum(wydatki_kategorii.values())
    wiersze_kategorii = ""
    dominujaca_kategoria = "Brak danych"
    if laczna_kwota_wydatkow > 0:
        dominujaca_kategoria = max(wydatki_kategorii.items(), key=lambda element: element[1])[0]
        for kategoria, kwota in sorted(wydatki_kategorii.items(), key=lambda element: element[1], reverse=True):
            szerokosc = max((kwota / laczna_kwota_wydatkow) * 100, 8)
            udzial = (kwota / laczna_kwota_wydatkow) * 100
            wiersze_kategorii += f"""
            <div class="wiersz-wykresu">
                <div class="naglowek-wykresu">
                    <span>{kategoria}</span>
                    <strong>{kwota:.2f} zl</strong>
                </div>
                <div class="tor-wykresu">
                    <div class="slupek-wykresu" style="width: {szerokosc:.1f}%"></div>
                </div>
                <p class="opis-pola">Udzial w wydatkach: {udzial:.1f}%</p>
            </div>
            """
    else:
        wiersze_kategorii = """
        <div class="brak-danych-analitycznych">
            <p>Dodaj wydatki, aby zobaczyc zestawienie kategorii i bardziej szczegolowa analityke.</p>
        </div>
        """

    komunikat_budzetowy = "Budzet nie zostal jeszcze ustawiony."
    if limit > 0:
        komunikat_budzetowy = f"Wykorzystanie budzetu wynosi obecnie {wykorzystanie_budzetu:.1f}%."

    maksymalna_wartosc_porownania = max(suma_wydatkow, suma_przychodow, 1.0)
    szerokosc_wydatkow = max((suma_wydatkow / maksymalna_wartosc_porownania) * 100, 10 if suma_wydatkow > 0 else 0)
    szerokosc_przychodow = max((suma_przychodow / maksymalna_wartosc_porownania) * 100, 10 if suma_przychodow > 0 else 0)

    return f"""
    <section class="siatka-analityczna">
        <article class="karta karta-analityczna">
            <div class="naglowek-karty-analitycznej">
                <div>
                    <p class="etykieta-kafelka">Analiza budzetu</p>
                    <h2>Wykorzystanie limitu miesiecznego</h2>
                </div>
                <strong>{wykorzystanie_budzetu:.1f}%</strong>
            </div>
            <div class="tor-postepu">
                <div class="wypelnienie-postepu {pasek_klasa}" style="width: {wykorzystanie_budzetu:.1f}%"></div>
            </div>
            <p class="opis-sekcji">{komunikat_budzetowy}</p>
            <div class="metryki-analityczne">
                <div>
                    <span>Wydatki</span>
                    <strong>{suma_wydatkow:.2f} zl</strong>
                </div>
                <div>
                    <span>Przychody</span>
                    <strong>{suma_przychodow:.2f} zl</strong>
                </div>
                <div>
                    <span>Limit</span>
                    <strong>{limit:.2f} zl</strong>
                </div>
            </div>
        </article>

        <article class="karta karta-analityczna">
            <div class="naglowek-karty-analitycznej">
                <div>
                    <p class="etykieta-kafelka">Wykres</p>
                    <h2>Wydatki wedlug kategorii</h2>
                </div>
            </div>
            <p class="opis-sekcji">
                Sekcja pokazuje, ktore obszary generuja najwieksze koszty i gdzie budzet jest obciazany najmocniej.
            </p>
            {wiersze_kategorii}
        </article>

        <article class="karta karta-analityczna">
            <div class="naglowek-karty-analitycznej">
                <div>
                    <p class="etykieta-kafelka">Bilans i insighty</p>
                    <h2>Porownanie przychodow i wydatkow</h2>
                </div>
            </div>
            <div class="wiersz-wykresu">
                <div class="naglowek-wykresu">
                    <span>Wydatki</span>
                    <strong>{suma_wydatkow:.2f} zl</strong>
                </div>
                <div class="tor-wykresu">
                    <div class="slupek-wykresu" style="width: {szerokosc_wydatkow:.1f}%"></div>
                </div>
            </div>
            <div class="wiersz-wykresu">
                <div class="naglowek-wykresu">
                    <span>Przychody</span>
                    <strong>{suma_przychodow:.2f} zl</strong>
                </div>
                <div class="tor-wykresu">
                    <div class="slupek-wykresu" style="width: {szerokosc_przychodow:.1f}%"></div>
                </div>
            </div>
            <div class="metryki-analityczne">
                <div>
                    <span>Najwieksza kategoria</span>
                    <strong>{dominujaca_kategoria}</strong>
                </div>
                <div>
                    <span>Liczba wydatkow</span>
                    <strong>{liczba_wydatkow}</strong>
                </div>
                <div>
                    <span>Liczba przychodow</span>
                    <strong>{liczba_przychodow}</strong>
                </div>
            </div>
        </article>
    </section>
    """


def uklad_strony(tytul: str, tresc: str, komunikat: str = "", uzytkownik: sqlite3.Row | None = None) -> str:
    blok_komunikatu = f'<div class="komunikat">{bezpieczny_tekst(komunikat)}</div>' if komunikat else ""
    nawigacja = (
        f"""
        <div class="nawigacja">
            <span>Zalogowano jako <strong>{bezpieczny_tekst(uzytkownik['username'])}</strong></span>
            <a href="/dashboard">Panel</a>
            <a href="/logout">Wyloguj</a>
        </div>
        """
        if uzytkownik
        else """
        <div class="nawigacja">
            <a href="/">Start</a>
            <a href="/register">Rejestracja</a>
            <a href="/login">Logowanie</a>
        </div>
        """
    )
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{bezpieczny_tekst(tytul)} | BudgetBuddy</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <header class="naglowek">
        <div>
            <p class="etykieta">BudgetBuddy</p>
            <h1>{bezpieczny_tekst(tytul)}</h1>
        </div>
        {nawigacja}
    </header>
    <main class="zawartosc">
        {blok_komunikatu}
        {tresc}
    </main>
</body>
</html>
"""


def strona_glowna() -> str:
    return uklad_strony(
        "Prosty system kontroli budzetu",
        """
        <section class="siatka">
            <article class="karta">
                <h2>Aktualny etap projektu</h2>
                <p>
                    Aplikacja po reorganizacji projektu odzyskuje podstawowe funkcje:
                    rejestracje, logowanie, ustawianie budzetu i dodawanie transakcji.
                </p>
                <div class="przyciski">
                    <a class="przycisk" href="/register">Zaloz konto</a>
                    <a class="przycisk przycisk-jasny" href="/login">Zaloguj sie</a>
                </div>
            </article>
            <article class="karta">
                <h2>Zakres obecnej wersji</h2>
                <ul>
                    <li>Rejestracja uzytkownika</li>
                    <li>Logowanie i wylogowanie</li>
                    <li>Ustawianie budzetu miesiecznego</li>
                    <li>Dodawanie transakcji</li>
                    <li>Prosty panel uzytkownika</li>
                </ul>
            </article>
        </section>
        <section class="karta karta-informacyjna">
            <h2>Co mozesz zrobic w tej wersji</h2>
            <p>
                Uzytkownik moze zalozyc konto, zalogowac sie, ustawic limit miesieczny oraz dodawac
                podstawowe transakcje. W kolejnych etapach interfejs bedzie dalej rozszerzany.
            </p>
        </section>
        """,
    )


def formularz_rejestracji(komunikat: str = "") -> str:
    return uklad_strony(
        "Rejestracja",
        """
        <section class="sekcja-pojedyncza">
            <article class="karta formularz-karta">
                <h2>Nowe konto</h2>
                <form method="post" action="/register">
                    <label>Login
                        <input type="text" name="username" required minlength="3" maxlength="32" placeholder="np. jan.kowalski">
                    </label>
                    <p class="opis-pola">Login powinien miec od 3 do 32 znakow.</p>
                    <label>Haslo
                        <input type="password" name="password" required minlength="4" maxlength="64" placeholder="minimum 4 znaki">
                    </label>
                    <p class="opis-pola">Haslo powinno miec od 4 do 64 znakow.</p>
                    <button class="przycisk" type="submit">Zarejestruj</button>
                </form>
            </article>
        </section>
        """,
        komunikat,
    )


def formularz_logowania(komunikat: str = "") -> str:
    return uklad_strony(
        "Logowanie",
        """
        <section class="sekcja-pojedyncza">
            <article class="karta formularz-karta">
                <h2>Wejscie do panelu</h2>
                <form method="post" action="/login">
                    <label>Login
                        <input type="text" name="username" required placeholder="podaj login">
                    </label>
                    <label>Haslo
                        <input type="password" name="password" required placeholder="podaj haslo">
                    </label>
                    <button class="przycisk" type="submit">Zaloguj</button>
                </form>
            </article>
        </section>
        """,
        komunikat,
    )


def panel_uzytkownika(
    uzytkownik: sqlite3.Row,
    budzet: sqlite3.Row | None,
    transakcje: list[sqlite3.Row],
    filtry: dict[str, str],
    edytowana_transakcja: sqlite3.Row | None = None,
    komunikat: str = "",
) -> str:
    limit = float(budzet["monthly_limit"]) if budzet else 0.0
    suma_wydatkow = sum(
        float(transakcja["amount"]) for transakcja in transakcje if transakcja["transaction_type"] == "expense"
    )
    suma_przychodow = sum(
        float(transakcja["amount"]) for transakcja in transakcje if transakcja["transaction_type"] == "income"
    )
    saldo = suma_przychodow - suma_wydatkow
    pozostaly_limit = limit - suma_wydatkow
    lista = ""
    for transakcja in transakcje:
        lista += (
            f"<tr><td>{bezpieczny_tekst(transakcja['transaction_date'])}</td>"
            f"<td>{bezpieczny_tekst(transakcja['title'])}</td>"
            f"<td>{bezpieczny_tekst(transakcja['category'])}</td>"
            f"<td>{'Wydatek' if transakcja['transaction_type'] == 'expense' else 'Przychod'}</td>"
            f"<td>{transakcja['amount']:.2f} zl</td>"
            f"""<td>
                <div class="przyciski">
                    <a class="przycisk przycisk-jasny" href="/dashboard?edit_transaction_id={transakcja['id']}">Edytuj</a>
                    <form method="post" action="/transaction/delete">
                        <input type="hidden" name="transaction_id" value="{transakcja['id']}">
                        <button class="przycisk" type="submit">Usun</button>
                    </form>
                </div>
            </td></tr>"""
        )
    if not lista:
        lista = '<tr><td colspan="6">Brak transakcji.</td></tr>'

    klasa_salda = "wartosc-neutralna"
    if saldo > 0:
        klasa_salda = "wartosc-dodatnia"
    elif saldo < 0:
        klasa_salda = "wartosc-ujemna"

    klasa_limitu = "wartosc-neutralna"
    if pozostaly_limit > 0:
        klasa_limitu = "wartosc-dodatnia"
    elif pozostaly_limit < 0:
        klasa_limitu = "wartosc-ujemna"

    wybrany_typ = filtry.get("transaction_type", "")
    wybrana_kategoria = filtry.get("category", "")
    wybrane_sortowanie = filtry.get("sortowanie", "najnowsze")
    zaznacz_wszystkie_typy = " selected" if not wybrany_typ else ""
    zaznacz_wydatki = " selected" if wybrany_typ == "expense" else ""
    zaznacz_przychody = " selected" if wybrany_typ == "income" else ""
    zaznacz_najnowsze = " selected" if wybrane_sortowanie == "najnowsze" else ""
    zaznacz_najstarsze = " selected" if wybrane_sortowanie == "najstarsze" else ""
    zaznacz_kwota_rosnaco = " selected" if wybrane_sortowanie == "kwota_rosnaco" else ""
    zaznacz_kwota_malejaco = " selected" if wybrane_sortowanie == "kwota_malejaco" else ""
    sekcja_analityczna = zbuduj_sekcje_analityczna(limit, suma_wydatkow, suma_przychodow, transakcje)
    formularz_transakcji = zbuduj_formularz_transakcji(edytowana_transakcja)

    return uklad_strony(
        "Panel uzytkownika",
        f"""
        <section class="kafelki">
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Budzet</p>
                <h2>Budzet miesieczny</h2>
                <p>{limit:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Wydatki</p>
                <h2>Suma wydatkow</h2>
                <p>{suma_wydatkow:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Przychody</p>
                <h2>Suma przychodow</h2>
                <p>{suma_przychodow:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Bilans</p>
                <h2>Saldo</h2>
                <p class="{klasa_salda}">{saldo:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Limit</p>
                <h2>Pozostaly limit</h2>
                <p class="{klasa_limitu}">{pozostaly_limit:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <p class="etykieta-kafelka">Status</p>
                <h2>Ostatnia aktualizacja</h2>
                <p>{datetime.now().strftime("%Y-%m-%d")}</p>
            </article>
        </section>

        {sekcja_analityczna}

        <section class="siatka">
            <article class="karta">
                <h2>Ustaw budzet</h2>
                <p class="opis-sekcji">Tutaj ustawiasz miesieczny limit wydatkow dla swojego konta.</p>
                <form method="post" action="/budget">
                    <label>Limit miesieczny
                        <input type="number" step="0.01" min="0" name="monthly_limit" value="{limit:.2f}" required>
                    </label>
                    <button class="przycisk" type="submit">Zapisz budzet</button>
                </form>
            </article>

            {formularz_transakcji}
        </section>

        <section class="karta">
            <h2>Filtrowanie i sortowanie transakcji</h2>
            <p class="opis-sekcji">
                Tutaj mozesz zawezic liste transakcji do wybranej kategorii, typu oraz sposobu sortowania.
            </p>
            <form method="get" action="/dashboard">
                <label>Kategoria
                    <select name="category">
                        {zbuduj_opcje_kategorii(wybrana_kategoria)}
                    </select>
                </label>
                <label>Typ transakcji
                    <select name="transaction_type">
                        <option value=""{zaznacz_wszystkie_typy}>Wszystkie typy</option>
                        <option value="expense"{zaznacz_wydatki}>Wydatki</option>
                        <option value="income"{zaznacz_przychody}>Przychody</option>
                    </select>
                </label>
                <label>Sortowanie
                    <select name="sortowanie">
                        <option value="najnowsze"{zaznacz_najnowsze}>Od najnowszych</option>
                        <option value="najstarsze"{zaznacz_najstarsze}>Od najstarszych</option>
                        <option value="kwota_rosnaco"{zaznacz_kwota_rosnaco}>Kwota rosnaco</option>
                        <option value="kwota_malejaco"{zaznacz_kwota_malejaco}>Kwota malejaco</option>
                    </select>
                </label>
                <div class="przyciski">
                    <button class="przycisk" type="submit">Zastosuj filtry</button>
                    <a class="przycisk przycisk-jasny" href="/dashboard">Wyczysc filtry</a>
                </div>
            </form>
        </section>

        <section class="karta">
            <h2>Lista transakcji</h2>
            <p class="opis-sekcji">Ponizej widzisz wszystkie zapisane transakcje dla aktualnie zalogowanego uzytkownika.</p>
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Nazwa</th>
                        <th>Kategoria</th>
                        <th>Typ</th>
                        <th>Kwota</th>
                        <th>Akcje</th>
                    </tr>
                </thead>
                <tbody>{lista}</tbody>
            </table>
        </section>
        """,
        komunikat,
        uzytkownik,
    )


class ObslugaBudgetBuddy(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        sciezka = urllib.parse.urlparse(self.path).path
        if sciezka.startswith("/static/"):
            self.obsluz_pliki_statyczne(sciezka)
            return
        if sciezka == "/":
            self.odpowiedz_html(strona_glowna())
            return
        if sciezka == "/register":
            self.odpowiedz_html(formularz_rejestracji(pobierz_komunikat(self.path)))
            return
        if sciezka == "/login":
            self.odpowiedz_html(formularz_logowania(pobierz_komunikat(self.path)))
            return
        if sciezka == "/logout":
            identyfikator_sesji = self.pobierz_id_sesji()
            if identyfikator_sesji:
                sesje.pop(identyfikator_sesji, None)
            self.przekieruj(
                zbuduj_lacze_z_komunikatem("/login", "Wylogowano poprawnie."),
                wyczysc_cookie=True,
            )
            return
        if sciezka == "/dashboard":
            uzytkownik = self.wymagaj_uzytkownika()
            if not uzytkownik:
                return
            filtry = self.pobierz_filtry_panelu()
            budzet, transakcje = self.pobierz_dane_panelu(uzytkownik["id"], filtry)
            edytowana_transakcja = self.pobierz_transakcje_do_edycji(uzytkownik["id"])
            self.odpowiedz_html(
                panel_uzytkownika(
                    uzytkownik,
                    budzet,
                    transakcje,
                    filtry,
                    edytowana_transakcja,
                    pobierz_komunikat(self.path),
                )
            )
            return
        self.odpowiedz_html(
            uklad_strony("Nie znaleziono", "<section class='karta'><p>Nie znaleziono strony.</p></section>"),
            status=404,
        )

    def do_POST(self) -> None:
        sciezka = urllib.parse.urlparse(self.path).path
        if sciezka == "/register":
            self.obsluz_rejestracje()
            return
        if sciezka == "/login":
            self.obsluz_logowanie()
            return
        if sciezka == "/budget":
            self.obsluz_budzet()
            return
        if sciezka == "/transaction":
            self.obsluz_transakcje()
            return
        if sciezka == "/transaction/update":
            self.obsluz_aktualizacje_transakcji()
            return
        if sciezka == "/transaction/delete":
            self.obsluz_usuwanie_transakcji()
            return
        self.odpowiedz_html(
            uklad_strony("Blad", "<section class='karta'><p>Nieobslugiwane zadanie.</p></section>"),
            status=405,
        )

    def obsluz_rejestracje(self) -> None:
        dane = self.pobierz_dane_formularza()
        login = dane.get("username", "").strip()
        haslo = dane.get("password", "").strip()

        if not poprawny_login(login):
            self.odpowiedz_html(
                formularz_rejestracji("Login musi miec od 3 do 32 znakow."),
                status=400,
            )
            return

        if not poprawne_haslo(haslo):
            self.odpowiedz_html(
                formularz_rejestracji("Haslo musi miec od 4 do 64 znakow."),
                status=400,
            )
            return

        try:
            with polaczenie_z_baza() as polaczenie:
                polaczenie.execute(
                    "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                    (login, haszuj_haslo(haslo), datetime.now().isoformat(timespec="seconds")),
                )
                polaczenie.commit()
        except sqlite3.IntegrityError:
            self.odpowiedz_html(
                formularz_rejestracji("Uzytkownik o takim loginie juz istnieje."),
                status=400,
            )
            return

        self.przekieruj(zbuduj_lacze_z_komunikatem("/login", "Konto zostalo utworzone."))

    def obsluz_logowanie(self) -> None:
        dane = self.pobierz_dane_formularza()
        login = dane.get("username", "").strip()
        haslo = dane.get("password", "").strip()

        if not login or not haslo:
            self.odpowiedz_html(
                formularz_logowania("Uzupelnij login i haslo."),
                status=400,
            )
            return

        with polaczenie_z_baza() as polaczenie:
            uzytkownik = polaczenie.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (login, haszuj_haslo(haslo)),
            ).fetchone()

        if not uzytkownik:
            self.odpowiedz_html(formularz_logowania("Niepoprawny login lub haslo."), status=401)
            return

        identyfikator_sesji = secrets.token_hex(16)
        sesje[identyfikator_sesji] = int(uzytkownik["id"])
        self.przekieruj(
            zbuduj_lacze_z_komunikatem("/dashboard", "Zalogowano poprawnie."),
            session_id=identyfikator_sesji,
        )

    def obsluz_budzet(self) -> None:
        uzytkownik = self.wymagaj_uzytkownika()
        if not uzytkownik:
            return
        dane = self.pobierz_dane_formularza()
        try:
            limit = float(dane.get("monthly_limit", "0"))
            if limit < 0:
                raise ValueError
        except ValueError:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Budzet musi byc liczba dodatnia lub rowna zero.",
                )
            )
            return

        teraz = datetime.now().isoformat(timespec="seconds")
        with polaczenie_z_baza() as polaczenie:
            istnieje = polaczenie.execute(
                "SELECT id FROM budgets WHERE user_id = ?",
                (uzytkownik["id"],),
            ).fetchone()
            if istnieje:
                polaczenie.execute(
                    "UPDATE budgets SET monthly_limit = ?, updated_at = ? WHERE user_id = ?",
                    (limit, teraz, uzytkownik["id"]),
                )
            else:
                polaczenie.execute(
                    "INSERT INTO budgets (user_id, monthly_limit, updated_at) VALUES (?, ?, ?)",
                    (uzytkownik["id"], limit, teraz),
                )
            polaczenie.commit()

        self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", "Budzet zapisany."))

    def obsluz_transakcje(self) -> None:
        uzytkownik = self.wymagaj_uzytkownika()
        if not uzytkownik:
            return
        dane = self.pobierz_dane_formularza()
        dane_transakcji, blad = self.przygotuj_dane_transakcji(dane)
        if blad:
            self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", blad))
            return

        with polaczenie_z_baza() as polaczenie:
            polaczenie.execute(
                """
                INSERT INTO transactions (
                    user_id, title, amount, category, transaction_type, transaction_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uzytkownik["id"],
                    dane_transakcji["title"],
                    dane_transakcji["amount"],
                    dane_transakcji["category"],
                    dane_transakcji["transaction_type"],
                    dane_transakcji["transaction_date"],
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            polaczenie.commit()

        self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", "Transakcja zostala dodana."))

    def obsluz_aktualizacje_transakcji(self) -> None:
        uzytkownik = self.wymagaj_uzytkownika()
        if not uzytkownik:
            return

        dane = self.pobierz_dane_formularza()
        identyfikator = dane.get("transaction_id", "").strip()
        if not identyfikator.isdigit():
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nie wybrano poprawnej transakcji do edycji.",
                )
            )
            return

        dane_transakcji, blad = self.przygotuj_dane_transakcji(dane)
        if blad:
            self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", blad))
            return

        with polaczenie_z_baza() as polaczenie:
            wynik = polaczenie.execute(
                """
                UPDATE transactions
                SET title = ?, amount = ?, category = ?, transaction_type = ?, transaction_date = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    dane_transakcji["title"],
                    dane_transakcji["amount"],
                    dane_transakcji["category"],
                    dane_transakcji["transaction_type"],
                    dane_transakcji["transaction_date"],
                    int(identyfikator),
                    uzytkownik["id"],
                ),
            )
            polaczenie.commit()

        if wynik.rowcount == 0:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nie znaleziono transakcji do edycji.",
                )
            )
            return

        self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", "Transakcja zostala zaktualizowana."))

    def obsluz_usuwanie_transakcji(self) -> None:
        uzytkownik = self.wymagaj_uzytkownika()
        if not uzytkownik:
            return

        dane = self.pobierz_dane_formularza()
        identyfikator = dane.get("transaction_id", "").strip()

        if not identyfikator.isdigit():
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nie wybrano poprawnej transakcji do usuniecia.",
                )
            )
            return

        with polaczenie_z_baza() as polaczenie:
            wynik = polaczenie.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                (int(identyfikator), uzytkownik["id"]),
            )
            polaczenie.commit()

        if wynik.rowcount == 0:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nie znaleziono transakcji do usuniecia.",
                )
            )
            return

        self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", "Transakcja zostala usunieta."))

    def pobierz_dane_formularza(self) -> dict[str, str]:
        dlugosc = int(self.headers.get("Content-Length", "0"))
        surowe = self.rfile.read(dlugosc).decode("utf-8")
        dane = urllib.parse.parse_qs(surowe, keep_blank_values=True)
        return {klucz: wartosci[0] for klucz, wartosci in dane.items()}

    def pobierz_parametry_zapytania(self) -> dict[str, str]:
        zapytanie = urllib.parse.urlparse(self.path).query
        dane = urllib.parse.parse_qs(zapytanie, keep_blank_values=True)
        return {klucz: wartosci[0] for klucz, wartosci in dane.items()}

    def przygotuj_dane_transakcji(self, dane: dict[str, str]) -> tuple[dict[str, object], str]:
        nazwa = dane.get("title", "").strip()
        kategoria = dane.get("category", "").strip() or "Inne"
        typ = dane.get("transaction_type", "").strip()
        data_transakcji = dane.get("transaction_date", "").strip()

        try:
            kwota = float(dane.get("amount", "0"))
            datetime.strptime(data_transakcji, "%Y-%m-%d")
            if kwota <= 0:
                raise ValueError
        except ValueError:
            return {}, "Kwota i data transakcji musza miec poprawny format."

        if not nazwa:
            return {}, "Nazwa transakcji nie moze byc pusta."

        if len(nazwa) > 80:
            return {}, "Nazwa transakcji moze miec maksymalnie 80 znakow."

        if kategoria not in DOZWOLONE_KATEGORIE:
            return {}, "Wybrano niepoprawna kategorie transakcji."

        if typ not in {"expense", "income"}:
            return {}, "Typ transakcji musi byc ustawiony jako wydatek lub przychod."

        return {
            "title": nazwa,
            "amount": kwota,
            "category": kategoria,
            "transaction_type": typ,
            "transaction_date": data_transakcji,
        }, ""

    def pobierz_filtry_panelu(self) -> dict[str, str]:
        parametry = self.pobierz_parametry_zapytania()
        kategoria = parametry.get("category", "").strip()
        typ = parametry.get("transaction_type", "").strip()
        sortowanie = parametry.get("sortowanie", "najnowsze").strip() or "najnowsze"

        if kategoria and kategoria not in DOZWOLONE_KATEGORIE:
            kategoria = ""
        if typ not in {"", "expense", "income"}:
            typ = ""
        if sortowanie not in DOZWOLONE_SORTOWANIA:
            sortowanie = "najnowsze"

        return {
            "category": kategoria,
            "transaction_type": typ,
            "sortowanie": sortowanie,
        }

    def pobierz_transakcje_do_edycji(self, user_id: int) -> sqlite3.Row | None:
        parametry = self.pobierz_parametry_zapytania()
        identyfikator = parametry.get("edit_transaction_id", "").strip()
        if not identyfikator.isdigit():
            return None

        with polaczenie_z_baza() as polaczenie:
            return polaczenie.execute(
                "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                (int(identyfikator), user_id),
            ).fetchone()

    def pobierz_id_sesji(self) -> str | None:
        cookie = self.headers.get("Cookie")
        if not cookie:
            return None
        sloik = cookies.SimpleCookie()
        sloik.load(cookie)
        identyfikator = sloik.get("session_id")
        return identyfikator.value if identyfikator else None

    def pobierz_biezacego_uzytkownika(self) -> sqlite3.Row | None:
        identyfikator_sesji = self.pobierz_id_sesji()
        user_id = sesje.get(identyfikator_sesji or "")
        if not user_id:
            return None
        with polaczenie_z_baza() as polaczenie:
            return polaczenie.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def wymagaj_uzytkownika(self) -> sqlite3.Row | None:
        uzytkownik = self.pobierz_biezacego_uzytkownika()
        if not uzytkownik:
            self.przekieruj(zbuduj_lacze_z_komunikatem("/login", "Najpierw sie zaloguj."))
            return None
        return uzytkownik

    def pobierz_dane_panelu(self, user_id: int, filtry: dict[str, str]) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
        warunki = ["user_id = ?"]
        parametry: list[object] = [user_id]

        if filtry.get("category"):
            warunki.append("category = ?")
            parametry.append(filtry["category"])

        if filtry.get("transaction_type"):
            warunki.append("transaction_type = ?")
            parametry.append(filtry["transaction_type"])

        sortowanie_sql = DOZWOLONE_SORTOWANIA.get(filtry.get("sortowanie", "najnowsze"), DOZWOLONE_SORTOWANIA["najnowsze"])
        zapytanie_transakcji = (
            "SELECT * FROM transactions WHERE "
            + " AND ".join(warunki)
            + f" ORDER BY {sortowanie_sql}"
        )

        with polaczenie_z_baza() as polaczenie:
            budzet = polaczenie.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,)).fetchone()
            transakcje = polaczenie.execute(zapytanie_transakcji, tuple(parametry)).fetchall()
        return budzet, transakcje

    def obsluz_pliki_statyczne(self, sciezka: str) -> None:
        plik = KATALOG_STATYCZNY / sciezka.removeprefix("/static/")
        if not plik.exists() or not plik.is_file():
            self.send_error(404)
            return
        zawartosc = plik.read_bytes()
        self.send_response(200)
        self.dodaj_naglowki_bezpieczenstwa()
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(zawartosc)))
        self.end_headers()
        self.wfile.write(zawartosc)

    def odpowiedz_html(self, tresc: str, status: int = 200) -> None:
        dane = tresc.encode("utf-8")
        self.send_response(status)
        self.dodaj_naglowki_bezpieczenstwa(dla_html=True)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(dane)))
        self.end_headers()
        self.wfile.write(dane)

    def przekieruj(
        self,
        lokalizacja: str,
        session_id: str | None = None,
        wyczysc_cookie: bool = False,
    ) -> None:
        self.send_response(303)
        self.dodaj_naglowki_bezpieczenstwa(dla_html=True)
        self.send_header("Location", lokalizacja)
        if session_id:
            self.send_header("Set-Cookie", f"session_id={session_id}; HttpOnly; SameSite=Lax; Path=/")
        if wyczysc_cookie:
            self.send_header("Set-Cookie", "session_id=deleted; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
        self.end_headers()

    def dodaj_naglowki_bezpieczenstwa(self, dla_html: bool = False) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        if dla_html:
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")


def uruchom() -> None:
    przygotuj_baze()
    port = int(os.environ.get("PORT", "8000"))
    serwer = HTTPServer(("127.0.0.1", port), ObslugaBudgetBuddy)
    print(f"BudgetBuddy dziala pod adresem http://127.0.0.1:{port}")
    serwer.serve_forever()


if __name__ == "__main__":
    uruchom()

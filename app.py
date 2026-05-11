import hashlib
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
sesje: dict[str, int] = {}


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


def uklad_strony(tytul: str, tresc: str, komunikat: str = "", uzytkownik: sqlite3.Row | None = None) -> str:
    blok_komunikatu = f'<div class="komunikat">{komunikat}</div>' if komunikat else ""
    nawigacja = (
        f"""
        <div class="nawigacja">
            <span>Zalogowano jako <strong>{uzytkownik['username']}</strong></span>
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
    <title>{tytul} | BudgetBuddy</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <header class="naglowek">
        <div>
            <p class="etykieta">BudgetBuddy</p>
            <h1>{tytul}</h1>
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
                        <input type="text" name="username" required minlength="3">
                    </label>
                    <label>Haslo
                        <input type="password" name="password" required minlength="4">
                    </label>
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
                        <input type="text" name="username" required>
                    </label>
                    <label>Haslo
                        <input type="password" name="password" required>
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
    komunikat: str = "",
) -> str:
    limit = float(budzet["monthly_limit"]) if budzet else 0.0
    lista = ""
    for transakcja in transakcje:
        lista += (
            f"<tr><td>{transakcja['transaction_date']}</td>"
            f"<td>{transakcja['title']}</td>"
            f"<td>{transakcja['category']}</td>"
            f"<td>{'Wydatek' if transakcja['transaction_type'] == 'expense' else 'Przychod'}</td>"
            f"<td>{transakcja['amount']:.2f} zl</td></tr>"
        )
    if not lista:
        lista = '<tr><td colspan="5">Brak transakcji.</td></tr>'

    return uklad_strony(
        "Panel uzytkownika",
        f"""
        <section class="kafelki">
            <article class="karta kafelek">
                <h2>Budzet miesieczny</h2>
                <p>{limit:.2f} zl</p>
            </article>
            <article class="karta kafelek">
                <h2>Ostatnia aktualizacja</h2>
                <p>{datetime.now().strftime("%Y-%m-%d")}</p>
            </article>
        </section>

        <section class="siatka">
            <article class="karta">
                <h2>Ustaw budzet</h2>
                <form method="post" action="/budget">
                    <label>Limit miesieczny
                        <input type="number" step="0.01" min="0" name="monthly_limit" value="{limit:.2f}" required>
                    </label>
                    <button class="przycisk" type="submit">Zapisz budzet</button>
                </form>
            </article>

            <article class="karta">
                <h2>Dodaj transakcje</h2>
                <form method="post" action="/transaction">
                    <label>Nazwa
                        <input type="text" name="title" required>
                    </label>
                    <label>Kwota
                        <input type="number" step="0.01" min="0.01" name="amount" required>
                    </label>
                    <label>Kategoria
                        <select name="category">
                            <option value="Jedzenie">Jedzenie</option>
                            <option value="Transport">Transport</option>
                            <option value="Rachunki">Rachunki</option>
                            <option value="Rozrywka">Rozrywka</option>
                            <option value="Inne">Inne</option>
                        </select>
                    </label>
                    <label>Typ
                        <select name="transaction_type">
                            <option value="expense">Wydatek</option>
                            <option value="income">Przychod</option>
                        </select>
                    </label>
                    <label>Data
                        <input type="date" name="transaction_date" value="{datetime.now().strftime("%Y-%m-%d")}" required>
                    </label>
                    <button class="przycisk" type="submit">Dodaj transakcje</button>
                </form>
            </article>
        </section>

        <section class="karta">
            <h2>Lista transakcji</h2>
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Nazwa</th>
                        <th>Kategoria</th>
                        <th>Typ</th>
                        <th>Kwota</th>
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
            budzet, transakcje = self.pobierz_dane_panelu(uzytkownik["id"])
            self.odpowiedz_html(
                panel_uzytkownika(
                    uzytkownik,
                    budzet,
                    transakcje,
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
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Kwota i data transakcji musza miec poprawny format.",
                )
            )
            return

        if not nazwa:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nazwa transakcji nie moze byc pusta.",
                )
            )
            return

        if len(nazwa) > 80:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Nazwa transakcji moze miec maksymalnie 80 znakow.",
                )
            )
            return

        if kategoria not in DOZWOLONE_KATEGORIE:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Wybrano niepoprawna kategorie transakcji.",
                )
            )
            return

        if typ not in {"expense", "income"}:
            self.przekieruj(
                zbuduj_lacze_z_komunikatem(
                    "/dashboard",
                    "Typ transakcji musi byc ustawiony jako wydatek lub przychod.",
                )
            )
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
                    nazwa,
                    kwota,
                    kategoria,
                    typ,
                    data_transakcji,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            polaczenie.commit()

        self.przekieruj(zbuduj_lacze_z_komunikatem("/dashboard", "Transakcja zostala dodana."))

    def pobierz_dane_formularza(self) -> dict[str, str]:
        dlugosc = int(self.headers.get("Content-Length", "0"))
        surowe = self.rfile.read(dlugosc).decode("utf-8")
        dane = urllib.parse.parse_qs(surowe, keep_blank_values=True)
        return {klucz: wartosci[0] for klucz, wartosci in dane.items()}

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

    def pobierz_dane_panelu(self, user_id: int) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
        with polaczenie_z_baza() as polaczenie:
            budzet = polaczenie.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,)).fetchone()
            transakcje = polaczenie.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY transaction_date DESC, id DESC",
                (user_id,),
            ).fetchall()
        return budzet, transakcje

    def obsluz_pliki_statyczne(self, sciezka: str) -> None:
        plik = KATALOG_STATYCZNY / sciezka.removeprefix("/static/")
        if not plik.exists() or not plik.is_file():
            self.send_error(404)
            return
        zawartosc = plik.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(zawartosc)))
        self.end_headers()
        self.wfile.write(zawartosc)

    def odpowiedz_html(self, tresc: str, status: int = 200) -> None:
        dane = tresc.encode("utf-8")
        self.send_response(status)
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
        self.send_header("Location", lokalizacja)
        if session_id:
            self.send_header("Set-Cookie", f"session_id={session_id}; HttpOnly; Path=/")
        if wyczysc_cookie:
            self.send_header("Set-Cookie", "session_id=deleted; HttpOnly; Path=/; Max-Age=0")
        self.end_headers()


def uruchom() -> None:
    przygotuj_baze()
    port = int(os.environ.get("PORT", "8000"))
    serwer = HTTPServer(("127.0.0.1", port), ObslugaBudgetBuddy)
    print(f"BudgetBuddy dziala pod adresem http://127.0.0.1:{port}")
    serwer.serve_forever()


if __name__ == "__main__":
    uruchom()

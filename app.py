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


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "budgetbuddy.db"
STATIC_DIR = BASE_DIR / "static"

sessions: dict[str, int] = {}


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
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
        conn.execute(
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
        conn.commit()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def layout(title: str, body: str, user: sqlite3.Row | None = None, flash: str = "") -> str:
    auth_links = (
        f"""
        <div class="nav-links">
            <span class="nav-user">Zalogowano jako <strong>{html.escape(user['username'])}</strong></span>
            <a href="/dashboard">Panel</a>
            <a href="/logout">Wyloguj</a>
        </div>
        """
        if user
        else """
        <div class="nav-links">
            <a href="/">Start</a>
            <a href="/login">Logowanie</a>
            <a href="/register">Rejestracja</a>
        </div>
        """
    )
    flash_html = f'<div class="flash">{html.escape(flash)}</div>' if flash else ""
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} | BudgetBuddy</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <header class="topbar">
        <div class="brand">
            <span class="brand-mark">BB</span>
            <div>
                <h1>BudgetBuddy</h1>
                <p>Prosty system zarządzania budżetem domowym</p>
            </div>
        </div>
        {auth_links}
    </header>
    <main class="page">
        {flash_html}
        {body}
    </main>
</body>
</html>"""


def hero_page() -> str:
    body = """
    <section class="hero">
        <div>
            <p class="eyebrow">Sprint 1 MVP</p>
            <h2>Pierwsza działająca wersja BudgetBuddy</h2>
            <p>
                Aplikacja umożliwia rejestrację użytkownika, logowanie, ustawianie budżetu
                miesięcznego oraz dodawanie transakcji przy pomocy prostego interfejsu WWW.
            </p>
            <div class="hero-actions">
                <a class="button" href="/register">Załóż konto</a>
                <a class="button button-secondary" href="/login">Zaloguj się</a>
            </div>
        </div>
        <div class="card">
            <h3>Zakres sprintu 1</h3>
            <ul>
                <li>Rejestracja użytkownika</li>
                <li>Logowanie i wylogowanie</li>
                <li>Dodawanie przychodów i wydatków</li>
                <li>Ustawianie miesięcznego limitu budżetu</li>
            </ul>
        </div>
    </section>
    """
    return layout("Strona główna", body)


def with_message(path: str, message: str) -> str:
    query = urllib.parse.urlencode({"message": message})
    return f"{path}?{query}"


def auth_form(title: str, action: str, submit_label: str, flash: str = "") -> str:
    body = f"""
    <section class="single-column">
        <div class="card form-card">
            <h2>{html.escape(title)}</h2>
            <form method="post" action="{action}">
                <label>Nazwa użytkownika
                    <input type="text" name="username" required minlength="3" maxlength="32">
                </label>
                <label>Hasło
                    <input type="password" name="password" required minlength="4" maxlength="64">
                </label>
                <button class="button" type="submit">{html.escape(submit_label)}</button>
            </form>
        </div>
    </section>
    """
    return layout(title, body, flash=flash)


def dashboard_page(user: sqlite3.Row, budget: sqlite3.Row | None, transactions: list[sqlite3.Row], flash: str = "") -> str:
    monthly_limit = float(budget["monthly_limit"]) if budget else 0.0
    expenses = sum(t["amount"] for t in transactions if t["transaction_type"] == "expense")
    income = sum(t["amount"] for t in transactions if t["transaction_type"] == "income")
    balance = income - expenses
    remaining = monthly_limit - expenses

    rows = ""
    for transaction in transactions:
        badge = "Wydatek" if transaction["transaction_type"] == "expense" else "Przychód"
        rows += f"""
        <tr>
            <td>{html.escape(transaction['transaction_date'])}</td>
            <td>{html.escape(transaction['title'])}</td>
            <td>{html.escape(transaction['category'])}</td>
            <td>{html.escape(badge)}</td>
            <td>{transaction['amount']:.2f} zł</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5" class="empty-state">Brak transakcji. Dodaj pierwszą pozycję poniżej.</td>
        </tr>
        """

    budget_value = f"{monthly_limit:.2f}" if budget else ""
    today = datetime.now().strftime("%Y-%m-%d")

    body = f"""
    <section class="dashboard">
        <div class="stats">
            <div class="card stat-card"><h3>Budżet miesięczny</h3><p>{monthly_limit:.2f} zł</p></div>
            <div class="card stat-card"><h3>Wydatki</h3><p>{expenses:.2f} zł</p></div>
            <div class="card stat-card"><h3>Przychody</h3><p>{income:.2f} zł</p></div>
            <div class="card stat-card"><h3>Saldo</h3><p>{balance:.2f} zł</p></div>
            <div class="card stat-card"><h3>Pozostało z budżetu</h3><p>{remaining:.2f} zł</p></div>
        </div>

        <div class="two-column">
            <div class="card">
                <h2>Ustaw budżet</h2>
                <form method="post" action="/budget">
                    <label>Limit miesięczny (zł)
                        <input type="number" name="monthly_limit" step="0.01" min="0" value="{budget_value}" required>
                    </label>
                    <button class="button" type="submit">Zapisz budżet</button>
                </form>
            </div>

            <div class="card">
                <h2>Dodaj transakcję</h2>
                <form method="post" action="/transaction">
                    <label>Nazwa transakcji
                        <input type="text" name="title" maxlength="80" required>
                    </label>
                    <label>Kwota (zł)
                        <input type="number" name="amount" step="0.01" min="0.01" required>
                    </label>
                    <label>Kategoria
                        <select name="category" required>
                            <option value="Jedzenie">Jedzenie</option>
                            <option value="Transport">Transport</option>
                            <option value="Rachunki">Rachunki</option>
                            <option value="Rozrywka">Rozrywka</option>
                            <option value="Zdrowie">Zdrowie</option>
                            <option value="Inne">Inne</option>
                        </select>
                    </label>
                    <label>Typ
                        <select name="transaction_type" required>
                            <option value="expense">Wydatek</option>
                            <option value="income">Przychód</option>
                        </select>
                    </label>
                    <label>Data
                        <input type="date" name="transaction_date" value="{today}" required>
                    </label>
                    <button class="button" type="submit">Dodaj transakcję</button>
                </form>
            </div>
        </div>

        <div class="card">
            <h2>Ostatnie transakcje</h2>
            <table>
                <thead>
                    <tr><th>Data</th><th>Nazwa</th><th>Kategoria</th><th>Typ</th><th>Kwota</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </section>
    """
    return layout("Panel użytkownika", body, user=user, flash=flash)


def demo_dashboard_page() -> str:
    user = {"username": "demo_user"}
    budget = {"monthly_limit": 2500.0}
    transactions = [
        {
            "transaction_date": "2026-04-12",
            "title": "Zakupy spozywcze",
            "category": "Jedzenie",
            "transaction_type": "expense",
            "amount": 123.45,
        },
        {
            "transaction_date": "2026-04-11",
            "title": "Wyplata",
            "category": "Inne",
            "transaction_type": "income",
            "amount": 4200.00,
        },
        {
            "transaction_date": "2026-04-10",
            "title": "Bilet miesieczny",
            "category": "Transport",
            "transaction_type": "expense",
            "amount": 150.00,
        },
    ]
    return dashboard_page(user, budget, transactions, flash="Widok demonstracyjny przygotowany do dokumentacji sprintu 1.")


class BudgetBuddyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/static/"):
            self.serve_static(path)
            return
        if path == "/":
            self.respond_html(hero_page())
            return
        if path == "/register":
            self.respond_html(auth_form("Rejestracja", "/register", "Zarejestruj"))
            return
        if path == "/login":
            self.respond_html(auth_form("Logowanie", "/login", "Zaloguj", flash=self.get_query_message()))
            return
        if path == "/demo-dashboard":
            self.respond_html(demo_dashboard_page())
            return
        if path == "/logout":
            session_id = self.get_session_id()
            if session_id:
                sessions.pop(session_id, None)
            self.redirect(with_message("/login", "Wylogowano pomyslnie."), clear_cookie=True)
            return
        if path == "/dashboard":
            user = self.require_user()
            if not user:
                return
            budget, transactions = self.load_dashboard_data(user["id"])
            self.respond_html(dashboard_page(user, budget, transactions, flash=self.get_query_message()))
            return
        self.respond_html(layout("Nie znaleziono", "<div class='card'><h2>404</h2><p>Nie znaleziono strony.</p></div>"), status=404)

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/register":
            self.handle_register()
            return
        if path == "/login":
            self.handle_login()
            return
        if path == "/budget":
            self.handle_budget()
            return
        if path == "/transaction":
            self.handle_transaction()
            return
        self.respond_html(layout("Błąd", "<div class='card'><p>Nieobsługiwane żądanie.</p></div>"), status=405)

    def handle_register(self) -> None:
        data = self.parse_form_data()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        if len(username) < 3 or len(password) < 4:
            self.respond_html(auth_form("Rejestracja", "/register", "Zarejestruj", flash="Nazwa użytkownika lub hasło są za krótkie."), status=400)
            return
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                    (username, hash_password(password), datetime.now().isoformat(timespec="seconds")),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            self.respond_html(auth_form("Rejestracja", "/register", "Zarejestruj", flash="Użytkownik o tej nazwie już istnieje."), status=400)
            return
        self.redirect(with_message("/login", "Konto zostalo utworzone. Mozesz sie zalogowac."))

    def handle_login(self) -> None:
        data = self.parse_form_data()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        with get_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, hash_password(password)),
            ).fetchone()
        if not user:
            self.respond_html(auth_form("Logowanie", "/login", "Zaloguj", flash="Niepoprawna nazwa użytkownika lub hasło."), status=401)
            return
        session_id = secrets.token_hex(16)
        sessions[session_id] = int(user["id"])
        self.redirect(with_message("/dashboard", "Zalogowano pomyslnie."), session_id=session_id)

    def handle_budget(self) -> None:
        user = self.require_user()
        if not user:
            return
        data = self.parse_form_data()
        try:
            monthly_limit = float(data.get("monthly_limit", "0"))
            if monthly_limit < 0:
                raise ValueError
        except ValueError:
            self.redirect(with_message("/dashboard", "Podaj poprawna wartosc budzetu."))
            return
        now = datetime.now().isoformat(timespec="seconds")
        with get_connection() as conn:
            exists = conn.execute("SELECT id FROM budgets WHERE user_id = ?", (user["id"],)).fetchone()
            if exists:
                conn.execute(
                    "UPDATE budgets SET monthly_limit = ?, updated_at = ? WHERE user_id = ?",
                    (monthly_limit, now, user["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO budgets (user_id, monthly_limit, updated_at) VALUES (?, ?, ?)",
                    (user["id"], monthly_limit, now),
                )
            conn.commit()
        self.redirect(with_message("/dashboard", "Budzet zostal zapisany."))

    def handle_transaction(self) -> None:
        user = self.require_user()
        if not user:
            return
        data = self.parse_form_data()
        title = data.get("title", "").strip()
        category = data.get("category", "").strip()
        transaction_type = data.get("transaction_type", "").strip()
        transaction_date = data.get("transaction_date", "").strip()
        try:
            amount = float(data.get("amount", "0"))
            datetime.strptime(transaction_date, "%Y-%m-%d")
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.redirect(with_message("/dashboard", "Nie udalo sie dodac transakcji. Sprawdz dane."))
            return
        if not title or transaction_type not in {"expense", "income"}:
            self.redirect(with_message("/dashboard", "Uzupelnij poprawnie formularz transakcji."))
            return
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO transactions (
                    user_id, title, amount, category, transaction_type, transaction_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["id"],
                    title,
                    amount,
                    category or "Inne",
                    transaction_type,
                    transaction_date,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
        self.redirect(with_message("/dashboard", "Transakcja zostala dodana."))

    def parse_form_data(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
        return {key: values[0] for key, values in parsed.items()}

    def get_session_id(self) -> str | None:
        raw_cookie = self.headers.get("Cookie")
        if not raw_cookie:
            return None
        jar = cookies.SimpleCookie()
        jar.load(raw_cookie)
        morsel = jar.get("session_id")
        return morsel.value if morsel else None

    def get_current_user(self) -> sqlite3.Row | None:
        session_id = self.get_session_id()
        user_id = sessions.get(session_id or "")
        if not user_id:
            return None
        with get_connection() as conn:
            return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def require_user(self) -> sqlite3.Row | None:
        user = self.get_current_user()
        if not user:
            self.redirect(with_message("/login", "Najpierw sie zaloguj."))
            return None
        return user

    def load_dashboard_data(self, user_id: int) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
        with get_connection() as conn:
            budget = conn.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,)).fetchone()
            transactions = conn.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY transaction_date DESC, id DESC",
                (user_id,),
            ).fetchall()
        return budget, transactions

    def get_query_message(self) -> str:
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        return params.get("message", [""])[0]

    def serve_static(self, path: str) -> None:
        file_path = STATIC_DIR / path.removeprefix("/static/")
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def respond_html(self, content: str, status: int = 200) -> None:
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, location: str, session_id: str | None = None, clear_cookie: bool = False) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        if session_id:
            self.send_header("Set-Cookie", f"session_id={session_id}; HttpOnly; Path=/")
        if clear_cookie:
            self.send_header("Set-Cookie", "session_id=deleted; HttpOnly; Path=/; Max-Age=0")
        self.end_headers()


def run() -> None:
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("127.0.0.1", port), BudgetBuddyHandler)
    print(f"BudgetBuddy działa na http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

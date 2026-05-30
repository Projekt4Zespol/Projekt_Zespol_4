import sqlite3
import threading
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
import shutil
from http.cookiejar import CookieJar
from http.server import HTTPServer

import app


class BudgetBuddyQATests(unittest.TestCase):
    def setUp(self) -> None:
        self.katalog_bazowy_testow = Path("tests_tmp")
        self.katalog_bazowy_testow.mkdir(exist_ok=True)
        self.katalog_tymczasowy = self.katalog_bazowy_testow / self._testMethodName
        if self.katalog_tymczasowy.exists():
            shutil.rmtree(self.katalog_tymczasowy)
        self.katalog_tymczasowy.mkdir(parents=True, exist_ok=True)
        self.stara_sciezka_bazy = app.SCIEZKA_BAZY
        self.stare_sesje = dict(app.sesje)
        app.SCIEZKA_BAZY = self.katalog_tymczasowy / "test_budgetbuddy.db"
        app.sesje.clear()
        app.przygotuj_baze()

        self.serwer = HTTPServer(("127.0.0.1", 0), app.ObslugaBudgetBuddy)
        self.port = self.serwer.server_address[1]
        self.watek = threading.Thread(target=self.serwer.serve_forever, daemon=True)
        self.watek.start()

    def tearDown(self) -> None:
        self.serwer.shutdown()
        self.serwer.server_close()
        self.watek.join(timeout=2)
        app.SCIEZKA_BAZY = self.stara_sciezka_bazy
        app.sesje.clear()
        app.sesje.update(self.stare_sesje)
        if self.katalog_tymczasowy.exists():
            shutil.rmtree(self.katalog_tymczasowy, ignore_errors=True)

    def nowy_klient(self) -> urllib.request.OpenerDirector:
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def otworz(self, klient: urllib.request.OpenerDirector, sciezka: str, dane: dict[str, str] | None = None) -> str:
        adres = f"http://127.0.0.1:{self.port}{sciezka}"
        if dane is None:
            odpowiedz = klient.open(adres)
        else:
            zakodowane = urllib.parse.urlencode(dane).encode("utf-8")
            odpowiedz = klient.open(adres, data=zakodowane)
        with odpowiedz:
            return odpowiedz.read().decode("utf-8")

    def zarejestruj(self, klient: urllib.request.OpenerDirector, login: str, haslo: str) -> str:
        return self.otworz(klient, "/register", {"username": login, "password": haslo})

    def zaloguj(self, klient: urllib.request.OpenerDirector, login: str, haslo: str) -> str:
        return self.otworz(klient, "/login", {"username": login, "password": haslo})

    def ustaw_budzet(self, klient: urllib.request.OpenerDirector, limit: str) -> str:
        return self.otworz(klient, "/budget", {"monthly_limit": limit})

    def dodaj_transakcje(
        self,
        klient: urllib.request.OpenerDirector,
        nazwa: str,
        kwota: str,
        kategoria: str,
        typ: str,
        data_transakcji: str,
    ) -> str:
        return self.otworz(
            klient,
            "/transaction",
            {
                "title": nazwa,
                "amount": kwota,
                "category": kategoria,
                "transaction_type": typ,
                "transaction_date": data_transakcji,
            },
        )

    def pobierz_id_transakcji(self, nazwa: str) -> int:
        with sqlite3.connect(app.SCIEZKA_BAZY) as polaczenie:
            wiersz = polaczenie.execute(
                "SELECT id FROM transactions WHERE title = ? ORDER BY id DESC",
                (nazwa,),
            ).fetchone()
        self.assertIsNotNone(wiersz)
        return int(wiersz[0])

    def test_rejestracja_logowanie_budzet_i_transakcja_dzialaja(self) -> None:
        klient = self.nowy_klient()

        strona_po_rejestracji = self.zarejestruj(klient, "damianqa", "haslo123")
        self.assertIn("Konto zostalo utworzone.", strona_po_rejestracji)

        strona_po_logowaniu = self.zaloguj(klient, "damianqa", "haslo123")
        self.assertIn("Zalogowano poprawnie.", strona_po_logowaniu)

        strona_po_budzecie = self.ustaw_budzet(klient, "1500")
        self.assertIn("Budzet zapisany.", strona_po_budzecie)

        strona_po_transakcji = self.dodaj_transakcje(
            klient,
            "Zakupy testowe",
            "45.50",
            "Jedzenie",
            "expense",
            "2026-05-21",
        )
        self.assertIn("Transakcja zostala dodana.", strona_po_transakcji)
        self.assertIn("Zakupy testowe", strona_po_transakcji)
        self.assertIn("45.50 zl", strona_po_transakcji)
        self.assertIn("1500.00 zl", strona_po_transakcji)

    def test_filtrowanie_i_sortowanie_zwieksza_uzytecznosc_panelu(self) -> None:
        klient = self.nowy_klient()
        self.zarejestruj(klient, "filtryuser", "haslo123")
        self.zaloguj(klient, "filtryuser", "haslo123")
        self.dodaj_transakcje(klient, "Pizza", "90.00", "Jedzenie", "expense", "2026-05-19")
        self.dodaj_transakcje(klient, "Autobus", "15.00", "Transport", "expense", "2026-05-20")
        self.dodaj_transakcje(klient, "Wyplata", "3000.00", "Inne", "income", "2026-05-21")

        strona = self.otworz(
            klient,
            "/dashboard/transactions?category=Jedzenie&transaction_type=expense&sortowanie=kwota_malejaco",
        )

        self.assertIn("Pizza", strona)
        self.assertNotIn("Autobus", strona)
        self.assertNotIn("Wyplata", strona)

    def test_edycja_i_usuwanie_dotycza_tylko_wlasnych_transakcji(self) -> None:
        klient_a = self.nowy_klient()
        self.zarejestruj(klient_a, "uzytkownik_a", "haslo123")
        self.zaloguj(klient_a, "uzytkownik_a", "haslo123")
        self.dodaj_transakcje(klient_a, "Laptop", "2500.00", "Inne", "expense", "2026-05-21")
        identyfikator = self.pobierz_id_transakcji("Laptop")

        klient_b = self.nowy_klient()
        self.zarejestruj(klient_b, "uzytkownik_b", "haslo123")
        self.zaloguj(klient_b, "uzytkownik_b", "haslo123")

        strona_po_nieudanym_usunieciu = self.otworz(
            klient_b,
            "/transaction/delete",
            {"transaction_id": str(identyfikator)},
        )
        self.assertIn("Nie znaleziono transakcji do usuniecia.", strona_po_nieudanym_usunieciu)

        strona_po_edycji = self.otworz(
            klient_a,
            "/transaction/update",
            {
                "transaction_id": str(identyfikator),
                "title": "Laptop sluzbowy",
                "amount": "2400.00",
                "category": "Inne",
                "transaction_type": "expense",
                "transaction_date": "2026-05-21",
            },
        )
        self.assertIn("Transakcja zostala zaktualizowana.", strona_po_edycji)
        self.assertIn("Laptop sluzbowy", strona_po_edycji)

        strona_po_usunieciu = self.otworz(
            klient_a,
            "/transaction/delete",
            {"transaction_id": str(identyfikator)},
        )
        self.assertIn("Transakcja zostala usunieta.", strona_po_usunieciu)
        self.assertNotIn("Laptop sluzbowy", strona_po_usunieciu)


if __name__ == "__main__":
    unittest.main()

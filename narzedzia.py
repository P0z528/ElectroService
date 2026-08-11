import socket
import threading
import hashlib
import secrets
from functools import wraps


def log_akcji(opis):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[LOG SYSTEMOWY] Wykonywana akcja: {opis}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class SystemPowiadomien:
    def __init__(self, funkcja_odswiezania):
        self.funkcja_odswiezania = funkcja_odswiezania
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('127.0.0.1', 65432))
            print("[KLIENT-SOCKET] Połączono z serwerem powiadomień na porcie 65432!")

            watek = threading.Thread(target=self._nasluchuj, daemon=True)
            watek.start()
        except Exception as e:
            print(f"[UWAGA - KLIENT-SOCKET] Brak serwera! Odpal 'serwer.py' przed apką! Błąd: {e}")
            self.sock = None

    def _nasluchuj(self):
        """Nasłuchuje czy serwer nie kazał odświeżyć ekranu"""
        while True:
            try:
                dane = self.sock.recv(1024)
                if not dane:
                    print("[KLIENT-SOCKET] Rozłączono z serwerem.")
                    break

                if b"ODSWIEZ" in dane:
                    print("[KLIENT-SOCKET] Serwer kazał odświeżyć!")
                    self.funkcja_odswiezania()
            except Exception as e:
                print(f"[KLIENT-SOCKET] Błąd podczas nasłuchiwania: {e}")
                break

    def wyslij_ping(self):
        """Informuje serwer, że zmieniliśmy coś w bazie"""
        if self.sock:
            try:
                self.sock.sendall(b"ZMIANA")
                print("[KLIENT-SOCKET] ---> PING wysłany do serwera!")
            except Exception as e:
                print(f"[KLIENT-SOCKET] Nie udało się wysłać PINGa: {e}")
        else:
            print("[KLIENT-SOCKET] Nie mogę wysłać PINGa - brak połączenia z serwerem.")


def hashuj_haslo(haslo):
    """Tworzy bezpieczny hash hasła z użyciem soli i PBKDF2."""
    # Generujemy losową sól (16 bajtów, format hex)
    sol = secrets.token_hex(16)

    # Hashujemy hasło (SHA-256, 100 000 iteracji)
    hash_hasla = hashlib.pbkdf2_hmac(
        'sha256',
        haslo.encode('utf-8'),
        sol.encode('utf-8'),
        100000
    ).hex()

    # Zwracamy połączoną sól i hash oddzielone znakiem '$'
    return f"{sol}${hash_hasla}"


def weryfikuj_haslo(haslo_wpisane, zapisany_hash):
    """Sprawdza, czy wpisane hasło pasuje do zapisanego hasha."""
    try:
        # Rozdzielamy zapisaną sól i hash
        sol, oryginalny_hash = zapisany_hash.split('$')

        # Hashujemy wpisane hasło używając odzyskanej soli
        nowy_hash = hashlib.pbkdf2_hmac(
            'sha256',
            haslo_wpisane.encode('utf-8'),
            sol.encode('utf-8'),
            100000
        ).hex()

        # secrets.compare_digest użyte w celu ochrony przed atakami czasowymi
        return secrets.compare_digest(oryginalny_hash, nowy_hash)
    except ValueError:
        return False  # Błędny format hasha w bazie
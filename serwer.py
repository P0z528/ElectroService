import socket
import threading
import os
import sys

HOST = '127.0.0.1'
PORT = 65432

klienci = []


def obsluz_klienta(conn, addr):
    print(f"[SERWER] Podłączył się nowy panel: {addr}")
    klienci.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            print(f"[SERWER] Dostałem sygnał od {addr}! Rozsyłam do reszty")
            for klient in klienci:
                if klient != conn:
                    try:
                        klient.sendall(b"ODSWIEZ")
                    except:
                        klienci.remove(klient)
    except ConnectionResetError:
        pass
    finally:
        if conn in klienci:
            klienci.remove(conn)
        conn.close()
        print(f"[SERWER] Panel rozłączony: {addr}")


def start_serwera():
    serwer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serwer.bind((HOST, PORT))
    serwer.listen()
    print(f"--- SERWER POWIADOMIEN DZIAŁA NA PORCIE {PORT} ---")
    print("Czekam na podłączenie paneli aplikacji...\n")

    while True:
        conn, addr = serwer.accept()
        watek = threading.Thread(target=obsluz_klienta, args=(conn, addr))
        watek.start()


if __name__ == "__main__":
    # --- DODANE ZABEZPIECZENIE BAZY DANYCH ---
    if not os.path.exists("serwis.db"):
        print("\n[BŁĄD KRYTYCZNY] Nie znaleziono pliku bazy danych 'serwis.db'!")
        print("-> Zanim uruchomisz serwer lub aplikację, wygeneruj bazę danych.")
        print("-> Uruchom najpierw skrypt: init_db.py\n")
        sys.exit(1)  # Natychmiastowe ubicie skryptu z kodem błędu
    # -----------------------------------------

    start_serwera()
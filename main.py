import sqlite3
import customtkinter as ctk
import socket
import sys

from narzedzia import weryfikuj_haslo
from tkinter import messagebox
from panel_recepcji import PanelRecepcji
from panel_admina import PanelAdmina
from panel_technika import PanelTechnika
from panel_magazynu import PanelMagazynu
from narzedzia import log_akcji, SystemPowiadomien


KOLOR_TLA = "#f8f9fa"
KOLOR_KARTY = "#ffffff"
KOLOR_GLOWNY = "#8b5cf6"
KOLOR_TEKSTU = "#212529"
KOLOR_TEKSTU_SZARY = "#6c757d"


# GŁÓWNA KLASA APLIKACJI

class SystemSerwisuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.withdraw()  # Ukrywa okno aplikacji na czas testu
        if not self._sprawdz_serwer():
            messagebox.showerror(
                "Błąd Krytyczny Systemu",
                "Serwer powiadomień jest wyłączony!\nNajpierw uruchom plik 'serwer.py', a dopiero potem włącz program."
            )
            self.destroy()
            sys.exit()  # Całkowicie ubija proces Pythona

        self.deiconify()  # Pokazuje okno, jeśli serwer odpowiedział

        # Wymuszenie jasnego motywu dla całej aplikacji
        ctk.set_appearance_mode("light")

        self.zalogowany_uzytkownik_id = None

        self.title("ElectroService - System Zarządzania")
        self.geometry("1400x800")  # Większy, domyślny rozmiar początkowy okna

        # Wymuszenie uruchomienia zmaksymalizowanego okna (pełny ekran)
        try:
            self.after(0, lambda: self.state('zoomed'))
        except Exception:
            pass  # Zabezpieczenie dla systemów Linux/Mac, gdzie 'zoomed' może nie działać

        # Zmiana kontenera na nowoczesną ramkę ctk
        kontener = ctk.CTkFrame(self, fg_color="transparent")
        kontener.pack(side="top", fill="both", expand=True)

        # Kluczowe: pozwala rozciągać się panelom wewnątrz kontenera
        kontener.grid_rowconfigure(0, weight=1)
        kontener.grid_columnconfigure(0, weight=1)

        self.panele = {}

        for PanelClass in (PanelLogowania, PanelAdmina, PanelTechnika, PanelRecepcji, PanelMagazynu):
            nazwa_panelu = PanelClass.__name__
            panel = PanelClass(parent=kontener, controller=self)
            self.panele[nazwa_panelu] = panel
            # sticky="nsew" rozciąga panel do wszystkich 4 krawędzi okna
            panel.grid(row=0, column=0, sticky="nsew")

        self.pokaz_panel("PanelLogowania")

        self.powiadamiacz = SystemPowiadomien(self.globalne_odswiezanie)

    def _sprawdz_serwer(self):
        try:
            # Szybki test połączenia na adres i port serwera z pliku serwer.py
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)  # Czekamy maksymalnie sekundę
            s.connect(('127.0.0.1', 65432))
            s.close()
            return True
        except Exception:
            return False

    def globalne_odswiezanie(self):
        self.after(0, self._odswiez_wszystkie_tabele)

    def _odswiez_wszystkie_tabele(self):
        for panel in self.panele.values():
            if hasattr(panel, 'odswiez_tabele'):
                panel.odswiez_tabele()
            if hasattr(panel, 'odswiez_liste'):
                panel.odswiez_liste()
            if hasattr(panel, 'odswiez_dane'):
                panel.odswiez_dane()

    def pokaz_panel(self, nazwa_panelu):
        panel = self.panele[nazwa_panelu]
        panel.tkraise()

        # Wymuszenie odświeżenia ekranu po zalogowaniu na inne konto
        if hasattr(panel, 'odswiez_dane'):
            panel.odswiez_dane()
        elif hasattr(panel, 'odswiez_tabele'):
            panel.odswiez_tabele()


# PANELE W GŁÓWNYM PLIKU

class PanelLogowania(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=KOLOR_TLA, corner_radius=0)
        self.controller = controller

        karta = ctk.CTkFrame(self, fg_color=KOLOR_KARTY, corner_radius=15, border_width=1, border_color="#e9ecef")
        karta.place(relx=0.5, rely=0.5, anchor="center")

        # Nagłówki
        ctk.CTkLabel(karta, text="ElectroService", font=("Arial", 24, "bold"), text_color=KOLOR_TEKSTU).pack(pady=(30, 5), padx=50)
        ctk.CTkLabel(karta, text="Zaloguj się do systemu", font=("Arial", 14), text_color=KOLOR_TEKSTU_SZARY).pack(pady=(0, 20))

        # Pole: Login
        ctk.CTkLabel(karta, text="Login:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(anchor="w", padx=40, pady=(10, 2))
        self.entry_login = ctk.CTkEntry(karta, fg_color="#f1f3f5", border_width=0, width=250, height=35)
        self.entry_login.pack(padx=40, pady=(0, 10))

        # Pole: Hasło
        ctk.CTkLabel(karta, text="Hasło:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(anchor="w", padx=40, pady=(10, 2))
        self.entry_haslo = ctk.CTkEntry(karta, show="*", fg_color="#f1f3f5", border_width=0, width=250, height=35)
        self.entry_haslo.pack(padx=40, pady=(0, 20))

        # Przycisk Zaloguj
        self.btn_zaloguj = ctk.CTkButton(karta, text="Zaloguj", fg_color=KOLOR_GLOWNY, hover_color="#7c3aed",
                                         text_color="white", height=40, command=self.zaloguj)
        self.btn_zaloguj.pack(pady=(10, 30), padx=40, fill="x")

        self.entry_haslo.bind("<Return>", lambda event: self.zaloguj())

    @log_akcji("Próba logowania użytkownika")
    def zaloguj(self):
        login = self.entry_login.get().strip()
        haslo = self.entry_haslo.get().strip()

        if not login or not haslo:
            messagebox.showwarning("Puste pola", "Wprowadź login i hasło!")
            return

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # Pobieramy hash hasła, ID i rolę po samym loginie
            cursor.execute("SELECT id, rola, haslo FROM Uzytkownicy WHERE login = ?", (login,))
            wynik = cursor.fetchone()
            conn.close()

            # wynik[2] to zapisany w bazie ciąg w formacie "sól$hash"
            if wynik and weryfikuj_haslo(haslo, wynik[2]):
                wynik = (wynik[0], wynik[1])  # (id, rola)
            else:
                wynik = None

            if wynik:
                user_id, rola = wynik

                # Zapisujemy ID zalogowanego gościa do kontrolera
                self.controller.zalogowany_uzytkownik_id = user_id

                # Czyścimy pola przed zmianą ekranu
                self.entry_login.delete(0, 'end')
                self.entry_haslo.delete(0, 'end')

                # Przekierowanie na podstawie roli z bazy danych
                if rola == 'Admin':
                    self.controller.pokaz_panel("PanelAdmina")
                elif rola == 'Technik':
                    self.controller.pokaz_panel("PanelTechnika")
                elif rola == 'Recepcja':
                    self.controller.pokaz_panel("PanelRecepcji")
                elif rola == 'Magazyn':
                    self.controller.pokaz_panel("PanelMagazynu")
                else:
                    messagebox.showerror("Błąd", "Konto nie ma przypisanej poprawnej roli w systemie!")
            else:
                messagebox.showerror("Odmowa dostępu", "Nieprawidłowy login lub hasło!")

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Wystąpił problem z bazą danych: {e}")


if __name__ == "__main__":
    app = SystemSerwisuApp()
    app.mainloop()

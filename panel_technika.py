import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import re
from narzedzia import log_akcji

# Kolory bazowe UI ze zdjęcia
KOLOR_TLA = "#f8f9fa"
KOLOR_KARTY = "#ffffff"
KOLOR_GLOWNY = "#8b5cf6"
KOLOR_TEKSTU = "#212529"
KOLOR_TEKSTU_SZARY = "#6c757d"


class PanelTechnika(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.set_appearance_mode("light")
        super().__init__(parent, fg_color=KOLOR_TLA, corner_radius=0)
        self.controller = controller

        # Główny layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._zbuduj_menu_boczne()
        self._zbuduj_obszar_roboczy()

        # Inicjalne ładowanie danych
        self.odswiez_dane()

    def _zbuduj_menu_boczne(self):
        self.menu_boczne = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=KOLOR_KARTY)
        self.menu_boczne.grid(row=0, column=0, sticky="nsew")
        self.menu_boczne.grid_rowconfigure(3, weight=1)

        # Logo / Tytuł
        ctk.CTkLabel(self.menu_boczne, text="ElectroService", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).grid(
            row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        ctk.CTkLabel(self.menu_boczne, text="Panel Technik", font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Przycisk Menu
        self.btn_menu_warsztat = ctk.CTkButton(self.menu_boczne, text="Warsztat", fg_color=KOLOR_GLOWNY,
                                               text_color="white", anchor="w", corner_radius=8)
        self.btn_menu_warsztat.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        # Profil na dole (technik)
        profil_frame = ctk.CTkFrame(self.menu_boczne, fg_color="transparent")
        profil_frame.grid(row=4, column=0, padx=15, pady=20, sticky="ew")
        ctk.CTkLabel(profil_frame, text="TE", width=30, height=30, corner_radius=15, fg_color=KOLOR_GLOWNY,
                     text_color="white").pack(side="left")
        opis_profilu = ctk.CTkFrame(profil_frame, fg_color="transparent")
        opis_profilu.pack(side="left", padx=10)
        ctk.CTkLabel(opis_profilu, text="Technik", font=("Arial", 12, "bold"), text_color=KOLOR_TEKSTU).pack(anchor="w")

        ctk.CTkButton(profil_frame, text="Wyloguj", width=60, fg_color="transparent", text_color="#ef4444",
                      hover_color="#fee2e2", command=self.wyloguj).pack(side="right")

    def _zbuduj_obszar_roboczy(self):
        self.obszar_roboczy = ctk.CTkFrame(self, fg_color=KOLOR_TLA, corner_radius=0)
        self.obszar_roboczy.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)

        # Nagłówek
        naglowek_frame = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        naglowek_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(naglowek_frame, text="Warsztat — panel technika", font=("Arial", 24, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(naglowek_frame, text="Wspólna pula zleceń i Twoje aktywne naprawy.", font=("Arial", 14),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        # KARTY KPI
        kpi_frame = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 20))
        kpi_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.kpi_dopodjecia = self._stworz_karte_kpi(kpi_frame, 0, "Do podjęcia", "0")
        self.kpi_aktywne = self._stworz_karte_kpi(kpi_frame, 1, "Moje aktywne", "0" )
        self.kpi_brakczesci = self._stworz_karte_kpi(kpi_frame, 2, "Brak części", "0")

        # RAMKI Z LISTAMI ZLECEŃ
        listy_frame = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        listy_frame.pack(fill="both", expand=True)
        listy_frame.grid_columnconfigure((0, 1), weight=1)
        listy_frame.grid_rowconfigure(0, weight=1)

        # Lewa strona - Wspólna pula
        lewa_karta = ctk.CTkFrame(listy_frame, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                  border_color="#e9ecef")
        lewa_karta.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(lewa_karta, text="Wspólna pula zleceń", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).pack(
            anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(lewa_karta, text="Zlecenia oczekujące na podjęcie przez technika.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))
        self.scroll_pula = ctk.CTkScrollableFrame(lewa_karta, fg_color="transparent")
        self.scroll_pula.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Prawa strona - Moje naprawy
        prawa_karta = ctk.CTkFrame(listy_frame, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                   border_color="#e9ecef")
        prawa_karta.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(prawa_karta, text="Moje naprawy", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).pack(
            anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(prawa_karta, text="Zlecenia, którymi się aktualnie zajmujesz.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))
        self.scroll_moje = ctk.CTkScrollableFrame(prawa_karta, fg_color="transparent")
        self.scroll_moje.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _stworz_karte_kpi(self, parent, col, tytul, wartosc):
        karta = ctk.CTkFrame(parent, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        karta.grid(row=0, column=col, sticky="nsew", padx=10)

        ctk.CTkLabel(karta, text=tytul, font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20,
                                                                                                pady=(15, 5))
        lbl_wartosc = ctk.CTkLabel(karta, text=wartosc, font=("Arial", 28, "bold"), text_color=KOLOR_TEKSTU)
        lbl_wartosc.pack(anchor="w", padx=20, pady=(0, 20))

        return lbl_wartosc

    def wyloguj(self):
        self.controller.pokaz_panel("PanelLogowania")

    def odswiez_dane(self):
        # Czyszczenie list
        for widget in self.scroll_pula.winfo_children(): widget.destroy()
        for widget in self.scroll_moje.winfo_children(): widget.destroy()

        id_zalogowanego_technika = str(getattr(self.controller, 'zalogowany_uzytkownik_id', 1)).strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # ZLECENIA WSPÓLNE
            cursor.execute("""
                SELECT Zlecenia.id, 
                       COALESCE(Urzadzenia.model, 'Nieznane urządzenie'), 
                       Zlecenia.status, 
                       COALESCE(Zlecenia.opis_usterki, 'Brak opisu')
                FROM Zlecenia
                LEFT JOIN Urzadzenia ON Zlecenia.id_urzadzenia = Urzadzenia.id
                WHERE Zlecenia.status LIKE '%W kolejce%' OR Zlecenia.status LIKE '%Przyjęte%'
            """)
            zlecenia_pula = cursor.fetchall()

            for zlec in zlecenia_pula:
                self._stworz_karte_zlecenia(self.scroll_pula, zlec, typ="pula")

            # ZLECENIA MOJE
            cursor.execute("""
                SELECT Zlecenia.id, 
                       COALESCE(Urzadzenia.model, 'Nieznane urządzenie'), 
                       Zlecenia.status,
                       COALESCE(Zlecenia.opis_usterki, 'Brak opisu')
                FROM Zlecenia
                LEFT JOIN Urzadzenia ON Zlecenia.id_urzadzenia = Urzadzenia.id
                WHERE CAST(Zlecenia.id_technika AS TEXT) = ?
                AND (
                    Zlecenia.status LIKE '%Poprawka%' OR 
                    Zlecenia.status LIKE '%W naprawie%' OR 
                    Zlecenia.status LIKE '%Czeka na części%' OR 
                    Zlecenia.status LIKE '%Części dostępne%'
                )
            """, (id_zalogowanego_technika,))
            zlecenia_moje = cursor.fetchall()

            if not zlecenia_moje:
                pusta_ramka = ctk.CTkFrame(self.scroll_moje, fg_color="#f8f9fa", border_width=1, border_color="#dee2e6",
                                           corner_radius=8, height=80)
                pusta_ramka.pack(fill="x", pady=5)
                pusta_ramka.pack_propagate(False)
                ctk.CTkLabel(pusta_ramka, text="Brak aktywnych napraw.", text_color=KOLOR_TEKSTU_SZARY).pack(
                    expand=True)
            else:
                for zlec in zlecenia_moje:
                    self._stworz_karte_zlecenia(self.scroll_moje, zlec, typ="moje")

            self.kpi_dopodjecia.configure(text=str(len(zlecenia_pula)))
            self.kpi_aktywne.configure(text=str(len(zlecenia_moje)))

            cursor.execute(
                "SELECT COUNT(*) FROM Zlecenia WHERE status LIKE '%Czeka na części%' AND CAST(id_technika AS TEXT) = ?",
                (id_zalogowanego_technika,))
            self.kpi_brakczesci.configure(text=str(cursor.fetchone()[0]))

            conn.close()
        except sqlite3.Error as e:
            from tkinter import messagebox
            messagebox.showerror("Błąd DB", f"Błąd odświeżania: {e}")

    def _stworz_karte_zlecenia(self, parent, zlec, typ):
        zid, model, status, usterka = zlec
        status_czysty = status.strip() if status else "Nieznany"

        karta = ctk.CTkFrame(parent, fg_color=KOLOR_KARTY, border_width=1, border_color="#e9ecef", corner_radius=8)
        karta.pack(fill="x", pady=5)

        karta.grid_columnconfigure(0, weight=1)
        karta.grid_rowconfigure((0, 1, 2), weight=1)

        top_frame = ctk.CTkFrame(karta, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        ctk.CTkLabel(top_frame, text=f"#{zid}", font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).pack(
            side="left", padx=(0, 10))

        kolor_statusu = "#e2e8f0"
        kolor_tekstu_statusu = "#475569"

        if 'Przyjęte' in status_czysty or 'W kolejce' in status_czysty:
            kolor_statusu, kolor_tekstu_statusu = "#e0e7ff", "#4338ca"
        elif 'Poprawka' in status_czysty:
            kolor_statusu, kolor_tekstu_statusu = "#fee2e2", "#b91c1c"
        elif 'W naprawie' in status_czysty:
            kolor_statusu, kolor_tekstu_statusu = "#dcfce7", "#15803d"
        elif 'Czeka na części' in status_czysty:
            kolor_statusu, kolor_tekstu_statusu = "#ffedd5", "#c2410c"
        elif 'Części dostępne' in status_czysty:
            kolor_statusu, kolor_tekstu_statusu = "#fce7f3", "#be185d"

        ctk.CTkLabel(top_frame, text=status_czysty, font=("Arial", 10, "bold"), fg_color=kolor_statusu,
                     text_color=kolor_tekstu_statusu, corner_radius=5, padx=8).pack(side="left")

        # --- Etykieta Typu Zlecenia bazująca na czystym opisie wygenerowanym w recepcji ---
        usterka_lower = usterka.lower() if usterka else ""

        if "wymiana:" in usterka_lower and "usługa:" in usterka_lower:
            tekst_rodzaju = "Kompleksowe"
            kolor_bg_rodzaju = "#e0f2fe"  # Niebieski
            kolor_fg_rodzaju = "#1e40af"
        elif "wymiana:" in usterka_lower or "wymiana/usługa:" in usterka_lower:  # awaryjnie dla starych wpisów
            tekst_rodzaju = "Wymiana"
            kolor_bg_rodzaju = "#fef08a"
            kolor_fg_rodzaju = "#854d0e"
        elif "usługa:" in usterka_lower:
            tekst_rodzaju = "Usługa"
            kolor_bg_rodzaju = "#e9d5ff"
            kolor_fg_rodzaju = "#6b21a8"
        else:
            tekst_rodzaju = "Ogólne"
            kolor_bg_rodzaju = "#f1f5f9"
            kolor_fg_rodzaju = "#475569"

        ctk.CTkLabel(top_frame, text=tekst_rodzaju, font=("Arial", 10, "bold"), fg_color=kolor_bg_rodzaju,
                     text_color=kolor_fg_rodzaju, corner_radius=5, padx=8).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(karta, text=model, font=("Arial", 14, "bold"), text_color=KOLOR_TEKSTU).grid(row=1, column=0,
                                                                                                  sticky="w", padx=15)

        # Skracanie opisu i jego normalne wyświetlenie
        opis_skrocony = usterka[:50] + "..." if len(usterka) > 50 else usterka
        ctk.CTkLabel(karta, text=opis_skrocony, font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).grid(row=2, column=0,
                                                                                                        sticky="w",
                                                                                                        padx=15,
                                                                                                        pady=(0, 10))

        if typ == "pula":
            btn = ctk.CTkButton(karta, text="Biorę", fg_color=KOLOR_GLOWNY, hover_color="#7c3aed", width=80,
                                command=lambda id=zid: self.rozpocznij_naprawe(id))
            btn.grid(row=1, column=1, rowspan=2, padx=15, pady=10, sticky="e")
        else:
            btn_frame = ctk.CTkFrame(karta, fg_color="transparent")
            btn_frame.grid(row=1, column=1, rowspan=2, padx=15, pady=10, sticky="e")

            # ZMIANA: Zablokowanie przycisku "Brak części" dla samych Usług
            if tekst_rodzaju == "Usługa":
                ctk.CTkButton(btn_frame, text="Brak części", fg_color="#f1f3f5", text_color="#adb5bd", border_width=1,
                              border_color="#e9ecef", hover_color="#f1f3f5", width=100, state="disabled").pack(
                    side="left", padx=5)
            else:
                ctk.CTkButton(btn_frame, text="Brak części", fg_color="white", text_color=KOLOR_TEKSTU,
                              border_width=1,
                              border_color="#dee2e6", hover_color="#f8f9fa", width=100,
                              command=lambda id=zid, mod=model: self.otworz_okno_czesci(id, mod)).pack(side="left",
                                                                                                       padx=5)

            ctk.CTkButton(btn_frame, text="Gotowe", fg_color="#059669", hover_color="#047857", text_color="white",
                          width=80, command=lambda id=zid: self.zakoncz_naprawe(id)).pack(side="left")

    @log_akcji("Technik rozpoczął naprawę")
    def rozpocznij_naprawe(self, id_zlecenia):
        # Standaryzacja: używamy castowania do `str()`, żeby zachować spójność z innymi metodami
        # i uniknąć błędu z porównywaniem typów INT w bazie
        id_zalogowanego_technika = str(getattr(self.controller, 'zalogowany_uzytkownik_id', 1)).strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # Zabezpieczenie przez rzutowanie id_technika na tekst tak jak we wcześniejszych funkcjach
            cursor.execute("SELECT status, CAST(id_technika AS TEXT) FROM Zlecenia WHERE id = ?", (id_zlecenia,))
            wynik = cursor.fetchone()

            if wynik:
                aktualny_status, przypisany_technik = wynik
                if aktualny_status not in ('W kolejce', 'Przyjęte') and przypisany_technik != id_zalogowanego_technika:
                    messagebox.showwarning("Uwaga", "To zlecenie zostało już zabrane przez innego technika!")
                    conn.close()
                    self.odswiez_dane()
                    return

            # --- NOWA LOGIKA: LIMIT 3 ZLECEŃ ---

            # 1. Obliczamy ile zadań aktualnie "trzyma" technik na warsztacie
            cursor.execute("""
                SELECT COUNT(*) FROM Zlecenia 
                WHERE CAST(id_technika AS TEXT) = ? 
                AND (
                    status LIKE '%Poprawka%' OR 
                    status LIKE '%W naprawie%' OR 
                    status LIKE '%Czeka na części%' OR 
                    status LIKE '%Części dostępne%'
                )
            """, (id_zalogowanego_technika,))
            ilosc_aktywnych = cursor.fetchone()[0]

            # 2. Sprawdzamy czy brane zlecenie to priorytet
            czy_priorytet = False
            try:
                # Jeśli masz w bazie kolumnę 'priorytet' (0 lub 1 / Tak lub Nie)
                cursor.execute("SELECT priorytet FROM Zlecenia WHERE id = ?", (id_zlecenia,))
                wynik_prio = cursor.fetchone()
                if wynik_prio and wynik_prio[0] in (1, '1', 'Tak', 'True', True):
                    czy_priorytet = True
            except sqlite3.OperationalError:
                # FALLBACK: Jeżeli w bazie nie ma jeszcze osobnej kolumny 'priorytet',
                # sprawdzamy czy w statusie albo opisie usterki nie widnieje słowo 'priorytet'.
                cursor.execute("SELECT COALESCE(opis_usterki, ''), COALESCE(status, '') FROM Zlecenia WHERE id = ?",
                               (id_zlecenia,))
                dane_zlec = cursor.fetchone()
                if dane_zlec:
                    opis_str, status_str = str(dane_zlec[0]).lower(), str(dane_zlec[1]).lower()
                    if 'priorytet' in opis_str or 'pilne' in opis_str or 'priorytet' in status_str:
                        czy_priorytet = True

            # 3. Właściwa blokada
            if ilosc_aktywnych >= 3 and not czy_priorytet:
                messagebox.showwarning(
                    "Przekroczono limit",
                    "Możesz mieć na warsztacie maksymalnie 3 aktywne zlecenia naraz!\n\n"
                    "Dokończ najpierw jedno z obecnych, chyba że chcesz wziąć zlecenie priorytetowe."
                )
                conn.close()
                return
            # -----------------------------------

            cursor.execute("""
                        UPDATE Zlecenia 
                        SET status = 'W naprawie', id_technika = ? 
                        WHERE id = ?
                    """, (id_zalogowanego_technika, id_zlecenia))

            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            self.odswiez_dane()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd DB: {e}")

    def otworz_okno_czesci(self, id_zlecenia, model_urzadzenia):
        if hasattr(self, 'okno_czesci') and self.okno_czesci.winfo_exists():
            self.okno_czesci.focus()
            return

        id_zalogowanego_technika = str(getattr(self.controller, 'zalogowany_uzytkownik_id', 1)).strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            cursor.execute("SELECT status, CAST(id_technika AS TEXT), opis_usterki FROM Zlecenia WHERE id = ?",
                           (id_zlecenia,))
            wynik = cursor.fetchone()

            self.lista_wymaganych_czesci_biezace = []
            usterka = ""
            if wynik:
                aktualny_status, przypisany_technik, usterka = wynik
                if przypisany_technik != id_zalogowanego_technika:
                    messagebox.showwarning("Brak uprawnień", "To nie jest twoje zlecenie!")
                    conn.close()
                    self.odswiez_dane()
                    return

                if 'Czeka na części' in aktualny_status:
                    messagebox.showwarning("Niedozwolona akcja", "To zlecenie już oczekuje na zamówione części!")
                    conn.close()
                    self.odswiez_dane()
                    return

                if 'Części dostępne' in aktualny_status:
                    messagebox.showwarning("Niedozwolona akcja",
                                           "Magazyn wydał już części! Nie możesz ich zamówić ponownie – dokończ naprawę i kliknij 'Gotowe'.")
                    conn.close()
                    self.odswiez_dane()
                    return

                usterka_lower = usterka.lower() if usterka else ""
                if "usługa:" in usterka_lower and "wymiana:" not in usterka_lower and "wymiana/usługa:" not in usterka_lower:
                    messagebox.showwarning("Odmowa",
                                           "To zlecenie obejmuje wyłącznie usługi serwisowe. Nie ma podstaw do zamawiania części.")
                    conn.close()
                    return

                # --- POPRAWA WYSZUKIWANIA WYMAGANYCH CZĘŚCI ---
                wymiana_match = re.search(r"wymiana:\s*([^\n;]+)", usterka_lower)
                if wymiana_match:
                    czesci_wymagane_str = wymiana_match.group(1)
                    # Rozdzielamy po przecinkach i czyścimy białe znaki
                    self.lista_wymaganych_czesci_biezace = [cz.strip() for cz in czesci_wymagane_str.split(',')]
                    # Opcjonalnie: można usunąć końcówki np. " | " lub podobne
                    self.lista_wymaganych_czesci_biezace = [cz.split('|')[0].strip() for cz in self.lista_wymaganych_czesci_biezace if cz]

            self.okno_czesci = ctk.CTkToplevel(self)
            self.okno_czesci.grab_set()
            self.okno_czesci.title(f"Części - Zlecenie #{id_zlecenia}")
            self.okno_czesci.geometry("450x400")
            self.okno_czesci.configure(fg_color=KOLOR_TLA)
            self.okno_czesci.attributes("-topmost", True)

            ctk.CTkLabel(self.okno_czesci, text=f"Zgłoś zapotrzebowanie", font=("Arial", 16, "bold"),
                         text_color=KOLOR_TEKSTU).pack(pady=(20, 5))
            ctk.CTkLabel(self.okno_czesci, text=f"Model: {model_urzadzenia}", font=("Arial", 12),
                         text_color=KOLOR_TEKSTU_SZARY).pack(pady=(0, 15))

            ramka_listy = ctk.CTkScrollableFrame(self.okno_czesci, fg_color=KOLOR_KARTY, border_width=1,
                                                 border_color="#e9ecef", corner_radius=10)
            ramka_listy.pack(pady=5, padx=20, fill="both", expand=True)

            cursor.execute("""
                SELECT ck.id, ck.nazwa_czesci 
                FROM CzesciKatalog ck
                JOIN ModeleApple m ON ck.id_modelu = m.id
                WHERE m.model = ? AND ck.typ = 'Część'
            """, (model_urzadzenia,))

            self.dostepne_czesci = cursor.fetchall()
            self.zmienne_czesci = []
            conn.close()

            if not self.dostepne_czesci:
                ctk.CTkLabel(ramka_listy, text="Brak fizycznych części w katalogu dla tego modelu.",
                             text_color=KOLOR_TEKSTU_SZARY).pack(pady=20)

            for id_czesci, nazwa_czesci in self.dostepne_czesci:
                zmienna = ctk.IntVar()
                self.zmienne_czesci.append(zmienna)

                is_required = nazwa_czesci.lower() in self.lista_wymaganych_czesci_biezace

                if is_required:
                    cb_text = f"{nazwa_czesci} (WYMAGANA)"
                    cb_font = ("Arial", 12, "bold")
                    cb_text_color = "#c2410c"
                else:
                    cb_text = nazwa_czesci
                    cb_font = ("Arial", 12)
                    cb_text_color = KOLOR_TEKSTU

                ctk.CTkCheckBox(ramka_listy, text=cb_text, variable=zmienna, fg_color=KOLOR_GLOWNY,
                                text_color=cb_text_color, font=cb_font).pack(anchor="w", padx=10, pady=8)

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Nie udało się załadować katalogu: {e}")
            if hasattr(self, 'okno_czesci') and self.okno_czesci.winfo_exists():
                self.okno_czesci.destroy()
            return

        ctk.CTkButton(self.okno_czesci, text="Zamów wybrane części",
                      command=lambda: self.zapisz_zapotrzebowanie(id_zlecenia), fg_color="#f59e0b",
                      hover_color="#d97706", text_color="white", font=("Arial", 12, "bold")).pack(pady=20)

    def zapisz_zapotrzebowanie(self, id_zlecenia):
        id_wybranych_czesci = []
        nazwy_wybranych_czesci_lower = []
        for i, zmienna in enumerate(self.zmienne_czesci):
            if zmienna.get() == 1:
                id_wybranych_czesci.append(self.dostepne_czesci[i][0])
                nazwy_wybranych_czesci_lower.append(self.dostepne_czesci[i][1].lower())

        if not id_wybranych_czesci:
            return messagebox.showwarning("Uwaga", "Zaznacz co najmniej jedną część!", parent=self.okno_czesci)

        if hasattr(self, 'lista_wymaganych_czesci_biezace') and self.lista_wymaganych_czesci_biezace:
            for wymagana_czesc_lower in self.lista_wymaganych_czesci_biezace:
                if wymagana_czesc_lower not in nazwy_wybranych_czesci_lower:
                    messagebox.showerror("Błąd",
                                           f"Musisz zaznaczyć wszystkie wymagane części.\n\nBrakuje: '{wymagana_czesc_lower.title()}'",
                                           parent=self.okno_czesci)
                    return
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            cursor.execute("UPDATE Zlecenia SET status = 'Czeka na części' WHERE id = ?", (id_zlecenia,))
            zapotrzebowania = [(id_zlecenia, id_czesci) for id_czesci in id_wybranych_czesci]
            cursor.executemany(
                "INSERT INTO Zapotrzebowania (id_zlecenia, id_czesci_katalog, status) VALUES (?, ?, 'Oczekuje')",
                zapotrzebowania)

            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            messagebox.showinfo("Sukces", "Zapotrzebowanie wysłane. Naprawa wstrzymana.", parent=self.okno_czesci)
            self.okno_czesci.destroy()
            self.odswiez_dane()

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd: {e}", parent=self.okno_czesci)

    @log_akcji("Technik zakończył naprawę - wysyła do kontroli")
    def zakoncz_naprawe(self, id_zlecenia):
        id_zalogowanego_technika = str(getattr(self.controller, 'zalogowany_uzytkownik_id', 1)).strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # Zabezpieczenie ID przez CAST
            cursor.execute("SELECT status, CAST(id_technika AS TEXT) FROM Zlecenia WHERE id = ?", (id_zlecenia,))
            wynik = cursor.fetchone()

            if wynik:
                aktualny_status, przypisany_technik = wynik
                if przypisany_technik != id_zalogowanego_technika:
                    messagebox.showwarning("Brak uprawnień", "Nie możesz zakończyć zlecenia innego technika!")
                    conn.close()
                    self.odswiez_dane()
                    return
                # Elastyczne sprawdzanie (odporne na spacje)
                if 'naprawie' not in aktualny_status and 'dostępne' not in aktualny_status and 'Poprawka' not in aktualny_status:
                    messagebox.showwarning("Niedozwolona akcja",
                                           "Aby zakończyć naprawę, sprzęt musi być w trakcie naprawy lub na poprawce!")
                    conn.close()
                    return

            cursor.execute("UPDATE Zlecenia SET status = 'Do kontroli' WHERE id = ?", (id_zlecenia,))
            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            messagebox.showinfo("Sukces", "Sprzęt naprawiony! Przekazano do kontroli.")
            self.odswiez_dane()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd", f"Błąd DB: {e}")
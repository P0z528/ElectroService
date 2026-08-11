import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from narzedzia import log_akcji

# Kolory bazowe UI
KOLOR_TLA = "#f8f9fa"
KOLOR_KARTY = "#ffffff"
KOLOR_GLOWNY = "#8b5cf6"
KOLOR_TEKSTU = "#212529"
KOLOR_TEKSTU_SZARY = "#6c757d"


class PanelMagazynu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.set_appearance_mode("light")
        super().__init__(parent, fg_color=KOLOR_TLA, corner_radius=0)
        self.controller = controller

        self.checkboxy_zapotrzebowania = []  # Przechowuje krotki (IntVar, dane_wiersza)

        # Główny layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._zbuduj_menu_boczne()
        self._zbuduj_obszar_roboczy()

        # Inicjalizacja
        self._laduj_typy_do_zamowienia()
        self.pokaz_zakladke("zapotrzebowania")

    def _zbuduj_menu_boczne(self):
        self.menu_boczne = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=KOLOR_KARTY)
        self.menu_boczne.grid(row=0, column=0, sticky="nsew")
        self.menu_boczne.grid_rowconfigure(5, weight=1)

        # Logo / Tytuł
        ctk.CTkLabel(self.menu_boczne, text="ElectroService", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).grid(
            row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        ctk.CTkLabel(self.menu_boczne, text="Panel Magazynier", font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        #Przyciski Menu
        self.btn_menu_zap = ctk.CTkButton(self.menu_boczne, text="Zapotrzebowania", fg_color="transparent",
                                          text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8, hover_color="#f1f3f5",
                                          command=lambda: self.pokaz_zakladke("zapotrzebowania"))
        self.btn_menu_zap.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_zakupy = ctk.CTkButton(self.menu_boczne, text="Lista zakupów", fg_color="transparent",
                                             text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                             hover_color="#f1f3f5",
                                             command=lambda: self.pokaz_zakladke("zakupy"))
        self.btn_menu_zakupy.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_stan = ctk.CTkButton(self.menu_boczne, text="Stan magazynu", fg_color="transparent",
                                           text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8, hover_color="#f1f3f5",
                                           command=lambda: self.pokaz_zakladke("stan"))
        self.btn_menu_stan.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        # Profil na dole
        profil_frame = ctk.CTkFrame(self.menu_boczne, fg_color="transparent")
        profil_frame.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        ctk.CTkLabel(profil_frame, text="MA", width=30, height=30, corner_radius=15, fg_color=KOLOR_GLOWNY,
                     text_color="white").pack(side="left")
        opis_profilu = ctk.CTkFrame(profil_frame, fg_color="transparent")
        opis_profilu.pack(side="left", padx=10)
        ctk.CTkLabel(opis_profilu, text="magazyn", font=("Arial", 12, "bold"), text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(opis_profilu, text="Magazynier", font=("Arial", 10), text_color=KOLOR_TEKSTU_SZARY).pack(
            anchor="w")

        ctk.CTkButton(profil_frame, text="Wyloguj", width=60, fg_color="transparent", text_color="#ef4444",
                      hover_color="#fee2e2", command=self.wyloguj).pack(side="right")

    def _zbuduj_obszar_roboczy(self):
        self.obszar_roboczy = ctk.CTkFrame(self, fg_color=KOLOR_TLA, corner_radius=0)
        self.obszar_roboczy.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)

        # Nagłówek
        naglowek_frame = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        naglowek_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(naglowek_frame, text="Magazyn — gospodarka materiałowa", font=("Arial", 24, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(naglowek_frame, text="Obsługa zapotrzebowań od techników, lista zakupów i stany magazynowe.",
                     font=("Arial", 14), text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        # KPI
        kpi_frame = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 20))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_zap = self._stworz_karte_kpi(kpi_frame, 0, "Aktywne zapotrzebowania", "0", "#f97316")
        self.kpi_zakupy = self._stworz_karte_kpi(kpi_frame, 1, "Pozycje na liście zakupów", "0", KOLOR_GLOWNY)
        self.kpi_stan = self._stworz_karte_kpi(kpi_frame, 2, "Pozycje w magazynie", "0", "#10b981")
        self.kpi_lacznie = self._stworz_karte_kpi(kpi_frame, 3, "Sztuki łącznie", "0", "#0ea5e9")

        # Kontenery zakładek
        self.kontener_glowny = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        self.kontener_glowny.pack(fill="both", expand=True)

        self.zakladka_zapotrzebowania = ctk.CTkFrame(self.kontener_glowny, fg_color="transparent")
        self.zakladka_lista_zakupow = ctk.CTkFrame(self.kontener_glowny, fg_color="transparent")
        self.zakladka_stan_magazynu = ctk.CTkFrame(self.kontener_glowny, fg_color="transparent")

        self._zbuduj_zakladke_zapotrzebowania()
        self._zbuduj_zakladke_lista_zakupow()
        self._zbuduj_zakladke_stan_magazynu()

    def _stworz_karte_kpi(self, parent, col, tytul, wartosc, kolor):
        karta = ctk.CTkFrame(parent, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        karta.grid(row=0, column=col, sticky="nsew", padx=10)

        gora = ctk.CTkFrame(karta, fg_color="transparent")
        gora.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(gora, text=tytul, font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).pack(side="left")

        lbl_wartosc = ctk.CTkLabel(karta, text=wartosc, font=("Arial", 28, "bold"), text_color=KOLOR_TEKSTU)
        lbl_wartosc.pack(anchor="w", padx=20, pady=(0, 15))
        return lbl_wartosc

    def _zbuduj_zakladke_zapotrzebowania(self):
        karta = ctk.CTkFrame(self.zakladka_zapotrzebowania, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                             border_color="#e9ecef")
        karta.pack(fill="both", expand=True)

        ctk.CTkLabel(karta, text="Nowe zapotrzebowania od techników", font=("Arial", 16, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(karta, text="Zaznacz pozycje, aby wydać je z magazynu lub dodać do listy zamówień.",
                     font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))

        # Nagłówki
        naglowki_frame = ctk.CTkFrame(karta, fg_color="#f8f9fa", corner_radius=5)
        naglowki_frame.pack(fill="x", padx=20)
        naglowki_frame.grid_columnconfigure(0, minsize=50)  # Checkbox
        naglowki_frame.grid_columnconfigure(1, weight=1)  # ID Zap
        naglowki_frame.grid_columnconfigure(2, weight=1)  # ID Zlec
        naglowki_frame.grid_columnconfigure(3, weight=4)  # Model
        naglowki_frame.grid_columnconfigure(4, weight=3)  # Czesc
        naglowki_frame.grid_columnconfigure(5, weight=1)  # Stan

        kolumny = ["", "ID Zap.", "ID Zlec.", "Model urządzenia", "Nazwa części", "Stan"]
        for i, text in enumerate(kolumny):
            ctk.CTkLabel(naglowki_frame, text=text, font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).grid(
                row=0, column=i, sticky="w", padx=10, pady=8)

        self.scroll_zap = ctk.CTkScrollableFrame(karta, fg_color="transparent")
        self.scroll_zap.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Przyciski dolne
        btn_frame = ctk.CTkFrame(karta, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Wydaj zaznaczoną część", fg_color="white", text_color=KOLOR_TEKSTU,
                      border_width=1, border_color="#dee2e6", hover_color="#f8f9fa", command=self.wydaj_czesc).grid(
            row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Dodaj do listy zamówień", fg_color=KOLOR_GLOWNY, text_color="white",
                      hover_color="#7c3aed", command=self.dodaj_do_zamowienia).grid(row=0, column=1, sticky="ew")

    def _zbuduj_zakladke_lista_zakupow(self):
        self.zakladka_lista_zakupow.grid_columnconfigure(0, weight=2)
        self.zakladka_lista_zakupow.grid_columnconfigure(1, weight=1)
        self.zakladka_lista_zakupow.grid_rowconfigure(0, weight=1)

        # Lewa strona - Lista
        lewa_karta = ctk.CTkFrame(self.zakladka_lista_zakupow, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                  border_color="#e9ecef")
        lewa_karta.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(lewa_karta, text="Lista zakupów (do zamówienia u dostawcy)", font=("Arial", 16, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(lewa_karta, text="Po dostawie zaksięguj — pozycje trafią na stan magazynu.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))

        self.scroll_zakupy = ctk.CTkScrollableFrame(lewa_karta, fg_color="transparent")
        self.scroll_zakupy.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        ctk.CTkButton(lewa_karta, text="+ Zaksięguj dostawę z listy zakupów", fg_color="#059669", hover_color="#047857",
                      text_color="white", command=self.przyjmij_dostawe_z_listy).pack(fill="x", padx=20, pady=20)

        # Prawa strona - Ręczne dodawanie
        prawa_karta = ctk.CTkFrame(self.zakladka_lista_zakupow, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                   border_color="#e9ecef")
        prawa_karta.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(prawa_karta, text="Ręczne uzupełnianie zapasów", font=("Arial", 16, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(prawa_karta, text="Dodaj pozycję spoza zapotrzebowań.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(prawa_karta, text="Typ urządzenia", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 2))
        self.combo_typ_zam = ctk.CTkComboBox(prawa_karta, state="readonly", fg_color="#f1f3f5", border_width=0,
                                             command=self._laduj_modele_do_zamowienia)
        self.combo_typ_zam.pack(fill="x", padx=20)

        ctk.CTkLabel(prawa_karta, text="Model urządzenia", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(15, 2))
        self.combo_model_zam = ctk.CTkComboBox(prawa_karta, state="readonly", fg_color="#f1f3f5", border_width=0,
                                               command=self._laduj_czesci_do_zamowienia)
        self.combo_model_zam.pack(fill="x", padx=20)

        ctk.CTkLabel(prawa_karta, text="Dostępna część", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(15, 2))
        self.combo_czesc_zam = ctk.CTkComboBox(prawa_karta, state="readonly", fg_color="#f1f3f5", border_width=0)
        self.combo_czesc_zam.pack(fill="x", padx=20)

        ctk.CTkLabel(prawa_karta, text="Ilość sztuk", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(15, 2))
        self.ent_ilosc_zam = ctk.CTkEntry(prawa_karta, fg_color="#f1f3f5", border_width=0)
        self.ent_ilosc_zam.insert(0, "1")
        self.ent_ilosc_zam.pack(fill="x", padx=20)

        ctk.CTkButton(prawa_karta, text="+ Dodaj do listy", fg_color=KOLOR_GLOWNY, hover_color="#7c3aed",
                      text_color="white", command=self.reczne_dodanie_do_zamowienia).pack(fill="x", padx=20, pady=25)

    def _zbuduj_zakladke_stan_magazynu(self):
        karta = ctk.CTkFrame(self.zakladka_stan_magazynu, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                             border_color="#e9ecef")
        karta.pack(fill="both", expand=True)

        ctk.CTkLabel(karta, text="Aktualny stan magazynu", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).pack(
            anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(karta, text="Wszystkie części dostępne do wydania technikom.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 15))

        # Nagłówki
        naglowki_frame = ctk.CTkFrame(karta, fg_color="#f8f9fa", corner_radius=5)
        naglowki_frame.pack(fill="x", padx=20)
        naglowki_frame.grid_columnconfigure(0, weight=1)
        naglowki_frame.grid_columnconfigure(1, weight=5)
        naglowki_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(naglowki_frame, text="ID", font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).grid(row=0,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                padx=10,
                                                                                                                pady=8)
        ctk.CTkLabel(naglowki_frame, text="Część (Model — Nazwa)", font=("Arial", 11, "bold"),
                     text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=1, sticky="w", padx=10, pady=8)
        ctk.CTkLabel(naglowki_frame, text="Sztuk na stanie", font=("Arial", 11, "bold"),
                     text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=2, sticky="e", padx=10, pady=8)

        self.scroll_stan = ctk.CTkScrollableFrame(karta, fg_color="transparent")
        self.scroll_stan.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    def pokaz_zakladke(self, nazwa):
        # Ukrywanie
        self.zakladka_zapotrzebowania.pack_forget()
        self.zakladka_lista_zakupow.pack_forget()
        self.zakladka_stan_magazynu.pack_forget()

        # Reset kolorów przycisków w menu bocznym (dodany jasnoszary hover_color)
        self.btn_menu_zap.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_zakupy.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_stan.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")

        # Pokazywanie ramki i zaznaczanie aktywnego przycisku w menu bocznym (dodany ciemniejszy hover_color)
        if nazwa == "zapotrzebowania":
            self.zakladka_zapotrzebowania.pack(fill="both", expand=True)
            self.btn_menu_zap.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
        elif nazwa == "zakupy":
            self.zakladka_lista_zakupow.pack(fill="both", expand=True)
            self.btn_menu_zakupy.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
        elif nazwa == "stan":
            self.zakladka_stan_magazynu.pack(fill="both", expand=True)
            self.btn_menu_stan.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")

        self.odswiez_tabele()

    # === LOGIKA BAZY DANYCH ===

    def _laduj_typy_do_zamowienia(self):
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT typ FROM ModeleApple ORDER BY typ")
            typy = [row[0] for row in cursor.fetchall()]
            self.combo_typ_zam.configure(values=typy)
            conn.close()
        except sqlite3.Error as e:
            print(f"Błąd ładowania typów: {e}")

    def _laduj_modele_do_zamowienia(self, wartosc):
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT model FROM ModeleApple WHERE typ = ? ORDER BY model", (wartosc,))
            modele = [row[0] for row in cursor.fetchall()]
            self.combo_model_zam.configure(values=modele)
            self.combo_model_zam.set('')
            self.combo_czesc_zam.set('')
            self.combo_czesc_zam.configure(values=[])
            conn.close()
        except sqlite3.Error as e:
            print(f"Błąd ładowania modeli: {e}")

    def _laduj_czesci_do_zamowienia(self, wartosc):
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # Zapytanie filtrujące po kolumnie 'typ'
            cursor.execute("""
                SELECT ck.nazwa_czesci 
                FROM CzesciKatalog ck 
                JOIN ModeleApple m ON ck.id_modelu = m.id 
                WHERE m.model = ? AND ck.typ = 'Część'
                ORDER BY ck.nazwa_czesci
            """, (wartosc,))

            czesci = [row[0] for row in cursor.fetchall()]

            self.combo_czesc_zam.configure(values=czesci)
            self.combo_czesc_zam.set('')
            conn.close()
        except sqlite3.Error as e:
            print(f"Błąd ładowania części: {e}")

    def odswiez_tabele(self):
        # Czyszczenie
        for widget in self.scroll_zap.winfo_children(): widget.destroy()
        for widget in self.scroll_zakupy.winfo_children(): widget.destroy()
        for widget in self.scroll_stan.winfo_children(): widget.destroy()
        self.checkboxy_zapotrzebowania.clear()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # --- ZAPOTRZEBOWANIA ---
            cursor.execute("""
                SELECT z.id, z.id_zlecenia, m.model, ck.nazwa_czesci, ck.id, z.status
                FROM Zapotrzebowania z
                JOIN CzesciKatalog ck ON z.id_czesci_katalog = ck.id
                JOIN ModeleApple m ON ck.id_modelu = m.id
                WHERE z.status IN ('Oczekuje', 'Do zamówienia') AND z.id_zlecenia > 0
            """)
            zap_dane = cursor.fetchall()

            for z in zap_dane:
                id_zap, id_zlec, model, nazwa, id_ck, status = z

                wiersz = ctk.CTkFrame(self.scroll_zap, fg_color="transparent", border_width=0)
                wiersz.pack(fill="x", pady=2)
                ctk.CTkFrame(wiersz, fg_color="#e9ecef", height=1).pack(side="bottom", fill="x")  # Separator

                wiersz_kontener = ctk.CTkFrame(wiersz, fg_color="transparent")
                wiersz_kontener.pack(fill="x", pady=8)

                wiersz_kontener.grid_columnconfigure(0, minsize=50)
                wiersz_kontener.grid_columnconfigure(1, weight=1)
                wiersz_kontener.grid_columnconfigure(2, weight=1)
                wiersz_kontener.grid_columnconfigure(3, weight=4)
                wiersz_kontener.grid_columnconfigure(4, weight=3)
                wiersz_kontener.grid_columnconfigure(5, weight=1)

                var = ctk.IntVar()
                self.checkboxy_zapotrzebowania.append((var, z))

                ctk.CTkCheckBox(wiersz_kontener, text="", variable=var, width=20, fg_color=KOLOR_GLOWNY).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10)
                ctk.CTkLabel(wiersz_kontener, text=str(id_zap), font=("Arial", 12)).grid(row=0, column=1, sticky="w",
                                                                                         padx=10)
                ctk.CTkLabel(wiersz_kontener, text=f"#{id_zlec}", font=("Arial", 12)).grid(row=0, column=2, sticky="w",
                                                                                           padx=10)
                ctk.CTkLabel(wiersz_kontener, text=model, font=("Arial", 12)).grid(row=0, column=3, sticky="w", padx=10)
                ctk.CTkLabel(wiersz_kontener, text=nazwa, font=("Arial", 12)).grid(row=0, column=4, sticky="w", padx=10)

                if status == 'Do zamówienia':
                    ramka_zamowiono = ctk.CTkFrame(wiersz_kontener, fg_color="#e0f2fe", border_width=1,
                                                   border_color="#7dd3fc", corner_radius=10)
                    ramka_zamowiono.grid(row=0, column=5, sticky="w", padx=10)
                    ctk.CTkLabel(ramka_zamowiono, text="Zamówiono", text_color="#0284c7", font=("Arial", 11, "bold")).pack(padx=8,
                                                                                                                          pady=2)
                else:
                    # Sprawdzenie dostępności do etykietki "Brak" / "Jest"
                    cursor.execute("SELECT ilosc FROM Czesci WHERE id_czesci_katalog = ?", (id_ck,))
                    stan = cursor.fetchone()
                    czy_jest = stan and stan[0] > 0

                    if czy_jest:
                        ctk.CTkLabel(wiersz_kontener, text="Jest", text_color="#059669", fg_color="#d1fae5",
                                     corner_radius=10, padx=8, font=("Arial", 11, "bold")).grid(row=0, column=5, sticky="w",
                                                                                                padx=10)
                    else:
                        ramka_brak = ctk.CTkFrame(wiersz_kontener, fg_color="#fef3c7", border_width=1,
                                                  border_color="#fcd34d", corner_radius=10)
                        ramka_brak.grid(row=0, column=5, sticky="w", padx=10)
                        ctk.CTkLabel(ramka_brak, text="Brak", text_color="#d97706", font=("Arial", 11, "bold")).pack(padx=8,
                                                                                                                     pady=2)

            # --- LISTA ZAKUPÓW ---
            cursor.execute("""
                SELECT ck.id, m.model, ck.nazwa_czesci, COUNT(z.id)
                FROM Zapotrzebowania z
                JOIN CzesciKatalog ck ON z.id_czesci_katalog = ck.id
                JOIN ModeleApple m ON ck.id_modelu = m.id
                WHERE z.status = 'Do zamówienia'
                GROUP BY ck.id, m.model, ck.nazwa_czesci
            """)
            zakupy_dane = cursor.fetchall()

            if not zakupy_dane:
                pusta_ramka = ctk.CTkFrame(self.scroll_zakupy, fg_color="transparent", border_width=1,
                                           border_color="#dee2e6", corner_radius=8, height=80)
                pusta_ramka.pack(fill="x", pady=5)
                pusta_ramka.pack_propagate(False)
                ctk.CTkLabel(pusta_ramka, text="Lista zakupów jest pusta.", text_color=KOLOR_TEKSTU_SZARY).pack(
                    expand=True)
            else:
                for z in zakupy_dane:
                    id_ck_zakupy, model, nazwa, ilosc = z
                    w = ctk.CTkFrame(self.scroll_zakupy, fg_color="transparent", border_width=0)
                    w.pack(fill="x", pady=2)
                    ctk.CTkFrame(w, fg_color="#e9ecef", height=1).pack(side="bottom", fill="x")

                    wk = ctk.CTkFrame(w, fg_color="transparent")
                    wk.pack(fill="x", pady=8)
                    wk.grid_columnconfigure(0, weight=4)
                    wk.grid_columnconfigure(1, weight=4)
                    wk.grid_columnconfigure(2, weight=1)

                    ctk.CTkLabel(wk, text=model, font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10)
                    ctk.CTkLabel(wk, text=nazwa, font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10)

                    # Kontener na ilość sztuk i przycisk "+"
                    ilosc_frame = ctk.CTkFrame(wk, fg_color="transparent")
                    ilosc_frame.grid(row=0, column=2, sticky="e", padx=10)

                    ctk.CTkLabel(ilosc_frame, text=f"{ilosc} szt.", font=("Arial", 12, "bold")).pack(side="left",
                                                                                                     padx=(0, 10))

                    # Nowy przycisk "+"
                    ctk.CTkButton(ilosc_frame, text="+", width=28, height=28, fg_color=KOLOR_GLOWNY,
                                  hover_color="#7c3aed",
                                  command=lambda m=model, n=nazwa: self.otworz_okno_dodaj_ilosc(m, n)).pack(side="left")

            # --- STAN MAGAZYNU ---
            cursor.execute("""
                SELECT c.id, m.model || ' — ' || ck.nazwa_czesci, c.ilosc 
                FROM Czesci c 
                JOIN CzesciKatalog ck ON c.id_czesci_katalog = ck.id
                JOIN ModeleApple m ON ck.id_modelu = m.id
                ORDER BY m.model, ck.nazwa_czesci
            """)
            stan_dane = cursor.fetchall()
            lacznie_sztuk = sum(row[2] for row in stan_dane)
            pozycje_w_magazynie = len(stan_dane)

            for z in stan_dane:
                cid, opis, ilosc = z
                w = ctk.CTkFrame(self.scroll_stan, fg_color="transparent", border_width=0)
                w.pack(fill="x", pady=2)
                ctk.CTkFrame(w, fg_color="#e9ecef", height=1).pack(side="bottom", fill="x")

                wk = ctk.CTkFrame(w, fg_color="transparent")
                wk.pack(fill="x", pady=8)
                wk.grid_columnconfigure(0, weight=1)
                wk.grid_columnconfigure(1, weight=5)
                wk.grid_columnconfigure(2, weight=1)

                ctk.CTkLabel(wk, text=str(cid), font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10)
                ctk.CTkLabel(wk, text=opis, font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10)

                # Dynamiczny kolor etykiety ilości (jak na zrzucie ekranu)
                # Dynamiczny kolor etykiety ilości (jak na zrzucie ekranu)
                kolor_badge = "#d1fae5" if ilosc > 2 else "#fef3c7"
                kolor_text = "#059669" if ilosc > 2 else "#d97706"
                border = "#a7f3d0" if ilosc > 2 else "#fcd34d"

                ramka_badge = ctk.CTkFrame(wk, fg_color=kolor_badge, border_width=1, border_color=border,
                                           corner_radius=10)
                ramka_badge.grid(row=0, column=2, sticky="e", padx=10)
                ctk.CTkLabel(ramka_badge, text=f"{ilosc} szt.", font=("Arial", 11, "bold"), text_color=kolor_text).pack(
                    padx=8, pady=2)

                # --- AKTUALIZACJA KPI I ZAKŁADEK ---
                self.kpi_zap.configure(text=str(len(zap_dane)))
                self.kpi_zakupy.configure(text=str(len(zakupy_dane)))
                self.kpi_stan.configure(text=str(pozycje_w_magazynie))
                self.kpi_lacznie.configure(text=str(lacznie_sztuk))

                # Aktualizacja tekstu przycisków w nowym menu bocznym
                self.btn_menu_zap.configure(text=f"Zapotrzebowania   {len(zap_dane)}")
                self.btn_menu_zakupy.configure(text=f"Lista zakupów   {len(zakupy_dane)}")

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd odświeżania tabel: {e}")

    def _pobierz_zaznaczone_zapotrzebowania(self):
        zaznaczone = []
        for var, dane in self.checkboxy_zapotrzebowania:
            if var.get() == 1:
                zaznaczone.append(dane)
        return zaznaczone

    @log_akcji("Magazyn: Wydano część ze stanu")
    def wydaj_czesc(self):
        wybrane = self._pobierz_zaznaczone_zapotrzebowania()
        if not wybrane:
            return messagebox.showwarning("Brak wyboru", "Zaznacz co najmniej jedno zapotrzebowanie do realizacji!")

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            wydane_czesci = []

            for z in wybrane:
                id_zapotrzebowania, id_zlecenia, model, nazwa_czesci, id_ck, status = z

                cursor.execute("SELECT id, ilosc FROM Czesci WHERE id_czesci_katalog = ?", (id_ck,))
                czesc_na_stanie = cursor.fetchone()

                if not czesc_na_stanie or czesc_na_stanie[1] <= 0:
                    messagebox.showwarning("Brak na stanie", f"Brak na stanie: {nazwa_czesci} do {model}")
                    continue

                id_czesci, nowa_ilosc = czesc_na_stanie[0], czesc_na_stanie[1] - 1
                cursor.execute("UPDATE Czesci SET ilosc = ? WHERE id = ?", (nowa_ilosc, id_czesci))
                cursor.execute("UPDATE Zapotrzebowania SET status = 'Wydano' WHERE id = ?", (id_zapotrzebowania,))

                wydane_czesci.append(nazwa_czesci)

                # Odblokowanie zlecenia dla technika, jeśli wszystko wydano
                cursor.execute("SELECT COUNT(*) FROM Zapotrzebowania WHERE id_zlecenia = ? AND status != 'Wydano'",
                               (id_zlecenia,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("UPDATE Zlecenia SET status = 'Części dostępne' WHERE id = ?", (id_zlecenia,))
                    messagebox.showinfo("Zlecenie odblokowane",
                                        f"Wydano komplet części. Technik może podjąć zlecenie #{id_zlecenia}.")

            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()

            if wydane_czesci:
                messagebox.showinfo("Sukces", f"Pomyślnie wydano zaznaczone części z magazynu.")

            self.odswiez_tabele()

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd wydawania: {e}")

    @log_akcji("Magazyn: Przeniesiono zapotrzebowanie technika do zamówienia")
    def dodaj_do_zamowienia(self):
        wybrane = self._pobierz_zaznaczone_zapotrzebowania()
        if not wybrane:
            return messagebox.showwarning("Brak wyboru", "Zaznacz zapotrzebowanie, które chcesz zamówić!")

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            przeniesiono_cos = False

            for z in wybrane:
                id_zap, id_zlec, model, nazwa_czesci, id_ck, status = z

                if status == 'Do zamówienia':
                    continue

                # --- ZABEZPIECZENIE: Sprawdzenie stanu magazynowego ---
                cursor.execute("SELECT ilosc FROM Czesci WHERE id_czesci_katalog = ?", (id_ck,))
                stan = cursor.fetchone()

                if stan and stan[0] > 0:
                    messagebox.showwarning("Dostępne na stanie",
                                           f"Część '{nazwa_czesci}' do '{model}' jest już w magazynie!\nSkorzystaj z przycisku 'Wydaj zaznaczoną część'.")
                    continue  # Pomija dodawanie do zamówienia
                # ------------------------------------------------------

                cursor.execute("UPDATE Zapotrzebowania SET status = 'Do zamówienia' WHERE id = ?", (id_zap,))
                przeniesiono_cos = True

            conn.commit()
            conn.close()

            if przeniesiono_cos:
                messagebox.showinfo("Przeniesiono",
                                    "Pozycje (których brakowało na stanie) zostały przeniesione do listy zakupów.")

            self.odswiez_tabele()

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd: {e}")

    @log_akcji("Magazyn: Ręczne dodanie części do listy zakupów")
    def reczne_dodanie_do_zamowienia(self):
        model = self.combo_model_zam.get()
        czesc = self.combo_czesc_zam.get()
        ilosc = self.ent_ilosc_zam.get()

        if not model or not czesc or not ilosc.isdigit() or int(ilosc) <= 0:
            messagebox.showwarning("Błąd", "Proszę uzupełnić wszystkie pola")
            return

        ilosc = int(ilosc)

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            cursor.execute("""
                    SELECT ck.id 
                    FROM CzesciKatalog ck 
                    JOIN ModeleApple m ON ck.id_modelu = m.id 
                    WHERE m.model = ? AND ck.nazwa_czesci = ? AND ck.typ = 'Część'
                """, (model, czesc))
            wynik = cursor.fetchone()

            if not wynik:
                messagebox.showerror("Błąd", "Nie znaleziono wybranej części w katalogu.")
                conn.close()
                return

            id_ck = wynik[0]

            cursor.execute("PRAGMA foreign_keys = OFF;")
            for _ in range(ilosc):
                cursor.execute("INSERT INTO Zapotrzebowania (id_zlecenia, id_czesci_katalog, status) VALUES (?, ?, ?)",
                               (0, id_ck, 'Do zamówienia'))
            cursor.execute("PRAGMA foreign_keys = ON;")

            conn.commit()
            conn.close()

            messagebox.showinfo("Sukces", f"Dodano {ilosc} szt. '{czesc}' ({model}) do listy zakupów.")
            self.odswiez_tabele()

            self.combo_czesc_zam.set('')
            self.ent_ilosc_zam.delete(0, 'end')
            self.ent_ilosc_zam.insert(0, '1')

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Wystąpił błąd bazy danych: {e}")

    @log_akcji("Magazyn: Zaksięgowano dostawę")
    def przyjmij_dostawe_z_listy(self):
        if not messagebox.askyesno("Dostawa", "Czy chcesz zaksięgować dostawę WSZYSTKICH pozycji z listy zamówień?"):
            return

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            # Pobranie elementów z listy zakupów
            cursor.execute("""
                SELECT ck.id, m.model, ck.nazwa_czesci, COUNT(z.id)
                FROM Zapotrzebowania z
                JOIN CzesciKatalog ck ON z.id_czesci_katalog = ck.id
                JOIN ModeleApple m ON ck.id_modelu = m.id
                WHERE z.status = 'Do zamówienia'
                GROUP BY ck.id, m.model, ck.nazwa_czesci
            """)
            zakupy_dane = cursor.fetchall()

            if not zakupy_dane:
                conn.close()
                return messagebox.showinfo("Pusto", "Lista zakupów jest pusta.")

            for z in zakupy_dane:
                id_ck, model, nazwa_czesci, ilosc = z

                cursor.execute("SELECT id, ilosc FROM Czesci WHERE id_czesci_katalog = ?", (id_ck,))
                istniejaca = cursor.fetchone()

                if istniejaca:
                    cursor.execute("UPDATE Czesci SET ilosc = ? WHERE id = ?", (istniejaca[1] + ilosc, istniejaca[0]))
                else:
                    cursor.execute("INSERT INTO Czesci (id_czesci_katalog, ilosc) VALUES (?, ?)", (id_ck, ilosc))

                cursor.execute("""
                    UPDATE Zapotrzebowania 
                    SET status = 'Oczekuje' 
                    WHERE id_czesci_katalog = ? AND status = 'Do zamówienia' AND id_zlecenia > 0
                """, (id_ck,))

                cursor.execute("""
                    DELETE FROM Zapotrzebowania 
                    WHERE id_czesci_katalog = ? AND status = 'Do zamówienia' AND (id_zlecenia = 0 OR id_zlecenia IS NULL)
                """, (id_ck,))

            conn.commit()
            conn.close()

            self.odswiez_tabele()
            messagebox.showinfo("Sukces", "Dostawa zaksięgowana. Zaktualizowano stany i listę zapotrzebowań.")

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd: {e}")

    def otworz_okno_dodaj_ilosc(self, model, nazwa_czesci):
        okno = ctk.CTkToplevel(self)
        okno.title("Zwiększ ilość")
        okno.geometry("350x250")
        okno.configure(fg_color=KOLOR_TLA)
        okno.attributes("-topmost", True)

        ctk.CTkLabel(okno, text="Zwiększ ilość na liście zakupów", font=("Arial", 16, "bold"),
                     text_color=KOLOR_TEKSTU).pack(pady=(20, 5))
        ctk.CTkLabel(okno, text=f"{model}\n{nazwa_czesci}", font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY,
                     justify="center").pack(pady=(0, 15))

        ctk.CTkLabel(okno, text="Ile dodatkowych sztuk zamówić?", font=("Arial", 12)).pack(pady=(10, 2))
        ent_ilosc = ctk.CTkEntry(okno, fg_color="#f1f3f5", border_width=0, justify="center")
        ent_ilosc.insert(0, "1")
        ent_ilosc.pack(pady=5)

        ctk.CTkButton(okno, text="Dodaj do listy", fg_color=KOLOR_GLOWNY, hover_color="#7c3aed", text_color="white",
                      command=lambda: self.zapisz_dodatkowa_ilosc(okno, model, nazwa_czesci, ent_ilosc.get())).pack(
            pady=20)

    @log_akcji("Magazyn: Szybkie zwiększenie ilości w liście zakupów")
    def zapisz_dodatkowa_ilosc(self, okno, model, czesc, ilosc_str):
        if not ilosc_str.isdigit() or int(ilosc_str) <= 0:
            messagebox.showwarning("Błąd", "Podaj prawidłową liczbę sztuk (większą od zera)!", parent=okno)
            return

        ilosc = int(ilosc_str)

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()

            cursor.execute("""
                    SELECT ck.id
                    FROM CzesciKatalog ck
                    JOIN ModeleApple m ON ck.id_modelu = m.id
                    WHERE m.model = ? AND ck.nazwa_czesci = ? AND ck.typ = 'Część'
                """, (model, czesc))
            wynik = cursor.fetchone()

            if not wynik:
                messagebox.showerror("Błąd", "Nie znaleziono wybranej części.", parent=okno)
                conn.close()
                return

            id_ck = wynik[0]

            cursor.execute("PRAGMA foreign_keys = OFF;")
            for _ in range(ilosc):
                cursor.execute("INSERT INTO Zapotrzebowania (id_zlecenia, id_czesci_katalog, status) VALUES (?, ?, ?)",
                               (0, id_ck, 'Do zamówienia'))
            cursor.execute("PRAGMA foreign_keys = ON;")

            conn.commit()
            conn.close()

            okno.destroy()
            self.odswiez_tabele()

        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Wystąpił błąd bazy danych: {e}", parent=okno)
    def wyloguj(self):
        self.controller.pokaz_panel("PanelLogowania")
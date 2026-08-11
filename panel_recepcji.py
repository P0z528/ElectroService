import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from narzedzia import log_akcji

# Kolory bazowe UI
KOLOR_TLA = "#f8f9fa"
KOLOR_KARTY = "#ffffff"
KOLOR_GLOWNY = "#8b5cf6"
KOLOR_TEKSTU = "#212529"
KOLOR_TEKSTU_SZARY = "#6c757d"


class PanelRecepcji(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.set_appearance_mode("light")
        super().__init__(parent, fg_color=KOLOR_TLA, corner_radius=0)
        self.controller = controller

        self._inicjalizuj_schemat()

        self.dostepne_czesci = []
        self.uslugi_zmienne = []  # Do przechowywania stanów checkboxów

        # Główny layout (Grid: Lewa kolumna menu, Prawa kolumna treść)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._zbuduj_menu_boczne()
        self._zbuduj_obszar_roboczy()

        # Inicjalizacja Danych
        self._zaladuj_typy_urzadzen()
        self.odswiez_tabele()

        self.pokaz_zakladke("obsluga")  # Domyślny widok

    def _inicjalizuj_schemat(self):
        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("ALTER TABLE Klienci ADD COLUMN pesel TEXT")
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass  # Kolumna prawdopodobnie już istnieje

    def _zbuduj_menu_boczne(self):
        self.menu_boczne = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=KOLOR_KARTY)
        self.menu_boczne.grid(row=0, column=0, sticky="nsew")
        self.menu_boczne.grid_rowconfigure(5, weight=1)

        # Logo / Tytuł
        ctk.CTkLabel(self.menu_boczne, text="ElectroService", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).grid(
            row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        ctk.CTkLabel(self.menu_boczne, text="Panel Recepcja", font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Przyciski Menu
        self.btn_menu_obsluga = ctk.CTkButton(self.menu_boczne, text="Obsługa klienta", fg_color=KOLOR_GLOWNY,
                                              text_color="white", anchor="w", corner_radius=8,
                                              command=lambda: self.pokaz_zakladke("obsluga"))
        self.btn_menu_obsluga.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_status = ctk.CTkButton(self.menu_boczne, text="Sprawdź status", fg_color="transparent",
                                             text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                             hover_color="#f1f3f5", command=lambda: self.pokaz_zakladke("status"))
        self.btn_menu_status.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_katalog = ctk.CTkButton(self.menu_boczne, text="Katalog", fg_color="transparent",
                                              text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                              hover_color="#f1f3f5", command=lambda: self.pokaz_zakladke("katalog"))
        self.btn_menu_katalog.grid(row=4, column=0, padx=15, pady=5, sticky="new")

        # Profil na dole (recepcja)
        profil_frame = ctk.CTkFrame(self.menu_boczne, fg_color="transparent")
        profil_frame.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        ctk.CTkLabel(profil_frame, text="RE", width=30, height=30, corner_radius=15, fg_color=KOLOR_GLOWNY,
                     text_color="white").pack(side="left")
        opis_profilu = ctk.CTkFrame(profil_frame, fg_color="transparent")
        opis_profilu.pack(side="left", padx=10)
        ctk.CTkLabel(opis_profilu, text="recepcja", font=("Arial", 12, "bold"), text_color=KOLOR_TEKSTU).pack(
            anchor="w")
        ctk.CTkLabel(opis_profilu, text="Recepcja", font=("Arial", 10), text_color=KOLOR_TEKSTU_SZARY).pack(
            anchor="w")

        ctk.CTkButton(profil_frame, text="Wyloguj", width=60, fg_color="transparent", text_color="#ef4444",
                      hover_color="#fee2e2", command=self.wyloguj).pack(side="right")

    def _zbuduj_obszar_roboczy(self):
        self.obszar_roboczy = ctk.CTkFrame(self, fg_color=KOLOR_TLA, corner_radius=0)
        self.obszar_roboczy.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        self.obszar_roboczy.grid_rowconfigure(1, weight=1)
        self.obszar_roboczy.grid_columnconfigure(0, weight=1)

        # ZAKŁADKI (Frames zarządzane przez grid_forget/grid)
        self.zakladka_obsluga = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        self.zakladka_status = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        self.zakladka_katalog = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")

        self._zbuduj_zawartosc_obsluga()
        self._zbuduj_zawartosc_status()
        self._zbuduj_zawartosc_katalog()

    def _zbuduj_zawartosc_obsluga(self):
        self.zakladka_obsluga.grid_columnconfigure(0, weight=5)
        self.zakladka_obsluga.grid_columnconfigure(1, weight=3)
        self.zakladka_obsluga.grid_rowconfigure(1, weight=1)

        # Tytuł
        tytul_frame = ctk.CTkFrame(self.zakladka_obsluga, fg_color="transparent")
        tytul_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(tytul_frame, text="Recepcja", font=("Arial", 24, "bold"), text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(tytul_frame, text="Przyjmuj nowe zlecenia napraw i wydawaj gotowy sprzęt.", font=("Arial", 14),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        # LEWA STRONA: Formularz Nowe Zlecenie
        formularz = ctk.CTkFrame(self.zakladka_obsluga, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                 border_color="#e9ecef")
        formularz.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # 4 kolumny wewnątrz formularza dla układu
        formularz.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(formularz, text="Nowe zlecenie naprawy", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).grid(
            row=0, column=0, columnspan=4, padx=20, pady=(20, 5), sticky="w")
        ctk.CTkLabel(formularz, text="Wprowadź dane klienta oraz urządzenia.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).grid(row=1, column=0, columnspan=4, padx=20, pady=(0, 20),
                                                         sticky="w")

        # Dane Klienta
        ctk.CTkLabel(formularz, text="Dane klienta", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=4,
                                                                                      padx=20, sticky="w")

        ctk.CTkLabel(formularz, text="Imię", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=3, column=0,
                                                                                                     padx=20,
                                                                                                     pady=(10, 2),
                                                                                                     sticky="w")
        self.ent_imie = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0, width=120)
        self.ent_imie.grid(row=4, column=0, padx=20, sticky="w")

        ctk.CTkLabel(formularz, text="Nazwisko", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=3,
                                                                                                         column=1,
                                                                                                         padx=5,
                                                                                                         pady=(10, 2),
                                                                                                         sticky="w")
        self.ent_nazwisko = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0, width=120)
        self.ent_nazwisko.grid(row=4, column=1, padx=5, sticky="w")

        ctk.CTkLabel(formularz, text="Telefon", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=3, column=2,
                                                                                                        padx=5,
                                                                                                        pady=(10, 2),
                                                                                                        sticky="w")
        # Kontener grupujący pole kierunkowego i numeru telefonu
        tel_frame = ctk.CTkFrame(formularz, fg_color="transparent")
        tel_frame.grid(row=4, column=2, padx=5, sticky="w")

        self.ent_kierunkowy = ctk.CTkEntry(tel_frame, fg_color="#f1f3f5", border_width=0, width=45)
        self.ent_kierunkowy.insert(0, "+48")
        self.ent_kierunkowy.pack(side="left", padx=(0, 5))

        self.ent_telefon = ctk.CTkEntry(tel_frame, fg_color="#f1f3f5", border_width=0, width=90)
        self.ent_telefon.pack(side="left")

        ctk.CTkLabel(formularz, text="PESEL", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=3, column=3,
                                                                                                      padx=(5, 20),
                                                                                                      pady=(10, 2),
                                                                                                      sticky="w")
        self.ent_pesel = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0, width=120)
        self.ent_pesel.grid(row=4, column=3, padx=(5, 20), sticky="w")

        # Dane urządzenia
        ctk.CTkLabel(formularz, text="Dane urządzenia", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4,
                                                                                         padx=20, pady=(20, 0),
                                                                                         sticky="w")

        ctk.CTkLabel(formularz, text="Typ urządzenia", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=6,
                                                                                                               column=0,
                                                                                                               padx=20,
                                                                                                               pady=(10,
                                                                                                                     2),
                                                                                                               sticky="w")
        self.cb_typ_urzadzenia = ctk.CTkComboBox(formularz, fg_color="#f1f3f5", border_width=0, button_color="#dee2e6",
                                                 state="readonly", command=self._on_typ_selected, width=120)
        self.cb_typ_urzadzenia.grid(row=7, column=0, padx=20, sticky="w")

        ctk.CTkLabel(formularz, text="Model", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=6, column=1,
                                                                                                      padx=5,
                                                                                                      pady=(10, 2),
                                                                                                      sticky="w")
        self.cb_model_urzadzenia = ctk.CTkComboBox(formularz, fg_color="#f1f3f5", border_width=0,
                                                   button_color="#dee2e6", state="readonly",
                                                   command=self._on_model_selected, width=120)
        self.cb_model_urzadzenia.grid(row=7, column=1, padx=5, sticky="w")

        ctk.CTkLabel(formularz, text="Nr seryjny", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(row=6,
                                                                                                           column=2,
                                                                                                           columnspan=2,
                                                                                                           padx=(5, 20),
                                                                                                           pady=(10, 2),
                                                                                                           sticky="w")
        self.ent_sn = ctk.CTkEntry(formularz, placeholder_text="SN...", fg_color="#f1f3f5", border_width=0, width=150)
        self.ent_sn.grid(row=7, column=2, columnspan=2, padx=(5, 20), sticky="w")

        # Usługi / Części
        ctk.CTkLabel(formularz, text="Wybierz usługi / części", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=8, column=0, columnspan=4, padx=20, pady=(20, 5), sticky="w")

        self.uslugi_frame = ctk.CTkScrollableFrame(formularz, fg_color="transparent", height=120)
        self.uslugi_frame.grid(row=9, column=0, columnspan=4, padx=15, sticky="nsew")

        # PRAWA STRONA: Podsumowanie i Wydawanie
        prawa_kolumna = ctk.CTkFrame(self.zakladka_obsluga, fg_color="transparent")
        prawa_kolumna.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        prawa_kolumna.grid_rowconfigure(1, weight=1)

        # Karta 1: Podsumowanie (z fioletowym blokiem kosztów)
        podsumowanie = ctk.CTkFrame(prawa_kolumna, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                    border_color="#e9ecef")
        podsumowanie.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(podsumowanie, text="Podsumowanie", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).pack(
            padx=20, pady=(15, 5), anchor="w")

        koszt_blok = ctk.CTkFrame(podsumowanie, fg_color=KOLOR_GLOWNY, corner_radius=8)
        koszt_blok.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(koszt_blok, text="Całkowity koszt", font=("Arial", 12), text_color="white").pack(anchor="w",
                                                                                                      padx=15,
                                                                                                      pady=(10, 0))
        self.lbl_suma = ctk.CTkLabel(koszt_blok, text="0.00 PLN", font=("Arial", 28, "bold"), text_color="white")
        self.lbl_suma.pack(anchor="w", padx=15, pady=(0, 10))

        btn_frame = ctk.CTkFrame(podsumowanie, fg_color="transparent")
        btn_frame.pack(padx=20, pady=10, fill="x")
        ctk.CTkButton(btn_frame, text="Akceptuj", fg_color="#059669", hover_color="#047857", text_color="white",
                      command=self.zarejestruj_w_bazie).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Odrzuć", fg_color="#ef4444", border_width=1, border_color="#dee2e6",
                      text_color=KOLOR_TEKSTU, hover_color="#f8f9fa", command=self.wyczysc_formularz).pack(side="right",
                                                                                                           fill="x",
                                                                                                           expand=True,
                                                                                                           padx=(5, 0))

        # Karta 2: Tabela wydawania
        ramka_wydan = ctk.CTkFrame(prawa_kolumna, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                   border_color="#e9ecef")
        ramka_wydan.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(ramka_wydan, text="Sprzęt gotowy do wydania", font=("Arial", 14, "bold"),
                     text_color=KOLOR_TEKSTU).pack(padx=20, pady=(15, 10), anchor="w")

        # Stylizacja dla ttk.Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="#212529", rowheight=30, fieldbackground="#ffffff",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', KOLOR_GLOWNY)])
        style.configure("Treeview.Heading", background="#f1f3f5", foreground="#212529", font=('Arial', 10, 'bold'),
                        borderwidth=0)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Usuwa ramki systemowe

        tabela_frame = ctk.CTkFrame(ramka_wydan, fg_color="transparent")
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.tab_wydania = ttk.Treeview(tabela_frame, columns=("id", "klient", "model", "koszt"), show="headings",
                                        height=8)
        self.tab_wydania.heading("id", text="ID")
        self.tab_wydania.heading("klient", text="Klient")
        self.tab_wydania.heading("model", text="Urządzenie")
        self.tab_wydania.heading("koszt", text="Koszt (PLN)")
        self.tab_wydania.column("id", width=30)
        self.tab_wydania.column("koszt", width=80)
        self.tab_wydania.pack(side="top", fill="both", expand=True)

        ctk.CTkButton(ramka_wydan, text="Wydaj zaznaczony sprzęt", fg_color="#3b82f6", text_color="white",
                      hover_color="#2563eb", command=self.wydaj_sprzet).pack(padx=20, pady=(0, 20), fill="x")

    def _zbuduj_zawartosc_status(self):
        self.zakladka_status.grid_columnconfigure(0, weight=1)
        self.zakladka_status.grid_rowconfigure(2, weight=1)

        # Nagłówek - czyste tło jak na zdjęciu
        tytul_frame = ctk.CTkFrame(self.zakladka_status, fg_color="transparent")
        tytul_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(tytul_frame, text="Sprawdź status zlecenia", font=("Arial", 22, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(tytul_frame, text="Wyszukaj zlecenia po numerze seryjnym urządzenia lub ID zlecenia.",
                     font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        # Kontener wyszukiwarki - Grid z labelami na górze
        wyszukiwarka_frame = ctk.CTkFrame(self.zakladka_status, fg_color="transparent")
        wyszukiwarka_frame.grid(row=1, column=0, sticky="ew")

        wyszukiwarka_frame.grid_columnconfigure(0, minsize=250)
        wyszukiwarka_frame.grid_columnconfigure(1, minsize=250)
        wyszukiwarka_frame.grid_columnconfigure(2, weight=1)

        # Kolumna 1: Nr Seryjny
        ctk.CTkLabel(wyszukiwarka_frame, text="Nr seryjny:", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self.ent_status_sn = ctk.CTkEntry(wyszukiwarka_frame, fg_color="#f1f3f5", border_width=0, height=35)
        self.ent_status_sn.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Kolumna 2: ID Zlecenia
        ctk.CTkLabel(wyszukiwarka_frame, text="ID zlecenia:", font=("Arial", 11), text_color=KOLOR_TEKSTU_SZARY).grid(
            row=0, column=1, sticky="w", pady=(0, 2))
        self.ent_status_id = ctk.CTkEntry(wyszukiwarka_frame, fg_color="#f1f3f5", border_width=0, height=35)
        self.ent_status_id.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        # Kolumna 3: Przycisk Wyczyść (zastępuje "Szukaj")
        ctk.CTkButton(wyszukiwarka_frame, text="Wyczyść", command=self.wyczysc_filtry_status, fg_color="#6c757d",
                      hover_color="#495057", height=35, corner_radius=0, width=100).grid(row=1, column=2, sticky="sw")

        # Filtrowanie na żywo przy wpisywaniu
        self.ent_status_sn.bind("<KeyRelease>", lambda e: self.sprawdz_status())
        self.ent_status_id.bind("<KeyRelease>", lambda e: self.sprawdz_status())

        # Przestrzeń na wyniki (tabela)
        self.status_info_frame = ctk.CTkFrame(self.zakladka_status, fg_color="transparent")
        self.status_info_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

        # Buduj tabelę i załaduj wszystkie zlecenia od razu
        self._zbuduj_tabele_statusow()
        self.zaladuj_wszystkie_zlecenia_status()

    def wyczysc_filtry_status(self):
        """Czyści pola filtrujące i ponownie ładuje wszystkie statusy."""
        self.ent_status_sn.delete(0, tk.END)
        self.ent_status_id.delete(0, tk.END)
        self.sprawdz_status()

    def _zbuduj_zawartosc_katalog(self):
        # Układ 2x2
        self.zakladka_katalog.grid_columnconfigure((0, 1), weight=1)

        tytul_frame = ctk.CTkFrame(self.zakladka_katalog, fg_color="transparent")
        tytul_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(tytul_frame, text="Katalog", font=("Arial", 24, "bold"), text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(tytul_frame, text="Zarządzaj typami, modelami urządzeń oraz cennikiem usług i części.",
                     font=("Arial", 14),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        # --- KARTA 1: DODAJ TYP ---
        karta_typ = ctk.CTkFrame(self.zakladka_katalog, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                 border_color="#e9ecef")
        karta_typ.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        ctk.CTkLabel(karta_typ, text="+ Dodaj nowy Typ", font=("Arial", 16, "bold")).pack(padx=20, pady=(20, 5),
                                                                                          anchor="w")
        ctk.CTkLabel(karta_typ, text="Nowa kategoria (np. Konsola).", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(padx=20, pady=(0, 20), anchor="w")

        ctk.CTkLabel(karta_typ, text="Nazwa Typu:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(padx=20,
                                                                                                      pady=(10, 2),
                                                                                                      anchor="w")
        self.ent_nowy_typ_nazwa = ctk.CTkEntry(karta_typ, fg_color="#f1f3f5", border_width=0)
        self.ent_nowy_typ_nazwa.pack(padx=20, fill="x", anchor="w")

        ctk.CTkLabel(karta_typ, text="Pierwszy model (wymagany):", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(
            padx=20, pady=(15, 2), anchor="w")
        self.ent_typ_pierwszy_model = ctk.CTkEntry(karta_typ, fg_color="#f1f3f5", border_width=0)
        self.ent_typ_pierwszy_model.pack(padx=20, fill="x", anchor="w")

        ctk.CTkButton(karta_typ, text="+ Dodaj typ", fg_color="#059669", text_color="white", hover_color="#047857",
                      command=self.dodaj_nowy_typ).pack(padx=20, pady=30, anchor="w")

        # --- KARTA 2: DODAJ MODEL ---
        karta_model = ctk.CTkFrame(self.zakladka_katalog, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                   border_color="#e9ecef")
        karta_model.grid(row=1, column=1, sticky="nsew", padx=(0, 0), pady=(0, 10))

        ctk.CTkLabel(karta_model, text="+ Dodaj Model", font=("Arial", 16, "bold")).pack(padx=20, pady=(20, 5),
                                                                                         anchor="w")
        ctk.CTkLabel(karta_model, text="Kolejny model do istniejącego typu.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(padx=20, pady=(0, 20), anchor="w")

        ctk.CTkLabel(karta_model, text="Wybierz Typ:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(padx=20,
                                                                                                         pady=(10, 2),
                                                                                                         anchor="w")
        self.cb_nowy_typ = ctk.CTkComboBox(karta_model, fg_color="#f1f3f5", border_width=0, button_color="#dee2e6",
                                           state="readonly")
        self.cb_nowy_typ.pack(padx=20, fill="x", anchor="w")

        ctk.CTkLabel(karta_model, text="Nazwa Modelu:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(padx=20,
                                                                                                          pady=(15, 2),
                                                                                                          anchor="w")
        self.ent_nowy_model = ctk.CTkEntry(karta_model, fg_color="#f1f3f5", border_width=0)
        self.ent_nowy_model.pack(padx=20, fill="x", anchor="w")

        ctk.CTkButton(karta_model, text="+ Dodaj model", fg_color="#059669", text_color="white", hover_color="#047857",
                      command=self.dodaj_nowy_model).pack(padx=20, pady=30, anchor="w")

        # --- KARTA 3: DODAJ CZĘŚĆ ---
        karta_czesc = ctk.CTkFrame(self.zakladka_katalog, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                   border_color="#e9ecef")
        karta_czesc.grid(row=2, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(karta_czesc, text="+ Dodaj część / usługę", font=("Arial", 16, "bold")).pack(padx=20, pady=(20, 5),
                                                                                                  anchor="w")
        ctk.CTkLabel(karta_czesc, text="Wybierz model i dodaj pozycję.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(padx=20, pady=(0, 20), anchor="w")

        ctk.CTkLabel(karta_czesc, text="Typ urządzenia:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(padx=20,
                                                                                                            pady=(10,
                                                                                                                  2),
                                                                                                            anchor="w")
        self.cb_katalog_typ = ctk.CTkComboBox(karta_czesc, fg_color="#f1f3f5", border_width=0, button_color="#dee2e6",
                                              state="readonly", command=self._on_katalog_typ_dla_czesci_changed)
        self.cb_katalog_typ.pack(padx=20, fill="x", anchor="w")

        ctk.CTkLabel(karta_czesc, text="Model:", font=("Arial", 12), text_color=KOLOR_TEKSTU).pack(padx=20,
                                                                                                   pady=(10, 2),
                                                                                                   anchor="w")
        self.cb_katalog_model = ctk.CTkComboBox(karta_czesc, fg_color="#f1f3f5", border_width=0, button_color="#dee2e6",
                                                state="readonly")
        self.cb_katalog_model.pack(padx=20, fill="x", anchor="w")

        pola_frame = ctk.CTkFrame(karta_czesc, fg_color="transparent")
        pola_frame.pack(padx=20, pady=15, fill="x")
        pola_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(pola_frame, text="Nazwa:", font=("Arial", 12), text_color=KOLOR_TEKSTU).grid(row=0, column=0,
                                                                                                  pady=(0, 2),
                                                                                                  sticky="w")
        self.ent_nowa_czesc = ctk.CTkEntry(pola_frame, placeholder_text="np. Bateria", fg_color="#f1f3f5",
                                           border_width=0)
        self.ent_nowa_czesc.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(pola_frame, text="Cena:", font=("Arial", 12), text_color=KOLOR_TEKSTU).grid(row=2, column=0,
                                                                                                 pady=(0, 2),
                                                                                                 sticky="w")
        self.ent_nowa_cena = ctk.CTkEntry(pola_frame, placeholder_text="299", fg_color="#f1f3f5", border_width=0)
        self.ent_nowa_cena.grid(row=3, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(pola_frame, text="Typ:", font=("Arial", 12), text_color=KOLOR_TEKSTU).grid(row=2, column=1,
                                                                                                pady=(0, 2), sticky="w")
        self.cb_nowy_typ_katalog = ctk.CTkComboBox(pola_frame, values=["Część", "Usługa"], fg_color="#f1f3f5",
                                                   border_width=0, state="readonly")
        self.cb_nowy_typ_katalog.grid(row=3, column=1, sticky="ew")

        ctk.CTkButton(karta_czesc, text="+ Dodaj część", fg_color=KOLOR_GLOWNY, text_color="white",
                      hover_color="#7c3aed", command=self.dodaj_nowa_czesc).pack(padx=20, pady=15, anchor="w")

        # --- KARTA 4: AKTUALIZACJA CENY (Niezależna logistycznie) ---
        karta_aktualizacja = ctk.CTkFrame(self.zakladka_katalog, fg_color=KOLOR_KARTY, corner_radius=10,
                                          border_width=1, border_color="#e9ecef")
        karta_aktualizacja.grid(row=2, column=1, sticky="nsew", padx=(0, 0))

        ctk.CTkLabel(karta_aktualizacja, text="Aktualizacja ceny", font=("Arial", 16, "bold")).pack(padx=20,
                                                                                                    pady=(20, 5),
                                                                                                    anchor="w")
        ctk.CTkLabel(karta_aktualizacja, text="Wybierz typ i model:", font=("Arial", 11),
                     text_color=KOLOR_TEKSTU_SZARY).pack(padx=20, pady=(0, 2), anchor="w")

        # Niezależny Typ
        self.cb_aktualizacja_typ = ctk.CTkComboBox(karta_aktualizacja, fg_color="#f1f3f5", border_width=0,
                                                   button_color="#dee2e6", state="readonly",
                                                   command=self._on_aktualizacja_typ_changed)
        self.cb_aktualizacja_typ.pack(padx=20, fill="x", pady=(0, 10))

        # Niezależny Model
        self.cb_aktualizacja_model = ctk.CTkComboBox(karta_aktualizacja, fg_color="#f1f3f5", border_width=0,
                                                     button_color="#dee2e6", state="readonly",
                                                     command=self._on_aktualizacja_model_changed)
        self.cb_aktualizacja_model.pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkLabel(karta_aktualizacja, text="Wybierz pozycję i wpisz nową cenę:", font=("Arial", 11),
                     text_color=KOLOR_TEKSTU_SZARY).pack(padx=20, pady=(10, 2), anchor="w")

        self.cb_aktualizacja_ceny = ctk.CTkComboBox(karta_aktualizacja, fg_color="#f1f3f5", border_width=0,
                                                    button_color="#dee2e6", state="readonly")
        self.cb_aktualizacja_ceny.pack(padx=20, fill="x", anchor="w")

        aktualizacja_frame = ctk.CTkFrame(karta_aktualizacja, fg_color="transparent")
        aktualizacja_frame.pack(padx=20, pady=8, fill="x")
        aktualizacja_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(aktualizacja_frame, text="Nowa cena:", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.ent_nowa_cena_aktualizacja = ctk.CTkEntry(aktualizacja_frame, placeholder_text="np. 399",
                                                       fg_color="#f1f3f5", border_width=0)
        self.ent_nowa_cena_aktualizacja.grid(row=1, column=0, sticky="ew")

        ctk.CTkButton(karta_aktualizacja, text="Zapisz nową cenę", fg_color="#3b82f6", text_color="white",
                      hover_color="#2563eb", command=self.zaktualizuj_cene).pack(padx=20, pady=(8, 20), anchor="w")

    def pokaz_zakladke(self, nazwa):
        self.zakladka_obsluga.grid_forget()
        self.zakladka_status.grid_forget()
        self.zakladka_katalog.grid_forget()

        # 1. Resetowanie wyglądu wszystkich przycisków do stanu nieaktywnego
        self.btn_menu_obsluga.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_status.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_katalog.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")

        # 2. Ustawianie wyglądu aktywnego przycisku (fioletowe tło, biały tekst i fioletowy hover)
        if nazwa == "obsluga":
            self.zakladka_obsluga.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_obsluga.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
        elif nazwa == "status":
            self.zakladka_status.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_status.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
        elif nazwa == "katalog":
            self.zakladka_katalog.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_katalog.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")

    # === LOGIKA BIZNESOWA I BAZA DANYCH ===

    def _zaladuj_typy_urzadzen(self):
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT typ FROM ModeleApple ORDER BY typ")
            typy = [row[0] for row in cursor.fetchall()]
            conn.close()

            self.cb_typ_urzadzenia.configure(values=typy)
            self.cb_nowy_typ.configure(values=typy)  # Opcja "Inny" całkowicie usunięta
            self.cb_katalog_typ.configure(values=typy)
            self.cb_aktualizacja_typ.configure(values=typy)

            if typy:
                self.cb_typ_urzadzenia.set(typy[0])
                self.cb_nowy_typ.set(typy[0])
                self.cb_katalog_typ.set(typy[0])
                self.cb_aktualizacja_typ.set(typy[0])

                self._zaladuj_modele_dla_typu(typy[0])
                self._on_katalog_typ_dla_czesci_changed(typy[0])
                self._on_aktualizacja_typ_changed(typy[0])
            else:
                self.cb_nowy_typ.set("")
                self.cb_katalog_typ.set("")
                self.cb_typ_urzadzenia.set("")
                self.cb_aktualizacja_typ.set("")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", f"Błąd: {e}")

    @log_akcji("Recepcja: Dodano nowy typ i model")
    def dodaj_nowy_typ(self):
        typ = self.ent_nowy_typ_nazwa.get().strip()
        model = self.ent_typ_pierwszy_model.get().strip()

        if not typ or not model:
            return messagebox.showwarning("Błąd walidacji", "Wypełnij nazwę nowego typu oraz pierwszego modelu!")

        typ = typ.strip()
        model = model.strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ModeleApple WHERE LOWER(TRIM(typ)) = ?", (typ.lower(),))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return messagebox.showwarning("Duplikat", f"Typ '{typ}' już istnieje w bazie danych!")
            cursor.execute("INSERT INTO ModeleApple (typ, model) VALUES (?, ?)", (typ, model))
            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            messagebox.showinfo("Sukces", f"Dodano nowy typ: {typ}\nModel: {model}")

            self.ent_nowy_typ_nazwa.delete(0, tk.END)
            self.ent_typ_pierwszy_model.delete(0, tk.END)

            self._zaladuj_typy_urzadzen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Ten model już istnieje w bazie!")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))

    @log_akcji("Recepcja: Dodano nowy model")
    def dodaj_nowy_model(self):
        typ = self.cb_nowy_typ.get()
        model = self.ent_nowy_model.get().strip()

        if not typ or not model:
            return messagebox.showwarning("Brak danych", "Wybierz Typ i wpisz nazwę modelu!")

        model = model.strip()

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ModeleApple WHERE LOWER(TRIM(model)) = ?", (model.lower(),))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return messagebox.showwarning("Duplikat", f"Model '{model}' już istnieje w bazie danych!")
            cursor.execute("INSERT INTO ModeleApple (typ, model) VALUES (?, ?)", (typ, model))
            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            messagebox.showinfo("Sukces", f"Dodano model: {model} do typu: {typ}")

            self.ent_nowy_model.delete(0, tk.END)

            # Odświeżenie interfejsu przy zachowaniu wybranego przed chwilą typu
            self._zaladuj_typy_urzadzen()
            self.cb_nowy_typ.set(typ)
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Ten model już istnieje!")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))

    def _on_katalog_typ_dla_czesci_changed(self, wybrany_typ):
        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("SELECT model FROM ModeleApple WHERE typ = ? ORDER BY model", (wybrany_typ,))
            modele = [r[0] for r in c.fetchall()]
            conn.close()

            self.cb_katalog_model.configure(values=modele)
            if modele:
                self.cb_katalog_model.set(modele[0])
            else:
                self.cb_katalog_model.set("")
        except sqlite3.Error as e:
            print(f"Błąd filtrowania modeli w katalogu: {e}")

    def _on_aktualizacja_typ_changed(self, wybrany_typ):
        """Obsługuje niezależną logikę zasilania Modeli dla karty Aktualizacji Ceny."""
        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("SELECT model FROM ModeleApple WHERE typ = ? ORDER BY model", (wybrany_typ,))
            modele = [r[0] for r in c.fetchall()]
            conn.close()

            self.cb_aktualizacja_model.configure(values=modele)
            if modele:
                self.cb_aktualizacja_model.set(modele[0])
                self._on_aktualizacja_model_changed(modele[0])
            else:
                self.cb_aktualizacja_model.set("")
                self._odswiez_cb_aktualizacja_ceny()
        except sqlite3.Error as e:
            print(f"Błąd filtrowania modeli w aktualizacji ceny: {e}")

    def _on_aktualizacja_model_changed(self, _):
        """Wywoływana tylko gdy zmieniony zostanie model w karcie Aktualizacji Ceny."""
        self._odswiez_cb_aktualizacja_ceny()

    def _odswiez_cb_aktualizacja_ceny(self):
        """Odświeża listę części/usług w ComboBoxie aktualizacji ceny dla wybranego modelu."""
        model = self.cb_aktualizacja_model.get()
        if not model:
            self.cb_aktualizacja_ceny.configure(values=[])
            self.cb_aktualizacja_ceny.set("")
            return
        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("""
                SELECT ck.id, ck.nazwa_czesci, ck.cena, ck.typ
                FROM CzesciKatalog ck
                JOIN ModeleApple m ON ck.id_modelu = m.id
                WHERE m.model = ?
                ORDER BY ck.typ, ck.nazwa_czesci
            """, (model,))
            pozycje = c.fetchall()
            conn.close()
            # Przechowujemy mapowanie "etykieta -> id" do późniejszego UPDATE
            self._mapa_pozycji_ceny = {f"{typ}: {nazwa} ({cena:.2f} PLN)": pid for pid, nazwa, cena, typ in pozycje}
            etykiety = list(self._mapa_pozycji_ceny.keys())
            self.cb_aktualizacja_ceny.configure(values=etykiety)
            if etykiety:
                self.cb_aktualizacja_ceny.set(etykiety[0])
            else:
                self.cb_aktualizacja_ceny.set("")
        except sqlite3.Error as e:
            print(f"Błąd odświeżania listy cen: {e}")

    def zaktualizuj_cene(self):
        """Aktualizuje cenę wybranej części/usługi w bazie danych."""
        etykieta = self.cb_aktualizacja_ceny.get()
        nowa_cena_str = self.ent_nowa_cena_aktualizacja.get().strip()

        if not etykieta or not nowa_cena_str:
            return messagebox.showwarning("Brak danych", "Wybierz pozycję i wpisz nową cenę!")

        if not hasattr(self, '_mapa_pozycji_ceny') or etykieta not in self._mapa_pozycji_ceny:
            return messagebox.showwarning("Błąd", "Nie można znaleźć wybranej pozycji. Odśwież katalog.")

        try:
            nowa_cena = float(nowa_cena_str.replace(",", "."))
            if nowa_cena < 0:
                return messagebox.showwarning("Błąd walidacji", "Cena nie może być ujemna!")
        except ValueError:
            return messagebox.showwarning("Błąd walidacji", "Podaj poprawną wartość liczbową dla ceny!")

        pid = self._mapa_pozycji_ceny[etykieta]
        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("UPDATE CzesciKatalog SET cena = ? WHERE id = ?", (nowa_cena, pid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukces", f"Cena została zaktualizowana na {nowa_cena:.2f} PLN.")
            self.ent_nowa_cena_aktualizacja.delete(0, tk.END)
            self._odswiez_cb_aktualizacja_ceny()
            self._on_model_selected()  # Odświeżenie widoku w "Obsłudze Klienta"
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))

    def wyloguj(self):
        self.controller.pokaz_panel("PanelLogowania")

    def _zaladuj_modele_dla_typu(self, typ):
        conn = sqlite3.connect("serwis.db")
        c = conn.cursor()
        c.execute("SELECT model FROM ModeleApple WHERE typ = ?", (typ,))
        modele = [r[0] for r in c.fetchall()]
        self.cb_model_urzadzenia.configure(values=modele)
        if modele:
            self.cb_model_urzadzenia.set(modele[0])
            self._on_model_selected(modele[0])
        else:
            self.cb_model_urzadzenia.set("")
            self._on_model_selected("")
        conn.close()

    def _on_typ_selected(self, wartosc):
        self._zaladuj_modele_dla_typu(wartosc)

    def _on_model_selected(self, wartosc=None):
        model = self.cb_model_urzadzenia.get()

        # Czyszczenie starych checkboxów i nagłówków
        for widget in self.uslugi_frame.winfo_children():
            widget.destroy()

        self.dostepne_czesci = []
        self.uslugi_zmienne = []

        if not model:
            self._przelicz_koszty()
            return

        conn = sqlite3.connect("serwis.db")
        c = conn.cursor()
        # Pobieramy również typ z bazy, aby wiedzieć jak pogrupować elementy
        c.execute(
            "SELECT c.nazwa_czesci, c.cena, c.typ FROM CzesciKatalog c JOIN ModeleApple m ON c.id_modelu = m.id WHERE m.model = ?",
            (model,))
        wyniki = c.fetchall()
        conn.close()

        # Grupowanie
        czesci = [w for w in wyniki if w[2] == 'Część']
        uslugi = [w for w in wyniki if w[2] == 'Usługa']

        aktualny_wiersz = 0

        # Sekcja: CZĘŚCI
        if czesci:
            lbl_cz = ctk.CTkLabel(self.uslugi_frame, text="Części (Wymiana):", font=("Arial", 12, "bold"),
                                  text_color=KOLOR_TEKSTU)
            lbl_cz.grid(row=aktualny_wiersz, column=0, columnspan=2, sticky="w", pady=(5, 5))
            aktualny_wiersz += 1

            for i, (nazwa, cena, typ) in enumerate(czesci):
                self.dostepne_czesci.append((nazwa, cena, typ))
                zmienna_cb = ctk.IntVar(value=0)
                self.uslugi_zmienne.append(zmienna_cb)

                cb = ctk.CTkCheckBox(self.uslugi_frame, text=f"{nazwa} ({cena:.2f} PLN)",
                                     variable=zmienna_cb, fg_color=KOLOR_GLOWNY, hover_color="#7c3aed",
                                     command=self._przelicz_koszty)
                # Ułożenie w 2 kolumnach
                cb.grid(row=aktualny_wiersz + (i // 2), column=i % 2, pady=8, padx=10, sticky="w")

            aktualny_wiersz += (len(czesci) + 1) // 2

        # Sekcja: USŁUGI
        if uslugi:
            lbl_usl = ctk.CTkLabel(self.uslugi_frame, text="Usługi serwisowe:", font=("Arial", 12, "bold"),
                                   text_color=KOLOR_TEKSTU)
            lbl_usl.grid(row=aktualny_wiersz, column=0, columnspan=2, sticky="w", pady=(15, 5))
            aktualny_wiersz += 1

            for i, (nazwa, cena, typ) in enumerate(uslugi):
                self.dostepne_czesci.append((nazwa, cena, typ))
                zmienna_cb = ctk.IntVar(value=0)
                self.uslugi_zmienne.append(zmienna_cb)

                cb = ctk.CTkCheckBox(self.uslugi_frame, text=f"{nazwa} ({cena:.2f} PLN)",
                                     variable=zmienna_cb, fg_color=KOLOR_GLOWNY, hover_color="#7c3aed",
                                     command=self._przelicz_koszty)
                cb.grid(row=aktualny_wiersz + (i // 2), column=i % 2, pady=8, padx=10, sticky="w")

        self._przelicz_koszty()

    def _przelicz_koszty(self):
        suma = 0.0
        self.zaznaczone_indeksy = []

        for i, zmienna in enumerate(self.uslugi_zmienne):
            if zmienna.get() == 1:
                suma += self.dostepne_czesci[i][1]
                self.zaznaczone_indeksy.append(i)

        self.lbl_suma.configure(text=f"{suma:.2f} PLN")

    @log_akcji("Recepcja: Dodano część/usługę")
    def dodaj_nowa_czesc(self):
        model = self.cb_katalog_model.get()
        nazwa = self.ent_nowa_czesc.get().strip()
        cena = self.ent_nowa_cena.get().strip()
        typ_pozycji = self.cb_nowy_typ_katalog.get()  # Pobieramy typ

        if not all([model, nazwa, cena, typ_pozycji]): return

        nazwa = nazwa.strip()

        try:
            p = float(cena.replace(",", "."))
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()
            c.execute("SELECT id FROM ModeleApple WHERE model = ?", (model,))
            mid = c.fetchone()[0]

            # Sprawdzenie duplikatu nazwy dla danego modelu i konkretnego typu (Część/Usługa)
            c.execute(
                "SELECT COUNT(*) FROM CzesciKatalog WHERE id_modelu = ? AND LOWER(TRIM(nazwa_czesci)) = ? AND typ = ?",
                (mid, nazwa.lower(), typ_pozycji))
            if c.fetchone()[0] > 0:
                conn.close()
                return messagebox.showwarning("Duplikat", f"{typ_pozycji} '{nazwa}' już istnieje dla modelu '{model}'!")

            c.execute("INSERT INTO CzesciKatalog (id_modelu, nazwa_czesci, cena, typ) VALUES (?, ?, ?, ?)",
                      (mid, nazwa, p, typ_pozycji))

            conn.commit()
            conn.close()
            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            messagebox.showinfo("Sukces", f"Dodano do katalogu: {nazwa} ({typ_pozycji})")
            self.ent_nowa_czesc.delete(0, tk.END)
            self.ent_nowa_cena.delete(0, tk.END)
            self._on_model_selected()

            # Odświeżamy listę w aktualizacji cen (jeśli jest tam ustawiony ten sam model)
            self._odswiez_cb_aktualizacja_ceny()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def odswiez_tabele(self):
        for w in self.tab_wydania.get_children(): self.tab_wydania.delete(w)
        conn = sqlite3.connect("serwis.db")
        c = conn.cursor()
        c.execute(
            "SELECT Z.id, K.imie || ' ' || K.nazwisko, U.model, Z.koszt FROM Zlecenia Z JOIN Urzadzenia U ON Z.id_urzadzenia = U.id JOIN Klienci K ON U.id_klienta = K.id WHERE Z.status = 'Gotowe'")
        for r in c.fetchall():
            self.tab_wydania.insert("", tk.END, values=r)
        conn.close()

    def wydaj_sprzet(self):
        sel = self.tab_wydania.selection()
        if not sel: return
        zid = self.tab_wydania.item(sel[0])['values'][0]
        conn = sqlite3.connect("serwis.db")
        c = conn.cursor()
        c.execute("UPDATE Zlecenia SET status = 'Wydane' WHERE id = ?", (zid,))
        conn.commit()
        conn.close()

        if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()

        messagebox.showinfo("Sukces", "Sprzęt wydany")
        self.odswiez_tabele()

    def wyczysc_formularz(self):
        for e in (self.ent_imie, self.ent_nazwisko, self.ent_telefon, self.ent_pesel, self.ent_sn):
            e.delete(0, tk.END)

        self.ent_kierunkowy.delete(0, tk.END)
        self.ent_kierunkowy.insert(0, "+48")

        self._zaladuj_typy_urzadzen()

    def zarejestruj_w_bazie(self):
        imie = self.ent_imie.get().strip()
        naz = self.ent_nazwisko.get().strip()
        kierunkowy = self.ent_kierunkowy.get().strip()
        tel = self.ent_telefon.get().strip()
        pesel = self.ent_pesel.get().strip()
        mod = self.cb_model_urzadzenia.get().strip()
        sn = self.ent_sn.get().strip()

        # Zmodyfikowana walidacja - PESEL przestał być wymaganym polem
        if not all([imie, naz, kierunkowy, tel, mod, sn]):
            messagebox.showwarning("Błąd walidacji", "Wszystkie podstawowe dane i urządzenie muszą być wypełnione!")
            return

        if len(imie) > 26 or len(naz) > 26:
            messagebox.showwarning("Błąd walidacji", "Imię i nazwisko mogą mieć maksymalnie 26 znaków!")
            return

        tel_czysty = tel.replace(" ", "").replace("-", "")

        if not tel_czysty.isdigit():
            messagebox.showwarning("Błąd walidacji", "Numer telefonu musi zawierać tylko cyfry!")
            return

        if kierunkowy == "+48":
            if len(tel_czysty) != 9:
                messagebox.showwarning("Błąd walidacji", "Dla prefiksu +48 numer telefonu musi składać się z 9 cyfr!")
                return
        else:
            if len(tel_czysty) > 15:
                messagebox.showwarning("Błąd walidacji",
                                       "Numer telefonu dla zagranicznego prefiksu może mieć maksymalnie 15 cyfr!")
                return

        # Zmodyfikowane sprawdzenie PESEL-u - maksymalnie 11 znaków lub wcale
        if pesel:
            if not pesel.isdigit() or len(pesel) > 11:
                messagebox.showwarning("Błąd walidacji",
                                       "PESEL musi składać się z samych cyfr (maksymalnie 11) lub pozostać pusty!")
                return

        if len(sn) > 16:
            messagebox.showwarning("Błąd walidacji", "Numer seryjny (SN) może mieć maksymalnie 16 znaków!")
            return

        pelny_telefon = f"{kierunkowy} {tel_czysty}"

        idx = self.zaznaczone_indeksy
        if not idx:
            messagebox.showwarning("Brak usług", "Musisz przypisać przynajmniej jedną część lub usługę do zlecenia!")
            return

        koszt = sum(self.dostepne_czesci[i][1] for i in idx)

        # Budowanie inteligentnego opisu usterki
        wybrane_czesci = [self.dostepne_czesci[i][0] for i in idx if self.dostepne_czesci[i][2] == 'Część']
        wybrane_uslugi = [self.dostepne_czesci[i][0] for i in idx if self.dostepne_czesci[i][2] == 'Usługa']

        opis_czesci = f"Wymiana: {', '.join(wybrane_czesci)}" if wybrane_czesci else ""
        opis_uslugi = f"Usługa: {', '.join(wybrane_uslugi)}" if wybrane_uslugi else ""
        opis = " | ".join(filter(None, [opis_czesci, opis_uslugi]))

        try:
            conn = sqlite3.connect("serwis.db")
            c = conn.cursor()

            c.execute("INSERT INTO Klienci (imie, nazwisko, telefon, pesel) VALUES (?, ?, ?, ?)",
                      (imie, naz, pelny_telefon, pesel))
            kid = c.lastrowid

            c.execute("INSERT INTO Urzadzenia (id_klienta, numer_seryjny, model) VALUES (?, ?, ?)", (kid, sn, mod))
            uid = c.lastrowid

            c.execute("INSERT INTO Zlecenia (id_urzadzenia, status, opis_usterki, koszt) VALUES (?, 'W kolejce', ?, ?)",
                      (uid, opis, koszt))
            zid = c.lastrowid

            conn.commit()
            conn.close()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()

            # Synchronizacja widoku tabeli statusów ze stanem bazy
            self.zaladuj_wszystkie_zlecenia_status()

            self.wyczysc_formularz()
            # Przekazanie do okienka również numeru seryjnego
            self._pokaz_powiadomienie_o_zleceniu(zid, sn, imie, naz)

        except Exception as e:
            messagebox.showerror("Błąd bazy danych", str(e))

    def _pokaz_powiadomienie_o_zleceniu(self, zid, sn, imie, nazwisko):
        popup = ctk.CTkToplevel(self)
        popup.title("Zlecenie zarejestrowane")
        popup.geometry("350x250")
        popup.attributes("-topmost", True)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Zlecenie zarejestrowane", font=("Arial", 16, "bold"), text_color="#059669").pack(
            pady=(20, 10))

        # ID Zlecenia
        ctk.CTkLabel(popup, text="Numer zlecenia:", font=("Arial", 10), text_color=KOLOR_TEKSTU_SZARY).pack()
        ctk.CTkLabel(popup, text=f"#{zid}", font=("Arial", 28, "bold"), text_color=KOLOR_GLOWNY).pack(pady=(0, 5))

        # Numer seryjny
        ctk.CTkLabel(popup, text="Numer seryjny:", font=("Arial", 10), text_color=KOLOR_TEKSTU_SZARY).pack()
        ctk.CTkLabel(popup, text=sn, font=("Arial", 14, "bold"), text_color=KOLOR_TEKSTU).pack(pady=(0, 10))

        def wydrukuj_i_zamknij():
            try:
                with open("zlecenia_wydruk.txt", "a", encoding="utf-8") as f:
                    f.write("------------------------\n")
                    f.write(f"Numer zlecenia: #{zid}\n")
                    f.write(f"Numer seryjny:  {sn}\n")
                    f.write(f"Klient: {imie} {nazwisko}\n")
                    f.write("------------------------\n\n")
            except Exception as e:
                messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać do pliku:\n{e}")
            popup.destroy()

        ctk.CTkButton(popup, text="Wydrukuj", command=wydrukuj_i_zamknij, width=200, fg_color=KOLOR_GLOWNY,
                      hover_color="#7c3aed").pack(pady=(10, 20))

        # Zamknięcie okna przez "X" również wywołuje zapis do pliku
        popup.protocol("WM_DELETE_WINDOW", wydrukuj_i_zamknij)

    def _zbuduj_tabele_statusow(self):
        """Buduje tabelę wyników w zakładce status (wywoływana raz)."""
        for widget in self.status_info_frame.winfo_children():
            widget.destroy()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="#212529", rowheight=35,
                        fieldbackground="#ffffff", borderwidth=0)
        style.map('Treeview', background=[('selected', KOLOR_GLOWNY)])
        style.configure("Treeview.Heading", background="#f8f9fa", foreground="#212529", font=('Arial', 10, 'bold'),
                        borderwidth=1, bordercolor="#cbd5e1")
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        ramka_tabeli = ctk.CTkFrame(self.status_info_frame, fg_color="transparent", border_width=1,
                                    border_color="#cbd5e1")
        ramka_tabeli.pack(fill="both", expand=True)

        self.tab_status_wyniki = ttk.Treeview(ramka_tabeli,
                                              columns=("id", "sn", "model", "opis", "status", "koszt"),
                                              show="headings", height=15)
        self.tab_status_wyniki.heading("id", text="ID Zlec.")
        self.tab_status_wyniki.heading("sn", text="Nr seryjny")
        self.tab_status_wyniki.heading("model", text="Model urządzenia")
        self.tab_status_wyniki.heading("opis", text="Opis / Wykonane usługi")
        self.tab_status_wyniki.heading("status", text="Status")
        self.tab_status_wyniki.heading("koszt", text="Koszt")

        self.tab_status_wyniki.column("id", width=60, anchor="center")
        self.tab_status_wyniki.column("sn", width=130, anchor="w")
        self.tab_status_wyniki.column("model", width=200, anchor="w")
        self.tab_status_wyniki.column("opis", width=300, anchor="w")
        self.tab_status_wyniki.column("status", width=110, anchor="center")
        self.tab_status_wyniki.column("koszt", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(ramka_tabeli, orient="vertical", command=self.tab_status_wyniki.yview)
        self.tab_status_wyniki.configure(yscrollcommand=scrollbar.set)
        self.tab_status_wyniki.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y")

    def _wypelnij_tabele_statusow(self, wiersze):
        """Czyści i wypełnia tabelę statusów podanymi wierszami."""
        for item in self.tab_status_wyniki.get_children():
            self.tab_status_wyniki.delete(item)
        for r in wiersze:
            zid, sn, model, opis, status, koszt = r
            self.tab_status_wyniki.insert("", tk.END, values=(zid, sn, model, opis, status, f"{koszt:.2f} PLN"))

    def zaladuj_wszystkie_zlecenia_status(self):
        """Ładuje wszystkie zlecenia do tabeli statusów bezpośrednio z tabeli Zlecenia."""
        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT Z.id, U.numer_seryjny, U.model, Z.opis_usterki, Z.status, Z.koszt
                FROM Zlecenia Z
                JOIN Urzadzenia U ON Z.id_urzadzenia = U.id
                ORDER BY Z.id DESC
            """)
            wiersze = cursor.fetchall()
            conn.close()
            self._wypelnij_tabele_statusow(wiersze)
        except sqlite3.Error:
            pass

    def sprawdz_status(self, *_):
        """Ciche filtrowanie bazy na podstawie pól wejściowych."""
        sn = self.ent_status_sn.get().strip()
        zid = self.ent_status_id.get().strip()

        if not sn and not zid:
            self.zaladuj_wszystkie_zlecenia_status()
            return

        warunki = []
        parametry = []

        if sn:
            warunki.append("U.numer_seryjny LIKE ?")
            parametry.append(f"%{sn}%")

        if zid:
            if not zid.isdigit():
                self._wypelnij_tabele_statusow([])
                return
            warunki.append("Z.id = ?")
            parametry.append(int(zid))

        try:
            conn = sqlite3.connect("serwis.db")
            cursor = conn.cursor()
            zapytanie = """
                SELECT DISTINCT Z.id, U.numer_seryjny, U.model, Z.opis_usterki, Z.status, Z.koszt
                FROM Zlecenia Z
                JOIN Urzadzenia U ON Z.id_urzadzenia = U.id
            """
            if warunki:
                zapytanie += " WHERE " + " AND ".join(warunki)
            zapytanie += " ORDER BY Z.id DESC"

            cursor.execute(zapytanie, parametry)
            wiersze = cursor.fetchall()
            conn.close()
            self._wypelnij_tabele_statusow(wiersze)
        except sqlite3.Error:
            pass
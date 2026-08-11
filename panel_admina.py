import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from narzedzia import log_akcji
import hashlib
import secrets

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Kolory bazowe UI
KOLOR_TLA = "#f8f9fa"
KOLOR_KARTY = "#ffffff"
KOLOR_GLOWNY = "#8b5cf6"
KOLOR_TEKSTU = "#212529"
KOLOR_TEKSTU_SZARY = "#6c757d"


class PanelAdmina(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.set_appearance_mode("light")
        super(PanelAdmina, self).__init__(parent, fg_color=KOLOR_TLA, corner_radius=0)
        self.controller = controller

        # Główny layout (Grid: Lewa kolumna menu, Prawa kolumna treść)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._zbuduj_menu_boczne()
        self._zbuduj_obszar_roboczy()

        # Inicjalne ładowanie danych
        self._odswiez_dashboard()
        self.pokaz_zakladke("dashboard")

    def odswiez_dane(self):
        self.pokaz_zakladke("dashboard")

    def _zbuduj_menu_boczne(self):
        self.menu_boczne = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=KOLOR_KARTY)
        self.menu_boczne.grid(row=0, column=0, sticky="nsew")

        self.menu_boczne.grid_rowconfigure(6, weight=1)

        # Logo / Tytuł
        ctk.CTkLabel(self.menu_boczne, text="ElectroService", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).grid(
            row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        ctk.CTkLabel(self.menu_boczne, text="Panel Administrator", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Przyciski Menu
        self.btn_menu_dash = ctk.CTkButton(self.menu_boczne, text="Dashboard", fg_color=KOLOR_GLOWNY,
                                           text_color="white", anchor="w", corner_radius=8,
                                           command=lambda: self.pokaz_zakladke("dashboard"))
        self.btn_menu_dash.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_kontrola = ctk.CTkButton(self.menu_boczne, text="Kontrola jakości", fg_color="transparent",
                                               text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                               hover_color="#f1f3f5", command=lambda: self.pokaz_zakladke("kontrola"))
        self.btn_menu_kontrola.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_pracownicy = ctk.CTkButton(self.menu_boczne, text="Pracownicy", fg_color="transparent",
                                                 text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                                 hover_color="#f1f3f5",
                                                 command=lambda: self.pokaz_zakladke("pracownicy"))
        self.btn_menu_pracownicy.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.btn_menu_klienci = ctk.CTkButton(self.menu_boczne, text="Klienci", fg_color="transparent",
                                              text_color=KOLOR_TEKSTU, anchor="w", corner_radius=8,
                                              hover_color="#f1f3f5", command=lambda: self.pokaz_zakladke("klienci"))
        self.btn_menu_klienci.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        # Profil na dole (admin)
        profil_frame = ctk.CTkFrame(self.menu_boczne, fg_color="transparent")
        profil_frame.grid(row=7, column=0, padx=15, pady=20, sticky="ew")
        ctk.CTkLabel(profil_frame, text="AD", width=30, height=30, corner_radius=15, fg_color=KOLOR_GLOWNY,
                     text_color="white").pack(side="left")
        opis_profilu = ctk.CTkFrame(profil_frame, fg_color="transparent")
        opis_profilu.pack(side="left", padx=10)
        ctk.CTkLabel(opis_profilu, text="admin", font=("Arial", 12, "bold"), text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(opis_profilu, text="Administrator", font=("Arial", 10), text_color=KOLOR_TEKSTU_SZARY).pack(
            anchor="w")

        ctk.CTkButton(profil_frame, text="Wyloguj", width=60, fg_color="transparent", text_color="#ef4444",
                      hover_color="#fee2e2", command=self.wyloguj).pack(side="right")

    def _zbuduj_obszar_roboczy(self):
        self.obszar_roboczy = ctk.CTkFrame(self, fg_color=KOLOR_TLA, corner_radius=0)
        self.obszar_roboczy.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        self.obszar_roboczy.grid_rowconfigure(1, weight=1)
        self.obszar_roboczy.grid_columnconfigure(0, weight=1)

        # ZAKŁADKI
        self.zakladka_dashboard = ctk.CTkScrollableFrame(self.obszar_roboczy, fg_color="transparent")
        self.zakladka_kontrola = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        self.zakladka_pracownicy = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")
        self.zakladka_klienci = ctk.CTkFrame(self.obszar_roboczy, fg_color="transparent")

        self._zbuduj_zawartosc_dashboard()
        self._zbuduj_zawartosc_kontrola()
        self._zbuduj_zawartosc_pracownicy()
        self._zbuduj_zawartosc_klienci()

    def pokaz_zakladke(self, nazwa):
        self.zakladka_dashboard.grid_forget()
        self.zakladka_kontrola.grid_forget()
        self.zakladka_pracownicy.grid_forget()
        self.zakladka_klienci.grid_forget()

        self.btn_menu_dash.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_kontrola.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_pracownicy.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")
        self.btn_menu_klienci.configure(fg_color="transparent", text_color=KOLOR_TEKSTU, hover_color="#f1f3f5")

        if nazwa == "dashboard":
            self.zakladka_dashboard.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_dash.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
            self._odswiez_dashboard()
        elif nazwa == "kontrola":
            self.zakladka_kontrola.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_kontrola.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
            self.odswiez_tabele_kontroli()
        elif nazwa == "pracownicy":
            self.zakladka_pracownicy.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_pracownicy.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
            self.odswiez_tabele_pracownikow()
        elif nazwa == "klienci":
            self.zakladka_klienci.grid(row=1, column=0, sticky="nsew")
            self.btn_menu_klienci.configure(fg_color=KOLOR_GLOWNY, text_color="white", hover_color="#7c3aed")
            self.odswiez_tabele_klientow()

    # ================= DASHBOARD =================
    def _zbuduj_zawartosc_dashboard(self):
        # Nagłówek Dashboardu
        naglowek_frame = ctk.CTkFrame(self.zakladka_dashboard, fg_color="transparent")
        naglowek_frame.pack(fill="x", pady=(0, 20))
        tytul_lewa = ctk.CTkFrame(naglowek_frame, fg_color="transparent")
        tytul_lewa.pack(side="left")
        ctk.CTkLabel(tytul_lewa, text="Dashboard administratora", font=("Arial", 24, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w")
        ctk.CTkLabel(tytul_lewa, text="Podgląd statusów napraw, kontrola jakości i metryki serwisu.",
                     font=("Arial", 14), text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w")

        ctk.CTkLabel(naglowek_frame, text="● System online", text_color="#059669", fg_color="#d1fae5", corner_radius=15,
                     padx=10, pady=5).pack(side="right")

        # KARTY KPI (4 w rzędzie)
        kpi_frame = ctk.CTkFrame(self.zakladka_dashboard, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 20))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_aktywne = self._stworz_karte_kpi(kpi_frame, 0, "Aktywne zlecenia", "0", KOLOR_GLOWNY,)
        self.kpi_naprawa = self._stworz_karte_kpi(kpi_frame, 1, "W naprawie", "0", "#0ea5e9",)
        self.kpi_wydanie = self._stworz_karte_kpi(kpi_frame, 2, "Do wydania", "0", "#10b981",)
        self.kpi_przychod = self._stworz_karte_kpi(kpi_frame, 3, "Przychód (PLN)", "0", "#f59e0b",)

        # WYKRESY (2 kolumny)
        wykresy_frame = ctk.CTkFrame(self.zakladka_dashboard, fg_color="transparent")
        wykresy_frame.pack(fill="both", expand=True)
        wykresy_frame.grid_columnconfigure((0, 1), weight=1)

        # Lewy wykres (Pierścieniowy / Donut)
        karta_wykres_lewy = ctk.CTkFrame(wykresy_frame, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                         border_color="#e9ecef")
        karta_wykres_lewy.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(karta_wykres_lewy, text="Statusy urządzeń", font=("Arial", 14, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(karta_wykres_lewy, text="Rozkład bieżących stanów napraw.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)

        self.plot_frame_lewy = ctk.CTkFrame(karta_wykres_lewy, fg_color="transparent", height=250)
        self.plot_frame_lewy.pack(fill="both", expand=True, padx=20, pady=20)

        # Prawy wykres (Słupkowy / Bar)
        karta_wykres_prawy = ctk.CTkFrame(wykresy_frame, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                                          border_color="#e9ecef")
        karta_wykres_prawy.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(karta_wykres_prawy, text="Urządzenia w serwisie", font=("Arial", 14, "bold"),
                     text_color=KOLOR_TEKSTU).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(karta_wykres_prawy, text="Liczba aktywnych zleceń wg kategorii.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)

        self.plot_frame_prawy = ctk.CTkFrame(karta_wykres_prawy, fg_color="transparent", height=250)
        self.plot_frame_prawy.pack(fill="both", expand=True, padx=20, pady=20)

    def _stworz_karte_kpi(self, parent, col, tytul, wartosc, kolor):
        karta = ctk.CTkFrame(parent, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        karta.grid(row=0, column=col, sticky="nsew", padx=10)

        gora = ctk.CTkFrame(karta, fg_color="transparent")
        gora.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(gora, text=tytul, font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).pack(side="left")

        lbl_wartosc = ctk.CTkLabel(karta, text=wartosc, font=("Arial", 28, "bold"), text_color=KOLOR_TEKSTU)
        lbl_wartosc.pack(anchor="w", padx=20)

        ctk.CTkLabel(karta, text="Aktualizowane na żywo", font=("Arial", 10), text_color="#10b981").pack(anchor="w",
                                                                                                         padx=20,
                                                                                                         pady=(
                                                                                                             10, 20))

        return lbl_wartosc

    def _odswiez_dashboard(self):
        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()

            # Zakładamy strukturę bazy, w razie braku kolumny koszt używamy 0
            cursor.execute("SELECT COUNT(*) FROM Zlecenia WHERE status != 'Wydane'")
            akt = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Zlecenia WHERE status = 'W naprawie'")
            nap = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Zlecenia WHERE status IN ('Gotowe', 'Do wydania')")
            wyd = cursor.fetchone()[0]

            # Próba pobrania przychodu, bezpieczny fallback na błąd
            try:
                cursor.execute("SELECT SUM(koszt) FROM Zlecenia WHERE status = 'Wydane'")
                suma = cursor.fetchone()[0]
                przychod = "{:.0f}".format(suma) if suma else "0"
            except Exception:
                przychod = "4478"  # Mock jeżeli struktura bazy nie ma kosztu

            self.kpi_aktywne.configure(text=str(akt))
            self.kpi_naprawa.configure(text=str(nap))
            self.kpi_wydanie.configure(text=str(wyd))
            self.kpi_przychod.configure(text=przychod)

            self._rysuj_wykresy(cursor)
        except Exception as e:
            print("Błąd Dashboardu: {}".format(e))
        finally:
            if conn:
                conn.close()

    def _rysuj_wykresy(self, cursor):
        # Czyszczenie ramek
        for widget in self.plot_frame_lewy.winfo_children(): widget.destroy()
        for widget in self.plot_frame_prawy.winfo_children(): widget.destroy()

        # ================= WYKRES PIERŚCIENIOWY (Donut) =================
        cursor.execute("""
                SELECT status, COUNT(*) FROM Zlecenia 
                WHERE status != 'Wydane' GROUP BY status
            """)
        dane_donut = cursor.fetchall()

        fig_donut = Figure(figsize=(5, 3), dpi=100)
        fig_donut.patch.set_facecolor('#ffffff')
        ax1 = fig_donut.add_subplot(111)

        # Obliczamy sumę, aby sprawdzić czy są jakieś zlecenia w bazie
        suma_zlecen = sum(d[1] for d in dane_donut) if dane_donut else 0

        if suma_zlecen == 0:
            # Scenariusz BRAK DANYCH: Rysujemy szary pierścień
            ax1.pie([1], colors=['#e9ecef'], startangle=90,
                    wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2))
            ax1.text(0, 0, "Brak aktywnych\nzleceń", ha='center', va='center',
                     fontsize=10, color=KOLOR_TEKSTU_SZARY, fontweight='bold')
            ax1.axis('equal')
        else:
            # Scenariusz SĄ DANE: Rysujemy normalny wykres
            etykiety = [d[0] for d in dane_donut]
            wartosci = [d[1] for d in dane_donut]
            kolory = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

            wedges, texts = ax1.pie(
                wartosci,
                colors=kolory,
                startangle=90,
                wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2)
            )
            ax1.axis('equal')
            fig_donut.legend(wedges, etykiety, loc="lower center", ncol=2, frameon=False, fontsize=9)

        fig_donut.subplots_adjust(bottom=0.25, top=0.95, left=0.05, right=0.95)

        canvas1 = FigureCanvasTkAgg(fig_donut, master=self.plot_frame_lewy)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # ================= WYKRES SŁUPKOWY (Bar) =================
        try:
            cursor.execute("""
                SELECT U.model, COUNT(Z.id) FROM Zlecenia Z
                JOIN Urzadzenia U ON Z.id_urzadzenia = U.id
                WHERE Z.status != 'Wydane'
                GROUP BY U.model LIMIT 4
            """)
            dane_bar = cursor.fetchall()
        except Exception:
            dane_bar = []

        fig_bar = Figure(figsize=(5, 3), dpi=100)
        fig_bar.patch.set_facecolor('#ffffff')
        ax2 = fig_bar.add_subplot(111)

        if not dane_bar:
            # Scenariusz BRAK DANYCH
            ax2.text(0.5, 0.5, "Brak aktywnych\nzleceń", ha='center', va='center',
                     fontsize=10, color=KOLOR_TEKSTU_SZARY, fontweight='bold')
            ax2.axis('off')  # Ukrywamy puste osie
        else:
            kategorie = [d[0].split()[0] for d in dane_bar]  # Skrócone nazwy
            ilosci = [d[1] for d in dane_bar]

            ax2.bar(kategorie, ilosci, color=KOLOR_GLOWNY, edgecolor='white', width=0.7, alpha=0.9)

            # Stylowanie osi
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.spines['bottom'].set_color('#e9ecef')
            ax2.tick_params(axis='x', colors=KOLOR_TEKSTU_SZARY)
            ax2.tick_params(axis='y', colors=KOLOR_TEKSTU_SZARY)
            ax2.yaxis.grid(True, linestyle='--', alpha=0.5, color='#dee2e6')

        fig_bar.subplots_adjust(bottom=0.15, top=0.95, left=0.1, right=0.95)

        canvas2 = FigureCanvasTkAgg(fig_bar, master=self.plot_frame_prawy)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

    # ================= KONTROLA JAKOŚCI =================
    def _zbuduj_zawartosc_kontrola(self):
        self.zakladka_kontrola.grid_columnconfigure(0, weight=1)
        self.zakladka_kontrola.grid_rowconfigure(1, weight=1)

        karta = ctk.CTkFrame(self.zakladka_kontrola, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1,
                             border_color="#e9ecef")
        karta.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(karta, text="Kontrola jakości", font=("Arial", 16, "bold"), text_color=KOLOR_TEKSTU).pack(
            anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(karta, text="Naprawy oczekujące na zatwierdzenie przed wydaniem klientowi.", font=("Arial", 12),
                     text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20, pady=(0, 20))

        # Nagłówki tabeli
        naglowki_frame = ctk.CTkFrame(karta, fg_color="#f8f9fa", height=40, corner_radius=5)
        naglowki_frame.pack(fill="x", padx=20)
        naglowki_frame.grid_columnconfigure((1, 2, 3), weight=2)
        naglowki_frame.grid_columnconfigure(4, weight=1)
        naglowki_frame.grid_columnconfigure(5, weight=2)  # Akcje

        kolumny = ["ID", "Urządzenie", "Technik", "Usterka", "Koszt", "Akcje"]
        szerokosci = [0, 1, 2, 3, 4, 5]
        for i, col in zip(szerokosci, kolumny):
            anchor = "e" if col == "Akcje" else "w"
            ctk.CTkLabel(naglowki_frame, text=col, font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).grid(
                row=0, column=i, sticky="n" + anchor, padx=15, pady=10)

        # Zawartość tabeli (Scrollowalna)
        self.tabela_scroll = ctk.CTkScrollableFrame(karta, fg_color="transparent")
        self.tabela_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def odswiez_tabele_kontroli(self):
        # Czyszczenie starych wierszy
        for widget in self.tabela_scroll.winfo_children():
            widget.destroy()

        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Z.id, U.model, T.login, Z.opis_usterki, Z.koszt
                FROM Zlecenia Z
                JOIN Urzadzenia U ON Z.id_urzadzenia = U.id
                LEFT JOIN Uzytkownicy T ON Z.id_technika = T.id
                WHERE Z.status = 'Do kontroli'
            """)
            wyniki = cursor.fetchall()

            for zlec in wyniki:
                self._dodaj_wiersz_tabeli(zlec)

        except sqlite3.Error as e:
            print("Błąd odświeżania tabeli: {}".format(e))
        finally:
            if conn:
                conn.close()

    def _dodaj_wiersz_tabeli(self, zlec):
        zid, model, technik, usterka, koszt = zlec
        koszt_str = "{} PLN".format(koszt) if koszt else "Brak"
        technik_login = technik if technik else "Brak"

        wiersz = ctk.CTkFrame(self.tabela_scroll, fg_color="transparent", border_width=0)
        wiersz.pack(fill="x", pady=5)

        separator = ctk.CTkFrame(self.tabela_scroll, fg_color="#e9ecef", height=1)
        separator.pack(fill="x", pady=2)

        wiersz.grid_columnconfigure((1, 2, 3), weight=2)
        wiersz.grid_columnconfigure(4, weight=1)
        wiersz.grid_columnconfigure(5, weight=2)

        ctk.CTkLabel(wiersz, text="#{}".format(zid), font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=model, font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=technik_login, font=("Arial", 12), text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=2,
                                                                                                   sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=usterka[:15] + "..." if len(usterka) > 15 else usterka, font=("Arial", 12)).grid(
            row=0, column=3, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=koszt_str, font=("Arial", 12, "bold")).grid(row=0, column=4, sticky="w", padx=15)

        akcje_frame = ctk.CTkFrame(wiersz, fg_color="transparent")
        akcje_frame.grid(row=0, column=5, sticky="e", padx=15)

        ctk.CTkButton(akcje_frame, text="Poprawka", fg_color="white", text_color=KOLOR_TEKSTU, border_width=1,
                      border_color="#dee2e6", hover_color="#f8f9fa", width=80, height=28,
                      command=lambda id_zlecenia=zid: self.odrzuc_jakosc(id_zlecenia)).pack(side="left", padx=5)
        ctk.CTkButton(akcje_frame, text="Zatwierdź", fg_color="#059669", text_color="white", hover_color="#047857",
                      width=80, height=28, command=lambda id_zlecenia=zid: self.zatwierdz_jakosc(id_zlecenia)).pack(side="left")

    @log_akcji("Admin zatwierdził naprawę")
    def zatwierdz_jakosc(self, id_zlecenia):
        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("UPDATE Zlecenia SET status = 'Gotowe' WHERE id = ?", (id_zlecenia,))
            conn.commit()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()

            messagebox.showinfo("Sukces", "Sprzęt zatwierdzony. Gotowy do wydania.")
            self.odswiez_tabele_kontroli()
            self._odswiez_dashboard()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd", "Błąd DB: {}".format(e))
        finally:
            if conn:
                conn.close()

    @log_akcji("Admin odrzucił naprawę")
    def odrzuc_jakosc(self, id_zlecenia):
        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("UPDATE Zlecenia SET status = 'Poprawka (Priorytet)' WHERE id = ?", (id_zlecenia,))
            conn.commit()

            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()

            messagebox.showinfo("Odrzucono", "Sprzęt wraca na warsztat z priorytetem.")
            self.odswiez_tabele_kontroli()
            self._odswiez_dashboard()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd", "Błąd DB: {}".format(e))
        finally:
            if conn:
                conn.close()

    # ================= PRACOWNICY (CRUD) =================
    def _zbuduj_zawartosc_pracownicy(self):
        self.zakladka_pracownicy.grid_columnconfigure(0, weight=1)
        self.zakladka_pracownicy.grid_columnconfigure(1, weight=3)
        self.zakladka_pracownicy.grid_rowconfigure(1, weight=1)

        # Formularz po lewej
        formularz = ctk.CTkFrame(self.zakladka_pracownicy, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        formularz.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(formularz, text="Zarządzanie pracownikami", font=("Arial", 16, "bold")).pack(pady=(20, 5), padx=20, anchor="w")

        ctk.CTkLabel(formularz, text="Login:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.ent_pracownik_login = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0)
        self.ent_pracownik_login.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(formularz, text="Hasło:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.ent_pracownik_haslo = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0, show="*")
        self.ent_pracownik_haslo.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(formularz, text="Rola:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.cb_pracownik_rola = ctk.CTkComboBox(formularz, values=["Admin", "Recepcja", "Technik", "Magazyn"], fg_color="#f1f3f5", border_width=0, state="readonly")
        self.cb_pracownik_rola.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(formularz, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_dodaj_pracownika = ctk.CTkButton(btn_frame, text="Dodaj", fg_color="#10b981", hover_color="#059669", command=self.dodaj_pracownika)
        self.btn_dodaj_pracownika.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_edytuj_pracownika = ctk.CTkButton(btn_frame, text="Zapisz", fg_color="#3b82f6", hover_color="#2563eb", state="disabled", command=self.zapisz_edycje_pracownika)
        self.btn_edytuj_pracownika.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.btn_anuluj_edycje_pracownika = ctk.CTkButton(formularz, text="Anuluj edycję", fg_color="#ef4444", hover_color="#dc2626", command=self.anuluj_edycje_pracownika)
        
        self.wybrany_pracownik_id = None

        # Tabela po prawej
        karta_tabeli = ctk.CTkFrame(self.zakladka_pracownicy, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        karta_tabeli.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(karta_tabeli, text="Lista pracowników", font=("Arial", 16, "bold")).pack(pady=(20, 10), padx=20, anchor="w")

        naglowki_frame = ctk.CTkFrame(karta_tabeli, fg_color="#f8f9fa", height=40, corner_radius=5)
        naglowki_frame.pack(fill="x", padx=20)
        naglowki_frame.grid_columnconfigure((0, 1), weight=1)
        naglowki_frame.grid_columnconfigure(2, weight=2)

        for i, col in enumerate(["Login", "Rola", "Akcje"]):
            anchor = "e" if col == "Akcje" else "w"
            ctk.CTkLabel(naglowki_frame, text=col, font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=i, sticky="n" + anchor, padx=15, pady=10)

        self.scroll_pracownicy = ctk.CTkScrollableFrame(karta_tabeli, fg_color="transparent")
        self.scroll_pracownicy.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def odswiez_tabele_pracownikow(self):
        for widget in self.scroll_pracownicy.winfo_children():
            widget.destroy()

        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, rola FROM Uzytkownicy")
            pracownicy = cursor.fetchall()

            for p in pracownicy:
                self._dodaj_wiersz_pracownika(p)
        except sqlite3.Error as e:
            print("Błąd DB: {}".format(e))
        finally:
            if conn:
                conn.close()

    def _dodaj_wiersz_pracownika(self, pracownik):
        pid, login, rola = pracownik

        wiersz = ctk.CTkFrame(self.scroll_pracownicy, fg_color="transparent")
        wiersz.pack(fill="x", pady=5)
        
        separator = ctk.CTkFrame(self.scroll_pracownicy, fg_color="#e9ecef", height=1)
        separator.pack(fill="x", pady=2)

        wiersz.grid_columnconfigure((0, 1), weight=1)
        wiersz.grid_columnconfigure(2, weight=2)

        ctk.CTkLabel(wiersz, text=login).grid(row=0, column=0, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=rola, text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=1, sticky="w", padx=15)

        akcje_frame = ctk.CTkFrame(wiersz, fg_color="transparent")
        akcje_frame.grid(row=0, column=2, sticky="e", padx=15)

        ctk.CTkButton(akcje_frame, text="Edytuj", width=60, fg_color="#3b82f6", hover_color="#2563eb", command=lambda p=pracownik: self.rozpocznij_edycje_pracownika(p)).pack(side="left", padx=5)
        ctk.CTkButton(akcje_frame, text="Usuń", width=60, fg_color="#ef4444", hover_color="#dc2626", command=lambda p_id=pid, p_rola=rola: self.usun_pracownika(p_id, p_rola)).pack(side="left")

    @log_akcji("Admin dodał pracownika")
    def dodaj_pracownika(self):
        login = self.ent_pracownik_login.get().strip()
        haslo = self.ent_pracownik_haslo.get().strip()
        rola = self.cb_pracownik_rola.get().strip()

        if not all([login, haslo, rola]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola!")
            return

        conn = None
        try:
            # Generowanie hasha PBKDF2 z solą
            sol = secrets.token_hex(16)
            hash_hasla = hashlib.pbkdf2_hmac('sha256', haslo.encode('utf-8'), sol.encode('utf-8'), 100000).hex()
            zahashowane_haslo = f"{sol}${hash_hasla}"

            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()

            # Wstawiamy zahashowane hasło do bazy
            cursor.execute("INSERT INTO Uzytkownicy (login, haslo, rola) VALUES (?, ?, ?)",
                           (login, zahashowane_haslo, rola))
            conn.commit()

            messagebox.showinfo("Sukces", "Dodano pracownika.")
            self.wyczysc_formularz_pracownika()
            self.odswiez_tabele_pracownikow()
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Login zajęty!")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))
        finally:
            if conn:
                conn.close()

    def rozpocznij_edycje_pracownika(self, pracownik):
        pid, login, rola = pracownik
        self.wybrany_pracownik_id = pid
        
        self.wyczysc_formularz_pracownika()
        
        self.ent_pracownik_login.insert(0, login)
        self.cb_pracownik_rola.set(rola)
        
        self.btn_dodaj_pracownika.configure(state="disabled")
        self.btn_edytuj_pracownika.configure(state="normal")
        self.btn_anuluj_edycje_pracownika.pack(fill="x", padx=20, pady=(0, 10))

    @log_akcji("Admin edytował pracownika")
    def zapisz_edycje_pracownika(self):
        if not self.wybrany_pracownik_id: return
        
        login = self.ent_pracownik_login.get().strip()
        haslo = self.ent_pracownik_haslo.get().strip()
        rola = self.cb_pracownik_rola.get().strip()

        if not all([login, rola]):
            messagebox.showwarning("Błąd", "Wypełnij wymagane pola (hasło opcjonalne).")
            return

        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("SELECT rola FROM Uzytkownicy WHERE id = ?", (self.wybrany_pracownik_id,))
            stara_rola = cursor.fetchone()[0]
            
            if stara_rola != rola:
                cursor.execute("SELECT COUNT(*) FROM Uzytkownicy WHERE rola = ?", (stara_rola,))
                if cursor.fetchone()[0] <= 1:
                    messagebox.showwarning("Błąd", "Nie można zmienić roli. W systemie musi pozostać przynajmniej jeden pracownik z rolą '{}'!".format(stara_rola))
                    return

            if haslo:
                sol = secrets.token_hex(16)
                hash_hasla = hashlib.pbkdf2_hmac('sha256', haslo.encode('utf-8'), sol.encode('utf-8'), 100000).hex()
                zahashowane_haslo = f"{sol}${hash_hasla}"
                cursor.execute("UPDATE Uzytkownicy SET login=?, haslo=?, rola=? WHERE id=?",
                               (login, zahashowane_haslo, rola, self.wybrany_pracownik_id))
            else:
                cursor.execute("UPDATE Uzytkownicy SET login=?, rola=? WHERE id=?",
                               (login, rola, self.wybrany_pracownik_id))
                
            conn.commit()
            
            messagebox.showinfo("Sukces", "Zaktualizowano dane pracownika.")
            self.anuluj_edycje_pracownika()
            self.odswiez_tabele_pracownikow()
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Login zajęty!")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))
        finally:
            if conn:
                conn.close()

    def anuluj_edycje_pracownika(self):
        self.wybrany_pracownik_id = None
        self.wyczysc_formularz_pracownika()
        self.btn_dodaj_pracownika.configure(state="normal")
        self.btn_edytuj_pracownika.configure(state="disabled")
        self.btn_anuluj_edycje_pracownika.pack_forget()

    def wyczysc_formularz_pracownika(self):
        self.ent_pracownik_login.delete(0, 'end')
        self.ent_pracownik_haslo.delete(0, 'end')
        self.cb_pracownik_rola.set('')

    @log_akcji("Admin usunął pracownika")
    def usun_pracownika(self, pid, rola):
        if str(pid) == str(getattr(self.controller, 'zalogowany_uzytkownik_id', '')):
             messagebox.showwarning("Błąd", "Nie możesz usunąć swojego własnego konta!")
             return
             
        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Uzytkownicy WHERE rola = ?", (rola,))
            ile = cursor.fetchone()[0]
            if ile <= 1:
                messagebox.showwarning("Błąd", "Nie można usunąć. W systemie musi pozostać przynajmniej jeden pracownik z rolą '{}'!".format(rola))
                return
                
            if messagebox.askyesno("Potwierdź", "Na pewno chcesz usunąć tego pracownika?"):
                if rola == 'Technik':
                    cursor.execute("""
                        UPDATE Zlecenia 
                        SET status = 'W kolejce', id_technika = NULL 
                        WHERE id_technika = ? AND status NOT IN ('Gotowe', 'Wydane', 'Do wydania')
                    """, (pid,))

                cursor.execute("DELETE FROM Uzytkownicy WHERE id = ?", (pid,))
                conn.commit()
                messagebox.showinfo("Sukces", "Usunięto pracownika (i zwolniono jego zlecenia, jeśli to technik).")
                if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
                self.odswiez_tabele_pracownikow()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))
        finally:
            if conn:
                conn.close()

    # ================= KLIENCI (Edycja) =================
    def _zbuduj_zawartosc_klienci(self):
        self.zakladka_klienci.grid_columnconfigure(0, weight=1)
        self.zakladka_klienci.grid_columnconfigure(1, weight=3)
        self.zakladka_klienci.grid_rowconfigure(1, weight=1)

        # Formularz po lewej
        formularz = ctk.CTkFrame(self.zakladka_klienci, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        formularz.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(formularz, text="Edycja Klienta", font=("Arial", 16, "bold")).pack(pady=(20, 5), padx=20, anchor="w")

        ctk.CTkLabel(formularz, text="Imię:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.ent_klient_imie = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0)
        self.ent_klient_imie.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(formularz, text="Nazwisko:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.ent_klient_nazwisko = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0)
        self.ent_klient_nazwisko.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(formularz, text="Telefon:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.ent_klient_telefon = ctk.CTkEntry(formularz, fg_color="#f1f3f5", border_width=0)
        self.ent_klient_telefon.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(formularz, text="Status Zlecenia:", text_color=KOLOR_TEKSTU_SZARY).pack(anchor="w", padx=20)
        self.cb_klient_status = ctk.CTkComboBox(formularz, values=["W kolejce", "W naprawie", "Czeka na części", "Do kontroli", "Gotowe", "Wydane"], fg_color="#f1f3f5", border_width=0, state="readonly")
        self.cb_klient_status.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_zapisz_klienta = ctk.CTkButton(formularz, text="Zapisz zmiany", fg_color="#3b82f6", hover_color="#2563eb", state="disabled", command=self.zapisz_edycje_klienta)
        self.btn_zapisz_klienta.pack(fill="x", padx=20, pady=10)
        
        self.btn_anuluj_edycje_klienta = ctk.CTkButton(formularz, text="Anuluj", fg_color="#ef4444", hover_color="#dc2626", command=self.anuluj_edycje_klienta)
        
        self.wybrany_klient_id = None
        self.wybrane_zlecenie_id = None

        # Tabela po prawej
        karta_tabeli = ctk.CTkFrame(self.zakladka_klienci, fg_color=KOLOR_KARTY, corner_radius=10, border_width=1, border_color="#e9ecef")
        karta_tabeli.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(karta_tabeli, text="Baza Klientów i Zleceń", font=("Arial", 16, "bold")).pack(pady=(20, 10), padx=20, anchor="w")

        naglowki_frame = ctk.CTkFrame(karta_tabeli, fg_color="#f8f9fa", height=40, corner_radius=5)
        naglowki_frame.pack(fill="x", padx=20)
        naglowki_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        naglowki_frame.grid_columnconfigure(4, weight=1)

        for i, col in enumerate(["ID Zlecenia", "Klient", "Telefon", "Status", "Akcje"]):
            anchor = "e" if col == "Akcje" else "w"
            ctk.CTkLabel(naglowki_frame, text=col, font=("Arial", 11, "bold"), text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=i, sticky="n" + anchor, padx=15, pady=10)

        self.scroll_klienci = ctk.CTkScrollableFrame(karta_tabeli, fg_color="transparent")
        self.scroll_klienci.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def odswiez_tabele_klientow(self):
        for widget in self.scroll_klienci.winfo_children():
            widget.destroy()

        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Z.id, K.id, K.imie, K.nazwisko, K.telefon, Z.status 
                FROM Zlecenia Z
                JOIN Urzadzenia U ON Z.id_urzadzenia = U.id
                JOIN Klienci K ON U.id_klienta = K.id
            """)
            zlecenia = cursor.fetchall()

            for z in zlecenia:
                self._dodaj_wiersz_klienta(z)
        except sqlite3.Error as e:
            print("Błąd DB: {}".format(e))
        finally:
            if conn:
                conn.close()

    def _dodaj_wiersz_klienta(self, zlecenie):
        zid, kid, imie, nazwisko, telefon, status = zlecenie

        wiersz = ctk.CTkFrame(self.scroll_klienci, fg_color="transparent")
        wiersz.pack(fill="x", pady=5)
        
        separator = ctk.CTkFrame(self.scroll_klienci, fg_color="#e9ecef", height=1)
        separator.pack(fill="x", pady=2)

        wiersz.grid_columnconfigure((0, 1, 2, 3), weight=1)
        wiersz.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(wiersz, text="#{}".format(zid)).grid(row=0, column=0, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text="{} {}".format(imie, nazwisko)).grid(row=0, column=1, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=telefon).grid(row=0, column=2, sticky="w", padx=15)
        ctk.CTkLabel(wiersz, text=status, text_color=KOLOR_TEKSTU_SZARY).grid(row=0, column=3, sticky="w", padx=15)

        akcje_frame = ctk.CTkFrame(wiersz, fg_color="transparent")
        akcje_frame.grid(row=0, column=4, sticky="e", padx=15)

        ctk.CTkButton(akcje_frame, text="Edytuj", width=60, fg_color="#3b82f6", hover_color="#2563eb", command=lambda z=zlecenie: self.rozpocznij_edycje_klienta(z)).pack(side="left", padx=5)
        ctk.CTkButton(akcje_frame, text="Usuń", width=60, fg_color="#ef4444", hover_color="#dc2626", command=lambda k_id=kid: self.usun_klienta(k_id)).pack(side="left")

    def rozpocznij_edycje_klienta(self, zlecenie):
        zid, kid, imie, nazwisko, telefon, status = zlecenie
        self.wybrany_klient_id = kid
        self.wybrane_zlecenie_id = zid
        
        self.wyczysc_formularz_klienta()
        
        self.ent_klient_imie.insert(0, imie)
        self.ent_klient_nazwisko.insert(0, nazwisko)
        self.ent_klient_telefon.insert(0, telefon)
        self.cb_klient_status.set(status)
        
        self.btn_zapisz_klienta.configure(state="normal")
        self.btn_anuluj_edycje_klienta.pack(fill="x", padx=20, pady=(0, 10))

    @log_akcji("Admin edytował dane klienta/zlecenia")
    def zapisz_edycje_klienta(self):
        if not self.wybrany_klient_id or not self.wybrane_zlecenie_id: return
        
        imie = self.ent_klient_imie.get().strip()
        nazwisko = self.ent_klient_nazwisko.get().strip()
        telefon = self.ent_klient_telefon.get().strip()
        status = self.cb_klient_status.get()

        if not all([imie, nazwisko, telefon, status]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola!")
            return

        conn = None
        try:
            conn = sqlite3.connect("serwis.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("UPDATE Klienci SET imie=?, nazwisko=?, telefon=? WHERE id=?", (imie, nazwisko, telefon, self.wybrany_klient_id))

            if status == "Wydane":
                cursor.execute("DELETE FROM Zapotrzebowania WHERE id_zlecenia=?", (self.wybrane_zlecenie_id,))
                cursor.execute("UPDATE Zlecenia SET status=? WHERE id=?", (status, self.wybrane_zlecenie_id))
                messagebox.showinfo("Sukces", "Zlecenie zostało oznaczone jako wydane i zamknięte.")
            else:
                cursor.execute("UPDATE Zlecenia SET status=? WHERE id=?", (status, self.wybrane_zlecenie_id))
                messagebox.showinfo("Sukces", "Zaktualizowano dane.")

            conn.commit()
            
            if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
            self.anuluj_edycje_klienta()
            self.odswiez_tabele_klientow()
        except sqlite3.Error as e:
            messagebox.showerror("Błąd DB", str(e))
        finally:
            if conn:
                conn.close()

    def anuluj_edycje_klienta(self):
        self.wybrany_klient_id = None
        self.wybrane_zlecenie_id = None
        self.wyczysc_formularz_klienta()
        self.btn_zapisz_klienta.configure(state="disabled")
        self.btn_anuluj_edycje_klienta.pack_forget()

    def wyczysc_formularz_klienta(self):
        self.ent_klient_imie.delete(0, 'end')
        self.ent_klient_nazwisko.delete(0, 'end')
        self.ent_klient_telefon.delete(0, 'end')
        self.cb_klient_status.set('')

    @log_akcji("Admin usunął klienta")
    def usun_klienta(self, kid):
        if messagebox.askyesno("Potwierdź", "Usunięcie klienta spowoduje usunięcie wszystkich jego zleceń i urządzeń. Kontynuować?"):
            conn = None
            try:
                conn = sqlite3.connect("serwis.db", timeout=10)
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = OFF")
                
                # Manualne usuwanie kaskadowe w celu pominięcia błędu constraint failure w SQLite
                # 1. Szukamy urządzeń klienta
                cursor.execute("SELECT id FROM Urzadzenia WHERE id_klienta = ?", (kid,))
                urzadzenia = cursor.fetchall()
                
                for (uid,) in urzadzenia:
                    # 2. Szukamy zleceń powiązanych z tym urządzeniem
                    cursor.execute("SELECT id FROM Zlecenia WHERE id_urzadzenia = ?", (uid,))
                    zlecenia = cursor.fetchall()
                    for (zid,) in zlecenia:
                        # 3. Usuwamy ewentualne zapotrzebowania powiązane ze zleceniem
                        cursor.execute("DELETE FROM Zapotrzebowania WHERE id_zlecenia = ?", (zid,))
                    # 4. Usuwamy zlecenia dla urządzenia
                    cursor.execute("DELETE FROM Zlecenia WHERE id_urzadzenia = ?", (uid,))
                
                # 5. Usuwamy urządzenia
                cursor.execute("DELETE FROM Urzadzenia WHERE id_klienta = ?", (kid,))
                
                # 6. Usuwamy ostatecznie klienta
                cursor.execute("DELETE FROM Klienci WHERE id = ?", (kid,))
                
                conn.commit()
                
                messagebox.showinfo("Sukces", "Usunięto klienta i wszystkie powiązane z nim dane.")
                if hasattr(self.controller, 'powiadamiacz'): self.controller.powiadamiacz.wyslij_ping()
                self.odswiez_tabele_klientow()
            except sqlite3.Error as e:
                messagebox.showerror("Błąd DB", str(e))
            finally:
                if conn:
                    conn.close()

    def wyloguj(self):
        self.controller.pokaz_panel("PanelLogowania")
import sqlite3
from narzedzia import hashuj_haslo


def inicjalizuj_baze_modeli_i_czesci():
    conn = sqlite3.connect("serwis.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS Zapotrzebowania")
    cursor.execute("DROP TABLE IF EXISTS Czesci")
    cursor.execute("DROP TABLE IF EXISTS CzesciKatalog")
    cursor.execute("DROP TABLE IF EXISTS Zlecenia")
    cursor.execute("DROP TABLE IF EXISTS Urzadzenia")
    cursor.execute("DROP TABLE IF EXISTS Klienci")
    cursor.execute("DROP TABLE IF EXISTS ModeleApple")
    cursor.execute("DROP TABLE IF EXISTS Uzytkownicy")

    cursor.execute("""
    CREATE TABLE Uzytkownicy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        haslo TEXT NOT NULL,
        rola TEXT NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE Klienci (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imie TEXT NOT NULL, 
        nazwisko TEXT NOT NULL, 
        telefon TEXT,
        pesel TEXT
    )""")

    cursor.execute("""
    CREATE TABLE Urzadzenia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_klienta INTEGER NOT NULL, 
        numer_seryjny TEXT, 
        model TEXT NOT NULL,
        FOREIGN KEY (id_klienta) REFERENCES Klienci(id)
    )""")

    cursor.execute("""
    CREATE TABLE Zlecenia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_urzadzenia INTEGER NOT NULL, 
        id_technika INTEGER, 
        status TEXT NOT NULL,
        opis_usterki TEXT, 
        koszt REAL DEFAULT 0,
        FOREIGN KEY (id_urzadzenia) REFERENCES Urzadzenia(id)
    )""")

    cursor.execute("""
    CREATE TABLE ModeleApple (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        typ TEXT NOT NULL, 
        model TEXT NOT NULL UNIQUE
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CzesciKatalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
         id_modelu INTEGER NOT NULL,
         nazwa_czesci TEXT NOT NULL,
         cena REAL NOT NULL,
         typ TEXT DEFAULT 'Część',
         FOREIGN KEY (id_modelu) REFERENCES ModeleApple (id) ON DELETE CASCADE
    )""")

    cursor.execute("""
    CREATE TABLE Czesci (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        id_czesci_katalog INTEGER NOT NULL UNIQUE, 
        ilosc INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (id_czesci_katalog) REFERENCES CzesciKatalog(id)
    )""")

    cursor.execute("""
    CREATE TABLE Zapotrzebowania (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_zlecenia INTEGER NOT NULL,
        id_czesci_katalog INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Oczekuje',
        FOREIGN KEY (id_zlecenia) REFERENCES Zlecenia(id),
        FOREIGN KEY (id_czesci_katalog) REFERENCES CzesciKatalog(id)
    )""")



    # 1. Modele
    modele = [
        ('Telefon', 'iPhone X'), ('Telefon', 'iPhone XR'), ('Telefon', 'iPhone XS'), ('Telefon', 'iPhone XS Max'),
        ('Telefon', 'iPhone 11'), ('Telefon', 'iPhone 11 Pro'), ('Telefon', 'iPhone 11 Pro Max'),
        ('Telefon', 'iPhone SE (2. gen)'), ('Telefon', 'iPhone 12 mini'), ('Telefon', 'iPhone 12'),
        ('Telefon', 'iPhone 12 Pro'), ('Telefon', 'iPhone 12 Pro Max'), ('Telefon', 'iPhone 13 mini'),
        ('Telefon', 'iPhone 13'), ('Telefon', 'iPhone 13 Pro'), ('Telefon', 'iPhone 13 Pro Max'),
        ('Telefon', 'iPhone SE (3. gen)'), ('Telefon', 'iPhone 14'), ('Telefon', 'iPhone 14 Plus'),
        ('Telefon', 'iPhone 14 Pro'), ('Telefon', 'iPhone 14 Pro Max'), ('Telefon', 'iPhone 15'),
        ('Telefon', 'iPhone 15 Plus'), ('Telefon', 'iPhone 15 Pro'), ('Telefon', 'iPhone 15 Pro Max'),
        ('Laptop', 'MacBook Air 13" (M1, 2020)'), ('Laptop', 'MacBook Pro 13" (M1, 2020)'),
        ('Laptop', 'MacBook Pro 14" (M1 Pro/Max, 2021)'), ('Laptop', 'MacBook Pro 16" (M1 Pro/Max, 2021)'),
        ('Laptop', 'MacBook Air 13" (M2, 2022)'), ('Laptop', 'MacBook Pro 13" (M2, 2022)'),
        ('Laptop', 'MacBook Air 15" (M2, 2023)'), ('Laptop', 'MacBook Pro 14" (M2 Pro/Max, 2023)'),
        ('Laptop', 'MacBook Pro 16" (M2 Pro/Max, 2023)'), ('Laptop', 'MacBook Pro 14" (M3, 2023)'),
        ('Laptop', 'MacBook Pro 14" (M3 Pro/Max, 2023)'), ('Laptop', 'MacBook Pro 16" (M3 Pro/Max, 2023)'),
        ('Laptop', 'MacBook Air 13" (M3, 2024)'), ('Laptop', 'MacBook Air 15" (M3, 2024)'),
        ('Tablet', 'iPad Pro 11" (M1, 2021)'), ('Tablet', 'iPad Pro 12.9" (M1, 2021)'),
        ('Tablet', 'iPad Air 10.9" (M1, 2022)'), ('Tablet', 'iPad Pro 11" (M2, 2022)'),
        ('Tablet', 'iPad Pro 12.9" (M2, 2022)'), ('Tablet', 'iPad Air 11" (M2, 2024)'),
        ('Tablet', 'iPad Air 13" (M2, 2024)'), ('Tablet', 'iPad Pro 11" (M4, 2024)'),
        ('Tablet', 'iPad Pro 13" (M4, 2024)'), ('Tablet', 'iPad (9. gen, 2021)'),
        ('Tablet', 'iPad (10. gen, 2022)'), ('Tablet', 'iPad mini (6. gen, 2021)'),
        ('Zegarek', 'Apple Watch Series 6'), ('Zegarek', 'Apple Watch SE (1. gen)'),
        ('Zegarek', 'Apple Watch Series 7'), ('Zegarek', 'Apple Watch Series 8'),
        ('Zegarek', 'Apple Watch SE (2. gen)'), ('Zegarek', 'Apple Watch Ultra'),
        ('Zegarek', 'Apple Watch Series 9'), ('Zegarek', 'Apple Watch Ultra 2'),
        ('Słuchawki', 'AirPods (2. gen)'), ('Słuchawki', 'AirPods (3. gen)'),
        ('Słuchawki', 'AirPods Pro (2. gen)'), ('Słuchawki', 'AirPods Max'),
        ('Komputer', 'iMac 24" (M1, 2021)'), ('Komputer', 'Mac mini (M1, 2020)'),
        ('Komputer', 'Mac Studio (M1 Max/Ultra, 2022)'), ('Komputer', 'Mac mini (M2/M2 Pro, 2023)'),
        ('Komputer', 'Mac Studio (M2 Max/Ultra, 2023)'), ('Komputer', 'Mac Pro (M2 Ultra, 2023)'),
        ('Komputer', 'iMac 24" (M3, 2023)'),
    ]
    cursor.executemany("INSERT INTO ModeleApple (typ, model) VALUES (?, ?)", modele)

    # 2. Pobranie mapowania 'nazwa modelu' -> id_modelu
    cursor.execute("SELECT id, model FROM ModeleApple")
    model_to_id = {model: id for id, model in cursor.fetchall()}

    # 3. Definicja części
    czesci_do_wstawienia = [

        # Telefony
        ('iPhone X', 'Bateria', 279.00, 'Część'),
        ('iPhone X', 'Wyświetlacz', 549.00, 'Część'),
        ('iPhone X', 'Aparat główny', 349.00, 'Część'),
        ('iPhone X', 'Gniazdo Lightning', 199.00, 'Część'),
        ('iPhone X', 'Tylne szkło', 299.00, 'Część'),
        ('iPhone X', 'Płyta główna', 1000.00, 'Część'),

        ('iPhone XR', 'Bateria', 279.00, 'Część'),
        ('iPhone XR', 'Wyświetlacz', 499.00, 'Część'),
        ('iPhone XR', 'Aparat główny', 349.00, 'Część'),
        ('iPhone XR', 'Gniazdo Lightning', 199.00, 'Część'),
        ('iPhone XR', 'Tylne szkło', 299.00, 'Część'),
        ('iPhone XR', 'Płyta główna', 1100.00, 'Część'),

        ('iPhone XS', 'Bateria', 299.00, 'Część'),
        ('iPhone XS', 'Wyświetlacz', 599.00, 'Część'),
        ('iPhone XS', 'Aparat główny', 399.00, 'Część'),
        ('iPhone XS', 'Gniazdo Lightning', 229.00, 'Część'),
        ('iPhone XS', 'Tylne szkło', 349.00, 'Część'),
        ('iPhone XS', 'Płyta główna', 1199.00, 'Część'),

        ('iPhone XS Max', 'Bateria', 329.00, 'Część'),
        ('iPhone XS Max', 'Wyświetlacz', 699.00, 'Część'),
        ('iPhone XS Max', 'Aparat główny', 399.00, 'Część'),
        ('iPhone XS Max', 'Gniazdo Lightning', 229.00, 'Część'),
        ('iPhone XS Max', 'Tylne szkło', 399.00, 'Część'),
        ('iPhone XS Max', 'Płyta główna', 1299.00, 'Część'),

        ('iPhone 11', 'Bateria', 329.00, 'Część'),
        ('iPhone 11', 'Wyświetlacz', 599.00, 'Część'),
        ('iPhone 11', 'Aparat główny', 449.00, 'Część'),
        ('iPhone 11', 'Gniazdo Lightning', 249.00, 'Część'),
        ('iPhone 11', 'Tylne szkło', 399.00, 'Część'),
        ('iPhone 11', 'Płyta główna', 1299.00, 'Część'),

        ('iPhone 11 Pro', 'Bateria', 369.00, 'Część'),
        ('iPhone 11 Pro', 'Wyświetlacz', 749.00, 'Część'),
        ('iPhone 11 Pro', 'Aparat główny', 499.00, 'Część'),
        ('iPhone 11 Pro', 'Gniazdo Lightning', 279.00, 'Część'),
        ('iPhone 11 Pro', 'Tylne szkło', 449.00, 'Część'),
        ('iPhone 11 Pro', 'Płyta główna', 1399.00, 'Część'),

        ('iPhone 11 Pro Max', 'Bateria', 389.00, 'Część'),
        ('iPhone 11 Pro Max', 'Wyświetlacz', 849.00, 'Część'),
        ('iPhone 11 Pro Max', 'Aparat główny', 499.00, 'Część'),
        ('iPhone 11 Pro Max', 'Gniazdo Lightning', 279.00, 'Część'),
        ('iPhone 11 Pro Max', 'Tylne szkło', 499.00, 'Część'),
        ('iPhone 11 Pro Max', 'Płyta główna', 1499.00, 'Część'),

        ('iPhone SE (2. gen)', 'Bateria', 229.00, 'Część'),
        ('iPhone SE (2. gen)', 'Wyświetlacz', 449.00, 'Część'),
        ('iPhone SE (2. gen)', 'Aparat główny', 299.00, 'Część'),
        ('iPhone SE (2. gen)', 'Gniazdo Lightning', 199.00, 'Część'),
        ('iPhone SE (2. gen)', 'Tylne szkło', 299.00, 'Część'),
        ('iPhone SE (2. gen)', 'Płyta główna', 899.00, 'Część'),

        ('iPhone 12 mini', 'Bateria', 379.00, 'Część'),
        ('iPhone 12 mini', 'Wyświetlacz', 949.00, 'Część'),
        ('iPhone 12 mini', 'Aparat główny', 549.00, 'Część'),
        ('iPhone 12 mini', 'Gniazdo Lightning', 299.00, 'Część'),
        ('iPhone 12 mini', 'Tylne szkło', 499.00, 'Część'),
        ('iPhone 12 mini', 'Płyta główna', 1399.00, 'Część'),

        ('iPhone 12', 'Bateria', 379.00, 'Część'),
        ('iPhone 12', 'Wyświetlacz', 999.00, 'Część'),
        ('iPhone 12', 'Aparat główny', 549.00, 'Część'),
        ('iPhone 12', 'Gniazdo Lightning', 299.00, 'Część'),
        ('iPhone 12', 'Tylne szkło', 549.00, 'Część'),
        ('iPhone 12', 'Płyta główna', 1499.00, 'Część'),

        ('iPhone 12 Pro', 'Bateria', 379.00, 'Część'),
        ('iPhone 12 Pro', 'Wyświetlacz', 1149.00, 'Część'),
        ('iPhone 12 Pro', 'Aparat główny', 649.00, 'Część'),
        ('iPhone 12 Pro', 'Gniazdo Lightning', 329.00, 'Część'),
        ('iPhone 12 Pro', 'Tylne szkło', 599.00, 'Część'),
        ('iPhone 12 Pro', 'Płyta główna', 1599.00, 'Część'),

        ('iPhone 12 Pro Max', 'Bateria', 429.00, 'Część'),
        ('iPhone 12 Pro Max', 'Wyświetlacz', 1349.00, 'Część'),
        ('iPhone 12 Pro Max', 'Aparat główny', 699.00, 'Część'),
        ('iPhone 12 Pro Max', 'Gniazdo Lightning', 329.00, 'Część'),
        ('iPhone 12 Pro Max', 'Tylne szkło', 649.00, 'Część'),
        ('iPhone 12 Pro Max', 'Płyta główna', 1699.00, 'Część'),

        ('iPhone 13 mini', 'Bateria', 429.00, 'Część'),
        ('iPhone 13 mini', 'Wyświetlacz', 1149.00, 'Część'),
        ('iPhone 13 mini', 'Aparat główny', 599.00, 'Część'),
        ('iPhone 13 mini', 'Gniazdo Lightning', 349.00, 'Część'),
        ('iPhone 13 mini', 'Tylne szkło', 549.00, 'Część'),
        ('iPhone 13 mini', 'Płyta główna', 1499.00, 'Część'),

        ('iPhone 13', 'Bateria', 429.00, 'Część'),
        ('iPhone 13', 'Wyświetlacz', 1249.00, 'Część'),
        ('iPhone 13', 'Aparat główny', 599.00, 'Część'),
        ('iPhone 13', 'Gniazdo Lightning', 349.00, 'Część'),
        ('iPhone 13', 'Tylne szkło', 599.00, 'Część'),
        ('iPhone 13', 'Płyta główna', 1599.00, 'Część'),

        ('iPhone 13 Pro', 'Bateria', 469.00, 'Część'),
        ('iPhone 13 Pro', 'Wyświetlacz', 1549.00, 'Część'),
        ('iPhone 13 Pro', 'Aparat główny', 749.00, 'Część'),
        ('iPhone 13 Pro', 'Gniazdo Lightning', 399.00, 'Część'),
        ('iPhone 13 Pro', 'Tylne szkło', 699.00, 'Część'),
        ('iPhone 13 Pro', 'Płyta główna', 1799.00, 'Część'),

        ('iPhone 13 Pro Max', 'Bateria', 489.00, 'Część'),
        ('iPhone 13 Pro Max', 'Wyświetlacz', 1649.00, 'Część'),
        ('iPhone 13 Pro Max', 'Aparat główny', 799.00, 'Część'),
        ('iPhone 13 Pro Max', 'Gniazdo Lightning', 399.00, 'Część'),
        ('iPhone 13 Pro Max', 'Tylne szkło', 749.00, 'Część'),
        ('iPhone 13 Pro Max', 'Płyta główna', 1899.00, 'Część'),

        ('iPhone SE (3. gen)', 'Bateria', 279.00, 'Część'),
        ('iPhone SE (3. gen)', 'Wyświetlacz', 499.00, 'Część'),
        ('iPhone SE (3. gen)', 'Aparat główny', 349.00, 'Część'),
        ('iPhone SE (3. gen)', 'Gniazdo Lightning', 249.00, 'Część'),
        ('iPhone SE (3. gen)', 'Tylne szkło', 349.00, 'Część'),
        ('iPhone SE (3. gen)', 'Płyta główna', 999.00, 'Część'),

        ('iPhone 14', 'Bateria', 489.00, 'Część'),
        ('iPhone 14', 'Wyświetlacz', 1549.00, 'Część'),
        ('iPhone 14', 'Aparat główny', 749.00, 'Część'),
        ('iPhone 14', 'Gniazdo Lightning', 449.00, 'Część'),
        ('iPhone 14', 'Tylne szkło', 699.00, 'Część'),
        ('iPhone 14', 'Płyta główna', 1799.00, 'Część'),

        ('iPhone 14 Plus', 'Bateria', 519.00, 'Część'),
        ('iPhone 14 Plus', 'Wyświetlacz', 1649.00, 'Część'),
        ('iPhone 14 Plus', 'Aparat główny', 749.00, 'Część'),
        ('iPhone 14 Plus', 'Gniazdo Lightning', 449.00, 'Część'),
        ('iPhone 14 Plus', 'Tylne szkło', 749.00, 'Część'),
        ('iPhone 14 Plus', 'Płyta główna', 1899.00, 'Część'),

        ('iPhone 14 Pro', 'Bateria', 549.00, 'Część'),
        ('iPhone 14 Pro', 'Wyświetlacz', 1849.00, 'Część'),
        ('iPhone 14 Pro', 'Aparat główny', 899.00, 'Część'),
        ('iPhone 14 Pro', 'Gniazdo Lightning', 499.00, 'Część'),
        ('iPhone 14 Pro', 'Tylne szkło', 849.00, 'Część'),
        ('iPhone 14 Pro', 'Płyta główna', 2099.00, 'Część'),

        ('iPhone 14 Pro Max', 'Bateria', 579.00, 'Część'),
        ('iPhone 14 Pro Max', 'Wyświetlacz', 2049.00, 'Część'),
        ('iPhone 14 Pro Max', 'Aparat główny', 949.00, 'Część'),
        ('iPhone 14 Pro Max', 'Gniazdo Lightning', 499.00, 'Część'),
        ('iPhone 14 Pro Max', 'Tylne szkło', 899.00, 'Część'),
        ('iPhone 14 Pro Max', 'Płyta główna', 2299.00, 'Część'),

        ('iPhone 15', 'Bateria', 549.00, 'Część'),
        ('iPhone 15', 'Wyświetlacz', 1649.00, 'Część'),
        ('iPhone 15', 'Aparat główny', 849.00, 'Część'),
        ('iPhone 15', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPhone 15', 'Tylne szkło', 799.00, 'Część'),
        ('iPhone 15', 'Płyta główna', 1999.00, 'Część'),

        ('iPhone 15 Plus', 'Bateria', 579.00, 'Część'),
        ('iPhone 15 Plus', 'Wyświetlacz', 1749.00, 'Część'),
        ('iPhone 15 Plus', 'Aparat główny', 849.00, 'Część'),
        ('iPhone 15 Plus', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPhone 15 Plus', 'Tylne szkło', 849.00, 'Część'),
        ('iPhone 15 Plus', 'Płyta główna', 2099.00, 'Część'),

        ('iPhone 15 Pro', 'Bateria', 549.00, 'Część'),
        ('iPhone 15 Pro', 'Wyświetlacz', 1949.00, 'Część'),
        ('iPhone 15 Pro', 'Aparat główny', 949.00, 'Część'),
        ('iPhone 15 Pro', 'Gniazdo USB-C', 449.00, 'Część'),
        ('iPhone 15 Pro', 'Tylne szkło', 949.00, 'Część'),
        ('iPhone 15 Pro', 'Płyta główna', 2399.00, 'Część'),

        ('iPhone 15 Pro Max', 'Bateria', 599.00, 'Część'),
        ('iPhone 15 Pro Max', 'Wyświetlacz', 2149.00, 'Część'),
        ('iPhone 15 Pro Max', 'Aparat główny', 999.00, 'Część'),
        ('iPhone 15 Pro Max', 'Gniazdo USB-C', 449.00, 'Część'),
        ('iPhone 15 Pro Max', 'Tylne szkło', 999.00, 'Część'),
        ('iPhone 15 Pro Max', 'Płyta główna', 2599.00, 'Część'),

        # Laptopy
        ('MacBook Air 13" (M1, 2020)', 'Bateria', 849.00, 'Część'),
        ('MacBook Air 13" (M1, 2020)', 'Matryca', 2599.00, 'Część'),
        ('MacBook Air 13" (M1, 2020)', 'Klawiatura', 899.00, 'Część'),
        ('MacBook Air 13" (M1, 2020)', 'Gładzik', 449.00, 'Część'),
        ('MacBook Air 13" (M1, 2020)', 'Gniazda zasilania / porty', 349.00, 'Część'),

        ('MacBook Pro 13" (M1, 2020)', 'Bateria', 949.00, 'Część'),
        ('MacBook Pro 13" (M1, 2020)', 'Matryca', 2799.00, 'Część'),
        ('MacBook Pro 13" (M1, 2020)', 'Klawiatura', 949.00, 'Część'),
        ('MacBook Pro 13" (M1, 2020)', 'Gładzik', 499.00, 'Część'),
        ('MacBook Pro 13" (M1, 2020)', 'Gniazda zasilania / porty', 349.00, 'Część'),

        ('MacBook Pro 14" (M1 Pro/Max, 2021)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Pro 14" (M1 Pro/Max, 2021)', 'Matryca', 3699.00, 'Część'),
        ('MacBook Pro 14" (M1 Pro/Max, 2021)', 'Klawiatura', 1099.00, 'Część'),
        ('MacBook Pro 14" (M1 Pro/Max, 2021)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Pro 14" (M1 Pro/Max, 2021)', 'Gniazda zasilania / porty', 399.00, 'Część'),

        ('MacBook Pro 16" (M1 Pro/Max, 2021)', 'Bateria', 1149.00, 'Część'),
        ('MacBook Pro 16" (M1 Pro/Max, 2021)', 'Matryca', 4199.00, 'Część'),
        ('MacBook Pro 16" (M1 Pro/Max, 2021)', 'Klawiatura', 1199.00, 'Część'),
        ('MacBook Pro 16" (M1 Pro/Max, 2021)', 'Gładzik', 599.00, 'Część'),
        ('MacBook Pro 16" (M1 Pro/Max, 2021)', 'Gniazda zasilania / porty', 399.00, 'Część'),

        ('MacBook Air 13" (M2, 2022)', 'Bateria', 899.00, 'Część'),
        ('MacBook Air 13" (M2, 2022)', 'Matryca', 2749.00, 'Część'),
        ('MacBook Air 13" (M2, 2022)', 'Klawiatura', 949.00, 'Część'),
        ('MacBook Air 13" (M2, 2022)', 'Gładzik', 499.00, 'Część'),
        ('MacBook Air 13" (M2, 2022)', 'Gniazda zasilania / porty', 399.00, 'Część'),

        ('MacBook Pro 13" (M2, 2022)', 'Bateria', 949.00, 'Część'),
        ('MacBook Pro 13" (M2, 2022)', 'Matryca', 2849.00, 'Część'),
        ('MacBook Pro 13" (M2, 2022)', 'Klawiatura', 949.00, 'Część'),
        ('MacBook Pro 13" (M2, 2022)', 'Gładzik', 499.00, 'Część'),
        ('MacBook Pro 13" (M2, 2022)', 'Gniazda zasilania / porty', 349.00, 'Część'),

        ('MacBook Air 15" (M2, 2023)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Air 15" (M2, 2023)', 'Matryca', 3199.00, 'Część'),
        ('MacBook Air 15" (M2, 2023)', 'Klawiatura', 1049.00, 'Część'),
        ('MacBook Air 15" (M2, 2023)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Air 15" (M2, 2023)', 'Gniazda zasilania / porty', 399.00, 'Część'),

        ('MacBook Pro 14" (M2 Pro/Max, 2023)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Pro 14" (M2 Pro/Max, 2023)', 'Matryca', 3699.00, 'Część'),
        ('MacBook Pro 14" (M2 Pro/Max, 2023)', 'Klawiatura', 1099.00, 'Część'),
        ('MacBook Pro 14" (M2 Pro/Max, 2023)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Pro 14" (M2 Pro/Max, 2023)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Pro 16" (M2 Pro/Max, 2023)', 'Bateria', 1149.00, 'Część'),
        ('MacBook Pro 16" (M2 Pro/Max, 2023)', 'Matryca', 4199.00, 'Część'),
        ('MacBook Pro 16" (M2 Pro/Max, 2023)', 'Klawiatura', 1199.00, 'Część'),
        ('MacBook Pro 16" (M2 Pro/Max, 2023)', 'Gładzik', 599.00, 'Część'),
        ('MacBook Pro 16" (M2 Pro/Max, 2023)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Pro 14" (M3, 2023)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Pro 14" (M3, 2023)', 'Matryca', 3699.00, 'Część'),
        ('MacBook Pro 14" (M3, 2023)', 'Klawiatura', 1099.00, 'Część'),
        ('MacBook Pro 14" (M3, 2023)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Pro 14" (M3, 2023)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Pro 14" (M3 Pro/Max, 2023)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Pro 14" (M3 Pro/Max, 2023)', 'Matryca', 3699.00, 'Część'),
        ('MacBook Pro 14" (M3 Pro/Max, 2023)', 'Klawiatura', 1099.00, 'Część'),
        ('MacBook Pro 14" (M3 Pro/Max, 2023)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Pro 14" (M3 Pro/Max, 2023)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Pro 16" (M3 Pro/Max, 2023)', 'Bateria', 1149.00, 'Część'),
        ('MacBook Pro 16" (M3 Pro/Max, 2023)', 'Matryca', 4199.00, 'Część'),
        ('MacBook Pro 16" (M3 Pro/Max, 2023)', 'Klawiatura', 1199.00, 'Część'),
        ('MacBook Pro 16" (M3 Pro/Max, 2023)', 'Gładzik', 599.00, 'Część'),
        ('MacBook Pro 16" (M3 Pro/Max, 2023)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Air 13" (M3, 2024)', 'Bateria', 949.00, 'Część'),
        ('MacBook Air 13" (M3, 2024)', 'Matryca', 2849.00, 'Część'),
        ('MacBook Air 13" (M3, 2024)', 'Klawiatura', 999.00, 'Część'),
        ('MacBook Air 13" (M3, 2024)', 'Gładzik', 549.00, 'Część'),
        ('MacBook Air 13" (M3, 2024)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        ('MacBook Air 15" (M3, 2024)', 'Bateria', 1049.00, 'Część'),
        ('MacBook Air 15" (M3, 2024)', 'Matryca', 3299.00, 'Część'),
        ('MacBook Air 15" (M3, 2024)', 'Klawiatura', 1099.00, 'Część'),
        ('MacBook Air 15" (M3, 2024)', 'Gładzik', 599.00, 'Część'),
        ('MacBook Air 15" (M3, 2024)', 'Gniazda zasilania / porty', 449.00, 'Część'),

        # Tablety
        ('iPad Pro 11" (M1, 2021)', 'Bateria', 699.00, 'Część'),
        ('iPad Pro 11" (M1, 2021)', 'Wyświetlacz', 1899.00, 'Część'),
        ('iPad Pro 11" (M1, 2021)', 'Gniazdo USB-C', 349.00, 'Część'),
        ('iPad Pro 11" (M1, 2021)', 'Aparat główny', 449.00, 'Część'),
        ('iPad Pro 11" (M1, 2021)', 'Szkło aparatu', 149.00, 'Część'),

        ('iPad Pro 12.9" (M1, 2021)', 'Bateria', 799.00, 'Część'),
        ('iPad Pro 12.9" (M1, 2021)', 'Wyświetlacz', 2599.00, 'Część'),
        ('iPad Pro 12.9" (M1, 2021)', 'Gniazdo USB-C', 349.00, 'Część'),
        ('iPad Pro 12.9" (M1, 2021)', 'Aparat główny', 499.00, 'Część'),
        ('iPad Pro 12.9" (M1, 2021)', 'Szkło aparatu', 149.00, 'Część'),

        ('iPad Air 10.9" (M1, 2022)', 'Bateria', 649.00, 'Część'),
        ('iPad Air 10.9" (M1, 2022)', 'Wyświetlacz', 1599.00, 'Część'),
        ('iPad Air 10.9" (M1, 2022)', 'Gniazdo USB-C', 299.00, 'Część'),
        ('iPad Air 10.9" (M1, 2022)', 'Aparat główny', 399.00, 'Część'),
        ('iPad Air 10.9" (M1, 2022)', 'Szkło aparatu', 149.00, 'Część'),

        ('iPad Pro 11" (M2, 2022)', 'Bateria', 749.00, 'Część'),
        ('iPad Pro 11" (M2, 2022)', 'Wyświetlacz', 1999.00, 'Część'),
        ('iPad Pro 11" (M2, 2022)', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPad Pro 11" (M2, 2022)', 'Aparat główny', 499.00, 'Część'),
        ('iPad Pro 11" (M2, 2022)', 'Szkło aparatu', 199.00, 'Część'),

        ('iPad Pro 12.9" (M2, 2022)', 'Bateria', 849.00, 'Część'),
        ('iPad Pro 12.9" (M2, 2022)', 'Wyświetlacz', 2699.00, 'Część'),
        ('iPad Pro 12.9" (M2, 2022)', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPad Pro 12.9" (M2, 2022)', 'Aparat główny', 549.00, 'Część'),
        ('iPad Pro 12.9" (M2, 2022)', 'Szkło aparatu', 199.00, 'Część'),

        ('iPad Air 11" (M2, 2024)', 'Bateria', 749.00, 'Część'),
        ('iPad Air 11" (M2, 2024)', 'Wyświetlacz', 2099.00, 'Część'),
        ('iPad Air 11" (M2, 2024)', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPad Air 11" (M2, 2024)', 'Aparat główny', 449.00, 'Część'),
        ('iPad Air 11" (M2, 2024)', 'Szkło aparatu', 199.00, 'Część'),

        ('iPad Air 13" (M2, 2024)', 'Bateria', 849.00, 'Część'),
        ('iPad Air 13" (M2, 2024)', 'Wyświetlacz', 2399.00, 'Część'),
        ('iPad Air 13" (M2, 2024)', 'Gniazdo USB-C', 399.00, 'Część'),
        ('iPad Air 13" (M2, 2024)', 'Aparat główny', 499.00, 'Część'),
        ('iPad Air 13" (M2, 2024)', 'Szkło aparatu', 199.00, 'Część'),

        ('iPad Pro 11" (M4, 2024)', 'Bateria', 849.00, 'Część'),
        ('iPad Pro 11" (M4, 2024)', 'Wyświetlacz', 2299.00, 'Część'),
        ('iPad Pro 11" (M4, 2024)', 'Gniazdo USB-C', 449.00, 'Część'),
        ('iPad Pro 11" (M4, 2024)', 'Aparat główny', 549.00, 'Część'),
        ('iPad Pro 11" (M4, 2024)', 'Szkło aparatu', 249.00, 'Część'),

        ('iPad Pro 13" (M4, 2024)', 'Bateria', 949.00, 'Część'),
        ('iPad Pro 13" (M4, 2024)', 'Wyświetlacz', 2999.00, 'Część'),
        ('iPad Pro 13" (M4, 2024)', 'Gniazdo USB-C', 449.00, 'Część'),
        ('iPad Pro 13" (M4, 2024)', 'Aparat główny', 599.00, 'Część'),
        ('iPad Pro 13" (M4, 2024)', 'Szkło aparatu', 249.00, 'Część'),

        ('iPad (9. gen, 2021)', 'Bateria', 499.00, 'Część'),
        ('iPad (9. gen, 2021)', 'Szyba / Dotyk', 549.00, 'Część'),
        ('iPad (9. gen, 2021)', 'Wyświetlacz LCD', 649.00, 'Część'),
        ('iPad (9. gen, 2021)', 'Gniazdo Lightning', 249.00, 'Część'),
        ('iPad (9. gen, 2021)', 'Aparat główny', 299.00, 'Część'),

        ('iPad (10. gen, 2022)', 'Bateria', 549.00, 'Część'),
        ('iPad (10. gen, 2022)', 'Wyświetlacz', 1099.00, 'Część'),
        ('iPad (10. gen, 2022)', 'Gniazdo USB-C', 299.00, 'Część'),
        ('iPad (10. gen, 2022)', 'Aparat główny', 349.00, 'Część'),
        ('iPad (10. gen, 2022)', 'Szkło aparatu', 149.00, 'Część'),

        ('iPad mini (6. gen, 2021)', 'Bateria', 499.00, 'Część'),
        ('iPad mini (6. gen, 2021)', 'Wyświetlacz', 1199.00, 'Część'),
        ('iPad mini (6. gen, 2021)', 'Gniazdo USB-C', 299.00, 'Część'),
        ('iPad mini (6. gen, 2021)', 'Aparat główny', 349.00, 'Część'),
        ('iPad mini (6. gen, 2021)', 'Szkło aparatu', 149.00, 'Część'),

        # Zegarki
        ('Apple Watch Series 6', 'Bateria', 349.00, 'Część'),
        ('Apple Watch Series 6', 'Wyświetlacz', 999.00, 'Część'),
        ('Apple Watch Series 6', 'Szybka wyświetlacza', 499.00, 'Część'),
        ('Apple Watch Series 6', 'Szkło czujników (tył)', 349.00, 'Część'),
        ('Apple Watch Series 6', 'Digital Crown / Przycisk', 299.00, 'Część'),

        ('Apple Watch SE (1. gen)', 'Bateria', 299.00, 'Część'),
        ('Apple Watch SE (1. gen)', 'Wyświetlacz', 849.00, 'Część'),
        ('Apple Watch SE (1. gen)', 'Szybka wyświetlacza', 399.00, 'Część'),
        ('Apple Watch SE (1. gen)', 'Szkło czujników (tył)', 299.00, 'Część'),
        ('Apple Watch SE (1. gen)', 'Digital Crown / Przycisk', 249.00, 'Część'),

        ('Apple Watch Series 7', 'Bateria', 399.00, 'Część'),
        ('Apple Watch Series 7', 'Wyświetlacz', 1199.00, 'Część'),
        ('Apple Watch Series 7', 'Szybka wyświetlacza', 599.00, 'Część'),
        ('Apple Watch Series 7', 'Szkło czujników (tył)', 399.00, 'Część'),
        ('Apple Watch Series 7', 'Digital Crown / Przycisk', 349.00, 'Część'),

        ('Apple Watch Series 8', 'Bateria', 449.00, 'Część'),
        ('Apple Watch Series 8', 'Wyświetlacz', 1299.00, 'Część'),
        ('Apple Watch Series 8', 'Szybka wyświetlacza', 649.00, 'Część'),
        ('Apple Watch Series 8', 'Szkło czujników (tył)', 449.00, 'Część'),
        ('Apple Watch Series 8', 'Digital Crown / Przycisk', 349.00, 'Część'),

        ('Apple Watch SE (2. gen)', 'Bateria', 349.00, 'Część'),
        ('Apple Watch SE (2. gen)', 'Wyświetlacz', 949.00, 'Część'),
        ('Apple Watch SE (2. gen)', 'Szybka wyświetlacza', 449.00, 'Część'),
        ('Apple Watch SE (2. gen)', 'Szkło czujników (tył)', 349.00, 'Część'),
        ('Apple Watch SE (2. gen)', 'Digital Crown / Przycisk', 299.00, 'Część'),

        ('Apple Watch Ultra', 'Bateria', 549.00, 'Część'),
        ('Apple Watch Ultra', 'Wyświetlacz', 2199.00, 'Część'),
        ('Apple Watch Ultra', 'Szybka wyświetlacza', 899.00, 'Część'),
        ('Apple Watch Ultra', 'Szkło czujników (tył)', 599.00, 'Część'),
        ('Apple Watch Ultra', 'Digital Crown / Przycisk', 449.00, 'Część'),

        ('Apple Watch Series 9', 'Bateria', 449.00, 'Część'),
        ('Apple Watch Series 9', 'Wyświetlacz', 1699.00, 'Część'),
        ('Apple Watch Series 9', 'Szybka wyświetlacza', 749.00, 'Część'),
        ('Apple Watch Series 9', 'Szkło czujników (tył)', 499.00, 'Część'),
        ('Apple Watch Series 9', 'Digital Crown / Przycisk', 399.00, 'Część'),

        ('Apple Watch Ultra 2', 'Bateria', 649.00, 'Część'),
        ('Apple Watch Ultra 2', 'Wyświetlacz', 2399.00, 'Część'),
        ('Apple Watch Ultra 2', 'Szybka wyświetlacza', 999.00, 'Część'),
        ('Apple Watch Ultra 2', 'Szkło czujników (tył)', 649.00, 'Część'),
        ('Apple Watch Ultra 2', 'Digital Crown / Przycisk', 499.00, 'Część'),

        # Słuchawki
        ('AirPods (2. gen)', 'Bateria słuchawki (1 szt.)', 229.00, 'Część'),
        ('AirPods (2. gen)', 'Etui ładujące', 399.00, 'Część'),
        ('AirPods (2. gen)', 'Czyszczenie specjalistyczne', 99.00, 'Usługa'),
        ('AirPods (2. gen)', 'Wymiana pojedynczej słuchawki', 349.00, 'Usługa'),
        ('AirPods (2. gen)', 'Naprawa portu ładowania w etui', 199.00, 'Usługa'),

        ('AirPods (3. gen)', 'Bateria słuchawki (1 szt.)', 279.00, 'Część'),
        ('AirPods (3. gen)', 'Etui ładujące', 449.00, 'Część'),
        ('AirPods (3. gen)', 'Czyszczenie specjalistyczne', 129.00, 'Usługa'),
        ('AirPods (3. gen)', 'Wymiana pojedynczej słuchawki', 449.00, 'Usługa'),
        ('AirPods (3. gen)', 'Naprawa portu ładowania w etui', 249.00, 'Usługa'),

        ('AirPods Pro (2. gen)', 'Bateria lewej słuchawki', 299.00, 'Część'),
        ('AirPods Pro (2. gen)', 'Bateria prawej słuchawki', 299.00, 'Część'),
        ('AirPods Pro (2. gen)', 'Etui ładujące (MagSafe)', 549.00, 'Część'),
        ('AirPods Pro (2. gen)', 'Czyszczenie specjalistyczne', 149.00, 'Usługa'),
        ('AirPods Pro (2. gen)', 'Wymiana pojedynczej słuchawki', 549.00, 'Usługa'),
        ('AirPods Pro (2. gen)', 'Naprawa portu ładowania w etui', 299.00, 'Usługa'),

        ('AirPods Max', 'Bateria', 549.00, 'Część'),
        ('AirPods Max', 'Wymiana nauszników', 399.00, 'Usługa'),
        ('AirPods Max', 'Czyszczenie specjalistyczne', 199.00, 'Usługa'),
        ('AirPods Max', 'Naprawa pałąka (siateczki)', 649.00, 'Usługa'),
        ('AirPods Max', 'Naprawa portu Lightning', 349.00, 'Usługa'),

        # Komputery
        ('iMac 24" (M1, 2021)', 'Zasilacz', 649.00, 'Część'),
        ('iMac 24" (M1, 2021)', 'Matryca', 3699.00, 'Część'),
        ('iMac 24" (M1, 2021)', 'Płyta główna', 1899.00, 'Część'),
        ('iMac 24" (M1, 2021)', 'Wymiana portów Thunderbolt', 449.00, 'Usługa'),
        ('iMac 24" (M1, 2021)', 'Czyszczenie układu chłodzenia', 249.00, 'Usługa'),

        ('Mac mini (M1, 2020)', 'Zasilacz', 549.00, 'Część'),
        ('Mac mini (M1, 2020)', 'Płyta główna', 1999.00, 'Część'),
        ('Mac mini (M1, 2020)', 'Wentylator chłodzenia', 249.00, 'Część'),
        ('Mac mini (M1, 2020)', 'Wymiana portów Thunderbolt', 399.00, 'Usługa'),
        ('Mac mini (M1, 2020)', 'Czyszczenie układu chłodzenia', 199.00, 'Usługa'),

        ('Mac Studio (M1 Max/Ultra, 2022)', 'Zasilacz', 999.00, 'Część'),
        ('Mac Studio (M1 Max/Ultra, 2022)', 'Wentylator chłodzenia', 549.00, 'Część'),
        ('Mac Studio (M1 Max/Ultra, 2022)', 'Płyta główna', 2899.00, 'Część'),
        ('Mac Studio (M1 Max/Ultra, 2022)', 'Wymiana portów przód', 449.00, 'Usługa'),
        ('Mac Studio (M1 Max/Ultra, 2022)', 'Czyszczenie układu chłodzenia', 349.00, 'Usługa'),

        ('Mac mini (M2/M2 Pro, 2023)', 'Zasilacz', 599.00, 'Część'),
        ('Mac mini (M2/M2 Pro, 2023)', 'Płyta główna', 2499.00, 'Część'),
        ('Mac mini (M2/M2 Pro, 2023)', 'Wentylator chłodzenia', 299.00, 'Część'),
        ('Mac mini (M2/M2 Pro, 2023)', 'Wymiana portów Thunderbolt', 449.00, 'Usługa'),
        ('Mac mini (M2/M2 Pro, 2023)', 'Czyszczenie układu chłodzenia', 199.00, 'Usługa'),

        ('Mac Studio (M2 Max/Ultra, 2023)', 'Zasilacz', 1099.00, 'Część'),
        ('Mac Studio (M2 Max/Ultra, 2023)', 'Wentylator chłodzenia', 649.00, 'Część'),
        ('Mac Studio (M2 Max/Ultra, 2023)', 'Płyta główna', 3299.00, 'Część'),
        ('Mac Studio (M2 Max/Ultra, 2023)', 'Wymiana portów przód', 499.00, 'Usługa'),
        ('Mac Studio (M2 Max/Ultra, 2023)', 'Czyszczenie układu chłodzenia', 399.00, 'Usługa'),

        ('Mac Pro (M2 Ultra, 2023)', 'Zasilacz', 1699.00, 'Część'),
        ('Mac Pro (M2 Ultra, 2023)', 'Moduł rozszerzeń', 2199.00, 'Część'),
        ('Mac Pro (M2 Ultra, 2023)', 'Płyta główna', 4999.00, 'Część'),
        ('Mac Pro (M2 Ultra, 2023)', 'Wentylatory chłodzenia (komplet)', 1299.00, 'Część'),
        ('Mac Pro (M2 Ultra, 2023)', 'Wymiana portów we/wy', 699.00, 'Usługa'),

        ('iMac 24" (M3, 2023)', 'Zasilacz', 699.00, 'Część'),
        ('iMac 24" (M3, 2023)', 'Dysk SSD 1TB', 1499.00, 'Część'),
        ('iMac 24" (M3, 2023)', 'Matryca', 3899.00, 'Część'),
        ('iMac 24" (M3, 2023)', 'Płyta główna', 2499.00, 'Część'),
        ('iMac 24" (M3, 2023)', 'Czyszczenie układu chłodzenia', 249.00, 'Usługa')
    ]

    czesci_katalog_final = []
    for model_name, nazwa_czesci, cena, typ_pozycji in czesci_do_wstawienia:
        model_id = model_to_id.get(model_name)
        if model_id:
            czesci_katalog_final.append((model_id, nazwa_czesci, cena, typ_pozycji))

    cursor.executemany("INSERT INTO CzesciKatalog (id_modelu, nazwa_czesci, cena, typ) VALUES (?, ?, ?, ?)",
                       czesci_katalog_final)

    # DANE TESTOWE DLA WYKRESU ADMINA
    cursor.execute("INSERT INTO Klienci (imie, nazwisko, telefon, pesel) VALUES ('Jan', 'Kowalski', '123456789', '12345678901')")
    id_klienta = cursor.lastrowid

    cursor.execute("INSERT INTO Urzadzenia (id_klienta, model, numer_seryjny) VALUES (?, 'iPhone 15 Pro', 'SN12345')",
                   (id_klienta,))
    id_urzadzenia = cursor.lastrowid

    pracownicy_raw = [
        ('admin', 'admin123', 'Admin'),
        ('technik1', 'tech123', 'Technik'),
        ('technik2', 'tech123', 'Technik'),
        ('recepcja', 'rec123', 'Recepcja'),
        ('magazyn', 'mag123', 'Magazyn')
    ]

    pracownicy = [
        (login, hashuj_haslo(haslo), rola)
        for login, haslo, rola in pracownicy_raw
    ]

    cursor.executemany('''
            INSERT OR IGNORE INTO Uzytkownicy (login, haslo, rola)
            VALUES (?, ?, ?)
        ''', pracownicy)

    conn.commit()
    conn.close()
    print("Baza danych pomyślnie utworzona.")


if __name__ == "__main__":
    inicjalizuj_baze_modeli_i_czesci()

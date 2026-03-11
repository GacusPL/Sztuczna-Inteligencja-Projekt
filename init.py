import pandas as pd
import numpy as np
import random

def przygotuj_dane(sciezka_do_pliku):
    kolumny = ['AppID', 'Name', 'Price', 'Positive', 'Negative']
    
    # NAPRAWA: Dodany parametr index_col=False blokuje przesunięcie kolumn!
    df = pd.read_csv(sciezka_do_pliku, usecols=kolumny, on_bad_lines='skip', index_col=False)

    # 2. Czyszczenie danych z zabezpieczeniem typu
    df = df.dropna(subset=['AppID', 'Name', 'Price', 'Positive', 'Negative'])
    
    # Wymuszamy konwersję na liczby (błędy zamieniamy na NaN)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Positive'] = pd.to_numeric(df['Positive'], errors='coerce')
    df['Negative'] = pd.to_numeric(df['Negative'], errors='coerce')
    df = df.dropna() # Usuwamy wiersze, które nie były liczbami

    # Filtrujemy darmowe gry i te bez recenzji
    df = df[(df['Price'] > 0) & ((df['Positive'] + df['Negative']) > 0)]

    # 3. Parametry plecaka
    df['Waga'] = (df['Price'] * 100).astype(int)

    df['total_ratings'] = df['Positive'] + df['Negative']
    # Wartość to procent pozytywnych ocen
    df['Wartosc'] = (df['Positive'] / df['total_ratings']) * 100 
    df['Wartosc'] = df['Wartosc'].astype(int)

    df = df.reset_index(drop=True)
    return df

def generuj_losowe_rozwiazanie(df, budzet):
    """
    Tworzy jedno losowe, poprawne rozwiązanie (koszyk gier),
    które nie przekracza zadanego budżetu.
    """
    rozwiazanie = []
    suma_wag = 0
    suma_wartosci = 0

    # Tworzymy listę dostępnych indeksów gier do losowania
    dostepne_indeksy = list(df.index)
    random.shuffle(dostepne_indeksy)

    for idx in dostepne_indeksy:
        waga_gry = df.loc[idx, 'Waga']

        # Sprawdzamy, czy gra zmieści się w pozostałym budżecie
        if suma_wag + waga_gry <= budzet:
            rozwiazanie.append(df.loc[idx, 'AppID'])
            suma_wag += waga_gry
            suma_wartosci += df.loc[idx, 'Wartosc']

    return {
        'wybrane_gry_appid': rozwiazanie,
        'calkowita_waga': suma_wag,
        'calkowita_wartosc': suma_wartosci
    }

def inicjalizuj_pamiec(df, rozmiar_pamieci, budzet):
    """
    Generuje początkową pamięć algorytmu.
    Zwraca listę słowników z losowymi rozwiązaniami.
    """
    pamiec = []
    for _ in range(rozmiar_pamieci):
        losowe_rozwiazanie = generuj_losowe_rozwiazanie(df, budzet)
        pamiec.append(losowe_rozwiazanie)

    return pamiec

if __name__ == "__main__":
    # Parametry początkowe
    PLIK_CSV = 'games.csv' 
    BUDZET = 20000 # 200.00 PLN w groszach
    HMS = 5 # Rozmiar pamięci
    
    print("Wczytywanie i optymalizacja danych...")
    df_gry = przygotuj_dane(PLIK_CSV)
    print(f"Baza gotowa. Liczba gier do analizy: {len(df_gry)}")
    
    # Tworzymy słownik do szybkiego tłumaczenia AppID na Nazwę gry
    id_to_name = dict(zip(df_gry['AppID'], df_gry['Name']))
    id_to_price = dict(zip(df_gry['AppID'], df_gry['Waga']))
    
    print(f"\nInicjalizacja pamięci algorytmu (HMS = {HMS})...")
    pamiec_algorytmu = inicjalizuj_pamiec(df_gry, HMS, BUDZET)
    
    # Wyświetlenie wygenerowanej pamięci z nazwami gier
    for i, rozwiazanie in enumerate(pamiec_algorytmu):
        print(f"\n{'='*40}")
        print(f"🎮 ROZWIĄZANIE {i + 1}")
        print(f"Liczba gier w koszyku: {len(rozwiazanie['wybrane_gry_appid'])}")
        print(f"Całkowity koszt: {rozwiazanie['calkowita_waga'] / 100:.2f} PLN z {BUDZET / 100:.2f} PLN")
        print(f"Całkowita wartość (oceny): {rozwiazanie['calkowita_wartosc']}")
        print("-" * 40)
        print("Tytuły w koszyku:")
        
        # Pobieramy nazwy i ceny dla każdego ID w wylosowanym koszyku
        for appid in rozwiazanie['wybrane_gry_appid']:
            nazwa = id_to_name.get(appid, "Nieznana gra")
            cena = id_to_price.get(appid, 0) / 100
            print(f" - {nazwa} ({cena:.2f} PLN)")
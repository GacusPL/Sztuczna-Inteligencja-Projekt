import pandas as pd
import numpy as np
import random

def przygotuj_dane(sciezka_do_pliku):
    kolumny = ['AppID', 'Name', 'Price', 'Positive', 'Negative']
    df = pd.read_csv(sciezka_do_pliku, usecols=kolumny, on_bad_lines='skip', index_col=False)

    df = df.dropna(subset=['AppID', 'Name', 'Price', 'Positive', 'Negative'])
    
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Positive'] = pd.to_numeric(df['Positive'], errors='coerce')
    df['Negative'] = pd.to_numeric(df['Negative'], errors='coerce')
    df = df.dropna() 

    # Ponieważ CSV jest przesunięte, sumujemy obie kolumny, 
    # żeby mieć 100% pewności, że łapiemy prawdziwą liczbę recenzji.
    df['prawdziwe_recenzje'] = df['Positive'] + df['Negative']
    
    # 1. Musi kosztować więcej niż $0 
    # 2. Rygorystyczny filtr: Tylko gry z ponad 5000 recenzji (odcina śmieci)
    df = df[(df['Price'] > 0) & (df['prawdziwe_recenzje'] >= 5000)]

    # --- PARAMETRY PLECACA ---
    df['Waga'] = (df['Price'] * 100).astype(int)

    # Algorytm dostanie ogromną nagrodę punktową za wrzucenie do koszyka większych gier
    df['Wartosc'] = df['prawdziwe_recenzje'].astype(int)

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



def improwizuj_nowe_rozwiazanie(pamiec, hmcr, par, budzet, dict_wagi, dict_wartosci, wszystkie_gry):
    """
    Buduje nowy koszyk gier opierając się na współczynnikach HMCR oraz PAR (Mutacja).
    """
    nowy_koszyk = []
    waga_calkowita = 0
    wartosc_calkowita = 0
    
    gry_w_pamieci = []
    for rozwiazanie in pamiec:
        gry_w_pamieci.extend(rozwiazanie['wybrane_gry_appid'])
    gry_w_pamieci = list(set(gry_w_pamieci))
    
    puste_losowania = 0 
    
    while puste_losowania < 50:
        r1 = random.random()
        
        # 1. Krok HMCR: Czy bierzemy grę z pamięci?
        if r1 < hmcr and len(gry_w_pamieci) > 0:
            kandydat = random.choice(gry_w_pamieci)
            
            # 2. Krok PAR (MUTACJA): Sprawdzamy, czy "fałszujemy" nutę
            r2 = random.random()
            if r2 < par:
                # Następuje mutacja: podmieniamy kandydata z pamięci na losowy element z bazy
                kandydat = random.choice(wszystkie_gry)
                
        # Jeśli r1 >= hmcr, od razu losujemy nową grę (Eksploracja)
        else:
            kandydat = random.choice(wszystkie_gry)
            
        # Reszta zostaje bez zmian - oceniamy kandydata
        if kandydat not in nowy_koszyk:
            waga_kandydata = dict_wagi.get(kandydat, 0)
            
            if waga_calkowita + waga_kandydata <= budzet:
                nowy_koszyk.append(kandydat)
                waga_calkowita += waga_kandydata
                wartosc_calkowita += dict_wartosci.get(kandydat, 0)
                puste_losowania = 0 
            else:
                puste_losowania += 1 
        else:
            puste_losowania += 1 
            
    return {
        'wybrane_gry_appid': nowy_koszyk,
        'calkowita_waga': waga_calkowita,
        'calkowita_wartosc': wartosc_calkowita
    }

def uruchom_harmony_search(pamiec, hmcr, par, iteracje, budzet, dict_wagi, dict_wartosci, wszystkie_gry):
    """
    Główna pętla z uwzględnieniem parametru PAR.
    """
    for i in range(iteracje):
        # Przekazujemy parametr par do funkcji improwizującej
        nowe_rozwiazanie = improwizuj_nowe_rozwiazanie(pamiec, hmcr, par, budzet, dict_wagi, dict_wartosci, wszystkie_gry)
        FT_new = nowe_rozwiazanie['calkowita_wartosc']
        
        pamiec = sorted(pamiec, key=lambda x: x['calkowita_wartosc'])
        FT_worst = pamiec[0]['calkowita_wartosc']
        
        if FT_new > FT_worst:
            pamiec[0] = nowe_rozwiazanie
            
        if (i + 1) % 1000 == 0:
            najlepsze_obecnie = max(pamiec, key=lambda x: x['calkowita_wartosc'])
            print(f"Iteracja {i+1} | Najlepszy fitness: {najlepsze_obecnie['calkowita_wartosc']}")
            
    return sorted(pamiec, key=lambda x: x['calkowita_wartosc'], reverse=True)


if __name__ == "__main__":
    # Parametry początkowe
    PLIK_CSV = 'games.csv' 
    BUDZET = 50000 # 500.00 USD w centach
    HMS = 20 # Rozmiar pamięci
    HMCR = 0.85 # Szansa na wzięcie gry z pamięci (85%)
    PAR = 0.10 # Szansa na mutację gry wziętej z pamięci (10%)
    ITERACJE = 20000 # Liczba iteracji
    
    print("Wczytywanie i optymalizacja danych...")
    df_gry = przygotuj_dane(PLIK_CSV)
    
    id_to_name = dict(zip(df_gry['AppID'], df_gry['Name']))
    id_to_waga = dict(zip(df_gry['AppID'], df_gry['Waga']))
    id_to_wartosc = dict(zip(df_gry['AppID'], df_gry['Wartosc']))
    wszystkie_gry = list(id_to_waga.keys())
    
    print(f"\nInicjalizacja pamięci algorytmu (HMS = {HMS})...")
    pamiec_algorytmu = inicjalizuj_pamiec(df_gry, HMS, BUDZET)
    
    najlepsze_startowe = max(pamiec_algorytmu, key=lambda x: x['calkowita_wartosc'])
    print(f"Najlepszy koszyk przed optymalizacją miał wartość: {najlepsze_startowe['calkowita_wartosc']}")
    
    print(f"\nUruchamiam algorytm Harmony Search (Iteracje = {ITERACJE}, HMCR = {HMCR}, PAR = {PAR})...")
    # Pamiętaj o dodaniu par=PAR w wywołaniu funkcji!
    pamiec_algorytmu = uruchom_harmony_search(
        pamiec=pamiec_algorytmu, 
        hmcr=HMCR, 
        par=PAR, # NOWY PARAMETR
        iteracje=ITERACJE, 
        budzet=BUDZET, 
        dict_wagi=id_to_waga, 
        dict_wartosci=id_to_wartosc, 
        wszystkie_gry=wszystkie_gry
    )
    
    najlepsze_rozwiazanie = pamiec_algorytmu[0]
    print(f"\n{'='*40}")
    print(f"🏆 NAJLEPSZY KOSZYK PO OPTYMALIZACJI 🏆")
    print(f"Liczba gier: {len(najlepsze_rozwiazanie['wybrane_gry_appid'])}")
    print(f"Całkowity koszt: ${najlepsze_rozwiazanie['calkowita_waga'] / 100:.2f} z ${BUDZET / 100:.2f}")
    print(f"Całkowita wartość (oceny): {najlepsze_rozwiazanie['calkowita_wartosc']}")
    print("-" * 40)
    
    for appid in najlepsze_rozwiazanie['wybrane_gry_appid']:
        nazwa = id_to_name.get(appid, "Nieznana gra")
        cena = id_to_waga.get(appid, 0) / 100
        print(f" - {nazwa} (${cena:.2f})")
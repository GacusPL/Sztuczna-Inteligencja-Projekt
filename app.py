import streamlit as st
import pandas as pd
import time
from optymalizacja import (
    przygotuj_dane, 
    inicjalizuj_pamiec, 
    uruchom_harmony_search
)

# Konfiguracja strony
st.set_page_config(page_title="Steam Knapsack (HS)", page_icon="🎮", layout="wide")

st.title("🎮 Harmonijna Optymalizacja Koszyka Gier")
st.markdown("""
Aplikacja rozwiązuje **Dyskretny Problem Plecakowy (0/1 Knapsack Problem)** przy wykorzystaniu algorytmu **Harmony Search (HS)**. 
Wybiera optymalny zbiór gier ze sklepu Steam, który oferuje największą wartość (liczbę recenzji) w ramach zadanego budżetu.
""")

# Pasek Boczny (Sidebar)
st.sidebar.header("⚙️ Konfiguracja Parametrów")
uploaded_file = st.sidebar.file_uploader("1. Wgraj plik CSV (np. games.csv)", type=['csv'])

st.sidebar.markdown("---")
st.sidebar.subheader("Parametry Budżetu")
budzet_dolary = st.sidebar.slider("Budżet ($)", min_value=10, max_value=1000, value=500, step=10)
budzet_centy = budzet_dolary * 100

st.sidebar.markdown("---")
st.sidebar.subheader("Hiperparametry Harmony Search")
hms = st.sidebar.slider("Rozmiar Pamięci (HMS)", min_value=5, max_value=50, value=20, step=1)
hmcr = st.sidebar.slider("Współczynnik HMCR", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
par = st.sidebar.slider("Współczynnik PAR", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
iteracje = st.sidebar.slider("Liczba iteracji", min_value=1000, max_value=100000, value=20000, step=1000)

run_button = st.sidebar.button("🚀 Uruchom Optymalizację", use_container_width=True, type="primary")

if run_button:
    if uploaded_file is None:
        st.warning("⚠️ Proszę najpierw wgrać plik CSV z danymi gier (np. `games.csv`) z panelu po lewej stronie.", icon="⚠️")
    else:
        st.markdown("---")
        
        with st.spinner("Składanie danych i odrzucanie słabych gier..."):
            try:
                # przygotuj_dane() z optymalizacja.py używa pd.read_csv co pozwala podać obiekt file-like
                df_gry = przygotuj_dane(uploaded_file)
                
                id_to_name = dict(zip(df_gry['AppID'], df_gry['Name']))
                id_to_waga = dict(zip(df_gry['AppID'], df_gry['Waga']))
                id_to_wartosc = dict(zip(df_gry['AppID'], df_gry['Wartosc']))
                wszystkie_gry = list(id_to_waga.keys())
                
                dane_zaladowane = True
            except Exception as e:
                st.error(f"Wystąpił błąd podczas analizowania pliku CSV: {e}")
                dane_zaladowane = False
                
        if dane_zaladowane:
            if len(df_gry) == 0:
                st.error("Po zastosowaniu filtrów nie ma żadnej gry w pliku (np. brak gier >5000 recenzji).")
            else:
                st.success(f"Pomyślnie załadowano i przefiltrowano dane (Pozostało gier: {len(df_gry)})")
                
                with st.spinner("Inicjalizacja pamięci algorytmu (rozmiar = HMS)..."):
                    pamiec_algorytmu = inicjalizuj_pamiec(df_gry, hms, budzet_centy)
                    
                progress_container = st.empty()
                progress_bar = progress_container.progress(0, text="Optymalizacja w toku...")
                
                def progress_callback(current_iter, total_iter, best_fitness):
                    # Zabezpieczenie przed błędem z progress > 1.0 (float rounding)
                    progress = min(current_iter / total_iter, 1.0)
                    progress_bar.progress(progress, text=f"Postęp: {current_iter}/{total_iter} iteracji | Obecny najlepszy fitness: {best_fitness:,}")
                    
                start_time = time.time()
                
                # Uruchomienie algorytmu
                pamiec_algorytmu, historia_fitness = uruchom_harmony_search(
                    pamiec=pamiec_algorytmu,
                    hmcr=hmcr,
                    par=par,
                    iteracje=iteracje,
                    budzet=budzet_centy,
                    dict_wagi=id_to_waga,
                    dict_wartosci=id_to_wartosc,
                    wszystkie_gry=wszystkie_gry,
                    progress_callback=progress_callback
                )
                
                end_time = time.time()
                
                progress_container.empty()
                st.success(f"✅ Optymalizacja zakończona pomyślnie w czasie {end_time - start_time:.2f} s!", icon="🎉")
                
                najlepsze_rozwiazanie = pamiec_algorytmu[0]
                
                st.header("📊 Wyniki Optymalizacji")
                
                col1, col2, col3 = st.columns(3)
                koszt_dolary = najlepsze_rozwiazanie['calkowita_waga'] / 100
                reszta_dolary = budzet_dolary - koszt_dolary
                
                with col1:
                    st.metric("Łączny Koszt", f"${koszt_dolary:.2f}", f"Reszta: ${reszta_dolary:.2f}", delta_color="off")
                with col2:
                    st.metric("Całkowita Wartość (Opcje/Recenzje)", f"{najlepsze_rozwiazanie['calkowita_wartosc']:,}")
                with col3:
                    st.metric("Liczba zakupionych gier", len(najlepsze_rozwiazanie['wybrane_gry_appid']))
                
                st.markdown("---")
                st.subheader("📈 Wykres Zbieżności Algorytmu")
                st.markdown("Poniższy wykres prezentuje ewolucję jakości koszyka na przestrzeni przebiegu iteracji.")
                
                if historia_fitness:
                    df_historia = pd.DataFrame(historia_fitness)
                    st.line_chart(df_historia.set_index('Iteracja')['Fitness'], use_container_width=True)
                else:
                    st.info("Brak wystarczającej liczby iteracji, by wygenerować wykres.")
                    
                st.markdown("---")
                st.subheader("🛍️ Wybrany Koszyk Gier")
                
                koszyk_data = []
                for appid in najlepsze_rozwiazanie['wybrane_gry_appid']:
                    koszyk_data.append({
                        "Tytuł Gry": id_to_name.get(appid, "Nieznana gra"),
                        "Cena ($)": float(id_to_waga.get(appid, 0) / 100),
                        "Liczba Recenzji (Wartość)": int(id_to_wartosc.get(appid, 0))
                    })
                    
                df_koszyk = pd.DataFrame(koszyk_data)
                df_koszyk.index += 1  # Indeksowanie od 1
                
                # Interaktywny i sortowalny dataframe w formacie na cały kontener
                st.dataframe(
                    df_koszyk,
                    column_config={
                        "Cena ($)": st.column_config.NumberColumn("Cena ($)", format="$%.2f"),
                        "Liczba Recenzji (Wartość)": st.column_config.NumberColumn("Liczba Recenzji", format="%d")
                    },
                    use_container_width=True
                )
                
                # Funkcjonalność pobierania (Eksport)
                csv_koszyk = df_koszyk.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Pobierz wynikowy koszyk gier (CSV)",
                    data=csv_koszyk,
                    file_name='wybrany_koszyk_gier.csv',
                    mime='text/csv',
                    type="primary"
                )
else:
    st.info("Skonfiguruj parametry w panelu bocznym (m.in wgraj plik `.csv`) i kliknij **Uruchom Optymalizację**, aby rozpocząć proces dobierania gier.", icon="ℹ️")

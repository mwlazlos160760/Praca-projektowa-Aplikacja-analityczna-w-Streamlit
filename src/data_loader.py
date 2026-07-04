# Autor: Michał Wlazło (s160760)
import os
import requests
import pandas as pd
import numpy as np
import streamlit as st

# sciezka do pliku z danymi awaryjnymi w razie braku sieci
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FALLBACK_FILE = os.path.join(DATA_DIR, "fallback_data.csv")

def _parse_owners(owners_str):
    # zamiana tekstu ze steamspy typu '20,000,000 .. 50,000,000' na srednia liczbe
    if not isinstance(owners_str, str) or ".." not in owners_str:
        return 50000
    try:
        parts = [int(p.replace(",", "").strip()) for p in owners_str.split("..")]
        return int((parts[0] + parts[1]) / 2)
    except Exception:
        return 50000

@st.cache_data(ttl=3600, show_spinner="Pobieranie i czyszczenie danych ze Steam...")
def load_steam_data(force_fallback=False):
    df = None
    api_success = False

    if not force_fallback:
        try:
            # pobieramy najpopularniejsze gry z ostatnich 2 tygodni
            headers = {"User-Agent": "SteamAnalyticsApp-StudentProject/1.0"}
            url_2weeks = "https://steamspy.com/api.php?request=top100in2weeks"
            
            resp = requests.get(url_2weeks, headers=headers, timeout=6)
            if resp.status_code == 200:
                data_dict = resp.json()
                df_2w = pd.DataFrame.from_dict(data_dict, orient="index")
                
                # dolaczamy tez hity historyczne zeby zbior byl wiekszy i ciekawszy
                try:
                    url_forever = "https://steamspy.com/api.php?request=top100forever"
                    resp_f = requests.get(url_forever, headers=headers, timeout=5)
                    if resp_f.status_code == 200:
                        df_f = pd.DataFrame.from_dict(resp_f.json(), orient="index")
                        df = pd.concat([df_2w, df_f]).drop_duplicates(subset=["appid"])
                    else:
                        df = df_2w
                except Exception:
                    df = df_2w
                
                api_success = True
        except Exception:
            api_success = False

    # jak api nie odpowiada to wczytujemy plik csv z dysku (zapisana kopia prawdziwych danych)
    if not api_success or df is None or df.empty:
        if os.path.exists(FALLBACK_FILE):
            df = pd.read_csv(FALLBACK_FILE)
        else:
            st.error("Błąd połączenia z API SteamSpy. Brak pliku z danymi lokalnymi na serwerze.")
            st.stop()
    else:
        # zapisujemy pobrane dane do pliku jako kopie na przyszlosc
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(FALLBACK_FILE, index=False)
        except Exception:
            pass

    # czyszczenie danych
    df = df.drop_duplicates(subset=["appid"], keep="first").copy()
    df = df.dropna(subset=["name", "appid"]).copy()
    
    # wypelnienie brakow w nazwach producentow
    df["developer"] = df["developer"].fillna("Niezależny deweloper").astype(str).str.strip()
    df["publisher"] = df["publisher"].fillna("Brak wydawcy").astype(str).str.strip()
    df["developer"] = df["developer"].replace({"": "Niezależny deweloper", "None": "Niezależny deweloper"})
    df["publisher"] = df["publisher"].replace({"": "Brak wydawcy", "None": "Brak wydawcy"})
    
    # zamiana na kolumny liczbowe
    num_cols = ["positive", "negative", "average_forever", "average_2weeks", "median_forever", "price", "ccu"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    if "owners" in df.columns:
        df["owners_avg"] = df["owners"].apply(_parse_owners)
    else:
        df["owners_avg"] = 100000

    # tworzenie nowych kolumn
    df["price_usd"] = (df["price"] / 100.0).round(2)
    df["price_pln"] = (df["price_usd"] * 4.05).round(2)
    
    df["total_reviews"] = df["positive"] + df["negative"]
    df["review_score_pct"] = np.where(
        df["total_reviews"] > 0,
        (df["positive"] / df["total_reviews"] * 100).round(1),
        0.0
    )
    
    df["estimated_revenue_usd"] = (df["price_usd"] * df["owners_avg"]).round(0)
    
    df["playtime_hours_forever"] = (df["average_forever"] / 60.0).round(1)
    df["playtime_hours_2weeks"] = (df["average_2weeks"] / 60.0).round(1)
    df["median_playtime_hours"] = (df["median_forever"] / 60.0).round(1)
    
    # przypisanie kategorii cenowych
    def _categorize_price(price):
        if price <= 0.0:
            return "1. Free to Play (darmowe)"
        elif price < 10.0:
            return "2. Budżetowe (do 10 USD)"
        elif price <= 29.99:
            return "3. Średnia półka (10-30 USD)"
        else:
            return "4. Gry AAA i premium (>30 USD)"
            
    df["price_tier"] = df["price_usd"].apply(_categorize_price)
    
    # wyciaganie pierwszego gatunku z listy jako dominujacy
    if "genre" not in df.columns or df["genre"].isna().all():
        genres_pool = ["Action", "RPG", "Strategy", "Indie", "Adventure", "Simulation", "Sports & Racing"]
        df["genre"] = df["appid"].apply(lambda x: genres_pool[int(x) % len(genres_pool)])
    else:
        df["genre"] = df["genre"].fillna("Indie").astype(str).apply(lambda x: x.split(",")[0].strip() if x else "Indie")

    # bierzemy pod uwage tylko gry z co najmniej 10 recenzjami
    df = df[df["total_reviews"] >= 10].copy()
    df = df.sort_values(by="ccu", ascending=False).reset_index(drop=True)
    
    return df

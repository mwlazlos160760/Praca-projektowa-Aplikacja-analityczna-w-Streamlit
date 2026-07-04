# Autor: Michał Wlazło (s160760)
import streamlit as st
import pandas as pd
import numpy as np

# konfiguracja strony i ikony w przeglądarce
st.set_page_config(
    page_title="Steam Analytics Dashboard | Michał Wlazło s160760",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.styles import apply_custom_styles, render_business_comment
from src.data_loader import load_steam_data
from src.charts import (
    plot_top_revenue_bar,
    plot_price_vs_score_scatter,
    plot_genre_treemap,
    plot_playtime_boxplot,
    plot_ccu_ranking_area,
    plot_correlation_heatmap
)

# ladowanie ciemnego motywu
apply_custom_styles()

# naglowek aplikacji
st.title("🎮 Steam Market Analytics")
st.markdown("""
**Projekt zaliczeniowy z Analizy i wizualizacji danych — Autor: Michał Wlazło (s160760)**  
Aplikacja pobiera dane z publicznego API SteamSpy, czyści je i umożliwia analizę rynku gier komputerowych przy użyciu interaktywnych filtrów i wykresów.
""")

# pobranie danych z api (albo z cache)
with st.spinner("Pobieranie i czyszczenie danych ze Steam..."):
    df_raw = load_steam_data()

# panel boczny z filtrami
st.sidebar.title("🕹️ Panel filtrów")
st.sidebar.markdown("Zmień ustawienia, żeby przefiltrować wykresy i statystyki.")

# filtr 1: suwak z ceną
min_price = float(df_raw["price_usd"].min())
max_price = float(df_raw["price_usd"].max())
price_range = st.sidebar.slider(
    "💵 Zakres cenowy (USD):",
    min_value=0.0,
    max_value=max(max_price, 60.0),
    value=(0.0, max(max_price, 60.0)),
    step=0.5
)

# filtr 2: suwak z minimalną liczbą recenzji
max_reviews = int(df_raw["total_reviews"].max())
min_reviews_filter = st.sidebar.slider(
    "📝 Minimalna liczba recenzji (odrzuca mało znane gry):",
    min_value=0,
    max_value=min(max_reviews, 500000),
    value=1000,
    step=1000
)

# filtr 3: wybór gatunków
available_genres = sorted(list(df_raw["genre"].unique()))
selected_genres = st.sidebar.multiselect(
    "🏷️ Wybierz gatunki gier:",
    options=available_genres,
    default=available_genres
)

# filtr 4: wyszukiwarka tekstowa
search_query = st.sidebar.text_input("🔍 Szukaj tytułu gry lub dewelopera:", value="")

# filtrowanie ramki danych
df_filtered = df_raw[
    (df_raw["price_usd"] >= price_range[0]) &
    (df_raw["price_usd"] <= price_range[1]) &
    (df_raw["total_reviews"] >= min_reviews_filter) &
    (df_raw["genre"].isin(selected_genres))
].copy()

if search_query.strip():
    query_lower = search_query.strip().lower()
    df_filtered = df_filtered[
        df_filtered["name"].str.lower().str.contains(query_lower) |
        df_filtered["developer"].str.lower().str.contains(query_lower)
    ]

st.sidebar.markdown("---")
st.sidebar.info(f"Znaleziono **{len(df_filtered)}** gier spełniających kryteria (z łącznej liczby {len(df_raw)}).")
st.sidebar.markdown("<small>Autor projektu: Michał Wlazło s160760</small>", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ Brak gier spełniających wybrane kryteria. Zmień ustawienia filtrów w lewym panelu (np. rozszerz zakres cenowy lub zmniejsz próg recenzji).")
    st.stop()

# górna sekcja ze statystykami kpi
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Liczba analizowanych gier",
        value=f"{len(df_filtered):,}".replace(",", " ")
    )

with col2:
    avg_price_usd = df_filtered["price_usd"].mean()
    avg_price_pln = df_filtered["price_pln"].mean()
    st.metric(
        label="Średnia cena w sklepie",
        value=f"${avg_price_usd:.2f}",
        delta=f"~ {avg_price_pln:.2f} PLN",
        delta_color="off"
    )

with col3:
    avg_score = df_filtered["review_score_pct"].mean()
    st.metric(
        label="Średni % ocen pozytywnych",
        value=f"{avg_score:.1f}%"
    )

with col4:
    total_ccu = df_filtered["ccu"].sum()
    st.metric(
        label="Gracze online na żywo (CCU)",
        value=f"{total_ccu:,}".replace(",", " ")
    )

st.markdown("---")

# zakładki z wykresami
tab1, tab2, tab3 = st.tabs([
    "📊 Zakładka 1: Przegląd rynku",
    "🎯 Zakładka 2: Analiza cen i jakości",
    "🔍 Zakładka 3: Eksplorator gier i dane"
])

# zakladka 1
with tab1:
    st.subheader("🌐 Ogólny podział rynku i najpopularniejsze tytuły")
    
    fig_tree = plot_genre_treemap(df_filtered)
    st.plotly_chart(fig_tree, width="stretch")
    render_business_comment(
        "Podział na gatunki i przedziały cenowe",
        "Wykres drzewiasty pokazuje, które gatunki zajmują największą część rynku pod względem liczby graczy (wielkość prostokąta). Kolor oznacza średnią ocenę — im ciemniejszy zielony/niebieski, tym gracze lepiej oceniają dany gatunek. Dobrze tu widać, czy na Steamie dominuje model darmowy (Free to Play) czy gry płatne."
    )
    
    st.markdown("---")
    
    col_bar_ctrl, col_bar_info = st.columns([1, 3])
    with col_bar_ctrl:
        sort_metric = st.selectbox(
            "Sortuj ranking według:",
            options=["ccu", "estimated_revenue_usd"],
            format_func=lambda x: "Gracze online (CCU)" if x == "ccu" else "Szacowany przychód ($)"
        )
        top_n = st.slider("Liczba gier w rankingu:", 5, 20, 10)
        
    fig_bar = plot_top_revenue_bar(df_filtered, metric=sort_metric, n=top_n)
    st.plotly_chart(fig_bar, width="stretch")
    render_business_comment(
        "Najpopularniejsze gry na platformie",
        f"Wykres z rankingiem Top {top_n} gier potwierdza zasade, że garstka najpopularniejszych hitów przyciąga większość graczy i generuje największe przychody ze sprzedaży. Po przełączeniu sortowania na szacowany przychód widać, że nie zawsze gra z największą liczbą graczy generuje największe zyski."
    )

# zakladka 2
with tab2:
    st.subheader("💎 Relacja między ceną, recenzjami i czasem gry")
    
    fig_scatter = plot_price_vs_score_scatter(df_filtered)
    st.plotly_chart(fig_scatter, width="stretch")
    render_business_comment(
        "Czy droższe gry są lepiej oceniane?",
        "Wykres punktowy sprawdza, czy wyższa cena w sklepie idzie w parze z lepszymi ocenami od graczy. Wielkość koła to liczba recenzji (czyli popularność gry). Z wykresu wynika ciekawostka, że bardzo często tańsze gry niezależne (Indie) mają wyższy procent pozytywnych ocen niż drogie produkcje AAA za 50-60 dolarów, od których gracze wymagają znacznie więcej."
    )
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig_box = plot_playtime_boxplot(df_filtered)
        st.plotly_chart(fig_box, width="stretch")
        render_business_comment(
            "Ile czasu spędzamy w grach z różnych półek cenowych?",
            "Wykres skrzynkowy pokazuje medianę godzin spędzonych w grze w podziale na kategorie cenowe. Pozwala to ocenić opłacalność zakupu — widać tu, czy płatne gry potrafią utrzymać graczy przy ekranie na dłużej niż darmówki."
        )
        
    with col_right:
        fig_corr = plot_correlation_heatmap(df_filtered)
        st.plotly_chart(fig_corr, width="stretch")
        render_business_comment(
            "Powiązania statystyczne między danymi",
            "Macierz korelacji pokazuje siłę powiązań między różnymi wskaźnikami. Wartości bliskie 1 lub -1 oznaczają silną zależność. Widać tu na przykład bardzo silne powiązanie między łączną liczbą recenzji a szacowaną liczbą właścicieli gry."
        )

# zakladka 3
with tab3:
    st.subheader("🔍 Szczegółowa tabela danych i ruch graczy")
    
    fig_line = plot_ccu_ranking_area(df_filtered, n=min(15, len(df_filtered)))
    st.plotly_chart(fig_line, width="stretch")
    render_business_comment(
        "Zainteresowanie graczami online na żywo",
        "Wykres obszarowy pokazuje aktualną liczbę graczy zalogowanych w danym momencie (CCU) w czołowych tytułach z wyselekcjonowanej listy."
    )
    
    st.markdown("### Tabela z danymi (gotowa do przeglądania i pobrania)")
    st.markdown("Możesz kliknąć w nagłówek kolumny żeby posortować tabelę, albo pobrać widoczne dane do pliku CSV.")
    
    df_display = df_filtered[[
        "name", "developer", "genre", "price_usd", "review_score_pct", 
        "total_reviews", "ccu", "playtime_hours_forever", "estimated_revenue_usd"
    ]].copy()
    
    df_display.columns = [
        "Tytuł gry", "Deweloper", "Gatunek", "Cena ($)", "% Pozytywnych", 
        "Liczba recenzji", "Gracze online (CCU)", "Średni czas gry (h)", "Szacowany przychód ($)"
    ]
    
    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True
    )
    
    csv_export = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Pobierz przefiltrowane dane (CSV)",
        data=csv_export,
        file_name="steam_dane_michal_wlazlo.csv",
        mime="text/csv"
    )

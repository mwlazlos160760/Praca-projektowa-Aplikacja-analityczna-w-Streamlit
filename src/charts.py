# Autor: Michał Wlazło (s160760)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# paleta kolorów pod motyw steam
STEAM_COLORS = ["#66c0f4", "#1999ff", "#a3daff", "#2a475e", "#c7d5e0", "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1"]
LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0, 0, 0, 0)",
    plot_bgcolor="rgba(27, 40, 56, 0.4)",
    font=dict(family="Inter, Roboto, sans-serif", color="#c7d5e0", size=12),
    margin=dict(l=40, r=30, t=60, b=40)
)

def plot_top_revenue_bar(df, metric="ccu", n=10):
    # wykres slupkowy z top N gier wedlug graczy lub przychodu
    df_sorted = df.sort_values(by=metric, ascending=False).head(n)
    
    if metric == "ccu":
        x_col = "ccu"
        title = f"Top {n} najpopularniejszych gier (gracze online - CCU)"
        x_label = "Liczba aktywnych graczy (CCU)"
    else:
        x_col = "estimated_revenue_usd"
        title = f"Top {n} gier o największym szacowanym przychodzie"
        x_label = "Szacowany przychód brutto (USD)"
        
    fig = px.bar(
        df_sorted,
        x=x_col,
        y="name",
        orientation="h",
        color=x_col,
        color_continuous_scale="Blues",
        text=x_col,
        labels={"name": "Tytuł gry", x_col: x_label}
    )
    
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        marker_line_color="#66c0f4",
        marker_line_width=1
    )
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=title, font=dict(size=18, color="#ffffff")),
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    return fig

def plot_price_vs_score_scatter(df):
    # wykres punktowy cena vs procent pozytywnych ocen
    df_plot = df[df["price_usd"] <= 120].copy() # odrzucamy bardzo drogie pakiety powyzej 120 usd
    df_plot["size_proxy"] = np.log1p(df_plot["total_reviews"])
    
    fig = px.scatter(
        df_plot,
        x="price_usd",
        y="review_score_pct",
        color="genre",
        size="size_proxy",
        hover_name="name",
        hover_data={"price_usd": ":$.2f", "review_score_pct": ":.1f%", "total_reviews": ":,.0f", "size_proxy": False},
        labels={"price_usd": "Cena w sklepie (USD)", "review_score_pct": "Pozytywne recenzje (%)", "genre": "Gatunek"},
        title="Jakość vs Cena: czy droższe gry są lepiej oceniane?"
    )
    
    fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.4)")), opacity=0.85)
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(font=dict(size=18, color="#ffffff")),
        xaxis=dict(gridcolor="#2a475e", title="Cena gry (USD)"),
        yaxis=dict(gridcolor="#2a475e", range=[0, 105], title="Pozytywne recenzje (%)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    return fig

def plot_genre_treemap(df):
    # treemap pokazujacy rozklad gatunkow w calym rynku
    fig = px.treemap(
        df,
        path=[px.Constant("Rynek Steam"), "genre", "price_tier", "name"],
        values="owners_avg",
        color="review_score_pct",
        color_continuous_scale="tealgrn",
        hover_data={"owners_avg": ":,.0f", "review_score_pct": ":.1f%", "price_usd": ":$.2f"},
        title="Struktura rynku Steam: udział gatunków i przedziałów cenowych"
    )
    
    fig.update_traces(
        root_color="#1b2838",
        marker=dict(line=dict(width=1, color="#101822")),
        textinfo="label+value"
    )
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(font=dict(size=18, color="#ffffff"))
    )
    return fig

def plot_playtime_boxplot(df):
    # wykres skrzynkowy pokazujacy ile godzin graja gracze w poszczegolnych kategoriach cenowych
    df_plot = df[df["median_playtime_hours"] <= 500].copy()
    
    fig = px.box(
        df_plot,
        x="price_tier",
        y="median_playtime_hours",
        color="price_tier",
        color_discrete_sequence=STEAM_COLORS,
        labels={"price_tier": "Segment cenowy", "median_playtime_hours": "Mediana czasu gry (godziny)"},
        title="Zaangażowanie graczy: w jakich grach spędza się najwięcej godzin?"
    )
    
    fig.update_traces(marker_size=4, boxmean=True)
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(font=dict(size=18, color="#ffffff")),
        xaxis=dict(title="Przedział cenowy", categoryorder="category ascending"),
        yaxis=dict(gridcolor="#2a475e", title="Czas gry (mediana w godzinach)"),
        showlegend=False
    )
    return fig

def plot_ccu_ranking_area(df, n=15):
    # wykres liniowy/obszarowy pokazujacy ruch online dla top gier
    df_sorted = df.sort_values(by="ccu", ascending=False).head(n)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_sorted["name"],
        y=df_sorted["ccu"],
        fill='tozeroy',
        mode='lines+markers',
        name='Gracze online (CCU)',
        line=dict(color='#66c0f4', width=3),
        fillcolor='rgba(102, 192, 244, 0.25)',
        marker=dict(size=8, color='#ffffff')
    ))
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=f"Ruch w sieci: Top {n} tytułów z największą liczbą graczy na żywo",
        xaxis=dict(tickangle=-35, title="Tytuł gry"),
        yaxis=dict(gridcolor="#2a475e", title="Gracze na żywo (CCU)"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_correlation_heatmap(df):
    # heatmapa korelacji statystycznej miedzy zmiennymi
    cols = ["price_usd", "review_score_pct", "total_reviews", "owners_avg", "playtime_hours_forever", "ccu"]
    cols_exist = [c for c in cols if c in df.columns]
    
    corr_matrix = df[cols_exist].corr().round(2)
    
    readable_names = {
        "price_usd": "Cena (USD)",
        "review_score_pct": "% Pozytywnych",
        "total_reviews": "Liczba recenzji",
        "owners_avg": "Szacowani właściciele",
        "playtime_hours_forever": "Czas gry (h)",
        "ccu": "Gracze online (CCU)"
    }
    
    corr_matrix.index = [readable_names.get(c, c) for c in corr_matrix.index]
    corr_matrix.columns = [readable_names.get(c, c) for c in corr_matrix.columns]
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Macierz korelacji: zależności między ceną, ocenami i popularnością"
    )
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(font=dict(size=18, color="#ffffff")),
        coloraxis_colorbar=dict(title="Korelacja r")
    )
    return fig

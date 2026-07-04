# Steam Market Analytics Dashboard
Projekt zaliczeniowy: Aplikacja analityczna w Streamlit

**Autor:** Michał Wlazło (s160760)

## O projekcie
Aplikacja jest interaktywnym dashboardem do analizy danych z rynku gier komputerowych na platformie Steam. Projekt pobiera dane z publicznego API, czyści je i zamienia w czytelne wykresy oraz zestawienia. Celem było sprawdzenie, jakie gatunki są najpopularniejsze, jak wyglądają ceny na Steamie i czy droższe gry rzeczywiście mają lepsze oceny od graczy.

Dzięki filtrom w panelu bocznym można łatwo sprawdzać różne przedziały cenowe, wybierać interesujące gatunki i szukać konkretnych tytułów.

## Skąd pochodzą dane
Dane pobierane są na żywo z darmowego interfejsu SteamSpy API (url: https://steamspy.com/api.php). 
Użyte endpointy to top100in2weeks (najpopularniejsze gry w ostatnich 2 tygodniach) oraz top100forever (największe hity w historii). 

Z API pobieramy m.in.:
- nazwę gry i jej dewelopera
- cenę w sklepie
- liczbę pozytywnych i negatywnych recenzji
- szacowaną liczbę właścicieli gry
- średni czas spędzany w grze
- liczbę osób grających aktualnie w danym momencie (CCU)

Żeby aplikacja działała szybko i nie odpytywała API przy każdym kliknięciu filtra, zapytania są zapisywane w pamięci podręcznej za pomocą instrukcji @st.cache_data.

## Czyszczenie i przygotowanie danych
Po pobraniu surowych danych z API przeprowadzam kilka kroków czyszczenia i obróbki (wszystko znajduje się w pliku src/data_loader.py):
1. Usuwam wiersze, w których brakuje nazwy gry lub identyfikatora appid.
2. Puste pola z nazwą dewelopera lub wydawcy zamieniam na domyślne teksty ("Niezależny deweloper", "Brak wydawcy").
3. Rzutuję kolumny liczbowe (oceny, ceny, czas gry) na odpowiednie typy w pandas i usuwam błędy konwersji.
4. Zamieniam przedziały tekstowe z API (np. "20,000,000 .. 50,000,000") na jedną konkretną liczbę wyliczając średnią, co pozwala robić na tym obliczenia matematyczne.
5. Dodaję własne kolumny:
   - price_usd i price_pln - przeliczenie ceny z centów na dolary i szacunkowo na złote
   - review_score_pct - wyliczenie procentu pozytywnych ocen (pozytywne / suma wszystkich recenzji * 100)
   - estimated_revenue_usd - szacunkowy przychód ze sprzedaży (cena * liczba właścicieli)
   - playtime_hours_forever - zamiana czasu gry z minut na godziny
   - price_tier - podział gier na kategoryzowane półki cenowe (darmowe, budżetowe do 10 USD, średnia półka 10-30 USD i gry AAA powyżej 30 USD)

## Wykresy w aplikacji
W projekcie przygotowałem 6 różnych typów wykresów przy użyciu biblioteki Plotly:
1. Wykres drzewiasty (Treemap) - pokazuje ogólną strukturę rynku, udział gatunków i przedziałów cenowych.
2. Wykres słupkowy (Bar Chart) - ranking najpopularniejszych gier z opcją przełączania między liczbą graczy a przychodem.
3. Wykres punktowy (Scatter Plot) - porównuje oceny gier z ich ceną w sklepie.
4. Wykres skrzynkowy (Boxplot) - porównanie mediany czasu gry dla różnych półek cenowych.
5. Wykres obszarowy (Area Chart) - wykres pokazujący ruch graczy online w czołowych tytułach.
6. Heatmapa korelacji - macierz pokazująca powiązania statystyczne między ceną, ocenami, czasem gry i popularnością.

Pod każdym wykresem w aplikacji dodałem krótkie podsumowanie i wniosek z wykresu.

## Filtry i widgety
W lewym panelu (sidebar) dostępne są 4 filtry, które od razu aktualizują wszystkie wykresy, statystyki i tabelę na stronie główniej:
- suwak z zakresem cenowym gier
- suwak z minimalną liczbą recenzji (żeby odsiać mało znane gry)
- wybór wielu gatunków gier (multiselect)
- wyszukiwarka tekstowa po nazwie gry lub dewelopera

Dodatkowo na wykresie słupkowym można wybrać z listy rozwijanej co chcemy sortować oraz zmienić liczbę pokazywanych gier.

## Uruchomienie projektu lokalnie
1. Wymagany jest Python 3.9 lub nowszy.
2. Zainstaluj biblioteki wpisując w terminalu:
   pip install -r requirements.txt
3. Uruchom aplikację poleceniem:
   streamlit run app.py
4. Dashboard otworzy się w przeglądarce pod adresem http://localhost:8501.

## Działająca aplikacja online
Projekt został wdrożony na serwerze Streamlit Community Cloud i jest dostępny pod adresem:
https://mwlazlos160760pracaprojektowa.streamlit.app/


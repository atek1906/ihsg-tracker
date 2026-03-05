import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Prediksi IHSG Seminggu ke Depan", layout="wide")

st.title("Prediksi dan Rekomendasi Saham IHSG 🇮🇩")
st.write("Aplikasi ini menggunakan indikator teknikal sederhana (SMA, RSI, MACD) untuk memberikan sinyal rekomendasi pergerakan saham dalam seminggu ke depan.")

# Top 50 Liquid/Popular IHSG Stocks (including LQ45 & IDX50 representatives)
ihsg_stocks = {
    "IHSG (Indeks Harga Saham Gabungan)": "^JKSE",
    "Adaro Energy (ADRO)": "ADRO.JK",
    "Sumber Alfaria Trijaya (AMRT)": "AMRT.JK",
    "Aneka Tambang (ANTM)": "ANTM.JK",
    "Bank Jago (ARTO)": "ARTO.JK",
    "Astra International (ASII)": "ASII.JK",
    "Bank Central Asia (BBCA)": "BBCA.JK",
    "Bank Negara Indonesia (BBNI)": "BBNI.JK",
    "Bank Rakyat Indonesia (BBRI)": "BBRI.JK",
    "Bank Tabungan Negara (BBTN)": "BBTN.JK",
    "Bank Mandiri (BMRI)": "BMRI.JK",
    "Bank Syariah Indonesia (BRIS)": "BRIS.JK",
    "Barito Pacific (BRPT)": "BRPT.JK",
    "Bumi Resources (BUMI)": "BUMI.JK",
    "Charoen Pokphand Indonesia (CPIN)": "CPIN.JK",
    "Energi Mega Persada (ENRG)": "ENRG.JK",
    "Elang Mahkota Teknologi (EMTK)": "EMTK.JK",
    "Erajaya Swasembada (ERAA)": "ERAA.JK",
    "XL Axiata (EXCL)": "EXCL.JK",
    "GoTo Gojek Tokopedia (GOTO)": "GOTO.JK",
    "Gudang Garam (GGRM)": "GGRM.JK",
    "Hanjaya Mandala Sampoerna (HMSP)": "HMSP.JK",
    "Harum Energy (HRUM)": "HRUM.JK",
    "Indofood CBP Sukses Makmur (ICBP)": "ICBP.JK",
    "Vale Indonesia (INCO)": "INCO.JK",
    "Indofood Sukses Makmur (INDF)": "INDF.JK",
    "Indah Kiat Pulp & Paper (INKP)": "INKP.JK",
    "Indocement Tunggal Prakarsa (INTP)": "INTP.JK",
    "Indo Tambangraya Megah (ITMG)": "ITMG.JK",
    "Jasa Marga (JSMR)": "JSMR.JK",
    "Kalbe Farma (KLBF)": "KLBF.JK",
    "Merdeka Copper Gold (MDKA)": "MDKA.JK",
    "Medco Energi Internasional (MEDC)": "MEDC.JK",
    "Mitra Keluarga Karyasehat (MIKA)": "MIKA.JK",
    "Media Nusantara Citra (MNCN)": "MNCN.JK",
    "MNC Digital Entertainment (MSIN)": "MSIN.JK",
    "Perusahaan Gas Negara (PGAS)": "PGAS.JK",
    "Bukit Asam (PTBA)": "PTBA.JK",
    "PP (PTPP)": "PTPP.JK",
    "Semen Indonesia (SMGR)": "SMGR.JK",
    "Summarecon Agung (SMRA)": "SMRA.JK",
    "Surya Citra Media (SCMA)": "SCMA.JK",
    "Tower Bersama Infrastructure (TBIG)": "TBIG.JK",
    "Timah (TINS)": "TINS.JK",
    "Telkom Indonesia (TLKM)": "TLKM.JK",
    "Sarana Menara Nusantara (TOWR)": "TOWR.JK",
    "Chandra Asri Petrochemical (TPIA)": "TPIA.JK",
    "United Tractors (UNTR)": "UNTR.JK",
    "Unilever Indonesia (UNVR)": "UNVR.JK",
    "Waskita Karya (WSKT)": "WSKT.JK",
    "Pakaraya (PBRX)": "PBRX.JK"
}

selected_stock_name = st.selectbox("Pilih Saham atau Indeks:", list(ihsg_stocks.keys()))
ticker_symbol = ihsg_stocks[selected_stock_name]

# Date range: 1 year of historical data for good technical indicator calculation
# Add 1 day to end_date because yfinance end date is exclusive
end_date = datetime.today() + timedelta(days=1)
start_date = end_date - timedelta(days=365)

@st.cache_data(ttl=3600)
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df

with st.spinner(f"Memuat data untuk {selected_stock_name} ({ticker_symbol})..."):
    df = load_data(ticker_symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

if df.empty:
    st.error("Gagal memuat data. Silakan coba lagi nanti.")
else:
    # Normalize yfinance 1.2.0 multi-index columns for single ticker
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Ensure columns are Series
    close_series = df['Close'].squeeze()

    # --- Technical Indicators ---

    # 1. Simple Moving Averages
    df['SMA_20'] = ta.trend.sma_indicator(close_series, window=20)
    df['SMA_50'] = ta.trend.sma_indicator(close_series, window=50)

    # 2. Relative Strength Index (RSI)
    df['RSI'] = ta.momentum.rsi(close_series, window=14)

    # 3. MACD
    macd = ta.trend.MACD(close_series)
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()

    # --- Analysis & Recommendation Logic for Next Week ---
    last_row = df.iloc[-1]

    # Analyze trends
    sma_trend = "Bullish" if last_row['SMA_20'] > last_row['SMA_50'] else "Bearish"
    rsi_status = "Overbought (Hati-hati turun)" if last_row['RSI'] > 70 else "Oversold (Potensi naik)" if last_row['RSI'] < 30 else "Netral"
    macd_trend = "Bullish" if last_row['MACD'] > last_row['MACD_Signal'] else "Bearish"

    # Overall Recommendation Logic
    score = 0
    if sma_trend == "Bullish": score += 1
    elif sma_trend == "Bearish": score -= 1

    if last_row['RSI'] < 40: score += 1
    elif last_row['RSI'] > 60: score -= 1

    if macd_trend == "Bullish": score += 1
    elif macd_trend == "Bearish": score -= 1

    if score >= 2:
        recommendation = "📈 POTENSI NAIK (BUY)"
        rec_color = "green"
    elif score <= -2:
        recommendation = "📉 POTENSI TURUN (SELL/HINDARI)"
        rec_color = "red"
    else:
        recommendation = "↔️ NETRAL (HOLD/WAIT & SEE)"
        rec_color = "orange"

    # --- UI Display ---
    st.subheader(f"Analisis Terkini: {selected_stock_name} ({ticker_symbol})")

    col1, col2, col3, col4 = st.columns(4)

    last_close = float(last_row['Close'].squeeze()) if isinstance(last_row['Close'], pd.Series) else float(last_row['Close'])

    col1.metric("Harga Terakhir", f"Rp {int(last_close):,}")
    col2.metric("Trend SMA (20 vs 50)", sma_trend)
    col3.metric("RSI (14 hari)", f"{last_row['RSI']:.2f}", delta_color="off", help=rsi_status)
    col4.metric("MACD Trend", macd_trend)

    st.markdown(f"### Prediksi 1 Minggu ke Depan: **:{rec_color}[{recommendation}]**")
    st.info("Catatan: Prediksi ini didasarkan pada indikator teknikal historis dan tidak menjamin kinerja masa depan. Keputusan investasi tetap berada di tangan Anda.")

    # --- Interactive Chart ---
    st.subheader("Grafik Harga dan Indikator")

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'].squeeze(),
                    high=df['High'].squeeze(),
                    low=df['Low'].squeeze(),
                    close=df['Close'].squeeze(),
                    name='Harga')])

    # Add SMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=1.5), name='SMA 20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='blue', width=1.5), name='SMA 50'))

    fig.update_layout(
        title=f"Pergerakan Harga {ticker_symbol} (1 Tahun Terakhir)",
        yaxis_title='Harga (IDR)',
        xaxis_title='Tanggal',
        xaxis_rangeslider_visible=False,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detail Data Tab
    with st.expander("Lihat Data Mentah"):
        st.dataframe(df.tail(10))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import re

def markdown_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # newline -> <br>
    text = text.replace('\n', '<br>')
    return text

#api
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")


PALETTE = {
    "bg":        "#0D1117",
    "surface":   "#161B22",
    "surface2":  "#21262D",
    "border":    "#30363D",
    "accent":    "#58A6FF",
    "accent2":   "#3FB950",
    "accent3":   "#F78166",
    "accent4":   "#D2A8FF",
    "accent5":   "#E3B341",
    "text":      "#E6EDF3",
    "muted":     "#8B949E",
}

CHART_COLORS = ["#58A6FF", "#3FB950", "#F78166", "#D2A8FF", "#FFA657", "#79C0FF"]

st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

#css
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Base */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {PALETTE['bg']};
        color: {PALETTE['text']};
    }}
    .stApp {{
        background-color: {PALETTE['bg']};
    }}

    /* Main content area */
    .main .block-container {{
        padding: 1.5rem 2.5rem 3rem;
        max-width: 1400px;
    }}

    /* Header */
    .dash-header {{
        border-bottom: 1px solid {PALETTE['border']};
        padding-bottom: 1.2rem;
        margin-bottom: 1.5rem;
    }}
    .dash-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {PALETTE['text']};
        letter-spacing: -0.02em;
        margin: 0;
    }}
    .dash-subtitle {{
        font-size: 0.8rem;
        color: {PALETTE['muted']};
        margin: 0.2rem 0 0;
        font-weight: 400;
    }}
    .badge {{
        display: inline-block;
        background: {PALETTE['surface2']};
        border: 1px solid {PALETTE['border']};
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        color: {PALETTE['accent']};
        font-family: 'JetBrains Mono', monospace;
        margin-left: 8px;
        vertical-align: middle;
    }}

    /* KPI Cards */
    .kpi-row {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .kpi-card {{
        flex: 1;
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
    }}
    .kpi-card.blue::before  {{ background: {PALETTE['accent']}; }}
    .kpi-card.green::before {{ background: {PALETTE['accent2']}; }}
    .kpi-card.red::before   {{ background: {PALETTE['accent3']}; }}
    .kpi-card.purple::before{{ background: {PALETTE['accent4']}; }}
    .kpi-label {{
        font-size: 0.72rem;
        color: {PALETTE['muted']};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }}
    .kpi-value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {PALETTE['text']};
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.03em;
        line-height: 1;
    }}
    .kpi-sub {{
        font-size: 0.72rem;
        color: {PALETTE['muted']};
        margin-top: 0.3rem;
    }}

    /* Section labels */
    .section-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {PALETTE['muted']};
        font-weight: 600;
        margin-bottom: 0.6rem;
    }}
    .chart-card {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }}
    .chart-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {PALETTE['text']};
        margin-bottom: 0.8rem;
    }}

    /* Filter bar */
    .filter-bar {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }}
    .filter-label {{
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {PALETTE['muted']};
    }}

    /* RFM Table */
    .rfm-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
    }}
    .rfm-table th {{
        background: {PALETTE['surface2']};
        color: {PALETTE['muted']};
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.6rem 0.8rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 1px solid {PALETTE['border']};
    }}
    .rfm-table td {{
        padding: 0.65rem 0.8rem;
        border-bottom: 1px solid {PALETTE['border']};
        color: {PALETTE['text']};
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }}
    .rfm-table tr:last-child td {{ border-bottom: none; }}
    .rfm-table tr:hover td {{ background: {PALETTE['surface2']}; }}
    .cluster-pill {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }}

    /* AI card */
    .ai-card {{
        background: linear-gradient(135deg, #161B22 0%, #1C2333 100%);
        border: 1px solid #2D419B;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-top: 0.8rem;
    }}
    .ai-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }}
    .ai-dot {{
        width: 8px; height: 8px;
        border-radius: 50%;
        background: {PALETTE['accent']};
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}
    .ai-label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {PALETTE['accent']};
        font-weight: 600;
    }}

    /* Streamlit component overrides */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stSlider"] label {{
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: {PALETTE['muted']} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
    }}
    div[data-testid="stTabs"] button {{
        font-size: 0.82rem;
        font-weight: 500;
    }}
    div[data-testid="metric-container"] {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }}
    .stSpinner > div {{
        border-top-color: {PALETTE['accent']} !important;
    }}
    hr {{
        border-color: {PALETTE['border']} !important;
        margin: 1rem 0;
    }}
</style>
""", unsafe_allow_html=True)


#load data
@st.cache_data
def load_data():
    df = pd.read_csv("retail_sales_clustered.csv")
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    df['Month-Year'] = df['Transaction Date'].dt.to_period('M').astype(str)
    df['Year-Month-dt'] = df['Transaction Date'].dt.to_period('M').dt.to_timestamp()
    df['Discount Applied'] = df['Discount Applied'].astype(str).str.strip().str.lower().map(
        {'true': True, 'false': False, '1': True, '0': False}
    )
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("file tidak ditemukan!")
    st.stop()


#chart
def chart_layout(fig, height=320):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=PALETTE['muted'], size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=PALETTE['border'],
            font=dict(size=10, color=PALETTE['muted']),
        ),
        xaxis=dict(
            gridcolor=PALETTE['border'],
            linecolor=PALETTE['border'],
            tickcolor=PALETTE['border'],
        ),
        yaxis=dict(
            gridcolor=PALETTE['border'],
            linecolor="rgba(0,0,0,0)",
        ),
    )
    return fig


#ai
@st.cache_data(show_spinner=False)
def generate_promo_with_api(cluster_name, profile_info, top_categories):
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_xxxxxx":
        return "⚠️ Silakan isi variabel `GROQ_API_KEY` dengan API Key Groq kamu!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Kamu adalah seorang Senior Marketing Strategist di perusahaan retail besar.
Profil klaster pelanggan:
- Nama Kelompok: {cluster_name}
- Karakteristik RFM: {profile_info}
- Kategori Produk Favorit: {top_categories}

Buatkan TEPAT 3 strategi promosi. Format output WAJIB seperti ini (jangan tambah teks lain):

1️⃣ **[Nama Strategi]** :
[1 kalimat penjelasan singkat]

2️⃣ **[Nama Strategi]** :
[1 kalimat penjelasan singkat]

3️⃣ **[Nama Strategi]** :
[1 kalimat penjelasan singkat]

Jangan tulis intro, kesimpulan, atau poin tambahan. Langsung 3 poin saja.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Gagal memanggil AI. Error: {str(e)}"


#atas
st.markdown("""
<div class="dash-header">
  <p class="dash-title">📊 Retail Intelligence Dashboard</p>
  <p class="dash-subtitle">Sales Performance · Customer Segmentation · AI-Powered Promotions</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈  Executive Sales Overview", "🤖  AI Customer Segmentation & Promo"])


#sales overview
with tab1:

    # filter
    with st.container():
        st.markdown('<div class="filter-label">🔽 Filter Data</div>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns([2, 2, 3])

        with fc1:
            loc_opts = ["Semua"] + sorted(df['Location'].dropna().unique().tolist())
            sel_location = st.selectbox("Lokasi", loc_opts)

        with fc2:
            pay_opts = ["Semua"] + sorted(df['Payment Method'].dropna().unique().tolist())
            sel_payment = st.selectbox("Metode Pembayaran", pay_opts)

        with fc3:
            min_date = df['Transaction Date'].min().date()
            max_date = df['Transaction Date'].max().date()
            date_range = st.date_input(
                "Rentang Tanggal",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

    # Apply filters
    dff = df.copy()
    if sel_location != "Semua":
        dff = dff[dff['Location'] == sel_location]
    if sel_payment != "Semua":
        dff = dff[dff['Payment Method'] == sel_payment]
    if len(date_range) == 2:
        start_d, end_d = date_range
        dff = dff[(dff['Transaction Date'].dt.date >= start_d) & (dff['Transaction Date'].dt.date <= end_d)]

    st.markdown("---")

    #kpi
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_rev   = dff['Total Spent'].sum()
    total_trx   = dff['Transaction ID'].nunique()
    total_cust  = dff['Customer ID'].nunique()
    avg_order   = dff['Total Spent'].mean()

    with kpi1:
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-label">Total Revenue</div>
          <div class="kpi-value">${total_rev:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-label">Transactions</div>
          <div class="kpi-value">{total_trx:,}</div>
        </div>""", unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="kpi-card red">
          <div class="kpi-label">Customers</div>
          <div class="kpi-value">{total_cust:,}</div>
        </div>""", unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-card purple">
          <div class="kpi-label">Avg Order Value</div>
          <div class="kpi-value">${avg_order:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    #chart 1 (monthly sales)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown('<div class="chart-title">Monthly Sales Trend</div>', unsafe_allow_html=True)
        df_trend = dff.groupby('Month-Year')['Total Spent'].sum().reset_index()
        df_trend = df_trend.sort_values('Month-Year')
        fig_trend = px.area(
            df_trend, x='Month-Year', y='Total Spent',
            color_discrete_sequence=[PALETTE['accent']],
        )
        fig_trend.update_traces(
            line=dict(width=2),
            fillcolor=f"rgba(88,166,255,0.12)",
            hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
        )
        fig_trend.update_xaxes(tickangle=45, tickfont=dict(size=9))
        fig_trend.update_yaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(chart_layout(fig_trend, 300), use_container_width=True)

    with r1c2:
        #chart 2 (revenue by product)
        st.markdown('<div class="chart-title">Revenue by Product Category</div>', unsafe_allow_html=True)
        df_cat = dff.groupby('Category')['Total Spent'].sum().reset_index().sort_values('Total Spent')
        fig_cat = px.bar(
            df_cat, x='Total Spent', y='Category', orientation='h',
            color='Total Spent',
            color_continuous_scale=[[0, "#1C2333"], [1, PALETTE['accent']]],
        )
        fig_cat.update_coloraxes(showscale=False)
        fig_cat.update_traces(
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        )
        fig_cat.update_xaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(chart_layout(fig_cat, 300), use_container_width=True)

    #chart 3 (Discount impact)
    st.markdown("---")
    r2c1, r2c2 = st.columns([3, 2])

    with r2c1:
        st.markdown('<div class="chart-title">Discount Impact — Revenue With vs Without Discount</div>', unsafe_allow_html=True)
        df_disc = dff.groupby(['Month-Year', 'Discount Applied'])['Total Spent'].sum().reset_index()
        df_disc['Discount Applied'] = df_disc['Discount Applied'].map(
            {True: 'With Discount', False: 'Without Discount'}
        )
        df_disc = df_disc.sort_values('Month-Year')
        fig_disc = px.line(
            df_disc, x='Month-Year', y='Total Spent',
            color='Discount Applied',
            markers=True,
            color_discrete_map={
                'With Discount':    PALETTE['accent2'],
                'Without Discount': PALETTE['accent3'],
            },
        )
        fig_disc.update_traces(
            line=dict(width=2),
            marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>%{data.name}<br>Revenue: $%{y:,.0f}<extra></extra>",
        )
        fig_disc.update_xaxes(tickangle=45, tickfont=dict(size=9))
        fig_disc.update_yaxes(tickprefix="$", tickformat=",.0f")
        fig_disc.update_layout(legend=dict(orientation="h", y=1.12, x=0))
        st.plotly_chart(chart_layout(fig_disc, 310), use_container_width=True)

    with r2c2:
        #chart 4 (Revenue)
        st.markdown('<div class="chart-title">Revenue Split</div>', unsafe_allow_html=True)

        tab_loc, tab_pay = st.tabs(["By Location", "By Payment"])
        with tab_loc:
            df_loc = dff.groupby('Location')['Total Spent'].sum().reset_index()
            fig_loc = px.pie(
                df_loc, values='Total Spent', names='Location',
                hole=0.5, color_discrete_sequence=CHART_COLORS,
            )
            fig_loc.update_traces(textfont_size=11, hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>")
            st.plotly_chart(chart_layout(fig_loc, 260), use_container_width=True)

        with tab_pay:
            df_pay = dff.groupby('Payment Method')['Total Spent'].sum().reset_index()
            fig_pay = px.pie(
                df_pay, values='Total Spent', names='Payment Method',
                hole=0.5, color_discrete_sequence=CHART_COLORS,
            )
            fig_pay.update_traces(textfont_size=11, hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>")
            st.plotly_chart(chart_layout(fig_pay, 260), use_container_width=True)


#ai recomendation
with tab2:

    CLUSTER_META = {
        0: {
            "name":  "Recent & Active Buyers",
            "emoji": "🟢",
            "desc":  "Pelanggan baru saja belanja belakangan ini (Recency sangat rendah, rata-rata 1.4 hari). Tingkat interaksi sedang tinggi, namun frekuensi dan total belanja masih di tingkat menengah.",
            "color": PALETTE['accent2'],
        },
        1: {
            "name":  "Hibernating Customers",
            "emoji": "🔴",
            "desc":  "Pelanggan sudah lama tidak belanja (Recency tinggi, rata-rata 3.8 hari). Frekuensi belanja mereka paling rendah dan total uang yang dihabiskan paling sedikit.",
            "color": PALETTE['accent3'],
        },
        2: {
            "name":  "Champions / Top Spenders",
            "emoji": "🟡",
            "desc":  "Pelanggan bintang lima. Frekuensi belanja mereka paling tinggi (rata-rata 530 transaksi) dan total pengeluarannya paling besar (rata-rata $69,837 per orang).",
            "color": PALETTE['accent5'],
        },
    }

    st.markdown("""
    <div style="margin-bottom:1.2rem">
      <div class="chart-title" style="font-size:1rem">AI Customer Clustering & Tailored Promo Recommendations</div>
      
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Recency, Frequency, Monetary
    st.markdown('<div class="chart-title">Recency, Frequency, Monetary Summary per Cluster</div>', unsafe_allow_html=True)

    if 'Cluster' in df.columns:
        rfm_agg = df.groupby('Cluster').agg(
            Recency   = ('Transaction Date', lambda x: (df['Transaction Date'].max() - x.max()).days),
            Frequency = ('Transaction ID',   'count'),
            Monetary  = ('Total Spent',      'mean'),
            Customers = ('Customer ID',      'nunique'),
        ).reset_index()

        rows_html = ""
        for _, row in rfm_agg.iterrows():
            c = int(row['Cluster'])
            m = CLUSTER_META.get(c, {})
            pill_color = m.get('color', PALETTE['accent'])
            rows_html += f"""
            <tr>
              <td><span class="cluster-pill" style="background:{pill_color}22;color:{pill_color};border:1px solid {pill_color}55">
                {m.get('emoji','')} Cluster {c}</span></td>
              <td>{m.get('name','—')}</td>
              <td>{int(row['Recency'])} days</td>
              <td>{int(row['Frequency']):,}</td>
              <td>${row['Monetary']:,.2f}</td>
              <td>{int(row['Customers']):,}</td>
            </tr>"""

        st.markdown(f"""
        <table class="rfm-table">
          <thead>
            <tr>
              <th>Cluster</th><th>Profil</th>
              <th>Avg Recency</th><th>Avg Frequency</th>
              <th>Avg Monetary</th><th>Customers</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("salah dataset")

    st.markdown("---")

    # Cluster selector
    sel_cluster = st.selectbox(
        "Pilih Cluster untuk Analisis Detail",
        options=["Tampilkan Semua", "Cluster 0", "Cluster 1", "Cluster 2"],
    )

    if sel_cluster == "Tampilkan Semua":
        # Pie chart distribution
        st.markdown('<div class="chart-title" style="margin-top:1rem">Distribusi Transaksi per Cluster</div>', unsafe_allow_html=True)
        df_cnt = df['Cluster'].value_counts().reset_index()
        df_cnt.columns = ['Cluster', 'Count']
        df_cnt['Label'] = df_cnt['Cluster'].apply(
            lambda x: f"{CLUSTER_META.get(x,{}).get('emoji','')} Cluster {x} — {CLUSTER_META.get(x,{}).get('name','')}"
        )
        cluster_color_map = {
            row['Label']: CLUSTER_META.get(row['Cluster'], {}).get('color', PALETTE['accent'])
            for _, row in df_cnt.iterrows()
        }
        fig_pie = px.pie(
            df_cnt, values='Count', names='Label',
            hole=0.45, color='Label', color_discrete_map=cluster_color_map,
        )
        fig_pie.update_traces(textfont_size=11, hovertemplate="<b>%{label}</b><br>%{value:,} transaksi (%{percent})<extra></extra>")
        st.plotly_chart(chart_layout(fig_pie, 350), use_container_width=True)

    else:
        cluster_num = int(sel_cluster.split()[-1])
        fdf = df[df['Cluster'] == cluster_num] if 'Cluster' in df.columns else df
        meta = CLUSTER_META[cluster_num]

        # Profile rfm
        st.markdown(f"""
        <div style="background:{meta['color']}11;border:1px solid {meta['color']}44;border-radius:10px;padding:1rem 1.2rem;margin:0.8rem 0 1.2rem">
          <div style="font-size:1rem;font-weight:700;color:{meta['color']};margin-bottom:0.3rem">{meta['emoji']} {meta['name']}</div>
          <div style="font-size:0.82rem;color:{PALETTE['muted']}">{meta['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Charts 5 (Top 5 items by revenue)
        ci1, ci2 = st.columns(2)

        with ci1:
            st.markdown('<div class="chart-title">Top 5 Items by Revenue</div>', unsafe_allow_html=True)
            if 'Item' in fdf.columns:
                top5 = fdf.groupby('Item')['Total Spent'].sum().nlargest(5).reset_index()
                fig_t5 = px.bar(
                    top5, x='Total Spent', y='Item', orientation='h',
                    color='Total Spent',
                    color_continuous_scale=[[0, "#1C2333"], [1, meta['color']]],
                )
                fig_t5.update_coloraxes(showscale=False)
                fig_t5.update_xaxes(tickprefix="$", tickformat=",.0f")
                fig_t5.update_traces(hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>")
                st.plotly_chart(chart_layout(fig_t5, 270), use_container_width=True)
            else:
                st.info("Kolom 'Item' tidak ditemukan.")

        with ci2:
            st.markdown('<div class="chart-title">Revenue by Category</div>', unsafe_allow_html=True)
            df_cc = fdf.groupby('Category')['Total Spent'].sum().reset_index().sort_values('Total Spent', ascending=False)
            fig_cc = px.bar(
                df_cc, x='Category', y='Total Spent',
                color='Category',
                color_discrete_sequence=CHART_COLORS,
            )
            fig_cc.update_layout(showlegend=False)
            fig_cc.update_xaxes(tickangle=20, tickfont=dict(size=9))
            fig_cc.update_yaxes(tickprefix="$", tickformat=",.0f")
            fig_cc.update_traces(hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>")
            st.plotly_chart(chart_layout(fig_cc, 270), use_container_width=True)

        # AI Promo recom
        st.markdown("---")
        top_cats = fdf['Category'].value_counts().head(2).index.tolist()
        top_cats_str = ", ".join(top_cats)

        st.markdown(f"""
        <div class="ai-header" style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
          <div class="ai-dot"></div>
          <span class="ai-label">AI Promo Recommendation</span>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Loading..."):
            ai_rec = generate_promo_with_api(meta['name'], meta['desc'], top_cats_str)
        ai_rec_html = markdown_to_html(ai_rec)  
        st.markdown(f'<div class="ai-card">{ai_rec_html}</div>', unsafe_allow_html=True)
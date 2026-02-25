import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List

# 1. KONFIGURĀCIJA
st.set_page_config(page_title="NordTech Dashboard", layout="wide")

# 2. CUSTOM CSS (Tavs inženiera stils + palielināts mērogs)
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .block-container {
            padding-top: 2rem;
            max-width: 95%;
        }
        
        div[data-testid="stMetric"] {
            background-color: white;
            padding: 60px 40px !important;
            border-radius: 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.08);
            
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }
        
        div[data-testid="stHorizontalBlock"] > div {
            align-items: stretch !important;
        }
        div[data-testid="column"] {
            display: flex !important;
        }

        div[data-testid="column"] > div {
            width: 100%;
        }

        [data-testid="stMetricValue"] {
            font-size: 38px !important;
            line-height: 1.1 !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            font-size: 18px !important;
            color: #546e7a !important;
        }

        html, body, [class*="st-"] {
            font-size: 18px; 
        }

        h1 { 
            font-size: 2.2rem !important;
            margin-bottom: 0.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Profesionāls grafiku stils (Palielināti fonti)
layout_theme = dict(
    template="simple_white",
    font=dict(family="Arial", size=16, color="#2c3e50"), 
    title=dict(font=dict(size=24, color="#1a252f"), x=0.05), 
    margin=dict(l=50, r=50, t=80, b=50)
)

@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    df = pd.read_csv('enriched_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    df['complaint_count'] = pd.to_numeric(df['complaint_count'], errors='coerce').fillna(0)
    return df

def get_unique_complaint_categories(df: pd.DataFrame) -> List[str]:
    categories = df['category'].dropna().unique()
    unique_cats = set()
    for cat_str in categories:
        if cat_str != 'No complaints':
            for c in cat_str.split(', '):
                unique_cats.add(c)
    return sorted(list(unique_cats))

# 3. DATU SAGATAVOŠANA
df = load_data()
all_complaint_types = get_unique_complaint_categories(df)

# 4. SĀNJOSLA (FILTRI)
st.sidebar.header("Filtri")
all_product_cats = sorted(df['Product_Category'].unique().tolist())
selected_product_cats = st.sidebar.multiselect("Produkta kategorija", all_product_cats, default=all_product_cats)
selected_complaint_cats = st.sidebar.multiselect("Sūdzību kategorija", all_complaint_types, default=all_complaint_types)
min_date, max_date = df['Date'].min().to_pydatetime(), df['Date'].max().to_pydatetime()
date_range = st.sidebar.date_input("Periods", [min_date, max_date])

# 5. FILTRĒŠANAS LOĢIKA
filtered_df = df.copy()
if selected_product_cats:
    filtered_df = filtered_df[filtered_df['Product_Category'].isin(selected_product_cats)]
if selected_complaint_cats:
    pattern = '|'.join(selected_complaint_cats)
    if len(selected_complaint_cats) < len(all_complaint_types):
        filtered_df = filtered_df[filtered_df['category'].str.contains(pattern, na=False)]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df['Date'] >= pd.Timestamp(date_range[0])) & 
                              (filtered_df['Date'] <= pd.Timestamp(date_range[1]))]

if filtered_df.empty:
    st.warning("Nav datu izvēlētajam filtram.")
    st.stop()

filtered_df = filtered_df.copy()

# 6. KPI RINDA
st.title("🚀 NordTech Biznesa Analītikas Panelis")
st.caption("Reāllaika biznesa veiktspējas pārskats")

kpi1, kpi2, kpi3 = st.columns(3)

total_revenue = filtered_df['Price'].sum()
total_returns_count = (filtered_df['Status'] == 'Processed').sum()
return_rate = (total_returns_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
linked_complaints = int(filtered_df['complaint_count'].sum())
total_system_complaints = 344

with kpi1:
    st.markdown(f"""
        <div style="
            background:white;
            padding:28px 24px;
            border-radius:22px;
            box-shadow:0 12px 30px rgba(0,0,0,0.08);
        ">
            <div style="font-size:22px;color:#546e7a;">
                Kopējie ieņēmumi
            </div>
            <div style="font-size:40px;font-weight:bold;">
                {total_revenue:,.2f} €
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div style="
            background:white;
            padding:28px 24px;
            border-radius:22px;
            box-shadow:0 12px 30px rgba(0,0,0,0.08);
        ">
            <div style="font-size:22px;color:#546e7a;margin-bottom:15px;">
                Atgriezumu likme (%)
            </div>
            <div style="font-size:40px;font-weight:700;color:#2c3e50;">
                {return_rate:.1f}%
            </div>
            <div style="
                margin-top:20px;
                display:inline-block;
                background:#e8f5e9;
                color:#2e7d32;
                padding:8px 16px;
                border-radius:30px;
                font-size:18px;
            ">
                ↑ {total_returns_count} gab
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div style="
            background:white;
            padding:28px 24px;
            border-radius:22px;
            box-shadow:0 12px 30px rgba(0,0,0,0.08);
        ">
            <div style="font-size:22px;color:#546e7a;margin-bottom:15px;">
                Sūdzību skaits
            </div>
            <div style="font-size:40px;font-weight:700;color:#2c3e50;">
                {linked_complaints}
            </div>
            <div style="
                margin-top:20px;
                display:inline-block;
                background:#eceff1;
                color:#546e7a;
                padding:8px 16px;
                border-radius:30px;
                font-size:18px;
            ">
                no {total_system_complaints} kopā
            </div>
        </div>
    """, unsafe_allow_html=True)

# 7. VIZUĀĻI (Tavi grafiki ar biezākiem stabiņiem un lielākiem fontiem)

filtered_df['Week'] = (
    filtered_df['Date']
    .dt.to_period('W')
    .dt.start_time
)
weekly_data = filtered_df.groupby('Week').agg({'Price': 'sum', 'Status': lambda x: (x == 'Processed').sum()}).reset_index()
fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(go.Scatter(x=weekly_data['Week'], y=weekly_data['Price'], name="Ieņēmumi", mode='lines+markers', line=dict(width=4, color='#3498db')), secondary_y=False)
fig1.add_trace(go.Scatter(x=weekly_data['Week'], y=weekly_data['Status'], name="Atgriezumi", mode='lines+markers', line=dict(width=4, color='#e74c3c')), secondary_y=True)
fig1.update_layout(**{k: v for k, v in layout_theme.items() if k != 'title'})
fig1.update_layout(title_text="<b>IEŅĒMUMU UN ATGRIEZUMU DINAMIKA</b>", hovermode="x unified", height=650, legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig1, use_container_width=True)

cat_returns = filtered_df.groupby('Product_Category').agg({'Transaction_ID': 'count', 'Status': lambda x: (x == 'Processed').sum()}).reset_index()
cat_returns['Return_Rate'] = (cat_returns['Status'] / cat_returns['Transaction_ID']) * 100
cat_returns = cat_returns.sort_values('Return_Rate')
colors = {cat: '#e74c3c' if cat == 'Smart Home' else '#34495e' for cat in cat_returns['Product_Category']}
fig2 = px.bar(cat_returns, y='Product_Category', x='Return_Rate', orientation='h', text_auto='.1f', color='Product_Category', color_discrete_map=colors)
fig2.update_layout(**{k: v for k, v in layout_theme.items() if k != 'title'})
fig2.update_layout(title_text="<b>ATGRIEZUMU LIKME PA KATEGORIJĀM (%)</b>", showlegend=False, height=650, bargap=0.15) # Biezāki stabiņi
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

complaints_sub = filtered_df[filtered_df['category'] != 'No complaints'].copy()
if not complaints_sub.empty:
    complaints_sub['cat_split'] = complaints_sub['category'].str.split(', ')
    exploded = complaints_sub.explode('cat_split')
    complaint_data = exploded['cat_split'].value_counts().reset_index().sort_values('count', ascending=True)
    nordtech_blues = ['#95a5a6', '#7fb3d5', '#5dade2', '#3498db', '#1b4f72', '#003366']
    fig3 = px.bar(complaint_data, y='cat_split', x='count', orientation='h', color='cat_split', color_discrete_sequence=nordtech_blues, text_auto=True)
    fig3.update_traces(textposition='outside', cliponaxis=False, marker_line_color='#2c3e50', marker_line_width=1, opacity=0.9)
    fig3.update_layout(**{k: v for k, v in layout_theme.items() if k != 'title'})
    fig3.update_layout(title_text="<b>SŪDZĪBU STRUKTŪRA</b>", showlegend=False, height=650, yaxis=dict(tickfont=dict(size=16)), xaxis=dict(tickfont=dict(size=16)), bargap=0.15) # Biezāki stabiņi
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("⚠️ Produktu kopsavilkums")
product_stats = filtered_df.groupby('Product_Name').agg({
    'Transaction_ID': 'count',
    'Status': lambda x: (x == 'Processed').sum(),
    'complaint_count': 'sum'
}).rename(columns={'Transaction_ID': 'Pārdošana', 'Status': 'Atgriezumi', 'complaint_count': 'Sūdzības'})
st.dataframe(product_stats.sort_values(by='Atgriezumi', ascending=False), use_container_width=True, height=450)

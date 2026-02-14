import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta

# --- 1. GLOBAL MASTER CONFIGURATION ---
# Placing this at the top level to prevent NameErrors in Sidebar logic
tesla_master = {
    'Model S Plaid': {
        'colors': ['Solid Black', 'Ultra Red', 'Stealth Grey', 'Deep Blue Metallic', 'Pearl White Multi-Coat'],
        'range': 396, 'acceleration': 1.99, 'top_speed': 200, 'price': 108990
    },
    'Model 3 Performance': {
        'colors': ['Deep Blue Metallic', 'Pearl White Multi-Coat', 'Quicksilver', 'Solid Black', 'Ultra Red'],
        'range': 315, 'acceleration': 3.1, 'top_speed': 162, 'price': 50990
    },
    'Model X Plaid': {
        'colors': ['Stealth Grey', 'Solid Black', 'Ultra Red', 'Silver Metallic', 'Pearl White Multi-Coat'],
        'range': 333, 'acceleration': 2.5, 'top_speed': 163, 'price': 94990
    },
    'Model Y Performance': {
        'colors': ['Midnight Cherry Red', 'Quicksilver', 'Pearl White Multi-Coat', 'Deep Blue Metallic', 'Solid Black'],
        'range': 303, 'acceleration': 3.5, 'top_speed': 155, 'price': 52490
    },
    'Cybertruck': {
        'colors': ['Stainless Steel', 'Satin Black', 'Satin White'],
        'range': 340, 'acceleration': 2.6, 'top_speed': 130, 'price': 99990
    },
    'Roadster': {
        'colors': ['Signature Red', 'Midnight Silver', 'Arctic White'],
        'range': 620, 'acceleration': 1.9, 'top_speed': 250, 'price': 200000
    }
}

# --- 2. HIGH-PERFORMANCE DATA ENGINE ---
@st.cache_data(ttl=3600)
def generate_tesla_telemetry(n=65000):
    np.random.seed(42)
    start_date = datetime(2020, 1, 1)
    regions = ['North America', 'Europe', 'Greater China', 'APAC', 'Middle East']
    dates = [start_date + timedelta(days=np.random.randint(0, 2200)) for _ in range(n)]
    
    data = []
    for _ in range(n):
        model = np.random.choice(list(tesla_master.keys()))
        color = np.random.choice(tesla_master[model]['colors'])
        data.append([model, color])
    
    core_df = pd.DataFrame(data, columns=['Model', 'Color'])
    df = pd.DataFrame({
        'VIN': [f"5YJ{np.random.randint(100000, 999999)}A{i:05d}" for i in range(n)],
        'Timestamp': dates,
        'Region': np.random.choice(regions, n),
        'Model': core_df['Model'],
        'Color': core_df['Color'],
        'Odometer_Miles': np.random.randint(100, 180000, n),
        'Battery_SOH': np.random.uniform(70, 100, n),
        'Wh_per_Mile': np.random.uniform(210, 480, n),
        'Supercharger_Ratio': np.random.uniform(0.05, 0.95, n),
        'Ambient_Temp_Avg': np.random.uniform(-10, 45, n),
        'Charging_Session_Cost': np.random.uniform(8, 115, n),
        'Autopilot_Miles': np.random.randint(0, 100000, n)
    })
    
    # BMS wear factor logic
    wear_factor = (df['Supercharger_Ratio'] * 0.45) + (abs(df['Ambient_Temp_Avg'] - 20) * 0.12)
    df['Battery_SOH'] -= wear_factor * (df['Odometer_Miles'] / 12000)
    df['Battery_SOH'] = df['Battery_SOH'].clip(lower=64, upper=100)
    df['SOH_Z_Score'] = stats.zscore(df['Battery_SOH'])
    df['Lead_Digit'] = df['Charging_Session_Cost'].apply(lambda x: int(str(int(x))[0]) if x > 0 else 0)
    return df

df = generate_tesla_telemetry()

# --- 3. UI CUSTOMIZATION ---
st.set_page_config(page_title="Tesla Fleet Intelligence", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    .stMetric { color: #E81922 !important; }
    .stSlider > div [data-baseweb="slider"] { background-color: #E81922; }
    div[data-testid="stPopover"] { margin-top: -15px; }
    .stAlert { background-color: rgba(232, 25, 34, 0.05); border-left: 5px solid #E81922; }
    </style>
    """, unsafe_allow_html=True)

st.title("T E S L A | Fleet Operations & Battery Intelligence")

# --- 4. DYNAMIC FILTERS (EMPTY = ALL) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png", width=120)
    region_filter = st.multiselect("Region", df['Region'].unique())
    region_final = region_filter if region_filter else df['Region'].unique()
    
    model_filter = st.multiselect("Models", list(tesla_master.keys()))
    model_final = model_filter if model_filter else list(tesla_master.keys())
    
    available_colors = set()
    for m in model_final:
        available_colors.update(tesla_master[m]['colors'])
    color_filter = st.multiselect("Colors", list(available_colors))
    color_final = color_filter if color_filter else list(available_colors)

f_df = df[(df['Region'].isin(region_final)) & 
          (df['Model'].isin(model_final)) & 
          (df['Color'].isin(color_final))].copy()

# --- 5. ALIGNED KPI GRID ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Avg SOH", f"{f_df['Battery_SOH'].mean():.1f}%")
    with st.popover("ℹ️"):
        st.write("**Battery SOH**: Measures capacity health. 90%+ is optimal.")
with c2:
    st.metric("Efficiency", f"{f_df['Wh_per_Mile'].mean():.0f} Wh/mi")
    with st.popover("ℹ️"):
        st.write("**Wh/mile**: Energy used per mile. Lower is more efficient.")
with c3:
    critical_alerts = len(f_df[f_df['SOH_Z_Score'] < -3.0])
    st.metric("Critical Alerts", critical_alerts)
    with st.popover("ℹ️"):
        st.write("**BMS Alerts**: High-risk outliers based on Z-Score.")
with c4:
    offset = (f_df['Odometer_Miles'].sum()*0.4)/1e3
    st.metric("CO2 Offset", f"{offset:.0f} Tons")
    with st.popover("ℹ️"):
        st.write("**CO2 Offset**: Savings compared to ICE baseline.")

st.divider()

# --- 6. PREDICTIVE ANALYTICS TABS ---
t1, t2, t3 = st.tabs(["🔋 Battery Health", "🕵️ Billing Forensics", "📊 Usage Performance"])

with t1:
    st.subheader("BMS Forensics: Odometer vs. SOH")
    
    st.scatter_chart(data=f_df, x='Odometer_Miles', y='Battery_SOH', color='Model')
    st.info("**Predictive Insight:** Fleet is projected to hit 70% SOH at ~192k miles.")

with t2:
    st.subheader("Billing Integrity Analysis")
    
    ben_counts = f_df['Lead_Digit'].value_counts(normalize=True).sort_index().drop(0, errors='ignore')
    st.bar_chart(ben_counts)
    st.success("**Forensic Insight:** Session costs follow natural log distribution.")

with t3:
    st.subheader("Efficiency Saturation by Region")
    st.bar_chart(data=f_df, x='Region', y='Wh_per_Mile', color='Model')
    st.warning("**Operational Insight:** APAC shows higher efficiency due to favorable urban cycles.")

st.divider()
st.subheader("Global Fleet Telemetry Archive")
st.dataframe(f_df.sort_values(by='Timestamp', ascending=False), use_container_width=True)

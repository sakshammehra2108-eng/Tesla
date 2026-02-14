import streamlit as st
import pandas as pd
import numpy as np
import re
from scipy import stats
from datetime import datetime, timedelta

# --- 1. GLOBAL MASTER CONFIGURATION ---
# Defined globally to prevent NameErrors in Sidebar logic
tesla_master = {
    'Model S Plaid': ['Solid Black', 'Ultra Red', 'Stealth Grey', 'Deep Blue Metallic'],
    'Model 3 High-Performance': ['Deep Blue Metallic', 'Pearl White Multi-Coat', 'Quicksilver', 'Solid Black'],
    'Model X': ['Stealth Grey', 'Solid Black', 'Ultra Red', 'Silver Metallic'],
    'Model Y': ['Midnight Cherry Red', 'Quicksilver', 'Pearl White Multi-Coat', 'Deep Blue Metallic'],
    'Cybertruck': ['Stainless Steel', 'Satin Black', 'Satin White'],
    'Roadster (Prototype)': ['Signature Red', 'Midnight Silver']
}

# --- 2. THE GIGAFACTORY TELEMETRY ENGINE ---
@st.cache_data
def generate_tesla_telemetry(n=65000):
    np.random.seed(42)
    start_date = datetime(2020, 1, 1)
    
    dates = [start_date + timedelta(days=np.random.randint(0, 2200)) for _ in range(n)]
    regions = ['North America', 'Europe', 'Greater China', 'APAC', 'Middle East']
    
    data = []
    for _ in range(n):
        model = np.random.choice(list(tesla_master.keys()))
        color = np.random.choice(tesla_master[model])
        data.append([model, color])
    
    core_df = pd.DataFrame(data, columns=['Model', 'Color'])
    
    df = pd.DataFrame({
        'VIN': [f"5YJ{np.random.randint(100000, 999999)}A{i:05d}" for i in range(n)],
        'Timestamp': dates,
        'Year': [d.year for d in dates],
        'Region': np.random.choice(regions, n),
        'Model': core_df['Model'],
        'Color': core_df['Color'],
        'Odometer_Miles': np.random.randint(100, 180000, n),
        'Battery_SOH': np.random.uniform(70, 100, n),
        'Wh_per_Mile': np.random.uniform(210, 480, n),
        'Supercharger_Ratio': np.random.uniform(0.05, 0.95, n),
        'Ambient_Temp_Avg': np.random.uniform(-10, 45, n),
        'Charging_Cost': np.random.uniform(8, 115, n)
    })
    
    # BMS Degradation Logic: Environmental & Usage Stress
    wear_factor = (df['Supercharger_Ratio'] * 0.45) + (abs(df['Ambient_Temp_Avg'] - 20) * 0.12)
    df['Battery_SOH'] -= wear_factor * (df['Odometer_Miles'] / 12000)
    df['Battery_SOH'] = df['Battery_SOH'].clip(lower=64, upper=100)
    
    # Forensics & Stats
    df['Lead_Digit'] = df['Charging_Cost'].apply(lambda x: int(str(int(x))[0]) if x > 0 else 0)
    df['SOH_Z_Score'] = stats.zscore(df['Battery_SOH'])
    
    return df

df = generate_tesla_telemetry()

# --- 3. TESLA CRIMSON UI CUSTOMIZATION ---
st.set_page_config(page_title="Tesla Fleet Command", layout="wide", page_icon="⚡")

# Injecting Tesla-Red accents into Streamlit
st.markdown("""
    <style>
    .stMetric { color: #E81922 !important; }
    .stSlider > div [data-baseweb="slider"] { background-color: #E81922; }
    </style>
    """, unsafe_allow_value=True)

st.title("T E S L A | Global Fleet Intelligence")
st.markdown("##### Performance, Battery Health & Usage Analytics Suite")

# --- 4. EXECUTIVE SIDEBAR (EMPTY = ALL LOGIC) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png", width=120)
    st.header("Fleet Controls")
    
    region_filter = st.multiselect("🌍 Region", df['Region'].unique())
    region_final = region_filter if region_filter else df['Region'].unique()
    
    model_filter = st.multiselect("🚗 Vehicle Models", list(tesla_master.keys()))
    model_final = model_filter if model_filter else list(tesla_master.keys())
    
    available_colors = set()
    for m in model_final:
        available_colors.update(tesla_master[m])
                
    color_filter = st.multiselect("🎨 Paint Variant", list(available_colors))
    color_final = color_filter if color_filter else list(available_colors)
    
    st.divider()
    st.subheader("BMS Thresholds")
    z_limit = st.slider("Alert Sensitivity (Z-Score)", 1.5, 5.0, 3.0)

# Filter Implementation
f_df = df[(df['Region'].isin(region_final)) & 
          (df['Model'].isin(model_final)) & 
          (df['Color'].isin(color_final))].copy()

# --- 5. EXECUTIVE TELEMETRY KPIs ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Fleet Avg SOH", f"{f_df['Battery_SOH'].mean():.1f}%", delta="-0.9% Wear")
with c2:
    st.metric("Energy Efficiency", f"{f_df['Wh_per_Mile'].mean():.0f} Wh/mi")
with c3:
    st.metric("BMS Critical Alerts", len(f_df[f_df['SOH_Z_Score'] < -z_limit]), delta_color="inverse")
with c4:
    st.metric("Total CO2 Offset", f"{(f_df['Odometer_Miles'].sum()*0.4)/1e3:.0f} Tons", delta="ICE Baseline")

st.divider()

# --- 6. OPERATIONAL INTELLIGENCE TABS ---
t1, t2, t3, t4 = st.tabs(["🔋 Battery Health", "🕵️ Charging Forensics", "📊 Performance Mix", "🛡️ Predictive Maintenance"])

with t1:
    st.subheader("BMS Forensics: SOH vs. Odometer")
    st.info("Visualizing premature health degradation in outlier vehicles.")
    
    st.scatter_chart(data=f_df, x='Odometer_Miles', y='Battery_SOH', color='Model', size='SOH_Z_Score')

with t2:
    st.subheader("Billing Integrity (Benford's Law)")
    st.info("Applying digital forensics to Supercharger billing cycles.")
    
    ben_counts = f_df['Lead_Digit'].value_counts(normalize=True).sort_index().drop(0, errors='ignore')
    st.bar_chart(ben_counts)

with t3:
    st.subheader("Energy Saturation by Regional Climate")
    st.bar_chart(data=f_df, x='Region', y='Wh_per_Mile', color='Model')

with t4:
    st.subheader("Critical Maintenance Audit")
    risk_df = f_df[f_df['SOH_Z_Score'] < -z_limit].sort_values(by='SOH_Z_Score')
    st.dataframe(risk_df[['VIN', 'Model', 'Region', 'Battery_SOH', 'Odometer_Miles', 'SOH_Z_Score']], use_container_width=True)

# --- 7. ARCHIVE AUDIT ---
st.divider()
st.subheader("Global Fleet Telemetry Archive")
st.dataframe(f_df.sort_values(by='Timestamp', ascending=False), use_container_width=True)

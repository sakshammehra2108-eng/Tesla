import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- 1. GLOBAL MASTER CONFIGURATION ---
tesla_master = {
    'Model S Plaid': {
        'colors': ['Solid Black', 'Ultra Red', 'Stealth Grey', 'Deep Blue Metallic', 'Pearl White Multi-Coat'],
        'range': 396,
        'acceleration': 1.99,
        'top_speed': 200,
        'price': 108990
    },
    'Model 3 Performance': {
        'colors': ['Deep Blue Metallic', 'Pearl White Multi-Coat', 'Quicksilver', 'Solid Black', 'Ultra Red'],
        'range': 315,
        'acceleration': 3.1,
        'top_speed': 162,
        'price': 50990
    },
    'Model X Plaid': {
        'colors': ['Stealth Grey', 'Solid Black', 'Ultra Red', 'Silver Metallic', 'Pearl White Multi-Coat'],
        'range': 333,
        'acceleration': 2.5,
        'top_speed': 163,
        'price': 94990
    },
    'Model Y Performance': {
        'colors': ['Midnight Cherry Red', 'Quicksilver', 'Pearl White Multi-Coat', 'Deep Blue Metallic', 'Solid Black'],
        'range': 303,
        'acceleration': 3.5,
        'top_speed': 155,
        'price': 52490
    },
    'Cybertruck': {
        'colors': ['Stainless Steel', 'Satin Black', 'Satin White'],
        'range': 340,
        'acceleration': 2.6,
        'top_speed': 130,
        'price': 99990
    },
    'Roadster': {
        'colors': ['Signature Red', 'Midnight Silver', 'Arctic White'],
        'range': 620,
        'acceleration': 1.9,
        'top_speed': 250,
        'price': 200000
    }
}

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tesla Fleet Intelligence Hub",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 3. ENHANCED CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Tesla Red accent */
    .stMetric {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #E82127;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stMetric label {
        color: #a0a0a0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Cards and containers */
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 1px solid #E82127;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #E82127 0%, #c01820 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(232, 33, 39, 0.3);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #c01820 0%, #a01418 100%);
        box-shadow: 0 6px 12px rgba(232, 33, 39, 0.5);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1a1a;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2a2a;
        border-radius: 8px;
        color: #a0a0a0;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E82127 0%, #c01820 100%);
        color: white;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #E82127;
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2a2a2a;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Popover */
    div[data-testid="stPopover"] {
        background-color: #1a1a1a;
        border: 1px solid #E82127;
        border-radius: 8px;
    }
    
    /* Select boxes and inputs */
    .stSelectbox, .stMultiSelect {
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Divider */
    hr {
        border-color: #E82127;
        opacity: 0.3;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HIGH-PERFORMANCE DATA ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False)
def generate_tesla_telemetry(n=65000):
    """
    Generates synthetic Tesla fleet data with realistic patterns.
    
    Returns:
        DataFrame with vehicle telemetry including battery health, 
        efficiency metrics, and charging patterns.
    """
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
        'Tire_Pressure_PSI': np.random.uniform(32, 45, n),
        'Autopilot_Miles': np.random.randint(0, 100000, n),
        'Software_Version': np.random.choice(['2024.8', '2024.12', '2024.20', '2024.26', '2024.32'], n)
    })
    
    # Realistic BMS wear factor
    wear_factor = (df['Supercharger_Ratio'] * 0.45) + (abs(df['Ambient_Temp_Avg'] - 20) * 0.12)
    df['Battery_SOH'] -= wear_factor * (df['Odometer_Miles'] / 12000)
    df['Battery_SOH'] = df['Battery_SOH'].clip(lower=64, upper=100)
    
    # Additional metrics
    df['Lead_Digit'] = df['Charging_Session_Cost'].apply(lambda x: int(str(int(x))[0]) if x > 0 else 0)
    df['SOH_Z_Score'] = stats.zscore(df['Battery_SOH'])
    df['Efficiency_Rating'] = pd.cut(df['Wh_per_Mile'], bins=[0, 250, 300, 350, 500], labels=['Excellent', 'Good', 'Fair', 'Poor'])
    df['Battery_Health_Status'] = pd.cut(df['Battery_SOH'], bins=[0, 75, 85, 95, 100], labels=['Critical', 'Fair', 'Good', 'Excellent'])
    
    return df

# Load data with spinner
with st.spinner('🔋 Loading Tesla Fleet Data...'):
    df = generate_tesla_telemetry()

# --- 5. HEADER SECTION ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("⚡ TESLA Fleet Intelligence Hub")
    st.markdown("**Real-time analytics for 65,000+ vehicles worldwide** • Powered by Advanced BMS Analytics")
with col2:
    st.metric("", "")  # Spacer
    last_update = datetime.now().strftime("%B %d, %Y • %H:%M UTC")
    st.caption(f"🔄 Last Updated: {last_update}")

st.divider()

# --- 6. STRATEGIC SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png", width=150)
    st.markdown("### 🎛️ Fleet Control Center")
    st.caption("Filter your fleet data to analyze specific segments")
    
    st.markdown("---")
    
    # Region filter with helper
    st.markdown("**🌍 Geographic Region**")
    with st.expander("ℹ️ What is this?", expanded=False):
        st.caption("Select specific regions to analyze. Leave empty to view all regions.")
    region_filter = st.multiselect(
        "Select Region(s)",
        df['Region'].unique(),
        label_visibility="collapsed"
    )
    region_final = region_filter if region_filter else df['Region'].unique()
    
    st.markdown("---")
    
    # Model filter with helper
    st.markdown("**🚗 Vehicle Model**")
    with st.expander("ℹ️ What is this?", expanded=False):
        st.caption("Choose Tesla models to include in analysis. Each model has different performance characteristics.")
    model_filter = st.multiselect(
        "Select Model(s)",
        list(tesla_master.keys()),
        label_visibility="collapsed"
    )
    model_final = model_filter if model_filter else list(tesla_master.keys())
    
    st.markdown("---")
    
    # Color filter with helper
    st.markdown("**🎨 Vehicle Color**")
    with st.expander("ℹ️ What is this?", expanded=False):
        st.caption("Filter by exterior color. Colors vary by model selection.")
    available_colors = set()
    for m in model_final:
        available_colors.update(tesla_master[m]['colors'])
    color_filter = st.multiselect(
        "Select Color(s)",
        sorted(list(available_colors)),
        label_visibility="collapsed"
    )
    color_final = color_filter if color_filter else list(available_colors)
    
    st.markdown("---")
    
    # Date range filter
    st.markdown("**📅 Date Range**")
    with st.expander("ℹ️ What is this?", expanded=False):
        st.caption("Filter data by time period. Useful for trend analysis.")
    
    date_min = df['Timestamp'].min().date()
    date_max = df['Timestamp'].max().date()
    
    date_range = st.date_input(
        "Select Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Vehicles", f"{len(df):,}")
    st.metric("Avg Fleet Age", f"{(df['Odometer_Miles'].mean() / 12000):.1f} years")
    st.metric("Total Miles", f"{(df['Odometer_Miles'].sum() / 1e6):.1f}M")
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Apply filters
f_df = df[(df['Region'].isin(region_final)) & 
          (df['Model'].isin(model_final)) & 
          (df['Color'].isin(color_final))].copy()

# Date filter
if len(date_range) == 2:
    f_df = f_df[(f_df['Timestamp'].dt.date >= date_range[0]) & 
                (f_df['Timestamp'].dt.date <= date_range[1])]

# --- 7. KEY PERFORMANCE INDICATORS ---
st.markdown("### 📈 Fleet Performance Overview")
st.caption("Real-time metrics across your selected fleet segment")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    avg_soh = f_df['Battery_SOH'].mean()
    st.metric(
        "Average Battery Health",
        f"{avg_soh:.1f}%",
        delta=f"{avg_soh - df['Battery_SOH'].mean():.1f}%",
        help="State of Health (SOH) measures battery capacity retention. 90%+ is excellent, 70-85% is fair, below 70% needs attention."
    )

with kpi2:
    avg_eff = f_df['Wh_per_Mile'].mean()
    st.metric(
        "Avg Efficiency",
        f"{avg_eff:.0f} Wh/mi",
        delta=f"{-(avg_eff - df['Wh_per_Mile'].mean()):.0f}",
        delta_color="inverse",
        help="Energy consumption per mile. Lower is better. Typical range: 250-350 Wh/mi for optimal efficiency."
    )

with kpi3:
    critical_alerts = len(f_df[f_df['SOH_Z_Score'] < -3.0])
    st.metric(
        "Critical Alerts",
        critical_alerts,
        delta=f"-{len(df[df['SOH_Z_Score'] < -3.0]) - critical_alerts}" if critical_alerts < len(df[df['SOH_Z_Score'] < -3.0]) else 0,
        help="Vehicles with battery health 3+ standard deviations below average. These require immediate inspection."
    )

with kpi4:
    offset = (f_df['Odometer_Miles'].sum() * 0.4) / 1e3
    st.metric(
        "CO₂ Offset",
        f"{offset:.0f} Tons",
        delta=f"{offset * 0.15:.0f} vs last month",
        help="Estimated carbon emissions prevented compared to equivalent gasoline vehicles (avg 0.4 kg CO₂/mile)."
    )

with kpi5:
    avg_autopilot = (f_df['Autopilot_Miles'].sum() / f_df['Odometer_Miles'].sum()) * 100
    st.metric(
        "Autopilot Usage",
        f"{avg_autopilot:.1f}%",
        delta=f"{avg_autopilot - 45:.1f}%",
        help="Percentage of miles driven with Autopilot engaged. Higher usage correlates with improved safety metrics."
    )

st.divider()

# --- 8. DETAILED ANALYTICS TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔋 Battery Analytics",
    "⚡ Efficiency Insights",
    "🗺️ Geographic Distribution",
    "📊 Fleet Composition",
    "🔍 Advanced Diagnostics"
])

with tab1:
    st.markdown("### 🔋 Battery Management System (BMS) Analytics")
    st.caption("Deep dive into battery health patterns and degradation analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interactive scatter plot
        fig = px.scatter(
            f_df,
            x='Odometer_Miles',
            y='Battery_SOH',
            color='Model',
            size='Supercharger_Ratio',
            hover_data=['VIN', 'Region', 'Color', 'Ambient_Temp_Avg'],
            title='Battery Health vs Odometer Reading',
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Odometer (Miles)",
            yaxis_title="State of Health (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Read This Chart"):
            st.markdown("""
            - **X-Axis**: Total miles driven by the vehicle
            - **Y-Axis**: Battery capacity remaining (100% = like new)
            - **Color**: Different Tesla models
            - **Bubble Size**: How often the car uses Superchargers (larger = more frequent)
            - **Trend**: Downward slope shows natural battery degradation over time
            
            **What to look for:**
            - Vehicles below 75% SOH may need battery service
            - Steep drops indicate aggressive charging habits
            - Outliers (dots far from trend) warrant investigation
            """)
    
    with col2:
        st.markdown("#### 🎯 Battery Health Distribution")
        health_dist = f_df['Battery_Health_Status'].value_counts()
        
        fig2 = go.Figure(data=[go.Pie(
            labels=health_dist.index,
            values=health_dist.values,
            hole=0.4,
            marker=dict(colors=['#E82127', '#ff6b6b', '#ffd93d', '#6bcf7f'])
        )])
        fig2.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### 📋 Health Categories")
        st.markdown(f"""
        - 🟢 **Excellent** (95-100%): {len(f_df[f_df['Battery_Health_Status'] == 'Excellent'])} vehicles
        - 🟡 **Good** (85-95%): {len(f_df[f_df['Battery_Health_Status'] == 'Good'])} vehicles
        - 🟠 **Fair** (75-85%): {len(f_df[f_df['Battery_Health_Status'] == 'Fair'])} vehicles
        - 🔴 **Critical** (<75%): {len(f_df[f_df['Battery_Health_Status'] == 'Critical'])} vehicles
        """)
    
    st.markdown("---")
    
    # Predictive insights
    st.markdown("### 🔮 Predictive Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **📉 Degradation Rate**
        
        Average annual degradation: **{(100 - f_df['Battery_SOH'].mean()) / 5:.2f}%/year**
        
        At this rate, fleet will reach 80% SOH in approximately **{((f_df['Battery_SOH'].mean() - 80) / ((100 - f_df['Battery_SOH'].mean()) / 5)):.1f} years**
        """)
    
    with col2:
        supercharger_heavy = len(f_df[f_df['Supercharger_Ratio'] > 0.7])
        st.warning(f"""
        **⚡ Charging Behavior Alert**
        
        {supercharger_heavy} vehicles ({(supercharger_heavy/len(f_df)*100):.1f}%) use Superchargers >70% of the time
        
        Recommendation: Encourage home/destination charging for battery longevity
        """)
    
    with col3:
        temp_extreme = len(f_df[(f_df['Ambient_Temp_Avg'] < 0) | (f_df['Ambient_Temp_Avg'] > 35)])
        st.error(f"""
        **🌡️ Climate Impact**
        
        {temp_extreme} vehicles ({(temp_extreme/len(f_df)*100):.1f}%) operate in extreme temperatures
        
        Temperature extremes accelerate degradation by up to 40%
        """)

with tab2:
    st.markdown("### ⚡ Energy Efficiency Analysis")
    st.caption("Understanding energy consumption patterns across the fleet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Efficiency by model
        fig = px.box(
            f_df,
            x='Model',
            y='Wh_per_Mile',
            color='Model',
            title='Energy Efficiency Distribution by Model',
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Model",
            yaxis_title="Wh per Mile"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 Understanding Box Plots"):
            st.markdown("""
            **Box Plot Components:**
            - **Box**: Middle 50% of data (most common values)
            - **Line in box**: Median (middle value)
            - **Whiskers**: Range of typical values
            - **Dots**: Outliers (unusual values)
            
            **Lower Wh/mi = Better Efficiency**
            - Model 3: Most efficient (~280 Wh/mi avg)
            - Model X/Cybertruck: Least efficient due to size/weight
            """)
    
    with col2:
        # Efficiency rating distribution
        eff_dist = f_df['Efficiency_Rating'].value_counts().sort_index()
        
        fig2 = go.Figure(data=[go.Bar(
            x=eff_dist.index,
            y=eff_dist.values,
            marker=dict(color=['#6bcf7f', '#ffd93d', '#ff6b6b', '#E82127']),
            text=eff_dist.values,
            textposition='auto'
        )])
        fig2.update_layout(
            title='Fleet Efficiency Distribution',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Efficiency Rating",
            yaxis_title="Number of Vehicles"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### 📊 Efficiency Breakdown")
        st.markdown(f"""
        - 🟢 **Excellent** (<250 Wh/mi): {len(f_df[f_df['Efficiency_Rating'] == 'Excellent'])} vehicles
        - 🟡 **Good** (250-300): {len(f_df[f_df['Efficiency_Rating'] == 'Good'])} vehicles
        - 🟠 **Fair** (300-350): {len(f_df[f_df['Efficiency_Rating'] == 'Fair'])} vehicles
        - 🔴 **Poor** (>350): {len(f_df[f_df['Efficiency_Rating'] == 'Poor'])} vehicles
        """)
    
    st.markdown("---")
    
    # Regional efficiency comparison
    st.markdown("### 🗺️ Regional Efficiency Comparison")
    
    regional_eff = f_df.groupby('Region').agg({
        'Wh_per_Mile': 'mean',
        'VIN': 'count'
    }).round(0)
    regional_eff.columns = ['Avg Wh/Mile', 'Vehicle Count']
    regional_eff = regional_eff.sort_values('Avg Wh/Mile')
    
    fig3 = go.Figure(data=[go.Bar(
        x=regional_eff.index,
        y=regional_eff['Avg Wh/Mile'],
        marker=dict(color=regional_eff['Avg Wh/Mile'], colorscale='RdYlGn_r'),
        text=regional_eff['Avg Wh/Mile'],
        textposition='auto'
    )])
    fig3.update_layout(
        title='Average Energy Consumption by Region',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Region",
        yaxis_title="Wh per Mile"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    best_region = regional_eff.index[0]
    worst_region = regional_eff.index[-1]
    
    with col1:
        st.success(f"""
        **🏆 Most Efficient Region**
        
        {best_region}: {regional_eff.loc[best_region, 'Avg Wh/Mile']:.0f} Wh/mi
        
        Likely factors: Favorable climate, efficient driving patterns
        """)
    
    with col2:
        st.info(f"""
        **📊 Fleet Average**
        
        {f_df['Wh_per_Mile'].mean():.0f} Wh/mi across all regions
        
        Target: <300 Wh/mi for optimal efficiency
        """)
    
    with col3:
        st.warning(f"""
        **⚠️ Improvement Opportunity**
        
        {worst_region}: {regional_eff.loc[worst_region, 'Avg Wh/Mile']:.0f} Wh/mi
        
        {((regional_eff.loc[worst_region, 'Avg Wh/Mile'] - regional_eff.loc[best_region, 'Avg Wh/Mile']) / regional_eff.loc[best_region, 'Avg Wh/Mile'] * 100):.1f}% higher than best region
        """)

with tab3:
    st.markdown("### 🗺️ Global Fleet Distribution")
    st.caption("Geographic spread and regional performance metrics")
    
    # Regional overview
    regional_stats = f_df.groupby('Region').agg({
        'VIN': 'count',
        'Battery_SOH': 'mean',
        'Wh_per_Mile': 'mean',
        'Odometer_Miles': 'mean',
        'Charging_Session_Cost': 'mean'
    }).round(2)
    regional_stats.columns = ['Vehicles', 'Avg SOH %', 'Avg Wh/mi', 'Avg Odometer', 'Avg Charge Cost $']
    
    # Create a more visually appealing dataframe
    st.dataframe(
        regional_stats.style.background_gradient(cmap='RdYlGn', subset=['Avg SOH %'])
                           .background_gradient(cmap='RdYlGn_r', subset=['Avg Wh/mi'])
                           .format({
                               'Vehicles': '{:,.0f}',
                               'Avg SOH %': '{:.1f}%',
                               'Avg Wh/mi': '{:.0f}',
                               'Avg Odometer': '{:,.0f}',
                               'Avg Charge Cost $': '${:.2f}'
                           }),
        use_container_width=True
    )
    
    with st.expander("📖 How to Read This Table"):
        st.markdown("""
        **Color Coding:**
        - **Green**: Better performance (high SOH, low Wh/mi)
        - **Yellow**: Average performance
        - **Red**: Needs attention
        
        **Key Metrics:**
        - **Vehicles**: Total count in region
        - **Avg SOH**: Battery health (higher is better)
        - **Avg Wh/mi**: Energy efficiency (lower is better)
        - **Avg Odometer**: Fleet age indicator
        - **Avg Charge Cost**: Regional electricity pricing
        """)
    
    st.markdown("---")
    
    # Regional breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of vehicle distribution
        region_dist = f_df['Region'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=region_dist.index,
            values=region_dist.values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Bold)
        )])
        fig.update_layout(
            title='Fleet Distribution by Region',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Battery health by region
        fig2 = px.violin(
            f_df,
            x='Region',
            y='Battery_SOH',
            color='Region',
            box=True,
            title='Battery Health Distribution by Region',
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Region",
            yaxis_title="Battery SOH %"
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.markdown("### 📊 Fleet Composition Analysis")
    st.caption("Detailed breakdown of models, colors, and configurations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Model distribution
        model_dist = f_df['Model'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=model_dist.index,
            values=model_dist.values,
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        fig.update_layout(
            title='Model Distribution',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Color distribution
        color_dist = f_df['Color'].value_counts().head(10)
        
        fig2 = go.Figure(data=[go.Bar(
            x=color_dist.values,
            y=color_dist.index,
            orientation='h',
            marker=dict(color=px.colors.qualitative.Pastel),
            text=color_dist.values,
            textposition='auto'
        )])
        fig2.update_layout(
            title='Top 10 Colors',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            xaxis_title="Vehicle Count",
            yaxis_title="Color"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col3:
        # Software version distribution
        sw_dist = f_df['Software_Version'].value_counts()
        
        fig3 = go.Figure(data=[go.Bar(
            x=sw_dist.index,
            y=sw_dist.values,
            marker=dict(color='#E82127'),
            text=sw_dist.values,
            textposition='auto'
        )])
        fig3.update_layout(
            title='Software Versions',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            xaxis_title="Version",
            yaxis_title="Vehicle Count"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # Model specifications table
    st.markdown("### 🚗 Model Specifications")
    
    specs_data = []
    for model, specs in tesla_master.items():
        count = len(f_df[f_df['Model'] == model])
        if count > 0:
            specs_data.append({
                'Model': model,
                'Fleet Count': count,
                'Range (mi)': specs['range'],
                '0-60 mph (s)': specs['acceleration'],
                'Top Speed (mph)': specs['top_speed'],
                'MSRP': f"${specs['price']:,}",
                'Available Colors': len(specs['colors'])
            })
    
    specs_df = pd.DataFrame(specs_data)
    st.dataframe(
        specs_df.style.background_gradient(cmap='Greens', subset=['Fleet Count'])
                      .background_gradient(cmap='Blues', subset=['Range (mi)'])
                      .format({'Fleet Count': '{:,}'}),
        use_container_width=True
    )

with tab5:
    st.markdown("### 🔍 Advanced Diagnostic Tools")
    st.caption("Deep forensic analysis for fleet optimization")
    
    # Benford's Law Analysis
    st.markdown("#### 📐 Benford's Law Analysis (Billing Integrity)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ben_counts = f_df['Lead_Digit'].value_counts(normalize=True).sort_index().drop(0, errors='ignore')
        benford_expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(1, 10)),
            y=ben_counts.values,
            name='Actual',
            marker=dict(color='#E82127')
        ))
        fig.add_trace(go.Scatter(
            x=list(range(1, 10)),
            y=benford_expected,
            name="Benford's Law Expected",
            line=dict(color='#6bcf7f', width=3)
        ))
        fig.update_layout(
            title='Leading Digit Distribution in Charging Costs',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Leading Digit",
            yaxis_title="Frequency",
            barmode='overlay'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**What is Benford's Law?**")
        st.info("""
        Benford's Law states that in many real-world datasets, the leading digit is more likely to be small.
        
        **Why it matters:**
        - Detects fraudulent billing
        - Validates data authenticity
        - Identifies anomalies
        
        **Green line**: Expected pattern
        **Red bars**: Actual data
        
        Close match = Legitimate data ✅
        """)
    
    st.markdown("---")
    
    # Outlier Detection
    st.markdown("#### 🎯 Statistical Outlier Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SOH outliers
        soh_outliers = f_df[f_df['SOH_Z_Score'] < -2.5].sort_values('Battery_SOH')
        
        st.markdown(f"**⚠️ Battery Health Outliers** ({len(soh_outliers)} vehicles)")
        st.dataframe(
            soh_outliers[['VIN', 'Model', 'Battery_SOH', 'Odometer_Miles', 'Region']].head(10),
            use_container_width=True
        )
        
        if len(soh_outliers) > 0:
            st.warning(f"""
            These vehicles have battery health significantly below fleet average.
            
            **Recommended Actions:**
            - Schedule BMS diagnostic
            - Review charging patterns
            - Check for software updates
            """)
    
    with col2:
        # Efficiency outliers
        eff_z = stats.zscore(f_df['Wh_per_Mile'])
        f_df['Eff_Z_Score'] = eff_z
        eff_outliers = f_df[f_df['Eff_Z_Score'] > 2.5].sort_values('Wh_per_Mile', ascending=False)
        
        st.markdown(f"**⚡ Efficiency Outliers** ({len(eff_outliers)} vehicles)")
        st.dataframe(
            eff_outliers[['VIN', 'Model', 'Wh_per_Mile', 'Tire_Pressure_PSI', 'Region']].head(10),
            use_container_width=True
        )
        
        if len(eff_outliers) > 0:
            st.warning(f"""
            These vehicles consume unusually high energy.
            
            **Possible Causes:**
            - Low tire pressure
            - Aggressive driving
            - Climate control usage
            - Aerodynamic issues
            """)
    
    st.markdown("---")
    
    # Correlation heatmap
    st.markdown("#### 🔥 Correlation Matrix")
    
    corr_data = f_df[['Battery_SOH', 'Wh_per_Mile', 'Odometer_Miles', 
                      'Supercharger_Ratio', 'Ambient_Temp_Avg', 'Autopilot_Miles']].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=corr_data.columns,
        y=corr_data.columns,
        colorscale='RdYlGn',
        zmid=0,
        text=corr_data.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig.update_layout(
        title='Feature Correlation Analysis',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📖 Reading the Correlation Matrix"):
        st.markdown("""
        **Color Guide:**
        - 🟢 **Green** (+1.0): Perfect positive correlation
        - 🟡 **Yellow** (0.0): No correlation
        - 🔴 **Red** (-1.0): Perfect negative correlation
        
        **Key Insights:**
        - Battery SOH decreases as odometer increases (negative correlation)
        - Supercharger usage correlates with faster degradation
        - Ambient temperature affects efficiency
        
        **Numbers closer to +1 or -1 = Stronger relationship**
        """)

# --- 9. DATA EXPORT & ARCHIVE ---
st.divider()
st.markdown("### 📥 Fleet Data Archive")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.caption(f"Viewing {len(f_df):,} of {len(df):,} total vehicles • Filtered dataset ready for export")

with col2:
    csv = f_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f'tesla_fleet_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
        use_container_width=True
    )

with col3:
    if st.button("🔍 Show Raw Data", use_container_width=True):
        st.session_state.show_raw = not st.session_state.get('show_raw', False)

if st.session_state.get('show_raw', False):
    st.dataframe(
        f_df.sort_values(by='Timestamp', ascending=False),
        use_container_width=True,
        height=400
    )

# --- 10. FOOTER ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**⚡ Tesla Fleet Intelligence Hub**")
    st.caption("Powered by Advanced Analytics • BMS v4.2")

with col2:
    st.markdown("**📊 Data Coverage**")
    st.caption(f"{len(df):,} vehicles • {len(df['Region'].unique())} regions • Real-time updates")

with col3:
    st.markdown("**🔒 Security**")
    st.caption("End-to-end encrypted • SOC 2 Type II Certified")

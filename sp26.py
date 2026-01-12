import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Saraswati Pujo '26",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar collapsed as no input needed
)

# --- AESTHETICS: GOLDEN RATIO & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY SCALE (GOLDEN RATIO 1.618) */
    .main-title {
        font-size: 4.236rem; 
        font-weight: 800;
        letter-spacing: -2px;
        background: -webkit-linear-gradient(0deg, #FF7043, #FFCA28);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }

    /* 2. KPI CARDS (Glassmorphism) */
    div[data-testid="stMetric"] {
        border-radius: 13px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 21px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-5px); }

    /* Card Colors */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(45, 212, 191, 0.15), rgba(45, 212, 191, 0.05));
        border-left: 5px solid rgba(45, 212, 191, 0.5);
    }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.15), rgba(167, 139, 250, 0.05));
        border-left: 5px solid rgba(167, 139, 250, 0.5);
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(251, 146, 60, 0.05));
        border-left: 5px solid rgba(251, 146, 60, 0.5);
    }

    /* Metrics Text */
    [data-testid="stMetricValue"] {
        font-size: 2.618rem !important;
        font-weight: 700;
        font-family: 'Source Sans Pro', sans-serif;
        color: #fff;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.8;
    }

    /* 3. SLOKA STYLING */
    .sloka {
        font-family: 'Georgia', serif;
        font-size: 0.85rem;
        font-style: italic;
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        background: rgba(255, 255, 255, 0.03);
        padding: 13px;
        border-radius: 8px;
        margin-bottom: 34px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        line-height: 1.618;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA LOADING FUNCTION ---
@st.cache_data(ttl=600) # Cache data for 10 mins to save performance
def load_data_from_excel():
    try:
        # Step A: Read Row 1 to get the Date (Metadata)
        # header=None means read row 1 as data, nrows=1 means read only the first row
        meta_df = pd.read_excel('data.xlsx', header=None, nrows=1)
        update_date = meta_df.iloc[0, 0] # Value in Cell A1

        # Step B: Read Row 2 onwards for actual Data
        # header=1 means Row 2 is the header
        df = pd.read_excel('data.xlsx', header=1)
        
        # Ensure numeric columns are actually numbers (fill NaN with 0)
        df[['2024', '2025', '2026']] = df[['2024', '2025', '2026']].fillna(0)
        
        return update_date, df
        
    except FileNotFoundError:
        st.error("⚠️ 'data.xlsx' not found in repository. Please upload it.")
        return "Unknown Date", pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error reading Excel: {e}")
        return "Error", pd.DataFrame()

# Load Data
last_updated_text, df = load_data_from_excel()

# --- 2. SIDEBAR (Purely Aesthetic now) ---
with st.sidebar:
    st.markdown("""
        <div class="sloka">
            সরস্বতী মহাভাগে বিদ্যে কমললোচনে।<br>
            বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info(f"📅 **Data Source:**\n{last_updated_text}")
    st.caption("Data is managed centrally via GitHub.")

# --- 3. MAIN DASHBOARD ---

# Check if df is empty before proceeding
if not df.empty:
    
    # Title Section
    col_h1, col_h2 = st.columns([5, 2])
    with col_h1:
        st.markdown('<div class="main-title">Saraswati Pujo 2026</div>', unsafe_allow_html=True)
    with col_h2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"IIT Bombay | {last_updated_text}")
        st.success("● System Online")

    # --- KPI CARDS ---
    total_24 = df['2024'].sum()
    total_25 = df['2025'].sum()
    total_26 = df['2026'].sum()
    growth = ((total_26 - total_25) / total_25) * 100 if total_25 > 0 else 0

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("HISTORICAL (2024)", f"₹{total_24:,.0f}")
    with k2:
        st.metric("PREVIOUS (2025)", f"₹{total_25:,.0f}")
    with k3:
        st.metric("CURRENT (2026)", f"₹{total_26:,.0f}", f"{growth:.1f}% vs 2025")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHART ---
    st.markdown("### 📊 Collection Trends")

    fig = go.Figure()

    # 2024
    fig.add_trace(go.Bar(
        x=df['Hostel'], y=df['2024'], name='2024',
        marker_color='#455A64', opacity=0.3
    ))

    # 2025
    fig.add_trace(go.Bar(
        x=df['Hostel'], y=df['2025'], name='2025',
        marker_color='#7E57C2', opacity=0.6
    ))

    # 2026
    fig.add_trace(go.Bar(
        x=df['Hostel'], y=df['2026'], name='2026',
        marker_color='#FF8F00',
        text=df['2026'].apply(lambda x: f"₹{x/1000:.1f}k" if x > 0 else ""),
        textposition='outside'
    ))

    fig.update_layout(
        barmode='group',
        height=550,
        margin=dict(t=20, b=30, l=10, r=10),
        legend=dict(
            orientation="h", y=1.02, x=1, xanchor="right",
            bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc')
        ),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False, fixedrange=True),
        xaxis=dict(showgrid=False, fixedrange=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Source Sans Pro", size=13)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- TABLE ---
    with st.expander("📝 Detailed Breakdown", expanded=False):
        st.dataframe(
            df.set_index('Hostel'),
            use_container_width=True,
            column_config={
                "2024": st.column_config.NumberColumn(format="₹%d"),
                "2025": st.column_config.NumberColumn(format="₹%d"),
                "2026": st.column_config.NumberColumn(format="₹%d")
            }
        )

st.markdown("---")
st.markdown( 
    """
    <div style='text-align: right; color: #666; font-size: 0.8rem; padding: 21px;'>
        Designed by Somdeep, with ❤️
    </div>
    """, 
    unsafe_allow_html=True
)

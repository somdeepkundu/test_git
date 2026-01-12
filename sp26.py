import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Saraswati Pujo '26",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AESTHETICS: GOLDEN RATIO & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY SCALE */
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

    /* Metric Text */
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

# --- 1. DATA LOADING FUNCTION (LIVE RAW GITHUB) ---
@st.cache_data(ttl=60) # Auto-refresh cache every 60 seconds
def load_data_from_github():
    # LINK TO RAW DATA
    # If your branch is 'main', change 'master' to 'main' below
    csv_url = "https://raw.githubusercontent.com/somdeepkundu/test_git/master/data.csv"
    
    try:
        # A. Read just the first row to get the Date (Metadata)
        meta_df = pd.read_csv(csv_url, header=None, nrows=1)
        raw_text = str(meta_df.iloc[0, 0])
        update_date = raw_text.replace("Last Updated:", "").strip() if "Last Updated" in raw_text else raw_text

        # B. Read the actual data (skip row 0 which is the date)
        df = pd.read_csv(csv_url, header=1)
        
        # Ensure numbers are treated as numbers
        cols_to_fix = ['2024', '2025', '2026']
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return update_date, df
        
    except Exception as e:
        # Return empty if failed so app doesn't crash completely
        return f"Error: {str(e)}", pd.DataFrame()

# --- 2. SIDEBAR ---
with st.sidebar:
    # LOGO: Centered, Circular, with White Background for Contrast
    st.markdown("""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
            <img src="https://lh3.googleusercontent.com/sitesv/AAzXCkeXhnG2uTGpo7OFv7aP46ax-_JBFyWuDOW9bp7QG5jgJ257fDG7RaYPZ0xPFLA8xSmYnIqgGJ1vK6rokJ9FzqeHqbLmYb6mNIjdKC13Zv93XsnpgfhfiWw9wAamMoUpyWu9K5E9H0wDbhv9zfKpS47VP0eAST5uydn2_XOXU6kqEUX-Trk7q8dQdyA=w16383" 
                 style="width: 110px; 
                        border-radius: 50%; 
                        border: 3px solid rgba(255, 112, 67, 0.6); /* Soft Orange Border */
                        padding: 4px; 
                        background-color: rgba(255, 255, 255, 1); /* White Background */
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        </div>
    """, unsafe_allow_html=True)

    # Sloka
    st.markdown("""
        <div class="sloka">
            সরস্বতী মহাভাগে বিদ্যে কমললোচনে।<br>
            বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # REFRESH BUTTON
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Load Data
    last_updated_text, df = load_data_from_github()
    
    if not df.empty:
        st.success(f"📅 **Updated:** {last_updated_text}")
    else:
        st.error("Could not load data.")
        
    st.caption("Data source: GitHub Raw")

# --- 3. MAIN DASHBOARD ---

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

    with k1: st.metric("HISTORICAL (2024)", f"₹{total_24:,.0f}")
    with k2: st.metric("PREVIOUS (2025)", f"₹{total_25:,.0f}")
    with k3: st.metric("CURRENT (2026)", f"₹{total_26:,.0f}", f"{growth:.1f}% vs 2025")

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
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc')),
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

else:
    st.warning("Please upload 'data.csv' to your GitHub repository to see the dashboard.")

st.markdown("---")
st.markdown("<div style='text-align: right; color: #666; font-size: 0.8rem; padding: 21px;'>Designed with ❤️, by Saraswati Puja 2026 Committee, IIT Powai.</div>", unsafe_allow_html=True)

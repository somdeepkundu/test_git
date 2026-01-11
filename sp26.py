import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Saraswati Pujo '26",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AESTHETICS: GOLDEN RATIO & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY SCALE (GOLDEN RATIO 1.618)
       Base: 1rem
       Lvl 1: 1.618rem (Subheaders)
       Lvl 2: 2.618rem (Metrics)
       Lvl 3: 4.236rem (Main Title)
    */
    
    /* Main Title */
    .main-title {
        font-size: 4.236rem; 
        font-weight: 800;
        letter-spacing: -2px;
        background: -webkit-linear-gradient(0deg, #FF7043, #FFCA28);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px; /* Fibonacci 21px approx */
    }

    /* 2. SEMI-TRANSPARENT COLORFUL BLOCKS (KPI CARDS) */
    div[data-testid="stMetric"] {
        border-radius: 13px; /* Fibonacci 13 */
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 21px; /* Fibonacci 21 */
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    /* Card 1: Historical (Teal/Blue Glass) */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(45, 212, 191, 0.15), rgba(45, 212, 191, 0.05));
        border-left: 5px solid rgba(45, 212, 191, 0.5);
    }

    /* Card 2: Previous (Violet/Purple Glass) */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.15), rgba(167, 139, 250, 0.05));
        border-left: 5px solid rgba(167, 139, 250, 0.5);
    }

    /* Card 3: Current (Orange/Gold Glass) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(251, 146, 60, 0.05));
        border-left: 5px solid rgba(251, 146, 60, 0.5);
    }

    /* Metric Values (Golden Ratio Lvl 2) */
    [data-testid="stMetricValue"] {
        font-size: 2.618rem !important;
        font-weight: 700;
        font-family: 'Source Sans Pro', sans-serif;
        color: #fff;
    }

    /* Metric Labels */
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.8;
    }

    /* 3. SLOKA STYLING (Smaller & Elegant) */
    .sloka {
        font-family: 'Georgia', serif;
        font-size: 0.85rem; /* Smaller size */
        font-style: italic;
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        background: rgba(255, 255, 255, 0.03);
        padding: 13px; /* Fibonacci */
        border-radius: 8px; /* Fibonacci */
        margin-bottom: 34px; /* Fibonacci */
        border: 1px solid rgba(255, 255, 255, 0.05);
        line-height: 1.618; /* Golden Ratio Line Height */
    }

    /* Sidebar Input Styling */
    .stNumberInput input {
        background-color: rgba(255,255,255,0.05);
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA INITIALIZATION ---
historical_data = {
    'H1':       {'2024': 10000, '2025': 10100},
    'H2':       {'2024': 12000, '2025': 9088},
    'H3':       {'2024': 15000, '2025': 14500},
    'H4+Tansa': {'2024': 20000, '2025': 24000}, 
    'H5':       {'2024': 12500, '2025': 13800},
    'H6':       {'2024': 10000, '2025': 12800},
    'H7':       {'2024': 15000, '2025': 0},
    'H8':       {'2024': 20000, '2025': 0},
    'H9':       {'2024': 5000,  '2025': 4000},
    'H10':      {'2024': 30000, '2025': 40000},
    'H11':      {'2024': 15000, '2025': 15600},
    'H12':      {'2024': 80000, '2025': 82000},
    'H13':      {'2024': 35000, '2025': 37800},
    'H14':      {'2024': 30000, '2025': 30000},
    'H15':      {'2024': 25000, '2025': 28800},
    'H16':      {'2024': 10000, '2025': 7550},
    'H17':      {'2024': 40000, '2025': 41000},
    'H18':      {'2024': 60000, '2025': 67500},
    'H21':      {'2024': 0,     '2025': 0},    
}

hostel_list = list(historical_data.keys())

# --- STATE MANAGEMENT ---
if 'collections_2026' not in st.session_state:
    st.session_state['collections_2026'] = {h: 0 for h in hostel_list}
else:
    for h in hostel_list:
        if h not in st.session_state['collections_2026']:
            st.session_state['collections_2026'][h] = 0

# --- 2. SIDEBAR ---
with st.sidebar:
    # Sloka (Styled with CSS class .sloka)
    st.markdown("""
        <div class="sloka">
            সরস্বতী মহাভাগে বিদ্যে কমললোচনে।<br>
            বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।
        </div>
    """, unsafe_allow_html=True)
    
    st.header("📝 Data Entry")
    search_query = st.text_input("🔍 Search Hostel", placeholder="Eg. H14...").upper()
    
    st.markdown("---")
    
    # Input Container
    with st.container(height=500, border=False):
        for hostel in hostel_list:
            if search_query in hostel.upper() or search_query == "":
                
                # Input Field
                val = st.number_input(
                    f"{hostel}",
                    min_value=0,
                    value=st.session_state['collections_2026'][hostel],
                    step=500,
                    key=f"input_{hostel}"
                )
                st.session_state['collections_2026'][hostel] = val
                
                # Minimal History Text
                prev = historical_data[hostel]['2025']
                hist_text = f"Prev: ₹{prev:,}" if prev > 0 else "New"
                st.markdown(f"<div style='text-align: right; font-size: 0.75rem; color: #888; margin-top: -8px; margin-bottom: 13px;'>{hist_text}</div>", unsafe_allow_html=True)

# --- 3. DATAFRAME PREP ---
rows = []
for h in hostel_list:
    rows.append({
        'Hostel': h,
        '2024': historical_data[h]['2024'],
        '2025': historical_data[h]['2025'],
        '2026 (Live)': st.session_state['collections_2026'][h]
    })
df = pd.DataFrame(rows)

# --- 4. MAIN DASHBOARD ---

# Title Section with Gradient Class
col_h1, col_h2 = st.columns([5, 2])
with col_h1:
    st.markdown('<div class="main-title">Saraswati Pujo 2026</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"IIT Bombay | Live Dashboard | {pd.Timestamp.now().strftime('%d %B %Y')}")
    st.success("● Live System Active")

# --- KPI CARDS (Semi-Transparent Blocks) ---
total_24 = df['2024'].sum()
total_25 = df['2025'].sum()
total_26 = df['2026 (Live)'].sum()
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

# 2024 (Background, Context)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2024'], name='2024',
    marker_color='#455A64', # Blue Grey
    opacity=0.3
))

# 2025 (Reference)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2025'], name='2025',
    marker_color='#7E57C2', # Deep Purple
    opacity=0.6
))

# 2026 (Focus - Golden/Orange)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2026 (Live)'], name='2026',
    marker_color='#FF8F00', # Amber 800
    text=df['2026 (Live)'].apply(lambda x: f"₹{x/1000:.1f}k" if x > 0 else ""),
    textposition='outside'
))

fig.update_layout(
    barmode='group',
    height=550, # Fibonacci 55 * 10
    margin=dict(t=20, b=30, l=10, r=10),
    legend=dict(
        orientation="h", y=1.02, x=1, xanchor="right",
        bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc')
    ),
    yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False),
    xaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Source Sans Pro", size=13)
)

st.plotly_chart(fig, use_container_width=True)

# --- TABLE ---
with st.expander("📝 Detailed Breakdown", expanded=False):
    st.dataframe(
        df.set_index('Hostel'),
        use_container_width=True,
        column_config={
            "2024": st.column_config.NumberColumn(format="₹%d"),
            "2025": st.column_config.NumberColumn(format="₹%d"),
            "2026 (Live)": st.column_config.NumberColumn(format="₹%d")
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

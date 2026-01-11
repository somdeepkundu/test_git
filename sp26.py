import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Saraswati Puja '26",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR AESTHETICS ---
# This injects custom styling to make metrics and headers look premium
st.markdown("""
    <style>
    /* Main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Styled Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #262730; /* Dark card background */
        border: 1px solid #41444e;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        border-color: #FF7043; /* Orange glow on hover */
    }
    
    /* Metric Value Text Size */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Custom Title Gradient */
    .gradient-text {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #FF7043, #ffb74d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0px;
    }
    
    /* Sanskrit Sloka Styling */
    .sloka {
        font-family: 'Georgia', serif;
        font-style: italic;
        text-align: center;
        color: #B0BEC5;
        background-color: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 3px solid #FF7043;
    }
    
    /* Footer Styling */
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        width: 100%;
        background-color: transparent;
        color: #888;
        text-align: right;
        padding: 10px 30px;
        font-size: 0.8rem;
        z-index: 100;
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

# --- ROBUST STATE MANAGEMENT ---
if 'collections_2026' not in st.session_state:
    st.session_state['collections_2026'] = {h: 0 for h in hostel_list}
else:
    for h in hostel_list:
        if h not in st.session_state['collections_2026']:
            st.session_state['collections_2026'][h] = 0

# --- 2. SIDEBAR - DATA ENTRY ---
with st.sidebar:
    # Aesthetic Sloka Display
    st.markdown("""
        <div class="sloka">
            সরস্বতী মহাভাগে বিদ্যে কমললোচনে।<br>
            বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।
        </div>
    """, unsafe_allow_html=True)
    
    st.header("📝 Data Entry")
    st.caption("Update **2026 Collection** below.")
    
    search_query = st.text_input("🔍 Search Hostel", placeholder="Type H1, H12...").upper()
    
    st.markdown("---")
    
    with st.container(height=500, border=False):
        for hostel in hostel_list:
            if search_query in hostel.upper() or search_query == "":
                # Cleaner layout for inputs
                val = st.number_input(
                    f"{hostel}",
                    min_value=0,
                    value=st.session_state['collections_2026'][hostel],
                    step=500,
                    key=f"input_{hostel}"
                )
                
                st.session_state['collections_2026'][hostel] = val
                
                # Subtle history text
                prev_val = historical_data[hostel]['2025']
                if prev_val > 0:
                    st.markdown(f"<div style='text-align: right; color: #666; font-size: 0.8em; margin-top: -10px; margin-bottom: 10px;'>Previous: ₹{prev_val:,}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: right; color: #666; font-size: 0.8em; margin-top: -10px; margin-bottom: 10px;'>No history</div>", unsafe_allow_html=True)

# --- 3. PREPARE DATAFRAME ---
rows = []
for h in hostel_list:
    rows.append({
        'Hostel': h,
        '2024': historical_data[h]['2024'],
        '2025': historical_data[h]['2025'],
        '2026 (Live)': st.session_state['collections_2026'][h]
    })
df = pd.DataFrame(rows)

# --- 4. MAIN DASHBOARD UI ---

# Custom Header
col_head_1, col_head_2 = st.columns([4, 1])
with col_head_1:
    st.markdown('<h1 class="gradient-text">Saraswati Puja 2026</h1>', unsafe_allow_html=True)
    st.caption(f"IIT Bombay | Live Dashboard | {pd.Timestamp.now().strftime('%d %B %Y')}")
with col_head_2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Live Updates Active")

st.markdown("---")

# --- KPI Section (Now styled by CSS) ---
total_24 = df['2024'].sum()
total_25 = df['2025'].sum()
total_26 = df['2026 (Live)'].sum()
growth = ((total_26 - total_25) / total_25) * 100 if total_25 > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

# Note: The CSS above automatically targets these st.metric calls
with kpi1:
    st.metric(label="HISTORICAL (2024)", value=f"₹{total_24:,.0f}", delta=None)
with kpi2:
    st.metric(label="LAST YEAR (2025)", value=f"₹{total_25:,.0f}", delta=None)
with kpi3:
    st.metric(
        label="CURRENT COLLECTION (2026)", 
        value=f"₹{total_26:,.0f}", 
        delta=f"{growth:.1f}% vs 2025"
    )

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- Interactive Chart (Polished) ---
st.subheader("📊 Collection Trends")

fig = go.Figure()

# 2024: Subtle Background
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2024'], name='2024',
    marker_color='#546E7A', # Blue Grey 600
    opacity=0.4,
    hovertemplate='<b>%{x}</b><br>2024: ₹%{y:,}<extra></extra>'
))

# 2025: Cool Tone
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2025'], name='2025',
    marker_color='#7986CB', # Indigo 300
    opacity=0.8,
    hovertemplate='<b>%{x}</b><br>2025: ₹%{y:,}<extra></extra>'
))

# 2026: Vibrant Hero Color
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2026 (Live)'], name='2026',
    marker_color='#FF7043', # Deep Orange 400
    text=df['2026 (Live)'].apply(lambda x: f"₹{x/1000:.1f}k" if x > 0 else ""),
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>2026: ₹%{y:,}<extra></extra>'
))

fig.update_layout(
    barmode='group',
    height=500,
    margin=dict(t=20, b=40, l=20, r=20),
    legend=dict(
        orientation="h", y=1.05, x=1, xanchor="right",
        bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='rgba(255, 255, 255, 0.08)', # Very subtle grid
        gridwidth=1,
        zeroline=False
    ),
    xaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)', # Transparent background
    font=dict(family="Source Sans Pro", size=14)
)

st.plotly_chart(fig, use_container_width=True)

# --- Detailed Table ---
with st.expander("📝 View Detailed Breakdown", expanded=False):
    st.dataframe(
        df.set_index('Hostel'),
        use_container_width=True,
        column_config={
            "2024": st.column_config.NumberColumn(format="₹%d"),
            "2025": st.column_config.NumberColumn(format="₹%d"),
            "2026 (Live)": st.column_config.NumberColumn(format="₹%d")
        }
    )

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: right; color: #888888; font-family: monospace; padding-bottom: 20px;'>
        Made by Somdeep, with ❤️
    </div>
    """, 
    unsafe_allow_html=True
)

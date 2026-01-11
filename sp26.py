import streamlit as st
import pandas as pd 
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Saraswati Puja '26 - Hostel wise collection",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Custom CSS for Polish ---
st.markdown("""
<style>
    /* Reduce padding on the main content area for a tighter layout */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Style for the Hindi/Bengali prayer text in sidebar */
    .prayer-text {
        font-size: 14px;
        margin-bottom: 0px;
        opacity: 0.8; /* Slightly faded for less prominence */
    }
    /* Adjustments for the specific KPI cards to ensure consistent height */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
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

# --- ROBUST STATE MANAGEMENT (Fixes KeyError) ---
if 'collections_2026' not in st.session_state:
    st.session_state['collections_2026'] = {h: 0 for h in hostel_list}
else:
    # Ensure all keys exist (handles updates/merges)
    for h in hostel_list:
        if h not in st.session_state['collections_2026']:
            st.session_state['collections_2026'][h] = 0

# --- 2. SIDEBAR - DATA ENTRY ---
with st.sidebar:
    st.markdown('<p class="prayer-text">সরস্বতী মহাভাগে বিদ্যে কমললোচনে।</p>', unsafe_allow_html=True)
    st.markdown('<p class="prayer-text">বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।</p>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.header("📝 Data Entry")
    st.markdown("Update **2026 Collection** below.")
    
    search_query = st.text_input("🔍 Search Hostel", placeholder="e.g. H14").upper()
    
    st.markdown("---")
    
    with st.container(height=600, border=False):
        for hostel in hostel_list:
            if search_query in hostel.upper() or search_query == "":
                
                # Use a cleaner layout in the sidebar
                val = st.number_input(
                    f"{hostel}",
                    min_value=0,
                    value=st.session_state['collections_2026'][hostel],
                    step=500,
                    key=f"input_{hostel}",
                    label_visibility="collapsed" # Hide the label, use markdown below
                )
                
                # Display hostel name and previous value cleanly
                st.markdown(f"**{hostel}**")
                st.session_state['collections_2026'][hostel] = val
                
                prev_val = historical_data[hostel]['2025']
                if prev_val > 0:
                    st.caption(f"Last Year: ₹{prev_val:,}")
                else:
                    st.caption("No history")
                
                st.markdown("") 

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
col_head_1, col_head_2 = st.columns([6, 1], gap="small")
with col_head_1:
    st.title("Saraswati Puja 2026 🛕")
    st.markdown(f"**Live Dashboard** | *{pd.Timestamp.now().strftime('%d %b %Y')}*")
with col_head_2:
    st.write("") # Add some vertical spacing
    st.markdown('<span style="color: green; font-weight: bold;">● Live</span>', unsafe_allow_html=True)


st.markdown("---")

# --- KPI Section ---
total_24 = df['2024'].sum()
total_25 = df['2025'].sum()
total_26 = df['2026 (Live)'].sum()
growth = ((total_26 - total_25) / total_25) * 100 if total_25 > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

def metric_card(col, title, value, subtext=None):
    with col:
        # Use border=True for all cards for visual uniformity
        with st.container(border=True): 
            st.metric(label=title, value=value, delta=subtext)

metric_card(kpi1, "HISTORICAL (2024)", f"₹{total_24:,.0f}")
metric_card(kpi2, "PREVIOUS (2025)", f"₹{total_25:,.0f}")

# Color the delta text automatically based on value (Streamlit does this by default)
if growth >= 0:
    delta_color = "normal"
else:
    delta_color = "inverse"

kpi3.metric(label="CURRENT (2026)", value=f"₹{total_26:,.0f}", delta=f"{growth:.1f}% vs 2025", delta_color=delta_color)


# --- Interactive Chart (Aesthetic Palette) ---
st.markdown("### 📊 3-Year Comparison")

fig = go.Figure()

# 2024: Soft Grey/Blue (Background context) - Using a slightly richer grey
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2024'], name='2024',
    marker_color='#78909C', # Richer Blue Grey
    opacity=0.7
))

# 2025: Cool Indigo (Recent history) - Brighter Indigo
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2025'], name='2025',
    marker_color='#5C6BC0', 
    opacity=0.9
))

# 2026: Vibrant Coral/Orange (Live & Active) - The accent color
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2026 (Live)'], name='2026',
    marker_color='#FF5722', # Deeper Orange
    text=df['2026 (Live)'].apply(lambda x: f"₹{x/1000:.1f}k" if x > 0 else ""),
    textposition='outside'
))

fig.update_layout(
    barmode='group',
    height=550,
    # Cleaned up margins
    margin=dict(t=40, b=40, l=40, r=40), 
    legend=dict(
        orientation="h", y=1.05, x=1, xanchor="right",
        bgcolor='rgba(0,0,0,0)'
    ),
    # Let Streamlit handle bgcolor/plot_bgcolor when in dark mode
    yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)', title="Collection (₹)"),
    xaxis=dict(title="Hostel"),
    # Add minor title padding
    title_pad=dict(t=20)
)

st.plotly_chart(fig, use_container_width=True)

# --- Detailed Table ---
with st.expander("View Detailed Breakdown", expanded=False): # Set expanded=False by default for cleaner dashboard
    st.dataframe(
        df.set_index('Hostel'),
        use_container_width=True,
        column_config={
            "2024": st.column_config.NumberColumn(format="₹%d"),
            "2025": st.column_config.NumberColumn(format="₹%d"),
            "2026 (Live)": st.column_config.NumberColumn(format="₹%d")
        }
    )


st.markdown(
    """
    <div style='text-align: right; color: #888888; padding-top: 20px; font-size: 0.8rem;'>
        Made by Somdeep, with ❤️
    </div>
    """, 
    unsafe_allow_html=True
)

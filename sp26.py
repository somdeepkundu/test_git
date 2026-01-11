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
    st.markdown("সরস্বতী মহাভাগে বিদ্যে কমললোচনে। ")
    st.markdown("বিশ্বরূপে বিশালাক্ষি বিদ্যাং দেহি নমোহস্তু তে।।")
    st.header("📝 Data Entry")
    st.markdown("Update **2026 Collection** below.")
    
    search_query = st.text_input("🔍 Search Hostel", placeholder="e.g. H14").upper()
    
    st.markdown("---")
    
    with st.container(height=600, border=False):
        for hostel in hostel_list:
            if search_query in hostel.upper() or search_query == "":
                
                # Visual grouping
                c1, c2 = st.columns([1, 2])
                
                val = st.number_input(
                    f"{hostel}",
                    min_value=0,
                    value=st.session_state['collections_2026'][hostel],
                    step=500,
                    key=f"input_{hostel}"
                )
                
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
    st.title("Saraswati Puja 2026")
    st.caption(f"Live Dashboard | {pd.Timestamp.now().strftime('%d %b %Y')}")
with col_head_2:
    st.write("")
    st.success("● Live")

st.markdown("---")

# --- KPI Section ---
total_24 = df['2024'].sum()
total_25 = df['2025'].sum()
total_26 = df['2026 (Live)'].sum()
growth = ((total_26 - total_25) / total_25) * 100 if total_25 > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

def metric_card(col, title, value, subtext=None):
    with col:
        with st.container(border=True):
            st.metric(label=title, value=value, delta=subtext)

metric_card(kpi1, "HISTORICAL (2024)", f"₹{total_24:,.0f}")
metric_card(kpi2, "PREVIOUS (2025)", f"₹{total_25:,.0f}")
metric_card(kpi3, "CURRENT (2026)", f"₹{total_26:,.0f}", f"{growth:.1f}% vs 2025")

# --- Interactive Chart (Aesthetic Palette) ---
st.markdown("### 📊 3-Year Comparison")

fig = go.Figure()

# 2024: Soft Grey/Blue (Background context)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2024'], name='2024',
    marker_color='#90A4AE', # Blue Grey
    opacity=0.6
))

# 2025: Cool Indigo (Recent history)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2025'], name='2025',
    marker_color='#5C6BC0', # Indigo
    opacity=0.8
))

# 2026: Vibrant Coral/Orange (Live & Active)
fig.add_trace(go.Bar(
    x=df['Hostel'], y=df['2026 (Live)'], name='2026',
    marker_color='#FF7043', # Deep Coral/Orange
    text=df['2026 (Live)'].apply(lambda x: f"₹{x/1000:.1f}k" if x > 0 else ""),
    textposition='outside'
))

fig.update_layout(
    barmode='group',
    height=550,
    margin=dict(t=30, b=30, l=20, r=20),
    legend=dict(
        orientation="h", y=1.1, x=1, xanchor="right",
        bgcolor='rgba(0,0,0,0)'
    ),
    yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)'),
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Hostel",
    yaxis_title="Collection (₹)"
)

st.plotly_chart(fig, use_container_width=True)

# --- Detailed Table ---
with st.expander("View Detailed Breakdown", expanded=True):
    st.dataframe(
        df.set_index('Hostel'),
        use_container_width=True,
        column_config={
            "2024": st.column_config.NumberColumn(format="₹%d"),
            "2025": st.column_config.NumberColumn(format="₹%d"),
            "2026 (Live)": st.column_config.NumberColumn(format="₹%d")
        }
    )


#st.markdown("---")
st.markdown(
    """
    <div style='text-align: right; color: #888888; padding: 20px;'>
        Made by Somdeep, with ❤️
    </div>
    """, 
    unsafe_allow_html=True
)

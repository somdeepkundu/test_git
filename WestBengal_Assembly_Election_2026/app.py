import streamlit as st
import pandas as pd
import requests, re, json
import xml.etree.ElementTree as ET
import folium
from streamlit_folium import st_folium

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WB Election 2026",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for better aesthetics ──────────────────────────────────────────
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e0e0e0;
    }
    
    /* Title styling */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
    }
    
    h1 {
        color: #1a1f3a;
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        font-size: 1.5rem !important;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #FF9800;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #e0e0e0;
        font-size: 1.1rem !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #FF9800;
    }
    
    /* Selectbox styling */
    [data-testid="stSelectbox"] {
        background: #fff !important;
    }
    
    /* Button styling */
    button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Expander styling */
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: white;
    }
    
    /* Caption and small text */
    small, .caption {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Markdown links */
    a {
        color: #FF9800;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s;
    }
    
    a:hover {
        color: #FFA726;
    }
    
    [data-testid="stSidebar"] a {
        color: #FFA726;
    }
    
    [data-testid="stSidebar"] a:hover {
        color: #FFB74D;
    }
    
    /* Logo container */
    .logo-container {
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(255,152,0,0.3);
    }
    
    /* District info box */
    .district-info {
        background: linear-gradient(135deg, rgba(255,152,0,0.1) 0%, rgba(26,31,58,0.05) 100%);
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* Responsive for mobile */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.2rem !important;
        }
        [data-testid="metric-container"] {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
REPO    = "https://raw.githubusercontent.com/somdeepkundu/test_git/master/WestBengal_Assembly_Election_2026"
CSV_URL = REPO + "/election_data.csv"
KML_URL = REPO + "/wb_acs_map.kml"

PARTY_COLORS = {
    "BJP":    "#FF9800",
    "AITC":   "#1E88E5",
    "INC":    "#4CAF50",
    "CPI(M)": "#D32F2F",
    "AISF":   "#9C27B0",
    "AJU":    "#FFC107",
    "Other":  "#757575",
}

PARTY_ABBREV = {
    "Bharatiya Janata Party":             "BJP",
    "All India Trinamool Congress":       "AITC",
    "Indian National Congress":           "INC",
    "Communist Party of India (Marxist)": "CPI(M)",
    "All India Secular Front":            "AISF",
    "Aam Janata Unnayan party":           "AJU",
}

WB_BOUNDS  = [[85.8, 21.4], [89.9, 27.3]]
WB_CENTER  = [23.4, 87.9]
MIN_ZOOM   = 7
MAX_ZOOM   = 12

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching data from GitHub...")
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Margin"]       = pd.to_numeric(df["Margin"],     errors="coerce")
    df["Const. No."]   = pd.to_numeric(df["Const. No."], errors="coerce")
    df["Constituency"] = df["Constituency"].str.strip()
    df["Party"]        = df["Leading Party"].map(PARTY_ABBREV).fillna("Other")

    def margin_cat(m):
        if pd.isna(m): return "Unknown"
        if m <  1000:  return "Extremely Close (<1K)"
        if m <  5000:  return "Very Close (1-5K)"
        if m < 10000:  return "Close (5-10K)"
        if m < 30000:  return "Comfortable (10-30K)"
        return         "Landslide (>30K)"

    df["Margin_Cat"] = df["Margin"].apply(margin_cat)
    return df

@st.cache_data(show_spinner="Parsing KML boundaries...")
def load_geojson():
    r = requests.get(KML_URL, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns   = {"kml": "http://www.opengis.net/kml/2.2"}
    features = []
    for pm in root.findall(".//kml:Placemark", ns):
        try:
            props = {}
            sd = pm.find(".//kml:SchemaData", ns)
            if sd is not None:
                for item in sd.findall(".//kml:SimpleData", ns):
                    props[item.get("name")] = item.text
            ce = pm.find(".//kml:coordinates", ns)
            if ce is None or not ce.text:
                continue
            coords = []
            for c in ce.text.strip().split():
                p = c.split(",")
                if len(p) >= 2:
                    coords.append([float(p[0]), float(p[1])])
            if len(coords) < 3:
                continue
            features.append({
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Polygon", "coordinates": [coords]},
            })
        except Exception:
            pass
    return {"type": "FeatureCollection", "features": features}

def clean(s):
    return re.sub(r"\s*\(SC\)|\s*\(ST\)", "", str(s)).strip().upper()

def district_bounds(geojson):
    bounds = {}
    for f in geojson["features"]:
        dist = f["properties"].get("dist_name", "Unknown")
        coords = f["geometry"]["coordinates"][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        if dist not in bounds:
            bounds[dist] = [min(lats), min(lons), max(lats), max(lons)]
        else:
            b = bounds[dist]
            bounds[dist] = [
                min(b[0], min(lats)), min(b[1], min(lons)),
                max(b[2], max(lats)), max(b[3], max(lons))
            ]
    return {d: [[v[0], v[1]], [v[2], v[3]]] for d, v in bounds.items()}

# ── Build Folium map ──────────────────────────────────────────────────────────
def build_map(df, geojson, district_filter="All Districts", dist_bbox=None):
    lookup = {clean(r["Constituency"]): r for _, r in df.iterrows()}

    dist_acs = {}
    for f in geojson["features"]:
        ac   = f["properties"].get("ac_name", "")
        dist = f["properties"].get("dist_name", "Unknown")
        dist_acs.setdefault(dist, set()).add(clean(ac))

    allowed = dist_acs.get(district_filter) if district_filter != "All Districts" else None

    if district_filter != "All Districts" and dist_bbox:
        start_location = [
            (dist_bbox[0][0] + dist_bbox[1][0]) / 2,
            (dist_bbox[0][1] + dist_bbox[1][1]) / 2,
        ]
        start_zoom = 10
    else:
        start_location = WB_CENTER
        start_zoom = 8

    m = folium.Map(
        location=start_location,
        zoom_start=start_zoom,
        tiles="CartoDB positron",
        prefer_canvas=True,
        min_zoom=MIN_ZOOM,
        max_zoom=MAX_ZOOM,
    )

    if district_filter != "All Districts" and dist_bbox:
        m.fit_bounds(dist_bbox)
    else:
        m.fit_bounds([
            [WB_BOUNDS[0][1], WB_BOUNDS[0][0]],
            [WB_BOUNDS[1][1], WB_BOUNDS[1][0]],
        ])

    m.options["maxBounds"] = [
        [WB_BOUNDS[0][1] - 0.5, WB_BOUNDS[0][0] - 0.5],
        [WB_BOUNDS[1][1] + 0.5, WB_BOUNDS[1][0] + 0.5],
    ]

    for feature in geojson["features"]:
        ac_raw  = feature["properties"].get("ac_name", "")
        ac_key  = clean(ac_raw)
        dist    = feature["properties"].get("dist_name", "Unknown")

        if allowed is not None and ac_key not in allowed:
            continue

        row    = lookup.get(ac_key)
        color  = PARTY_COLORS.get(row["Party"] if row is not None else "Other", "#CCCCCC") \
                 if row is not None else "#CCCCCC"
        margin_str = f"{int(row['Margin']):,}" \
                     if row is not None and pd.notna(row["Margin"]) else "N/A"

        if row is not None:
            popup_html = f"""
            <div style='font-family:Arial,sans-serif;font-size:13px;
                        line-height:1.75;min-width:230px;max-width:290px'>
              <div style='background:{color};color:white;padding:7px 11px;
                          border-radius:6px 6px 0 0;font-weight:700;font-size:14px;
                          display:flex;justify-content:space-between;align-items:center'>
                <span>{row['Constituency']}</span>
                <span style='font-size:11px;opacity:.9;font-weight:600'>{row['Party']}</span>
              </div>
              <div style='padding:9px 11px;border:1px solid #ddd;
                          border-top:none;border-radius:0 0 6px 6px;background:#fff'>
                <div style='margin-bottom:3px'><b>Winner</b>: {str(row['Leading Candidate']).title()}</div>
                <div style='margin-bottom:3px'><b>Runner-up</b>: {str(row['Trailing Candidate']).title()}</div>
                <div style='margin-bottom:3px'><b>Margin</b>: {margin_str} votes</div>
                <div style='margin-bottom:3px'><b>Category</b>: {row['Margin_Cat']}</div>
                <div style='margin-bottom:3px'><b>District</b>: {dist}</div>
                <div><b>Status</b>:
                  <span style='background:#e8f5e9;color:#2e7d32;padding:1px 6px;
                               border-radius:3px;font-size:11px;font-weight:600'>{row['Status']}</span>
                </div>
              </div>
            </div>"""
        else:
            popup_html = f"<b>{ac_raw}</b><br><i>No election data</i>"

        tooltip_text = ac_raw if row is None \
                       else f"{row['Constituency']} — {row['Party']} (+{margin_str})"

        folium.GeoJson(
            feature,
            style_function=lambda x, c=color: {
                "fillColor": c, "color": "#555", "weight": 0.7, "fillOpacity": 0.75
            },
            highlight_function=lambda x: {
                "weight": 2.5, "color": "#000", "fillOpacity": 0.92
            },
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_text, sticky=False),
        ).add_to(m)

    seat_counts = df["Party"].value_counts().to_dict()
    legend_rows = "".join(
        f"""<div style='display:flex;align-items:center;margin-bottom:6px'>
              <div style='width:14px;height:14px;min-width:14px;background:{col};
                          border-radius:3px;margin-right:9px'></div>
              <span style='font-size:12px;color:#111;font-family:Arial,sans-serif'>
                <b>{p}</b> ({seat_counts.get(p, 0)})
              </span>
            </div>"""
        for p, col in PARTY_COLORS.items() if p != "Other"
    )
    legend_html = f"""
    <div style='position:fixed;bottom:40px;right:40px;z-index:9999;
                background:#ffffff;padding:14px 18px;border-radius:10px;
                border:1px solid #ccc;box-shadow:0 2px 10px rgba(0,0,0,0.25);
                font-family:Arial,sans-serif'>
      <div style='font-size:13px;font-weight:700;color:#111;margin-bottom:10px'>
        Winning Party
      </div>
      {legend_rows}
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar(df, geojson, dist_bbox_map):
    # Logo
    st.sidebar.markdown("""
    <div class='logo-container'>
        <h1 style='color: #FFB74D; font-size: 1.8rem; margin: 0;'>🗳️</h1>
        <h2 style='color: #e0e0e0; font-size: 1.4rem; margin: 0.3rem 0;'>WB Election</h2>
        <p style='color: #FF9800; font-size: 1rem; margin: 0; font-weight: 600;'>2026</p>
    </div>
    """, unsafe_allow_html=True)

    districts = sorted({
        f["properties"].get("dist_name", "Unknown")
        for f in geojson["features"]
        if f["properties"].get("dist_name")
    })
    
    st.sidebar.markdown("### Filter by District")
    dist_choice = st.sidebar.selectbox(
        "Select District:",
        ["All Districts"] + districts,
        help="Zoom into a single district",
        label_visibility="collapsed"
    )

    # District detail panel
    if dist_choice != "All Districts":
        dist_map_lookup = {
            clean(f["properties"].get("ac_name", "")): f["properties"].get("dist_name", "")
            for f in geojson["features"]
        }
        ddf = df.copy()
        ddf["District"] = ddf["Constituency"].apply(
            lambda x: dist_map_lookup.get(clean(x), "Unknown")
        )
        ddf = ddf[ddf["District"] == dist_choice]

        st.sidebar.markdown(f"""
        <div class='district-info'>
            <h3 style='margin: 0 0 0.5rem 0;'>{dist_choice}</h3>
            <p style='margin: 0; color: #FFB74D; font-weight: 600;'>{len(ddf)} constituencies</p>
        </div>
        """, unsafe_allow_html=True)

        d_seats = ddf["Party"].value_counts()
        for party, n in d_seats.items():
            col = PARTY_COLORS.get(party, "#757575")
            st.sidebar.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
                f"<div style='width:10px;height:10px;background:{col};"
                f"border-radius:50%;flex-shrink:0'></div>"
                f"<span style='font-size:13px;color:#e0e0e0'><b>{party}</b> — {n}</span></div>",
                unsafe_allow_html=True
            )

        st.sidebar.markdown("**Closest race:**")
        closest = ddf.nsmallest(1, "Margin").iloc[0]
        st.sidebar.caption(
            f"**{closest['Constituency']}** — {int(closest['Margin']):,} votes"
        )

        st.sidebar.markdown("**Biggest win:**")
        biggest = ddf.nlargest(1, "Margin").iloc[0]
        st.sidebar.caption(
            f"**{biggest['Constituency']}** — {int(biggest['Margin']):,} votes"
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### State Summary")
    seats = df["Party"].value_counts()
    total = len(df)
    for party, col in PARTY_COLORS.items():
        if party == "Other":
            continue
        n = seats.get(party, 0)
        if n == 0:
            continue
        pct = n / total * 100
        st.sidebar.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
            f"<div style='width:10px;height:10px;background:{col};"
            f"border-radius:50%;flex-shrink:0'></div>"
            f"<span style='font-size:13px;color:#e0e0e0'><b>{party}</b> {n} "
            f"<span style='color:#999'>({pct:.1f}%)</span></span></div>",
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Last Updated**\n
    04:00 AM On 05/05/2026
    
    **App developed by**\n
    [Somdeep Kundu](https://www.somdeepkundu.in)\n
    RuDRA Lab, C-TARA, IIT Bombay
    
    **Data Source**\n
    [Election Commission of India](https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S25.htm)
    """)

    return dist_choice

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df        = load_data()
    geojson   = load_geojson()
    bbox_map  = district_bounds(geojson)

    dist_choice = sidebar(df, geojson, bbox_map)
    dist_bbox   = bbox_map.get(dist_choice) if dist_choice != "All Districts" else None

    # Header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1>West Bengal Assembly Election 2026</h1>
        <p style='font-size: 1.1rem; color: #666; margin: 0;'>
            Interactive constituency results with detailed analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    seats = df["Party"].value_counts()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Constituencies", len(df), delta=None)
    with col2:
        st.metric("BJP", seats.get("BJP", 0), delta=f"{seats.get('BJP',0)/len(df)*100:.1f}%")
    with col3:
        st.metric("AITC", seats.get("AITC", 0), delta=f"{seats.get('AITC',0)/len(df)*100:.1f}%")
    with col4:
        other_count = len(df) - seats.get("BJP", 0) - seats.get("AITC", 0)
        st.metric("Others", other_count, delta=f"{other_count/len(df)*100:.1f}%")

    st.markdown("---")

    # Map
    with st.spinner("Rendering interactive map..."):
        m = build_map(df, geojson, district_filter=dist_choice, dist_bbox=dist_bbox)

    st_folium(m, width="100%", height=640, returned_objects=[])

    st.caption(
        "💡 **Hover** for quick info · **Click/Tap** for full details · "
        f"Zoom locked {MIN_ZOOM}–{MAX_ZOOM}"
    )

    # Results table
    if dist_choice != "All Districts":
        dist_map2 = {
            clean(f["properties"].get("ac_name", "")): f["properties"].get("dist_name", "")
            for f in geojson["features"]
        }
        show_df = df.copy()
        show_df["District"] = show_df["Constituency"].apply(
            lambda x: dist_map2.get(clean(x), "Unknown")
        )
        show_df = show_df[show_df["District"] == dist_choice][
            ["Constituency", "Party", "Leading Candidate",
             "Trailing Candidate", "Margin", "Margin_Cat", "Status"]
        ].sort_values("Margin", ascending=False).reset_index(drop=True)

        with st.expander(f"📋 Full Results — {dist_choice} ({len(show_df)} seats)", expanded=False):
            st.dataframe(show_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()

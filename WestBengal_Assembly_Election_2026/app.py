import streamlit as st
import pandas as pd
import requests, re, json
import xml.etree.ElementTree as ET
import folium
from streamlit_folium import st_folium

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WB Election 2026",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Constants ─────────────────────────────────────────────────────────────────
REPO = "https://raw.githubusercontent.com/somdeepkundu/test_git/master/WestBengal_Assembly_Election_2026"
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

# West Bengal bounding box
WB_BOUNDS = [[85.8, 21.4], [89.9, 27.3]]   # [[lon_min,lat_min],[lon_max,lat_max]]
WB_CENTER = [23.4, 87.9]
MIN_ZOOM, MAX_ZOOM = 7, 12

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching data from GitHub…")
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Margin"]     = pd.to_numeric(df["Margin"],     errors="coerce")
    df["Const. No."] = pd.to_numeric(df["Const. No."], errors="coerce")
    df["Constituency"] = df["Constituency"].str.strip()
    df["Party"] = df["Leading Party"].map(PARTY_ABBREV).fillna("Other")

    def margin_cat(m):
        if pd.isna(m):  return "Unknown"
        if m <  1000:   return "🔴 Extremely Close  (<1K)"
        if m <  5000:   return "🟠 Very Close  (1–5K)"
        if m < 10000:   return "🟡 Close  (5–10K)"
        if m < 30000:   return "🟢 Comfortable  (10–30K)"
        return          "💪 Landslide  (>30K)"

    df["Margin_Cat"] = df["Margin"].apply(margin_cat)
    return df

@st.cache_data(show_spinner="Parsing KML boundaries…")
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

# ── Build Folium map ──────────────────────────────────────────────────────────
def build_map(df, geojson, district_filter="All Districts"):
    lookup = {clean(r["Constituency"]): r for _, r in df.iterrows()}

    # district → set of ac_names
    dist_acs = {}
    for f in geojson["features"]:
        ac   = f["properties"].get("ac_name", "")
        dist = f["properties"].get("dist_name", "Unknown")
        dist_acs.setdefault(dist, set()).add(clean(ac))

    # which features to include
    if district_filter != "All Districts":
        allowed = dist_acs.get(district_filter, set())
    else:
        allowed = None

    m = folium.Map(
        location=WB_CENTER,
        zoom_start=8,
        tiles="CartoDB positron",
        prefer_canvas=True,
        min_zoom=MIN_ZOOM,
        max_zoom=MAX_ZOOM,
    )

    # Lock bounding box
    m.fit_bounds([[WB_BOUNDS[0][1], WB_BOUNDS[0][0]],
                  [WB_BOUNDS[1][1], WB_BOUNDS[1][0]]])
    m.options["maxBounds"] = [
        [WB_BOUNDS[0][1] - 0.5, WB_BOUNDS[0][0] - 0.5],
        [WB_BOUNDS[1][1] + 0.5, WB_BOUNDS[1][0] + 0.5],
    ]

    added = 0
    for feature in geojson["features"]:
        ac_raw  = feature["properties"].get("ac_name", "")
        ac_key  = clean(ac_raw)
        dist    = feature["properties"].get("dist_name", "Unknown")

        if allowed is not None and ac_key not in allowed:
            continue

        row   = lookup.get(ac_key)
        color = PARTY_COLORS.get(row["Party"] if row is not None else "Other", "#CCCCCC") if row is not None else "#CCCCCC"
        margin_str = f"{int(row['Margin']):,}" if row is not None and pd.notna(row["Margin"]) else "N/A"

        # Rich popup (click / tap)
        if row is not None:
            popup_html = f"""
            <div style='font-family:sans-serif;font-size:13px;line-height:1.75;min-width:220px'>
              <div style='background:{color};color:white;padding:6px 10px;
                          border-radius:6px 6px 0 0;font-weight:700;font-size:14px'>
                {row['Constituency']}
                <span style='float:right;font-size:11px;opacity:.85'>{row['Party']}</span>
              </div>
              <div style='padding:8px 10px;border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px'>
                <b>🏆 Winner:</b> {str(row['Leading Candidate']).title()}<br>
                <b>🥈 Runner-up:</b> {str(row['Trailing Candidate']).title()}<br>
                <b>📊 Margin:</b> {margin_str} votes<br>
                <b>🏷 Category:</b> {row['Margin_Cat']}<br>
                <b>🏘 District:</b> {dist}<br>
                <b>✅ Status:</b> {row['Status']}
              </div>
            </div>"""
        else:
            popup_html = f"<b>{ac_raw}</b><br><i>No election data</i>"

        # Lightweight tooltip (hover on desktop)
        tooltip_text = ac_raw if row is None else f"{row['Constituency']} — {row['Party']} (+{margin_str})"

        folium.GeoJson(
            feature,
            style_function=lambda x, c=color: {
                "fillColor": c, "color": "#333", "weight": 0.7, "fillOpacity": 0.75
            },
            highlight_function=lambda x: {
                "weight": 2.5, "color": "#000", "fillOpacity": 0.92
            },
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_text, sticky=False),
        ).add_to(m)
        added += 1

    # Legend
    seat_counts = df["Party"].value_counts().to_dict()
    legend_rows = "".join(
        f"""<div style='display:flex;align-items:center;margin-bottom:5px'>
              <div style='width:14px;height:14px;background:{col};border-radius:3px;
                          margin-right:8px;flex-shrink:0'></div>
              <span style='font-size:12px'><b>{p}</b> &nbsp;({seat_counts.get(p,0)})</span>
            </div>"""
        for p, col in PARTY_COLORS.items() if p != "Other"
    )
    legend_html = f"""
    <div style='position:fixed;bottom:40px;right:40px;z-index:9999;
                background:white;padding:14px 18px;border-radius:10px;
                box-shadow:0 2px 10px rgba(0,0,0,.25);font-family:sans-serif'>
      <b style='font-size:13px'>Winning Party</b><br><br>
      {legend_rows}
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    return m, added

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar(df, geojson):
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_West_Bengal.svg/200px-Flag_of_West_Bengal.svg.png",
        width=120
    )
    st.sidebar.title("🗳️ WB Election 2026")

    # Collect districts from GeoJSON
    districts = sorted({
        f["properties"].get("dist_name", "Unknown")
        for f in geojson["features"]
        if f["properties"].get("dist_name")
    })
    dist_choice = st.sidebar.selectbox(
        "📍 Filter by District",
        ["All Districts"] + districts,
        help="Zoom into a single district — feature not on ECI portal!"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
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
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
            f"<div style='width:12px;height:12px;background:{col};"
            f"border-radius:2px;flex-shrink:0'></div>"
            f"<span style='font-size:13px'><b>{party}</b> {n} &nbsp;"
            f"<span style='color:#888'>({pct:.1f}%)</span></span></div>",
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.caption("Data: ECA · Last updated 05/05/2026")

    return dist_choice

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df      = load_data()
    geojson = load_geojson()

    dist_choice = sidebar(df, geojson)

    # Header
    col1, col2, col3, col4 = st.columns(4)
    seats = df["Party"].value_counts()
    col1.metric("Total Constituencies", len(df))
    col2.metric("BJP", seats.get("BJP", 0), help="Bharatiya Janata Party")
    col3.metric("AITC", seats.get("AITC", 0), help="All India Trinamool Congress")
    col4.metric("Others", len(df) - seats.get("BJP",0) - seats.get("AITC",0))

    st.markdown("---")

    # District info strip
    if dist_choice != "All Districts":
        ddf = df.copy()
        # attach district from geojson
        dist_map = {clean(f["properties"].get("ac_name","")): f["properties"].get("dist_name","")
                    for f in geojson["features"]}
        ddf["District"] = ddf["Constituency"].apply(lambda x: dist_map.get(clean(x), "Unknown"))
        ddf = ddf[ddf["District"] == dist_choice]

        st.subheader(f"📍 {dist_choice} District — {len(ddf)} Constituencies")
        d_seats = ddf["Party"].value_counts()
        cols = st.columns(len(d_seats))
        for i, (party, n) in enumerate(d_seats.items()):
            cols[i].metric(party, n)
        st.markdown("---")

    # Map
    with st.spinner("Rendering map…"):
        m, n_drawn = build_map(df, geojson, district_filter=dist_choice)

    st_folium(
        m,
        width="100%",
        height=620,
        returned_objects=[],
    )

    st.caption(
        f"🖱️ **Hover** for quick info · **Click / Tap** for full details · "
        f"Zoom locked {MIN_ZOOM}–{MAX_ZOOM} · Showing {n_drawn} constituencies"
    )

    # Constituency table for selected district
    if dist_choice != "All Districts":
        with st.expander(f"📋 Full results table — {dist_choice}", expanded=False):
            dist_map2 = {clean(f["properties"].get("ac_name","")): f["properties"].get("dist_name","")
                         for f in geojson["features"]}
            show_df = df.copy()
            show_df["District"] = show_df["Constituency"].apply(lambda x: dist_map2.get(clean(x), "Unknown"))
            show_df = show_df[show_df["District"] == dist_choice][
                ["Constituency", "Party", "Leading Candidate", "Trailing Candidate", "Margin", "Margin_Cat"]
            ].sort_values("Margin", ascending=False).reset_index(drop=True)
            st.dataframe(show_df, use_container_width=True)

if __name__ == "__main__":
    main()

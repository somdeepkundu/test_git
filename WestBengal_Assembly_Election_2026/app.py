import streamlit as st
import pandas as pd
import requests, re, json
import xml.etree.ElementTree as ET
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WB Election 2026",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
FETCH_TIME = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

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

# ── Compute district bounding boxes ──────────────────────────────────────────
def district_bounds(geojson):
    """Return {dist_name: [[lat_min,lon_min],[lat_max,lon_max]]} """
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
    # convert to [[lat_min,lon_min],[lat_max,lon_max]]
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

    # Centre/zoom on district if selected
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
                <div style='margin-bottom:3px'>
                  <b>Winner</b>: {str(row['Leading Candidate']).title()}
                </div>
                <div style='margin-bottom:3px'>
                  <b>Runner-up</b>: {str(row['Trailing Candidate']).title()}
                </div>
                <div style='margin-bottom:3px'>
                  <b>Margin</b>: {margin_str} votes
                </div>
                <div style='margin-bottom:3px'>
                  <b>Category</b>: {row['Margin_Cat']}
                </div>
                <div style='margin-bottom:3px'>
                  <b>District</b>: {dist}
                </div>
                <div>
                  <b>Status</b>:
                  <span style='background:#e8f5e9;color:#2e7d32;padding:1px 6px;
                               border-radius:3px;font-size:11px;font-weight:600'>
                    {row['Status']}
                  </span>
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

    # Legend — solid background, explicit dark text
    seat_counts = df["Party"].value_counts().to_dict()
    legend_rows = "".join(
        f"""<div style='display:flex;align-items:center;margin-bottom:6px'>
              <div style='width:14px;height:14px;min-width:14px;background:{col};
                          border-radius:3px;margin-right:9px'></div>
              <span style='font-size:12px;color:#111;font-family:Arial,sans-serif'>
                <b>{p}</b> &nbsp;({seat_counts.get(p, 0)})
              </span>
            </div>"""
        for p, col in PARTY_COLORS.items() if p != "Other"
    )
    legend_html = f"""
    <div style='position:fixed;bottom:40px;right:40px;z-index:9999;
                background:#ffffff;padding:14px 18px;border-radius:10px;
                border:1px solid #ccc;
                box-shadow:0 2px 10px rgba(0,0,0,0.25);font-family:Arial,sans-serif'>
      <div style='font-size:13px;font-weight:700;color:#111;margin-bottom:10px'>
        Winning Party
      </div>
      {legend_rows}
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar(df, geojson, dist_bbox_map):
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_West_Bengal.svg/200px-Flag_of_West_Bengal.svg.png",
        width=110
    )
    st.sidebar.title("WB Election 2026")

    districts = sorted({
        f["properties"].get("dist_name", "Unknown")
        for f in geojson["features"]
        if f["properties"].get("dist_name")
    })
    dist_choice = st.sidebar.selectbox(
        "Filter by District",
        ["All Districts"] + districts,
        help="Zoom into a single district"
    )

    # ── District detail panel ────────────────────────────────────────────────
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

        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### {dist_choice}")
        st.sidebar.markdown(f"**{len(ddf)} constituencies**")

        d_seats = ddf["Party"].value_counts()
        for party, n in d_seats.items():
            col = PARTY_COLORS.get(party, "#757575")
            st.sidebar.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                f"<div style='width:12px;height:12px;background:{col};"
                f"border-radius:2px;flex-shrink:0'></div>"
                f"<span style='font-size:13px'><b>{party}</b> — {n} seats</span></div>",
                unsafe_allow_html=True
            )

        st.sidebar.markdown("**Closest race:**")
        closest = ddf.nsmallest(1, "Margin").iloc[0]
        st.sidebar.caption(
            f"{closest['Constituency']}: "
            f"{closest['Leading Candidate'].title()} ({closest['Party']}) "
            f"by {int(closest['Margin']):,} votes"
        )

        st.sidebar.markdown("**Biggest win:**")
        biggest = ddf.nlargest(1, "Margin").iloc[0]
        st.sidebar.caption(
            f"{biggest['Constituency']}: "
            f"{biggest['Leading Candidate'].title()} ({biggest['Party']}) "
            f"by {int(biggest['Margin']):,} votes"
        )

        st.sidebar.markdown("**Avg margin:**")
        st.sidebar.caption(f"{int(ddf['Margin'].mean()):,} votes")

    # ── State-level stats ────────────────────────────────────────────────────
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
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
            f"<div style='width:12px;height:12px;background:{col};"
            f"border-radius:2px;flex-shrink:0'></div>"
            f"<span style='font-size:13px'><b>{party}</b> {n}"
            f"<span style='color:#888'> ({pct:.1f}%)</span></span></div>",
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Source: ECA\nLast fetched: {FETCH_TIME}")

    return dist_choice

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df        = load_data()
    geojson   = load_geojson()
    bbox_map  = district_bounds(geojson)

    dist_choice = sidebar(df, geojson, bbox_map)
    dist_bbox   = bbox_map.get(dist_choice) if dist_choice != "All Districts" else None

    # Header metrics
    seats = df["Party"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Constituencies", len(df))
    c2.metric("BJP",  seats.get("BJP",  0))
    c3.metric("AITC", seats.get("AITC", 0))
    c4.metric("Others", len(df) - seats.get("BJP", 0) - seats.get("AITC", 0))

    st.markdown("---")

    # Map
    with st.spinner("Rendering map..."):
        m = build_map(df, geojson,
                      district_filter=dist_choice,
                      dist_bbox=dist_bbox)

    st_folium(m, width="100%", height=640, returned_objects=[])

    st.caption(
        "Hover for quick info · Click / tap for full details · "
        f"Zoom locked {MIN_ZOOM}–{MAX_ZOOM} · "
        f"Data: ECA · Fetched: {FETCH_TIME}"
    )

    # Results table for selected district
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

        with st.expander(f"Full results table — {dist_choice} ({len(show_df)} seats)", expanded=True):
            st.dataframe(show_df, use_container_width=True)

if __name__ == "__main__":
    main()

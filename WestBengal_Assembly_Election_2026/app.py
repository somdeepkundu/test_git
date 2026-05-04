import streamlit as st
import pandas as pd
import requests, re
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

st.markdown("""
<style>
  *{margin:0;padding:0}
  .main{background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%)}
  [data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1f3a 0%,#16213e 100%)}
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{color:#e0e0e0}
  h1,h2,h3{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;font-weight:600}
  h1{color:#1a1f3a;font-size:2.2rem!important;margin-bottom:.5rem}
  h2{color:#2c3e50;font-size:1.5rem!important;margin-top:1.5rem;margin-bottom:.8rem;
     border-bottom:2px solid #FF9800;padding-bottom:.5rem}
  h3{color:#e0e0e0;font-size:1.1rem!important}
  [data-testid="stExpander"]{border:1px solid #e0e0e0;border-radius:8px;background:white!important}
  [data-testid="stExpander"] summary{background:white!important;border-radius:8px}
  [data-testid="stExpander"] summary p,
  [data-testid="stExpander"] summary span,
  [data-testid="stExpander"] summary div,
  .streamlit-expanderHeader,.streamlit-expanderHeader p{color:#1a1f3a!important;font-weight:600!important}
  [data-testid="stExpander"]>details>summary:hover{background:#f5f5f5!important}
  [data-testid="stExpander"]>details{background:white!important;border-radius:8px}
  a{color:#FF9800;text-decoration:none;font-weight:600;transition:color .2s}
  a:hover{color:#FFA726}
  [data-testid="stSidebar"] a{color:#FFA726}
  [data-testid="stSidebar"] a:hover{color:#FFB74D}
  .logo-container{text-align:center;margin-bottom:1.5rem;padding:1rem 0;
                  border-bottom:2px solid rgba(255,152,0,.3)}
  .district-info{background:linear-gradient(135deg,rgba(255,152,0,.1) 0%,rgba(26,31,58,.05) 100%);
                 border-left:4px solid #FF9800;padding:1rem;border-radius:6px;margin:1rem 0}
  /* party-filter buttons */
  .stButton>button{width:100%;border-radius:8px;font-weight:600;
                   border:2px solid transparent;transition:all .2s}
  @media(max-width:768px){h1{font-size:1.4rem!important}}
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
WB_BOUNDS = [[85.8, 21.4], [89.9, 27.3]]
WB_CENTER = [23.4, 87.9]
MIN_ZOOM, MAX_ZOOM = 7, 12

# ── Session state defaults ────────────────────────────────────────────────────
if "party_filter" not in st.session_state:
    st.session_state["party_filter"] = "All"

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching data from GitHub...")
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Margin"]       = pd.to_numeric(df["Margin"],     errors="coerce")
    df["Const. No."]   = pd.to_numeric(df["Const. No."], errors="coerce")
    df["Constituency"] = df["Constituency"].str.strip()
    df["Party"]        = df["Leading Party"].map(PARTY_ABBREV).fillna("Other")
    def mcat(m):
        if pd.isna(m): return "Unknown"
        if m <  1000:  return "Extremely Close (<1K)"
        if m <  5000:  return "Very Close (1-5K)"
        if m < 10000:  return "Close (5-10K)"
        if m < 30000:  return "Comfortable (10-30K)"
        return         "Landslide (>30K)"
    df["Margin_Cat"] = df["Margin"].apply(mcat)
    return df

@st.cache_data(show_spinner="Parsing KML boundaries...")
def load_geojson():
    r = requests.get(KML_URL, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
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
        dist   = f["properties"].get("dist_name", "Unknown")
        coords = f["geometry"]["coordinates"][0]
        lons   = [c[0] for c in coords]
        lats   = [c[1] for c in coords]
        if dist not in bounds:
            bounds[dist] = [min(lats), min(lons), max(lats), max(lons)]
        else:
            b = bounds[dist]
            bounds[dist] = [min(b[0],min(lats)), min(b[1],min(lons)),
                            max(b[2],max(lats)), max(b[3],max(lons))]
    return {d: [[v[0],v[1]],[v[2],v[3]]] for d,v in bounds.items()}

# ── Map builder ───────────────────────────────────────────────────────────────
def build_map(df, geojson, district_filter="All Districts",
              dist_bbox=None, party_filter="All"):

    lookup = {clean(r["Constituency"]): r for _, r in df.iterrows()}

    dist_acs = {}
    for f in geojson["features"]:
        ac   = f["properties"].get("ac_name", "")
        dist = f["properties"].get("dist_name", "Unknown")
        dist_acs.setdefault(dist, set()).add(clean(ac))

    allowed_dist  = dist_acs.get(district_filter) if district_filter != "All Districts" else None

    if district_filter != "All Districts" and dist_bbox:
        start_loc  = [(dist_bbox[0][0]+dist_bbox[1][0])/2,
                      (dist_bbox[0][1]+dist_bbox[1][1])/2]
        start_zoom = 10
    else:
        start_loc  = WB_CENTER
        start_zoom = 8

    m = folium.Map(location=start_loc, zoom_start=start_zoom,
                   tiles="CartoDB positron", prefer_canvas=True,
                   min_zoom=MIN_ZOOM, max_zoom=MAX_ZOOM)

    if district_filter != "All Districts" and dist_bbox:
        m.fit_bounds(dist_bbox)
    else:
        m.fit_bounds([[WB_BOUNDS[0][1], WB_BOUNDS[0][0]],
                      [WB_BOUNDS[1][1], WB_BOUNDS[1][0]]])

    m.options["maxBounds"] = [
        [WB_BOUNDS[0][1]-0.5, WB_BOUNDS[0][0]-0.5],
        [WB_BOUNDS[1][1]+0.5, WB_BOUNDS[1][0]+0.5],
    ]

    for feature in geojson["features"]:
        ac_raw = feature["properties"].get("ac_name", "")
        ac_key = clean(ac_raw)
        dist   = feature["properties"].get("dist_name", "Unknown")

        if allowed_dist is not None and ac_key not in allowed_dist:
            continue

        row = lookup.get(ac_key)

        # Dim constituencies not in party filter
        is_others = (party_filter == "Others")
        in_others = (row is not None and row["Party"] not in ("BJP", "AITC"))
        in_single = (row is not None and row["Party"] == party_filter)

        if party_filter not in ("All", "Others") and not in_single:
            # Single-party filter: dim everything else
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    "fillColor": "#cccccc", "color": "#aaa",
                    "weight": 0.4, "fillOpacity": 0.20
                },
            ).add_to(m)
            continue
        elif is_others and row is not None and not in_others:
            # Others filter: dim BJP and AITC
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    "fillColor": "#cccccc", "color": "#aaa",
                    "weight": 0.4, "fillOpacity": 0.20
                },
            ).add_to(m)
            continue

        color = PARTY_COLORS.get(row["Party"] if row is not None else "Other", "#CCCCCC") \
                if row is not None else "#CCCCCC"
        margin_str = f"{int(row['Margin']):,}" \
                     if row is not None and pd.notna(row["Margin"]) else "N/A"

        if row is not None:
            popup_html = (
                "<div style=\"font-family:Arial,sans-serif;font-size:13px;"
                "line-height:1.75;min-width:230px;max-width:290px\">"
                "<div style=\"background:" + color + ";color:white;padding:7px 11px;"
                "border-radius:6px 6px 0 0;font-weight:700;font-size:14px;"
                "display:flex;justify-content:space-between;align-items:center\">"
                "<span>" + str(row["Constituency"]) + "</span>"
                "<span style=\"font-size:11px;opacity:.9\">" + str(row["Party"]) + "</span>"
                "</div>"
                "<div style=\"padding:9px 11px;border:1px solid #ddd;"
                "border-top:none;border-radius:0 0 6px 6px;background:#fff\">"
                "<div style=\"margin-bottom:3px\"><b>Winner</b>: " + str(row["Leading Candidate"]).title() + "</div>"
                "<div style=\"margin-bottom:3px\"><b>Runner-up</b>: " + str(row["Trailing Candidate"]).title() + "</div>"
                "<div style=\"margin-bottom:3px\"><b>Margin</b>: " + margin_str + " votes</div>"
                "<div style=\"margin-bottom:3px\"><b>Category</b>: " + str(row["Margin_Cat"]) + "</div>"
                "<div style=\"margin-bottom:3px\"><b>District</b>: " + dist + "</div>"
                "<div><b>Status</b>: <span style=\"background:#e8f5e9;color:#2e7d32;"
                "padding:1px 6px;border-radius:3px;font-size:11px;font-weight:600\">"
                + str(row["Status"]) + "</span></div>"
                "</div></div>"
            )
        else:
            popup_html = "<b>" + ac_raw + "</b><br><i>No election data</i>"

        tooltip_text = ac_raw if row is None \
                       else str(row["Constituency"]) + " — " + str(row["Party"]) + " (+" + margin_str + ")"

        folium.GeoJson(
            feature,
            style_function=lambda x, c=color: {
                "fillColor": c, "color": "#555", "weight": 0.7, "fillOpacity": 0.78
            },
            highlight_function=lambda x: {
                "weight": 2.5, "color": "#000", "fillOpacity": 0.93
            },
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_text, sticky=False),
        ).add_to(m)

    # Legend
    seat_counts = df["Party"].value_counts().to_dict()
    legend_rows = "".join(
        "<div style=\"display:flex;align-items:center;margin-bottom:6px\">"
        "<div style=\"width:14px;height:14px;min-width:14px;background:" + col + ";"
        "border-radius:3px;margin-right:9px\"></div>"
        "<span style=\"font-size:12px;color:#111;font-family:Arial,sans-serif\">"
        "<b>" + p + "</b> (" + str(seat_counts.get(p,0)) + ")"
        "</span></div>"
        for p, col in PARTY_COLORS.items() if p != "Other"
    )
    m.get_root().html.add_child(folium.Element(
        "<div style=\"position:fixed;bottom:40px;right:40px;z-index:9999;"
        "background:#ffffff;padding:14px 18px;border-radius:10px;"
        "border:1px solid #ccc;box-shadow:0 2px 10px rgba(0,0,0,.25);"
        "font-family:Arial,sans-serif\">"
        "<div style=\"font-size:13px;font-weight:700;color:#111;margin-bottom:10px\">"
        "Winning Party</div>" + legend_rows + "</div>"
    ))

    return m

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar(df, geojson, dist_bbox_map):
    st.sidebar.markdown("""
    <div class="logo-container">
        <div style="font-size:2rem">🗳️</div>
        <div style="color:#e0e0e0;font-size:1.3rem;font-weight:600;margin:.3rem 0">WB Election</div>
        <div style="color:#FF9800;font-size:1rem;font-weight:700">2026</div>
    </div>
    """, unsafe_allow_html=True)

    districts = sorted({
        f["properties"].get("dist_name", "Unknown")
        for f in geojson["features"]
        if f["properties"].get("dist_name")
    })
    st.sidebar.markdown("### Filter by District")
    dist_choice = st.sidebar.selectbox(
        "Select District:", ["All Districts"] + districts,
        help="Zoom into a single district", label_visibility="collapsed"
    )

    if dist_choice != "All Districts":
        dlookup = {clean(f["properties"].get("ac_name","")): f["properties"].get("dist_name","")
                   for f in geojson["features"]}
        ddf = df.copy()
        ddf["District"] = ddf["Constituency"].apply(lambda x: dlookup.get(clean(x),"Unknown"))
        ddf = ddf[ddf["District"] == dist_choice]

        st.sidebar.markdown(
            "<div class=\"district-info\">"
            "<div style=\"color:#FFB74D;font-size:1rem;font-weight:700;margin-bottom:.3rem\">"
            + dist_choice +
            "</div><div style=\"color:#aaa;font-size:.9rem\">"
            + str(len(ddf)) + " constituencies</div></div>",
            unsafe_allow_html=True
        )
        for party, n in ddf["Party"].value_counts().items():
            col = PARTY_COLORS.get(party, "#757575")
            st.sidebar.markdown(
                "<div style=\"display:flex;align-items:center;gap:8px;margin-bottom:5px\">"
                "<div style=\"width:10px;height:10px;background:" + col + ";"
                "border-radius:50%;flex-shrink:0\"></div>"
                "<span style=\"font-size:13px;color:#e0e0e0\"><b>" + party + "</b> — " + str(n) + "</span></div>",
                unsafe_allow_html=True
            )
        closest = ddf.nsmallest(1, "Margin").iloc[0]
        biggest = ddf.nlargest(1,  "Margin").iloc[0]
        st.sidebar.caption(f"Closest: **{closest['Constituency']}** {int(closest['Margin']):,} votes")
        st.sidebar.caption(f"Biggest: **{biggest['Constituency']}** {int(biggest['Margin']):,} votes")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### State Summary")
    seats = df["Party"].value_counts()
    for party, col in PARTY_COLORS.items():
        if party == "Other": continue
        n = seats.get(party, 0)
        if n == 0: continue
        pct = n / len(df) * 100
        st.sidebar.markdown(
            "<div style=\"display:flex;align-items:center;gap:8px;margin-bottom:5px\">"
            "<div style=\"width:10px;height:10px;background:" + col + ";"
            "border-radius:50%;flex-shrink:0\"></div>"
            "<span style=\"font-size:13px;color:#e0e0e0\"><b>" + party + "</b> " + str(n) +
            " <span style=\"color:#999\">(" + f"{pct:.1f}%" + ")</span></span></div>",
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Last Updated**  \n04:00 AM On 05/05/2026\n\n"
        "**App developed by**  \n[Somdeep Kundu](https://www.somdeepkundu.in)  \nRuDRA Lab, CTARA\n\n"
        "**Data Source**  \n[Election Commission of India]"
        "(https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S25.htm)"
    )
    return dist_choice

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df      = load_data()
    geojson = load_geojson()
    bbox_map = district_bounds(geojson)

    dist_choice = sidebar(df, geojson, bbox_map)
    dist_bbox   = bbox_map.get(dist_choice) if dist_choice != "All Districts" else None

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        "<div style=\"text-align:center;margin-bottom:1rem\">"
        "<h1 style=\"font-size:clamp(1.4rem,4vw,2.2rem);margin-bottom:.3rem\">"
        "West Bengal Assembly Election 2026</h1>"
        "<p style=\"font-size:clamp(.85rem,2.5vw,1.1rem);color:#666;margin:0\">"
        "Interactive constituency results — click a card to filter the map"
        "</p></div>",
        unsafe_allow_html=True
    )

    # ── Party filter cards — styled buttons in a 2×2 grid ──────────────────
    seats       = df["Party"].value_counts()
    other_count = len(df) - seats.get("BJP", 0) - seats.get("AITC", 0)
    active      = st.session_state["party_filter"]

    CARDS = [
        ("All",   "ALL SEATS", 294,                  "All constituencies",                 "#607D8B"),
        ("BJP",   "BJP",       seats.get("BJP",  0), f"{seats.get('BJP', 0)/len(df)*100:.1f}%", "#FF9800"),
        ("AITC",  "AITC",      seats.get("AITC", 0), f"{seats.get('AITC',0)/len(df)*100:.1f}%", "#1E88E5"),
        ("Others","OTHERS",    other_count,           f"{other_count/len(df)*100:.1f}%",           "#4CAF50"),
    ]

    # Inject CSS: style every button to look like a card
    btn_styles = ""
    for key, label, value, pct, color in CARDS:
        is_active = (active == key)
        outline   = f"3px solid {color}" if is_active else f"1.5px solid {color}55"
        shadow    = f"0 4px 14px {color}44" if is_active else "0 2px 6px rgba(0,0,0,.06)"
        tick      = "✓  " if is_active else ""
        # Each button gets a unique data-testid via its key
        btn_styles += f"""
        [data-testid="stButton"] button[kind="secondary"]:has(+ *),
        div[data-testid="column"] button {{}}
        """
    # Card backgrounds and tints keyed per party
    CARD_BG = {
        "All":    "#EEF2F7",
        "BJP":    "#FFF3E0",
        "AITC":   "#E3F2FD",
        "Others": "#E8F5E9",
    }

    # Global button styles — applied once
    st.markdown("""
    <style>
    /* Force every button in these card columns to render as a styled card */
    [class*="btn-card-"] button {
        width: 100% !important;
        min-height: 80px !important;
        border-radius: 12px !important;
        text-align: left !important;
        padding: 10px 12px !important;
        line-height: 1.5 !important;
        white-space: pre-wrap !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all .2s !important;
        border: none !important;
    }
    [class*="btn-card-"] button:hover { filter: brightness(.94) !important; }
    /* Tinted backgrounds — explicit for each key */
    .btn-card-All    button { background: #EEF2F7 !important; color: #37474F !important; border-left: 5px solid #607D8B !important; }
    .btn-card-BJP    button { background: #FFF3E0 !important; color: #E65100 !important; border-left: 5px solid #FF9800 !important; }
    .btn-card-AITC   button { background: #E3F2FD !important; color: #0D47A1 !important; border-left: 5px solid #1E88E5 !important; }
    .btn-card-Others button { background: #E8F5E9 !important; color: #1B5E20 !important; border-left: 5px solid #4CAF50 !important; }
    /* Active glow ring */
    .active-All    button { box-shadow: 0 0 0 3px #607D8B !important; }
    .active-BJP    button { box-shadow: 0 0 0 3px #FF9800 !important; }
    .active-AITC   button { box-shadow: 0 0 0 3px #1E88E5 !important; }
    .active-Others button { box-shadow: 0 0 0 3px #4CAF50 !important; }
    </style>
    """, unsafe_allow_html=True)

    row1 = st.columns(2)
    row2 = st.columns(2)
    all_cols = [row1[0], row1[1], row2[0], row2[1]]

    for col_obj, (key, label, value, pct, color) in zip(all_cols, CARDS):
        is_active = (active == key)
        tick      = "✓ " if is_active else ""
        btn_text  = f"{tick}{label}\n{value}\n{pct}"
        active_cls = f"active-{key}" if is_active else ""

        col_obj.markdown(
            f'<div class="btn-card-{key} {active_cls}">',
            unsafe_allow_html=True
        )
        if col_obj.button(btn_text, key=f"btn_{key}", use_container_width=True):
            st.session_state["party_filter"] = key
            st.rerun()
        col_obj.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Map ───────────────────────────────────────────────────────────────────
    pf = st.session_state["party_filter"]
    # "Others" = all non-BJP/AITC; pass None and filter in map
    map_party = None if pf in ("All", "Others") else pf

    # For "Others", build list of other parties
    other_parties = [p for p in df["Party"].unique() if p not in ("BJP","AITC")]

    with st.spinner("Rendering map..."):
        m = build_map(df, geojson,
                      district_filter=dist_choice,
                      dist_bbox=dist_bbox,
                      party_filter=map_party if pf not in ("All","Others") else pf)

    st_folium(m, width="100%", height=620, returned_objects=[])
    st.caption(f"Hover for quick info · Click/tap for details")

    # ── Party-filtered results table ──────────────────────────────────────────
    show_df = df.copy()

    # Attach district
    dlookup2 = {clean(f["properties"].get("ac_name","")): f["properties"].get("dist_name","")
                for f in geojson["features"]}
    show_df["District"] = show_df["Constituency"].apply(lambda x: dlookup2.get(clean(x),"Unknown"))

    # Apply district filter
    if dist_choice != "All Districts":
        show_df = show_df[show_df["District"] == dist_choice]

    # Apply party filter
    if pf == "Others":
        show_df = show_df[~show_df["Party"].isin(["BJP","AITC"])]
    elif pf != "All":
        show_df = show_df[show_df["Party"] == pf]

    show_df = show_df[["Constituency","Party","Leading Candidate",
                        "Trailing Candidate","Margin","Margin_Cat","District","Status"]]\
              .sort_values("Margin", ascending=False)\
              .reset_index(drop=True)

    title_parts = []
    if pf != "All":   title_parts.append(pf)
    if dist_choice != "All Districts": title_parts.append(dist_choice)
    title_str = " · ".join(title_parts) if title_parts else "All Constituencies"

    with st.expander(
        f"📋 Results: {title_str} — {len(show_df)} seats  "
        f"(sorted highest → lowest margin)",
        expanded=(pf != "All" or dist_choice != "All Districts")
    ):
        st.dataframe(show_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()

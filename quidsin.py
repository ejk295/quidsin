import os
import requests
from datetime import datetime
import pytz
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from fractions import Fraction

# 1. Page Configurations & MASTER Layout Credentials
st.set_page_config(
    page_title="Byway World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 3 minutes to keep live scores syncing
st_autorefresh(interval=180 * 1000, key="datarefresh")

API_TOKEN = st.secrets.get("FOOTBALL_API_TOKEN", os.environ.get("FOOTBALL_API_TOKEN", "placeholder"))
ODDS_API_TOKEN = st.secrets.get("ODDS_API_TOKEN", os.environ.get("ODDS_API_TOKEN", "placeholder"))
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

DEFAULT_LEFT_COLOR = "#ff7d23"
DEFAULT_RIGHT_COLOR = "#ff7d23"

# 2. Master Structural Dictionaries & Environment Mappings
SWEEPSTAKE_MAPPING = {
    "Mexico": "Evon", "South Africa": "Iwan", "Canada": "Holly", "Switzerland": "Yannis",
    "Argentina": "Alba", "France": "Marc", "Brazil": "Andy", "Spain": "Ciaran",
    "Bosnia and Herzegovina": "Izzy", "Bosnia-Herzegovina": "Izzy", "Czechia": "Pablo", "Qatar": "Jess", "Morocco": "Bartek",
    "Haiti": "Hatty", "Turkey": "Adrienne", "Paraguay": "Becca", "Germany": "Oliwia",
    "Curaçao": "Justin", "Ecuador": "Cat", "Japan": "Adem", "Belgium": "Mart",
    "Egypt": "Chris", "Tunisia": "Jess 2", "Netherlands": "Louis", "Ivory Coast": "Suzie",
    "Australia": "Amy", "Cape Verde Islands": "Justin 2", "Cape Verde": "Justin 2", "Uruguay": "Paul 2", "Sweden": "Kat",
    "Saudi Arabia": "Aurelie", "Scotland": "Elaine 2", "United States": "Neil", "Senegal": "Sara",
    "New Zealand": "James", "Iran": "Elaine", "Iraq": "Paul", "Norway": "Claire",
    "Algeria": "Adrienne 2", "Austria": "Rich", "Jordan": "Maria", "Congo DR": "Ellis", "DR Congo": "Ellis",
    "Portugal": "Lucy 2", "Uzbekistan": "Kat 2", "Colombia": "Neil 2", "England": "Marijke",
    "Panama": "Lucy", "Ghana": "Sam", "Croatia": "Kurt", "South Korea": "Beau",
}

COUNTRY_ABBREVIATIONS = {
    "Mexico": "MEX", "South Africa": "RSA", "Canada": "CAN", "Switzerland": "SUI",
    "Argentina": "ARG", "France": "FRA", "Brazil": "BRA", "Spain": "ESP",
    "Bosnia and Herzegovina": "BIH", "Bosnia-Herzegovina": "BIH", "Czechia": "CZE", "Qatar": "QAT", "Morocco": "MAR",
    "Haiti": "HAI", "Turkey": "TUR", "Paraguay": "PAR", "Germany": "GER",
    "Curaçao": "CUW", "Ecuador": "ECU", "Japan": "JPN", "Belgium": "BEL",
    "Egypt": "EGY", "Tunisia": "TUN", "Netherlands": "NED", "Ivory Coast": "CIV",
    "Australia": "AUS", "Cape Verde Islands": "CPV", "Cape Verde": "CPV", "Uruguay": "URU", "Sweden": "SWE",
    "Saudi Arabia": "KSA", "Scotland": "SCO", "United States": "USA", "Senegal": "SEN",
    "New Zealand": "NZL", "Iran": "IRN", "Iraq": "IRQ", "Norway": "NOR",
    "Algeria": "ALG", "Austria": "AUT", "Jordan": "JOR", "Congo DR": "COD", "DR Congo": "COD",
    "Portugal": "POR", "Uzbekistan": "UZB", "Colombia": "COL", "England": "ENG",
    "Panama": "PAN", "Ghana": "GHA", "Croatia": "CRO", "South Korea": "KOR"
}

EXPECTED_RANKINGS = {
    "France": 1, "Spain": 2, "Argentina": 3, "England": 4, "Portugal": 5, "Brazil": 6,
    "Netherlands": 7, "Morocco": 8, "Belgium": 9, "Germany": 10, "Croatia": 11, "Colombia": 12,
    "Senegal": 13, "Mexico": 14, "United States": 15, "Uruguay": 16, "Japan": 17, "Switzerland": 18,
    "Iran": 19, "Turkey": 20, "Ecuador": 21, "Austria": 22, "South Korea": 23, "Australia": 24,
    "Algeria": 25, "Egypt": 26, "Canada": 27, "Norway": 28, "Panama": 29, "Ivory Coast": 30,
    "Sweden": 31, "Paraguay": 32, "Czechia": 33, "Scotland": 34, "Tunisia": 35, "Congo DR": 36, 
    "DR Congo": 36, "Uzbekistan": 37, "Qatar": 38, "Iraq": 39, "South Africa": 40, "Saudi Arabia": 41,
    "Jordan": 42, "Bosnia-Herzegovina": 43, "Bosnia and Herzegovina": 43, "Cape Verde Islands": 44, "Cape Verde": 44, "Ghana": 45, 
    "Curaçao": 46, "Haiti": 47, "New Zealand": 48
}

TEAM_COLORS = {
    "Mexico": "#006847", "South Africa": "#007A4D", "Canada": "#FF0000", "Switzerland": "#D52B1E",
    "Argentina": "#74ACDF", "France": "#002395", "Brazil": "#009739", "Spain": "#AA151B",
    "Bosnia-Herzegovina": "#002F6C", "Bosnia and Herzegovina": "#002F6C", "Czechia": "#11457E", "Qatar": "#8A1538", "Morocco": "#C1272D",
    "Haiti": "#00209F", "Turkey": "#E30A17", "Paraguay": "#D52B1E", "Germany": "#222222",
    "Curaçao": "#002B7F", "Ecuador": "#FFDD00", "Japan": "#00005C", "Belgium": "#E30A17",
    "Egypt": "#C1272D", "Tunisia": "#E70013", "Netherlands": "#E05206", "Ivory Coast": "#E87722",
    "Australia": "#00008B", "Cape Verde Islands": "#003893", "Cape Verde": "#003893", "Uruguay": "#0081C8", 
    "Sweden": "#006AA7", "Saudi Arabia": "#006C35", "Scotland": "#005EB8", "United States": "#002868", 
    "Senegal": "#00853F", "New Zealand": "#111111", "Iran": "#239E46", "Iraq": "#007A3D", 
    "Norway": "#EF2B2D", "Algeria": "#006233", "Austria": "#ED2939", "Jordan": "#1A1A1A", 
    "Congo DR": "#007FFF", "DR Congo": "#007FFF", "Portugal": "#FF0000", "Uzbekistan": "#0099B5", 
    "Colombia": "#FCD116", "England": "#CE1124", "Panama": "#DA121A", "Ghana": "#DA121A", 
    "Croatia": "#FF0000", "South Korea": "#111111"
}

GROUP_PLAYERS = {
    "Spain": {"player_name": "Lamine Yamal", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/lamine-yamal-spain-forward-profile-full.png"},
    "France": {"player_name": "Kylian Mbappe", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kylian-mbappe-france-forward-profile-full.png"},
    "England": {"player_name": "Bukayo Saka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/bukayo-saka-england-forward-profile-full.png"},
    "Brazil": {"player_name": "Vinícius Jr.", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/vinicius-junior-brazil-forward-profile-full.png"},
    "Germany": {"player_name": "Kai Havertz", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kai-havertz-germany-forward-profile-full.png"},
    "Portugal": {"player_name": "Bruno Fernandes", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/bruno-fernandes-portugal-midfielder-profile-full.png"},
    "Netherlands": {"player_name": "Frenkie de Jong", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/frenkie-de-jong-netherlands-midfielder-profile-full.png"},
    "Argentina": {"player_name": "Lionel Messi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/lionel-messi-argentina-forward-profile-full.png"},
    "Ivory Coast": {"player_name": "Yan Diomande", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/yan-diomande-ivory-coast-forward-profile-full.png"}
}

BROADCAST_BRANDS = {
    "bbc one": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/BBC_One_logo_2021.svg/1920px-BBC_One_logo_2021.svg.png",
        "live_url": "https://www.bbc.co.uk/iplayer/live/bbcone"
    },
    "bbc two": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/BBC_Two_logo_2021.svg/1920px-BBC_Two_logo_2021.svg.png",
        "live_url": "https://www.bbc.co.uk/iplayer/live/bbctwo"
    },
    "itv1": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/ITV1_Logo_2022.svg/250px-ITV1_Logo_2022.svg.png",
        "live_url": "https://www.itv.com/watch?channel=itv"
    },
    "itv4": {
        "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/57/ITV4_logo_%282022%29.svg/1280px-ITV4_logo_%282022%29.svg.png",
        "live_url": "https://www.itv.com/watch?channel=itv4"
    }
}

GLOBAL_STYLE_TOKENS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght=0,300..900;1,300..900&display=swap');
    
    body, html {
        background-color: #FAFAFA !important;
        color: #333333 !important;
        font-family: 'Figtree', sans-serif !important;
        margin: 0;
        padding: 0;
    }

    .multi-match-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 100%;
        margin-bottom: 15px;
    }

    .match-banner-card {
        background: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        overflow: hidden;
        width: 100%;
    }

    .banner-top-pane {
        background-color: #444444;
        padding: 6px 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .next-match-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800;
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.15);
        padding: 4px 8px;
        border-radius: 4px;
    }

    .matchup-split-screen {
        display: flex;
        position: relative;
        align-items: center;
        height: 65px;
        width: 100%;
    }

    .team-panel {
        width: 50%;
        display: flex;
        align-items: center;
        padding: 5px 20px;
        box-sizing: border-box;
        height: 100%;
    }
    
    .home-panel { justify-content: flex-end; padding-right: 45px; }
    .away-panel { justify-content: flex-start; padding-left: 45px; }

    .team-panel-text {
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 800;
        text-shadow: 0px 1px 2px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
    }

    .team-panel-text span {
        font-size: 11px !important;
        font-weight: 400;
        opacity: 0.9;
        color: #FFFFFF !important;
        margin: 0 4px;
    }

    .vs-marker-bubble, .score-bubble {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        background-color: #111111;
        color: #FFFFFF !important;
        font-weight: 900;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }

    .vs-marker-bubble { font-size: 11px; padding: 4px 7px; border-radius: 50%; }
    .score-bubble { font-size: 14px; padding: 4px 10px; border-radius: 4px; background-color: #444444; }

    .banner-bottom-bar {
        background-color: #F8F9FA;
        border-top: 1px solid #EEEEEE;
        padding: 6px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        font-weight: 700;
    }

    .watch-live-btn-fixed {
        font-weight: 800;
        font-size: 10px;
        text-transform: uppercase;
        text-decoration: none !important;
        padding: 4px 8px;
        border-radius: 4px;
        color: #FFFFFF !important;
        background-color: #ff7d23;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .watch-live-btn-fixed:hover { background-color: #CC0000; }

    .banner-flag {
        width: 24px; height: 16px; object-fit: cover; border-radius: 2px; margin: 0 6px;
    }

    .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-left: 6px; }
    .dot-green { background-color: #28a745; }
    .dot-red { background-color: #dc3545; }
</style>
"""

st.markdown(GLOBAL_STYLE_TOKENS, unsafe_allow_html=True)
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #FAFAFA !important; }
        h1, h2, h3, h1 span, h2 span, h3 span { color: #ff7d23 !important; font-family: 'Figtree', sans-serif !important; font-weight: 800 !important; }
        .stat-banner-box { background: #FFFFFF !important; padding: 12px 20px; border-radius: 8px; border: 1px solid #EAEAEA; display: flex; align-items: center; justify-content: space-between; }
        .custom-dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .custom-dashboard-table th { border-bottom: 2px solid #ff7d23; padding: 6px; font-weight: 700; }
        .custom-dashboard-table td { padding: 6px; border-bottom: 1px solid #EAEAEA; background: #FFFFFF; }
        .fixture-row { background: #FFFFFF; padding: 6px 10px; border: 1px solid #EAEAEA; border-radius: 4px; display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
    </style>
""", unsafe_allow_html=True)

# 3. Core Helper Utility Functions
@st.cache_data(ttl=86400)
def get_cached_team_crests():
    crests = {}
    if API_TOKEN == "placeholder": return crests
    try:
        url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/teams"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            for t in res.json().get("teams", []):
                name = t.get("name")
                if name and t.get("crest"):
                    crests[name] = t.get("crest")
                    if name == "DR Congo": crests["Congo DR"] = t.get("crest")
                    if name == "Cape Verde": crests["Cape Verde Islands"] = t.get("crest")
                    if name == "Bosnia and Herzegovina": crests["Bosnia-Herzegovina"] = t.get("crest")
    except Exception: pass
    return crests

CACHED_CRESTS = get_cached_team_crests()

def get_banner_flag_html(team_name):
    url = CACHED_CRESTS.get(team_name)
    return f'<img src="{url}" class="banner-flag">' if url else ''

def get_group_flag_html(team_name):
    url = CACHED_CRESTS.get(team_name)
    return f'<img src="{url}" style="width:20px; height:14px; object-fit:cover; vertical-align:middle; margin-right:4px;">' if url else ''

def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return pytz.utc.localize(dt).astimezone(pytz.timezone("Europe/London"))
    except Exception: return None

def get_live_score(match):
    score_obj = match.get("score", {})
    for k in ["fullTime", "regularTime", "halfTime"]:
        s = score_obj.get(k, {})
        if s.get("home") is not None: return int(s["home"]), int(s["away"])
    return 0, 0

# Master Spreadsheet Engine Ingestion 
@st.cache_data(ttl=15)
def fetch_spreadsheet_overrides_master():
    override_dict = {}
    try:
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQeLButP4o4374i0KJP_YdOnTW1wN-Wzgqabuulvd1cMVmIuCfFTEM3CjJ4FmFIbBW6FLNDfaB9Hg4w/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(csv_url, header=None)
        for _, row in df.iterrows():
            if len(row) >= 7:
                home_t = str(row[2]).strip()
                away_t = str(row[3]).strip()
                if home_t and away_t:
                    override_dict[f"{home_t.lower()}_v_{away_t.lower()}"] = {
                        "status": str(row[4]).strip().lower(),
                        "homeScore": str(row[5]).strip(),
                        "awayScore": str(row[6]).strip(),
                        "highlightsUrl": str(row[7]).strip() if len(row) >= 8 and pd.notna(row[7]) else "https://www.youtube.com/@fifa/videos",
                        "tvNetwork": str(row[8]).strip() if len(row) >= 9 and pd.notna(row[8]) else ""
                    }
    except Exception: pass
    return override_dict

SPREADSHEET_OVERRIDES = fetch_spreadsheet_overrides_master()

# ── DYNAMIC BLOCK GENERATION ENGINE ──
def build_dashboard_match_grid(matches, is_live=False, is_result=False):
    if not matches: return ""
    html_out = f"{GLOBAL_STYLE_TOKENS}<div class='multi-match-container'>"
    
    for idx, match in enumerate(matches):
        h_name = match.get("homeTeam", {}).get("name", "TBD")
        a_name = match.get("awayTeam", {}).get("name", "TBD")
        
        left_color = TEAM_COLORS.get(h_name, DEFAULT_LEFT_COLOR)
        right_color = TEAM_COLORS.get(a_name, DEFAULT_RIGHT_COLOR)
        if left_color == right_color: right_color = "#222222"

        h_score, a_score = get_live_score(match)
        tv_channel = ""
        highlights_url = "https://www.youtube.com/@fifa/videos"
        
        lookup_key = f"{h_name.lower()}_v_{a_name.lower()}"
        if lookup_key in SPREADSHEET_OVERRIDES:
            overrides = SPREADSHEET_OVERRIDES[lookup_key]
            h_score = overrides["homeScore"]
            a_score = overrides["awayScore"]
            tv_channel = overrides["tvNetwork"]
            highlights_url = overrides["highlightsUrl"]

        # Card status label setup
        if is_live: status_lbl, bubble = "🔴 Live Now", f'<div class="score-bubble">{h_score} – {a_score}</div>'
        elif is_result: status_lbl, bubble = "✅ Result", f'<div class="score-bubble">{h_score} – {a_score}</div>'
        else: status_lbl, bubble = "⏳ Scheduled", '<div class="vs-marker-bubble">VS</div>'

        dt_uk = format_to_uk_time(match.get("utcDate"))
        time_meta = dt_uk.strftime("%d/%m %H:%M") if dt_uk else "TBD"
        
        # Broadcast Action Button integration
        btn_html = ""
        if tv_channel:
            norm_ch = tv_channel.lower().strip()
            if norm_ch in BROADCAST_BRANDS:
                brand = BROADCAST_BRANDS[norm_ch]
                btn_html = f'<a href="{brand["live_url"]}" target="_blank" class="watch-live-btn-fixed">Watch Live <img src="{brand["logo"]}" style="height:11px; width:auto;"></a>'
            else:
                btn_html = f'<span style="color:#666; font-size:11px;">📺 {tv_channel}</span>'
        elif is_result:
            btn_html = f'<a href="{highlights_url}" target="_blank" class="watch-live-btn-fixed" style="background:#444;">Highlights</a>'

        html_out += f"""
        <div class="match-banner-card">
            <div class="banner-top-pane">
                <span class="next-match-title">{status_lbl}</span>
                <span style="color:#FFF; font-size:11px; font-weight:700;">{time_meta}</span>
            </div>
            <div class="matchup-split-screen">
                <div class="team-panel home-panel" style="background-color: {left_color};">
                    <div class="team-panel-text">
                        {get_banner_flag_html(h_name)}
                        <span style="font-weight:800;">{COUNTRY_ABBREVIATIONS.get(h_name, h_name[:3].upper())}</span>
                        <span>({SWEEPSTAKE_MAPPING.get(h_name, 'Unassigned')})</span>
                    </div>
                </div>
                {bubble}
                <div class="team-panel away-panel" style="background-color: {right_color};">
                    <div class="team-panel-text">
                        <span>({SWEEPSTAKE_MAPPING.get(a_name, 'Unassigned')})</span>
                        <span style="font-weight:800;">{COUNTRY_ABBREVIATIONS.get(a_name, a_name[:3].upper())}</span>
                        {get_banner_flag_html(a_name)}
                    </div>
                </div>
            </div>
            <div class="banner-bottom-bar">
                <span style="color:#555; font-size:11px;">World Cup Sweepstake State</span>
                {btn_html}
            </div>
        </div>
        """
    html_out += "</div>"
    return html_out

# Data Processing Core
all_matches, standings_list = fetch_football_data()

processed_standings = {}
third_place_pool = []
all_group_games_finished = True

for group in standings_list:
    g_name = group.get("group", "Group")
    rows = []
    for row in group.get("table", []):
        t_info = row.get("team", {})
        t_name = t_info.get("name", "Unknown")
        played = row.get("playedGames", 0)
        if played < 3: all_group_games_finished = False
        
        rows.append({
            "name": t_name, "played": played, "won": row.get("won", 0),
            "draw": row.get("draw", 0), "lost": row.get("lost", 0),
            "gf": row.get("goalsFor", 0), "ga": row.get("goalsAgainst", 0),
            "gd": row.get("goalDifference", 0), "pts": row.get("points", 0)
        })
        
    # Official Multi-factor Custom Sorting Logic Engine
    rows.sort(key=lambda x: (-x["pts"], -x["gd"], -x["gf"]))
    
    # Evaluate explicit Head-to-Head structural adjustments if points match
    idx = 0
    while idx < len(rows) - 1:
        if rows[idx]["pts"] == rows[idx+1]["pts"]:
            for m in all_matches:
                if m.get("status") == "FINISHED":
                    h = m.get("homeTeam", {}).get("name")
                    a = m.get("awayTeam", {}).get("name")
                    if {h, a} == {rows[idx]["name"], rows[idx+1]["name"]}:
                        hs, _ = get_live_score(m)
                        _, as_ = get_live_score(m)
                        if hs < as_ and h == rows[idx]["name"]:
                            rows[idx], rows[idx+1] = rows[idx+1], rows[idx]
        idx += 1
        
    processed_standings[g_name] = rows
    if len(rows) >= 3: third_place_pool.append(rows[2])

third_place_pool.sort(key=lambda x: (-x["pts"], -x["gd"], -x["gf"]))
highest_8_third_place = [t["name"] for t in third_place_pool[:8]]

# Dynamic Node Position Resolution Wrapper Function
def resolve_pos(group_letter, position):
    g_key = f"Group {group_letter}"
    if g_key in processed_standings and len(processed_standings[g_key]) >= position:
        return processed_standings[g_key][position-1]["name"]
    return f"{position if position==1 else 'Runner-up'} Group {group_letter}"

# Ingest and Category Pipeline Sort Arrays
live_m, upcoming_m, finished_m = [], [], []
for m in all_matches:
    h_n = m.get("homeTeam", {}).get("name", "")
    a_n = m.get("awayTeam", {}).get("name", "")
    lookup_key = f"{h_n.lower()}_v_{a_n.lower()}"
    
    if lookup_key in SPREADSHEET_OVERRIDES:
        st_str = SPREADSHEET_OVERRIDES[lookup_key]["status"]
        if "live" in st_str: live_m.append(m)
        elif "finished" in st_str or "completed" in st_str: finished_m.append(m)
        else: upcoming_m.append(m)
    else:
        status = m.get("status")
        if status in ["IN_PLAY", "PAUSED"]: live_m.append(m)
        elif status == "FINISHED": finished_m.append(m)
        else: upcoming_m.append(m)

upcoming_m = sorted(upcoming_m, key=lambda x: x.get("utcDate", ""))
finished_m = sorted(finished_m, key=lambda x: x.get("utcDate", ""), reverse=True)

# ── RENDERING HEADER LAYOUT CELLS ──
cols = st.columns([1, 1], gap="medium")
with cols[0]:
    st.markdown('<div class="title-area" style="padding-top:10px;"><h1>🏆 BYWAY SWEEPSTAKE</h1><p>Tournament Arena Dashboard</p></div>', unsafe_allow_html=True)
with cols[1]:
    if live_m:
        st.markdown(build_dashboard_match_grid([live_m[0]], is_live=True), unsafe_allow_html=True)
    elif upcoming_m:
        tk = upcoming_m[0].get("utcDate")
        same_time = [m for m in upcoming_m if m.get("utcDate") == tk]
        components.html(build_dashboard_match_grid(same_time, is_live=False), height=90 * len(same_time) + 20)

# Stat Box Row
sc1, sc2, sc3 = st.columns(3)
sc1.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
sc2.markdown('<div class="stat-banner-box"><medium>🚀 Status</medium><span>Live Tracking Active</span></div>', unsafe_allow_html=True)
sc3.markdown('<div class="stat-banner-box"><medium>⚽ Played Match States</medium><span>' + str(len(finished_m)) + ' Logged</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:15px 0; border-top:1px solid #ff7d23;'>", unsafe_allow_html=True)

# Toggle configurations automatically based on stage criteria matches completed
ko_open = all_group_games_finished
group_open = not all_group_games_finished

# ── COLLAPSIBLE MODULE 1: KNOCKOUT PHASE ──
with st.expander("🏅 KNOCKOUT STAGE BRACKET", expanded=ko_open):
    
    # Dynamic Brackets Layout Object Schema
    ko_structure = {
        "Round of 32": [
            {"date": "June 28 @ 17:00", "t1": resolve_pos("A", 2), "t2": resolve_pos("B", 2)},
            {"date": "June 29 @ 21:00", "t1": resolve_pos("E", 1), "t2": "3rd Group A/B/C/D/F"},
            {"date": "June 29 @ 18:00", "t1": resolve_pos("F", 1), "t2": resolve_pos("C", 2)},
            {"date": "June 29 @ 20:00", "t1": resolve_pos("C", 1), "t2": resolve_pos("F", 2)},
            {"date": "June 30 @ 16:00", "t1": resolve_pos("I", 1), "t2": "3rd Group C/D/F/G/H"},
            {"date": "June 30 @ 19:00", "t1": resolve_pos("E", 2), "t2": resolve_pos("I", 2)},
            {"date": "June 30 @ 22:00", "t1": resolve_pos("A", 1), "t2": "3rd Group C/E/F/H/I"}
        ],
        "Round of 16": [
            {"date": "July 4 @ 18:00", "t1": "Winner Match 74", "t2": "Winner Match 77"},
            {"date": "July 4 @ 21:00", "t1": "Winner Match 73", "t2": "Winner Match 76"},
            {"date": "July 5 @ 17:00", "t1": "Winner Match 78", "t2": "Winner Match 91"},
            {"date": "July 5 @ 20:00", "t1": "Winner Match 92", "t2": "Winner Match 79"}
        ],
        "Quarter-Finals": [
            {"date": "July 9 @ 19:00", "t1": "Winner Match 89", "t2": "Winner Match 90"},
            {"date": "July 10 @ 20:00", "t1": "Winner Match 83", "t2": "Winner Match 84"}
        ],
        "Semi-Finals": [
            {"date": "July 14 @ 20:00", "t1": "Winner Match 97", "t2": "Winner Match 98"},
            {"date": "July 15 @ 20:00", "t1": "Winner Match 99", "t2": "Winner Match 100"}
        ],
        "Finals": [
            {"date": "July 18 @ 21:00 (Third Place Play-off)", "t1": "Loser Match 101", "t2": "Loser Match 102"},
            {"date": "July 19 @ 20:00 (World Cup Final)", "t1": "Winner Match 101", "t2": "Winner Match 102"}
        ]
    }

    for round_name, round_matches in ko_structure.items():
        st.markdown(f"#### 🏆 {round_name}")
        rcs = st.columns(len(round_matches) if len(round_matches) <= 4 else 4)
        for idx, rm in enumerate(round_matches):
            col_target = rcs[idx % 4]
            with col_target:
                st.markdown(f"""
                <div style="background:#FFF; padding:8px; border-radius:6px; border:1px solid #ff7d23; margin-bottom:8px;">
                    <span style="font-size:10px; color:#ff7d23; font-weight:800; display:block;">🕒 {rm['date']}</span>
                    <span style="font-size:12px; font-weight:700; color:#333; display:block; margin-top:3px;">⚽ {rm['t1']}</span>
                    <span style="font-size:12px; font-weight:700; color:#333; display:block;">⚽ {rm['t2']}</span>
                </div>
                """, unsafe_allow_html=True)

# ── COLLAPSIBLE MODULE 2: GROUP STAGE STATE TABLES ──
with st.expander("📊 GROUP STAGE LIVE TABLES", expanded=group_open):
    g_keys = list(processed_standings.keys())
    for i in range(0, len(g_keys), 2):
        r_cols = st.columns(2)
        for j in range(2):
            if i + j < len(g_keys):
                gname = g_keys[i + j]
                t_rows = processed_standings[gname]
                
                with r_cols[j]:
                    st.markdown(f"<span class='group-header-text'>🔹 {gname}</span>", unsafe_allow_html=True)
                    t_html = """<div class="table-responsive-wrapper"><table class="custom-dashboard-table">
                        <thead><tr><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead><tbody>"""
                    
                    for ranking_pos, r in enumerate(t_rows, start=1):
                        owner = SWEEPSTAKE_MAPPING.get(r["name"], "Unassigned")
                        
                        # Apply Status Validation progress dot indicators explicitly to right of owner names
                        dot_indicator = ""
                        if r["played"] == 3:
                            if ranking_pos <= 2:
                                dot_indicator = "<span class='status-dot dot-green'></span>"
                            elif ranking_pos == 3 and r["name"] in highest_8_third_place:
                                dot_indicator = "<span class='status-dot dot-green'></span>"
                            else:
                                dot_indicator = "<span class='status-dot dot-red'></span>"

                        t_html += f"""<tr>
                            <td>{get_group_flag_html(r['name'])}<b>{r['name']}</b> <span style="font-size:11px; color:#666;">({owner}){dot_indicator}</span></td>
                            <td>{r['played']}</td><td>{r['won']}</td><td>{r['draw']}</td><td>{r['lost']}</td><td>{r['gd']}</td><td><b>{r['pts']}</b></td>
                        </tr>"""
                    t_html += "</tbody></table></div>"
                    st.markdown(t_html, unsafe_allow_html=True)

# ── SEPARATED DASHBOARD OVERPERFORMANCE BOARD MODULE ──
st.markdown("<h2 style='text-align:center; margin:25px 0 5px 0;'>📈 OUTRIGHT OVERPERFORMANCE LEADERBOARD</h2>", unsafe_allow_html=True)

master_flat_leaderboard = []
for gname, rows in processed_standings.items():
    for r in rows:
        master_flat_leaderboard.append(r.copy())

if master_flat_leaderboard:
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

    master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))

    op_table_html = """
    <div class="table-responsive-wrapper">
        <table class="custom-dashboard-table" style="width:100%;">
            <thead>
                <tr>
                    <th>Pos</th>
                    <th>Team</th>
                    <th>Expected Rank</th>
                    <th>Actual Rank</th>
                    <th>Played</th>
                    <th>GD</th>
                    <th>Points</th>
                    <th style="text-align:right; padding-right:15px;">Differential Score</th>
                </tr>
            </thead>
            <tbody>"""
    
    for idx, r in enumerate(master_flat_leaderboard, start=1):
        owner = SWEEPSTAKE_MAPPING.get(r["name"], "Unassigned")
        op_formatted = f"+{r['overperformance']}" if r['overperformance'] > 0 else str(r['overperformance'])
        score_color = "#107C41" if r['overperformance'] > 0 else ("#A80000" if r['overperformance'] < 0 else "#333333")
        
        op_table_html += f"""<tr>
            <td><b>#{idx}</b></td>
            <td>{get_group_flag_html(r['name'])}<b>{r['name']}</b> <span style='font-size:11px; color:#666;'>({owner})</span></td>
            <td>#{r['expected_rank']}</td>
            <td>#{r['actual_rank']}</td>
            <td>{r['played']}</td>
            <td>{r['gd']}</td>
            <td><b>{r['pts']}</b></td>
            <td style='text-align:right; padding-right:15px; font-weight:800; color:{score_color};'>{op_formatted}</td>
        </tr>"""
    op_table_html += "</tbody></table></div>"
    st.markdown(op_table_html, unsafe_allow_html=True)

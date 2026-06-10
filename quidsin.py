import streamlit as st
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import os

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="Byway World Cup Sweepstake",
    page_icon="⚽",
    layout="wide"
)

# Run page auto-refresh every 30 seconds to keep live scores syncing
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Custom branding & layout styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        p, span, div, label, small, td, th, b {
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        h1, h2, h3 {
            color: #FF6B00 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        .title-area h1 { margin: 0px !important; font-size: 28px; font-weight: 900 !important; }
        .title-area p { margin: 4px 0px 0px 0px !important; color: #555555 !important; font-weight: 700 !important; font-size: 16px; }
        .next-match-banner {
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%) !important;
            padding: 15px; border-radius: 10px; box-shadow: 0px 3px 10px rgba(0,0,0,0.08); margin: 15px 0px;
            display: flex; flex-direction: column; gap: 10px; text-align: center; color: #FFFFFF !important;
        }
        .next-match-title { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 800 !important; opacity: 0.9; }
        .next-match-teams { font-size: 18px; font-weight: 800 !important; }
        .next-match-teams span { font-size: 13px; font-weight: 400 !important; opacity: 0.85; }
        .next-match-time { font-size: 14px; font-weight: 700 !important; background: rgba(25, 25, 25, 0.15) !important; padding: 6px 14px; border-radius: 6px; display: inline-block; }
        .stat-banner-box {
            background: #FFFFFF !important; padding: 12px 20px; border-radius: 8px; border: 2px solid #EAEAEA;
            display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;
        }
        .stat-banner-box medium { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 800 !important; color: #FF6B00 !important; }
        .stat-banner-box span { font-size: 14px; font-weight: 800 !important; text-align: right; }
        .table-responsive-wrapper { width: 100%; overflow-x: auto; margin-bottom: 20px; }
        .custom-dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .custom-dashboard-table th { background-color: #FAFAFA !important; border-bottom: 2px solid #FF6B00; padding: 8px 6px; }
        .custom-dashboard-table td { padding: 8px 6px; border-bottom: 1px solid #EAEAEA; background-color: #FFFFFF !important; }
        .fixture-row {
            background-color: #FFFFFF !important; padding: 8px 10px; border-radius: 4px; margin-bottom: 4px; border: 1px solid #EAEAEA;
            font-size: 12px; display: flex; align-items: center; justify-content: space-between;
        }
        .flag-img { width: 20px !important; height: 14px !important; object-fit: cover !important; display: inline-block; margin: 0px 4px; }
        .group-header-text { color: #FF6B00 !important; font-size: 18px; font-weight: 800 !important; margin-bottom: 8px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN", "placeholder")
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

SWEEPSTAKE_MAPPING = {
    "Mexico": "Evon", "South Africa": "Iwan", "Canada": "Holly", "Switzerland": "Yannis",
    "Argentina": "Alba", "France": "Marc", "Brazil": "Andy", "Spain": "Ciaran",
    "Bosnia-Herzegovina": "Izzy", "Czechia": "Pablo", "Qatar": "Jess", "Morocco": "Bartek",
    "Haiti": "Hatty", "Turkey": "Adrienne", "Paraguay": "Becca", "Germany": "Oliwia",
    "Curaçao": "Justin", "Ecuador": "Cat", "Japan": "Adem", "Belgium": "Mart",
    "Egypt": "Chris", "Tunisia": "Jess 2", "Netherlands": "Ellis", "Ivory Coast": "Suzie",
    "Australia": "Amy", "Cape Verde Islands": "Justin 2", "Uruguay": "Paul 2", "Sweden": "Kat",
    "Saudi Arabia": "Aurelie", "Scotland": "Elaine 2", "United States": "Neil", "Senegal": "Sara",
    "New Zealand": "James", "Iran": "Elaine", "Iraq": "Paul", "Norway": "Claire",
    "Algeria": "Adrienne 2", "Austria": "Rich", "Jordan": "Maria", "Congo DR": "Izzy",
    "Portugal": "Lucy 2", "Uzbekistan": "Kat 2", "Colombia": "Neil 2", "England": "Marijke",
    "Panama": "Lucy", "Ghana": "Sam", "Croatia": "Kurt", "South Korea": "Beau",
}

EXPECTED_RANKINGS = {
    "France": 1, "Spain": 2, "Argentina": 3, "England": 4, "Portugal": 5, "Brazil": 6,
    "Netherlands": 7, "Morocco": 8, "Belgium": 9, "Germany": 10, "Croatia": 11, "Colombia": 12,
    "Senegal": 13, "Mexico": 14, "United States": 15, "Uruguay": 16, "Japan": 17, "Switzerland": 18,
    "Iran": 19, "Turkey": 20, "Ecuador": 21, "Austria": 22, "South Korea": 23, "Australia": 24,
    "Algeria": 25, "Egypt": 26, "Canada": 27, "Norway": 28, "Panama": 29, "Ivory Coast": 30,
    "Sweden": 31, "Paraguay": 32, "Czechia": 33, "Scotland": 34, "Tunisia": 35, "Congo DR": 36, 
    "DR Congo": 36, "Uzbekistan": 37, "Qatar": 38, "Iraq": 39, "South Africa": 40, "Saudi Arabia": 41,
    "Jordan": 42, "Bosnia-Herzegovina": 43, "Cape Verde Islands": 44, "Cape Verde": 44, "Ghana": 45, 
    "Curaçao": 46, "Haiti": 47, "New Zealand": 48
}

def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        return dt_utc.astimezone(pytz.timezone("Europe/London"))
    except: return None

# Data Retrieval
next_home, next_away, next_home_owner, next_away_owner, next_date = "None", "Scheduled", "", "", ""
all_matches, standings_list, master_flat_leaderboard = [], [], []
top_performer_text = "N/A"

if API_TOKEN != "placeholder":
    try:
        standings_res = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings", headers=HEADERS).json()
        standings_list = standings_res.get("standings", [])
        
        for group in standings_list:
            for row in group.get("table", []):
                t_info = row.get("team", {})
                master_flat_leaderboard.append({
                    "name": t_info.get("name"), "crest": t_info.get("crest"),
                    "played": row.get("playedGames"), "won": row.get("won"),
                    "drawn": row.get("draw"), "lost": row.get("lost"),
                    "gf": row.get("goalsFor"), "ga": row.get("goalsAgainst"),
                    "gd": row.get("goalDifference"), "pts": row.get("points")
                })
        
        if master_flat_leaderboard:
            master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
            for idx, item in enumerate(master_flat_leaderboard, start=1):
                exp = EXPECTED_RANKINGS.get(item["name"], 25)
                item.update({"actual_rank": idx, "expected_rank": exp, "overperformance": exp - idx})
            best = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
            top_performer_text = f"{best['name']} ({SWEEPSTAKE_MAPPING.get(best['name'], 'Unassigned')})"
            
        all_matches = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches", headers=HEADERS).json().get("matches", [])
        upcoming = sorted([m for m in all_matches if m.get("status") in ["TIMED", "SCHEDULED"]], key=lambda x: x.get("utcDate", ""))
        if upcoming:
            m = upcoming[0]
            next_home, next_away = m.get("homeTeam", {}).get("name", "TBD"), m.get("awayTeam", {}).get("name", "TBD")
            next_home_owner, next_away_owner = f"({SWEEPSTAKE_MAPPING.get(next_home, 'Unassigned')})", f"({SWEEPSTAKE_MAPPING.get(next_away, 'Unassigned')})"
            dt = format_to_uk_time(m.get("utcDate"))
            next_date = dt.strftime("%d/%m @ %H:%M") if dt else "TBD"
    except: pass

# --- UI Rendering ---
st.markdown("<div class='title-area'><h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1><p>Live standings</p></div>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="next-match-banner">
        <div class="next-match-title">⏳ Next Match</div>
        <div class="next-match-teams">
            {next_home} <span>{next_home_owner}</span> v {next_away} <span>{next_away_owner}</span>
        </div>
        <div class="next-match-time">🗓️ {next_date}</div>
    </div>
""", unsafe_allow_html=True)

stat_cols = st.columns(3)
stat_cols[0].markdown(f'<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
stat_cols[1].markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({SWEEPSTAKE_MAPPING.get("France")})</span></div>', unsafe_allow_html=True)
stat_cols[2].markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Standings Loop
for i in range(0, len(standings_list), 2):
    row_cols = st.columns(2)
    for j in range(2):
        if i + j < len(standings_list):
            group = standings_list[i + j]
            with row_cols[j]:
                st.markdown(f"<span class='group-header-text'>🔹 {group.get('group')}</span>", unsafe_allow_html=True)
                table_html = "<div class='table-responsive-wrapper'><table class='custom-dashboard-table'><thead><tr><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead><tbody>"
                for row in group.get("table", []):
                    name, crest = row.get("team", {}).get("name"), row.get("team", {}).get("crest")
                    table_html += f"<tr><td><img src='{crest}' class='flag-img'> <b>{name}</b> <small>({SWEEPSTAKE_MAPPING.get(name, 'Unassigned')})</small></td><td>{row.get('playedGames')}</td><td>{row.get('won')}</td><td>{row.get('draw')}</td><td>{row.get('lost')}</td><td>{row.get('goalDifference')}</td><td><b>{row.get('points')}</b></td></tr>"
                st.markdown(table_html + "</tbody></table></div>", unsafe_allow_html=True)
                
                # Fixtures
                st.markdown("<span style='font-size:12px; font-weight:700; color:#FF6B00;'>📅 Group Fixtures</span>", unsafe_allow_html=True)
                group_fixtures = [m for m in all_matches if m.get("homeTeam", {}).get("name") in [r.get("team", {}).get("name") for r in group.get("table", [])]]
                for match in group_fixtures[:4]:
                    h, a = match.get("homeTeam", {}).get("name"), match.get("awayTeam", {}).get("name")
                    st.markdown(f"<div class='fixture-row'><span>{h}</span> <span>{match.get('score', {}).get('fullTime', {}).get('home', '-')} : {match.get('score', {}).get('fullTime', {}).get('away', '-')}</span> <span>{a}</span></div>", unsafe_allow_html=True)
                st.write("<br>")

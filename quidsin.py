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

# Custom branding & layout safety styles with strict light-mode overrides and Figtree font
st.markdown("""
    <style>
        /* Import Figtree from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');

        /* Force global app body background, standard text, and Figtree font */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        
        /* Force all standard text elements to stay dark charcoal and use Figtree */
        p, span, div, label, small, td, th, b {
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        
        /* Keep headers fixed to brand orange and use Figtree with heavy weight */
        h1, h2, h3 {
            color: #FF6B00 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        
        .header-container {
            border-bottom: 2px solid #FF6B00;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title-area h1 {
            margin: 0px !important;
            font-size: 28px;
            font-weight: 900 !important;
        }
        .title-area p {
            margin: 4px 0px 0px 0px !important;
            color: #555555 !important;
            font-weight: 700 !important;
            font-size: 16px;
        }
        
        /* --- NEW SPLIT-SCREEN BANNER CSS --- */
        .match-banner-container {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 15px 0px;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD;
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%);
        }
        .banner-top-pane { background-color: rgba(0,0,0,0.2); padding: 10px 20px; }
        .next-match-title {
            font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: 800 !important;
            color: #FFFFFF !important; background: rgba(255, 255, 255, 0.2); padding: 4px 10px;
            border-radius: 6px; display: inline-block;
        }
        .matchup-split-screen { display: flex; position: relative; align-items: center; }
        .team-panel { width: 50%; display: flex; align-items: center; padding: 20px; box-sizing: border-box; height: 90px; }
        .home-panel { justify-content: flex-end; padding-right: 45px; border-right: 1px solid rgba(255,255,255,0.3); }
        .away-panel { justify-content: flex-start; padding-left: 45px; }
        .team-panel-text { color: #FFFFFF !important; font-size: 18px; font-weight: 900 !important; text-shadow: 0px 1px 2px rgba(0,0,0,0.3); }
        .team-panel-text span { font-size: 12px; font-weight: 400 !important; display: block; opacity: 0.9; }
        .vs-marker-bubble {
            position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
            z-index: 10; background-color: #FFFFFF; color: #FF6B00 !important;
            font-size: 12px; font-weight: 900 !important; padding: 6px; border-radius: 50%;
            border: 2px solid #FF6B00; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .banner-bottom-time { background-color: rgba(0,0,0,0.2); padding: 8px; font-size: 13px; font-weight: 700 !important; color: #FFFFFF !important; }

        /* Responsive Table Canvas Controls */
        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 20px;
        }
        
        .custom-dashboard-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
            white-space: nowrap;
            font-family: 'Figtree', sans-serif !important;
        }
        .custom-dashboard-table th {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-weight: 700 !important;
            padding: 8px 6px;
            border-bottom: 2px solid #FF6B00;
        }
        .custom-dashboard-table td {
            padding: 8px 6px;
            border-bottom: 1px solid #EAEAEA;
            vertical-align: middle;
            background-color: #FFFFFF !important;
            color: #333333 !important;
        }
        /* Ensure table text markers are protected */
        .custom-dashboard-table td b, .custom-dashboard-table td span {
            color: #333333 !important;
        }

        /* Custom compact match list element */
        .fixture-row {
            background-color: #FFFFFF !important;
            padding: 8px 10px;
            border-radius: 4px;
            margin-bottom: 4px;
            border: 1px solid #EAEAEA;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'Figtree', sans-serif !important;
        }
        .fixture-row div, .fixture-row span, .fixture-row b {
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        .flag-img {
            vertical-align: middle;
            margin: 0px 4px;
            width: 20px !important;
            height: 14px !important;
            object-fit: cover !important;
            display: inline-block;
        }
        .group-header-text {
            color: #FF6B00 !important;
            font-family: 'Figtree', sans-serif !important;
            font-size: 18px;
            font-weight: 800 !important;
            margin-bottom: 8px;
            display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN", "placeholder")
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Sweepstake Mappings
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

TEAM_COLORS = {
    "Mexico": "#006847", "South Africa": "#007A4D", "Canada": "#FF0000", "Switzerland": "#D52B1E",
    "Argentina": "#74ACDF", "France": "#002395", "Brazil": "#009739", "Spain": "#AA151B",
    "Bosnia-Herzegovina": "#002F6C", "Czechia": "#11457E", "Qatar": "#8A1538", "Morocco": "#C1272D",
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

# Baseline Expected Rankings Map
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

# Helper to convert UTC time strings safely to UK Local Time
def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except Exception:
        return None

# Fallbacks
next_home = "None"
next_away = "Scheduled"
next_home_owner = ""
next_away_owner = ""
next_date = ""

all_matches = []
standings_list = []
master_flat_leaderboard = []
top_performer_text = "N/A"

if API_TOKEN != "placeholder":
    try:
        # Fetch Standings Data
        standings_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings"
        standings_res = requests.get(standings_url, headers=HEADERS)
        standings_list = standings_res.json().get("standings", [])
        
        # Build Master Flat Leaderboard across all groups combined
        for group in standings_list:
            for row in group.get("table", []):
                t_info = row.get("team", {})
                t_name = t_info.get("name", "Unknown")
                master_flat_leaderboard.append({
                    "name": t_name,
                    "crest": t_info.get("crest", ""),
                    "played": row.get("playedGames", 0),
                    "won": row.get("won", 0),
                    "drawn": row.get("draw", 0),
                    "lost": row.get("lost", 0),
                    "gf": row.get("goalsFor", 0),
                    "ga": row.get("goalsAgainst", 0),
                    "gd": row.get("goalDifference", 0),
                    "pts": row.get("points", 0)
                })
        
        # Sort calculation: Pts DESC, Won DESC, GD DESC, GF DESC, Alphabetical ASC
        if master_flat_leaderboard:
            master_flat_leaderboard.sort(
                key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"])
            )
            
            # Compute overperformance values
            for idx, team_item in enumerate(master_flat_leaderboard, start=1):
                name = team_item["name"]
                expected_rank = EXPECTED_RANKINGS.get(name, 25)
                team_item["actual_rank"] = idx
                team_item["expected_rank"] = expected_rank
                team_item["overperformance"] = expected_rank - idx
            
            best_overperformer = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
            op_owner = SWEEPSTAKE_MAPPING.get(best_overperformer["name"], "Unassigned")
            top_performer_text = f"{best_overperformer['name']} ({op_owner})"
        
        # Fetch Match Data
        matches_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        matches_res = requests.get(matches_url, headers=HEADERS)
        all_matches = matches_res.json().get("matches", [])
        
        # Extract the absolute next upcoming match
        if all_matches:
            upcoming_matches = [m for m in all_matches if m.get("status") in ["TIMED", "SCHEDULED"]]
            if upcoming_matches:
                upcoming_matches.sort(key=lambda x: x.get("utcDate", ""))
                next_m = upcoming_matches[0]
                
                next_home = next_m.get("homeTeam", {}).get("name", "TBD")
                next_away = next_m.get("awayTeam", {}).get("name", "TBD")
                next_home_owner = f" ({SWEEPSTAKE_MAPPING.get(next_home, 'Unassigned')})"
                next_away_owner = f" ({SWEEPSTAKE_MAPPING.get(next_away, 'Unassigned')})"
                
                dt_uk = format_to_uk_time(next_m.get("utcDate"))
                if dt_uk:
                    day = dt_uk.day
                    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
                    next_date = dt_uk.strftime(f"{day}{suffix} %B @ %H:%M")
                else:
                    next_date = "TBD"
    except Exception:
        next_home, next_away, next_date = "API Connection", "Error", ""

# 1. Fetching crests correctly for the banner
def get_crest(team_name):
    for group in standings_list:
        for row in group.get("table", []):
            if row.get("team", {}).get("name") == team_name:
                return row.get("team", {}).get("crest", "")
    return ""

# --- BRANDING HEADER TITLE ---
st.markdown("""
    <div class="title-area">
        <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings</p>
    </div>
""", unsafe_allow_html=True)

# --- NEW STABLE BANNER ---
st.markdown("<div style='margin-top: 20px; font-size: 11px; font-weight: 800; color: #666; text-transform: uppercase;'>⏳ Next Match</div>", unsafe_allow_html=True)

# Create 3 columns: Home, VS, Away
cols = st.columns([5, 1, 5])

home_col_color = TEAM_COLORS.get(next_home, "#FF6B00")
away_col_color = TEAM_COLORS.get(next_away, "#FF6B00")

with cols[0]:
    st.markdown(f"""
        <div style="background-color: {home_col_color}; color: white; padding: 15px; border-radius: 10px 0 0 10px; text-align: center;">
            <img src="{get_crest(next_home)}" style="width: 40px; margin-bottom: 5px;">
            <div style="font-weight: 900; font-size: 18px;">{next_home}</div>
            <div style="font-size: 12px; opacity: 0.8;">{next_home_owner.replace('(','').replace(')','')}</div>
        </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown("""
        <div style="background-color: #333; color: white; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 12px;">
            VS
        </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
        <div style="background-color: {away_col_color}; color: white; padding: 15px; border-radius: 0 10px 10px 0; text-align: center;">
            <img src="{get_crest(next_away)}" style="width: 40px; margin-bottom: 5px;">
            <div style="font-weight: 900; font-size: 18px;">{next_away}</div>
            <div style="font-size: 12px; opacity: 0.8;">{next_away_owner.replace('(','').replace(')','')}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div style='text-align: center; margin-top: 10px; font-weight: 700; color: #333;'>🗓️ {next_date}</div>", unsafe_allow_html=True)

# --- REPLACED SPLIT-SCREEN BANNER ---
st.markdown(f"""
    <div style="display: flex; height: 100px; border-radius: 12px; overflow: hidden; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); margin: 20px 0;">
        <div style="flex: 1; background-color: {home_color}; color: white; display: flex; align-items: center; justify-content: center; flex-direction: column; font-weight: 800;">
            <img src="{h_crest}" style="width: 30px; margin-bottom: 4px;">
            <div style="font-size: 14px;">{next_home}</div>
            <div style="font-size: 10px; opacity: 0.8;">{next_home_owner.replace('(','').replace(')','')}</div>
        </div>
        <div style="background-color: #333; color: white; display: flex; align-items: center; padding: 0 15px; font-weight: 900; font-size: 12px;">VS</div>
        <div style="flex: 1; background-color: {away_color}; color: white; display: flex; align-items: center; justify-content: center; flex-direction: column; font-weight: 800;">
            <img src="{a_crest}" style="width: 30px; margin-bottom: 4px;">
            <div style="font-size: 14px;">{next_away}</div>
            <div style="font-size: 10px; opacity: 0.8;">{next_away_owner.replace('(','').replace(')','')}</div>
        </div>
    </div>
    <div style="text-align: center; font-weight: 700; color: #333; margin-top: -15px; margin-bottom: 20px;">
        🗓️ {next_date}
    </div>
""", unsafe_allow_html=True)

# --- TRIPLE STATS ROW ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #FF6B00;'>", unsafe_allow_html=True)

# 3. Render Dashboard Core Content Loop
if API_TOKEN == "placeholder":
    st.warning("⚠️ Using placeholder API key. Please insert your true Football-Data.org token to pull live group lists and matches.")
else:
    if standings_list:
        for i in range(0, len(standings_list), 2):
            row_cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(standings_list):
                    group_data = standings_list[i + j]
                    group_name = group_data.get("group")
                    
                    teams_in_group = [row.get("team", {}).get("name") for row in group_data.get("table", [])]
                    
                    with row_cols[j]:
                        st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)
                        
                        # --- MOBILE SAFENED GROUP TABLES ---
                        table_html = """
                        <div class="table-responsive-wrapper">
                            <table class="custom-dashboard-table">
                                <thead>
                                    <tr>
                                        <th>Team</th>
                                        <th style="text-align:center;">P</th>
                                        <th style="text-align:center;">W</th>
                                        <th style="text-align:center;">D</th>
                                        <th style="text-align:center;">L</th>
                                        <th style="text-align:center;">GF</th>
                                        <th style="text-align:center;">GA</th>
                                        <th style="text-align:center;">GD</th>
                                        <th style="text-align:center;">Pts</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """
                        
                        for row in group_data.get("table", []):
                            team_info = row.get("team", {})
                            t_name = team_info.get("name")
                            t_crest = team_info.get("crest", "")
                            owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                            flag_html = f'<img src="{t_crest}" class="flag-img">' if t_crest else ''
                            
                            table_html += "<tr>"
                            table_html += f'<td>{flag_html} <b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner})</span></td>'
                            table_html += f'<td style="text-align:center;">{row.get("playedGames")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("won")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("draw")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("lost")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("goalsFor")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("goalsAgainst")}</td>'
                            table_html += f'<td style="text-align:center;">{row.get("goalDifference")}</td>'
                            table_html += f'<td style="text-align:center;"><b>{row.get("points")}</b></td>'
                            table_html += "</tr>"
                            
                        table_html += "</tbody></table></div>"
                        
                        st.markdown(table_html, unsafe_allow_html=True)
                        
                        # --- CHRONOLOGICAL FIXTURES SUBSECTION ---
                        st.write("<span style='font-size:12px; font-weight:700; color:#FF6B00;'>📅 Group Fixtures & Results</span>", unsafe_allow_html=True)
                        
                        group_fixtures = [m for m in all_matches if m.get("homeTeam", {}).get("name") in teams_in_group or m.get("awayTeam", {}).get("name") in teams_in_group]
                        
                        if not group_fixtures:
                            st.caption("No fixtures currently listed for this group.")
                        else:
                            group_fixtures.sort(key=lambda x: x.get("utcDate", ""))
                            for match in group_fixtures[:6]:
                                m_status = match.get("status")
                                home_t, away_t = match.get("homeTeam", {}), match.get("awayTeam", {})
                                h_name, a_name = home_t.get("name", "TBD"), away_t.get("name", "TBD")
                                h_owner, a_owner = SWEEPSTAKE_MAPPING.get(h_name, "Unassigned"), SWEEPSTAKE_MAPPING.get(a_name, "Unassigned")
                                
                                dt_uk = format_to_uk_time(match.get("utcDate"))
                                local_time_str = dt_uk.strftime("%d/%m %H:%M") if dt_uk else "TBD"
                                h_flag = f'<img src="{home_t.get("crest", "")}" class="flag-img">' if home_t.get("crest") else ''
                                a_flag = f'<img src="{away_t.get("crest", "")}" class="flag-img">' if away_t.get("crest") else ''
                                
                                if m_status == "FINISHED":
                                    display_score = f"<b>{match.get('score', {}).get('fullTime', {}).get('home')} - {match.get('score', {}).get('fullTime', {}).get('away')}</b>"
                                elif m_status in ["IN_PLAY", "PAUSED"]:
                                    display_score = f"<span style='color:red; font-weight:700;'>🔴 {match.get('score', {}).get('fullTime', {}).get('home', 0)}-{match.get('score', {}).get('fullTime', {}).get('away', 0)}</span>"
                                else:
                                    display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                
                                st.markdown(f"""
                                    <div class="fixture-row">
                                        <div style="text-align: left; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            {h_flag} <span>{h_name}</span> <span style="font-size:9px; color:#777;">({h_owner})</span>
                                        </div>
                                        <div style="text-align: center; width: 16%; font-size:11px;">
                                            {display_score}
                                        </div>
                                        <div style="text-align: right; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            <span style="font-size:9px; color:#777;">({a_owner})</span> <span>{a_name}</span> {a_flag}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        st.write("<br>", unsafe_allow_html=True)

        # --- OVERPERFORMANCE LEADERBOARD ---
        st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 3px solid #FF6B00;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overperformance table</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 13px; margin-bottom: 20px;'>Ranked by overperformance: (Rank - Performance)</p>", unsafe_allow_html=True)
        
        master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))
        
        master_table_html = """
        <div class="table-responsive-wrapper">
            <table class="custom-dashboard-table" style="width:100%;">
                <thead>
                    <tr>
                        <th style="width: 60px;">Pos</th>
                        <th>Team</th>
                        <th style="text-align:center;">Rank</th>
                        <th style="text-align:center;">Actual</th>
                        <th style="text-align:center;">P</th>
                        <th style="text-align:center;">GD</th>
                        <th style="text-align:center;">Pts</th>
                        <th style="text-align:right; padding-right:15px;">Score</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
            owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
            flag_html = f'<img src="{team_row["crest"]}" class="flag-img">' if team_row["crest"] else ''
            
            pos_str = f"🚀 {display_idx}" if display_idx == 1 else str(display_idx)
            op_val = team_row["overperformance"]
            op_formatted = f"+{op_val}" if op_val > 0 else str(op_val)
            score_color = "#107C41" if op_val > 0 else ("#A80000" if op_val < 0 else "#333333")
            
            master_table_html += "<tr>"
            master_table_html += f"<td><b>{pos_str}</b></td>"
            master_table_html += f"<td>{flag_html} <b>{team_row['name']}</b> <span style='font-size:11px; color:#666;'>({owner})</span></td>"
            master_table_html += f"<td style='text-align:center; color:#555;'>#{team_row['expected_rank']}</td>"
            master_table_html += f"<td style='text-align:center; color:#555;'>#{team_row['actual_rank']}</td>"
            master_table_html += f"<td style='text-align:center;'>{team_row['played']}</td>"
            master_table_html += f"<td style='text-align:center;'>{team_row['gd']}</td>"
            master_table_html += f"<td style='text-align:center;'>{team_row['pts']}</td>"
            master_table_html += f"<td style='text-align:right; padding-right:15px; color:{score_color}; font-weight:bold;'>{op_formatted}</td>"
            master_table_html += "</tr>"
            
        master_table_html += "</tbody></table></div>"
        
        m_center_cols = st.columns([1, 10, 1])
        with m_center_cols[1]:
            st.markdown(master_table_html, unsafe_allow_html=True)

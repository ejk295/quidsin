import streamlit as st
import requests
from datetime import datetime
import pytz
import os
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

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
        
        /* All text elements */
        p, span, div, label, small, td, th, b {
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #FF6B00 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        
        /* Title area */
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

        /* Next match banner styles (mobile responsive) */
        .next-match-banner {
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%) !important;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
            margin: 15px 0px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            text-align: center;
            font-family: 'Figtree', sans-serif !important;
        }
        @media (min-width: 768px) {
            .next-match-banner {
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
        }
        /* ... (rest of your existing styles for banners, tables, etc.) ... */

        /* --- Key Players Banner Styles (new) --- */
        .key-players-banner {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 20px 0;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD;
            background-color: #fff; /* optional background */
        }
        .key-players-header {
            background-color: #006847; /* same as your theme */
            padding: 10px 20px;
            color: #fff;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .key-players-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            padding: 10px 0;
        }
        .key-player-card {
            width: 130px;
            height: 130px;
            background: #fff;
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            margin: 8px;
            padding: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            text-align: center;
            display: inline-block;
        }
        .key-player-card img {
            width: 100%;
            height: 90px;
            object-fit: contain;
            border-radius: 4px;
        }
        .key-player-name {
            font-size: 11px;
            font-weight: 800;
            color: #333;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .key-player-team {
            font-size: 9px;
            font-weight: 600;
            color: #006847;
            margin-top: 2px;
            text-transform: uppercase;
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

# --- HEADER ---
st.markdown("""
    <div class="title-area">
        <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings</p>
    </div>
""", unsafe_allow_html=True)

# --- NEW FULL-WIDTH NEXT MATCH BANNER ---
st.markdown(f"""
    <div class="next-match-banner">
        <div class="next-match-title">⏳ Next Match</div>
        <div class="matchup-split-screen">
            <div class="team-panel home-panel" style="background-color: #FF6B00;">
                {next_home}<span>{next_home_owner}</span>
            </div>
            <div class="vs-marker-bubble">VS</div>
            <div class="team-panel away-panel" style="background-color: #FF8533;">
                {next_away}<span>{next_away_owner}</span>
            </div>
        </div>
        <div class="banner-bottom-time">🗓️ {next_date}</div>
    </div>
""", unsafe_allow_html=True)

# --- STATS ROW ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #FF6B00;'>", unsafe_allow_html=True)

# --- GROUPS CANVAS ---
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
                        # Wrap inside structural spacing class
                        st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                        st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)
                        
                        # Render Standings Table
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
                            
                            table_html += f"""<tr>
                                <td>{flag_html} <b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner})</span></td>
                                <td style="text-align:center;">{row.get("playedGames")}</td>
                                <td style="text-align:center;">{row.get("won")}</td>
                                <td style="text-align:center;">{row.get("draw")}</td>
                                <td style="text-align:center;">{row.get("lost")}</td>
                                <td style="text-align:center;">{row.get("goalsFor")}</td>
                                <td style="text-align:center;">{row.get("goalsAgainst")}</td>
                                <td style="text-align:center;">{row.get("goalDifference")}</td>
                                <td style="text-align:center;"><b>{row.get("points")}</b></td>
                            </tr>"""
                            
                        table_html += "</tbody></table></div>"
                        st.markdown(table_html, unsafe_allow_html=True)
                        
                        # Render Group Fixtures - wrapped in a tight flex/spacing div
                        st.markdown("<div style='margin-bottom:6px;'><span style='font-size:12px; font-weight:700; color:#006847;'>📅 Group Fixtures & Results</span></div>", unsafe_allow_html=True)
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
            
            master_table_html += f"""<tr>
                <td><b>{pos_str}</b></td>
                <td>{flag_html} <b>{team_row['name']}</b> <span style='font-size:11px; color:#666;'>({owner})</span></td>
                <td style='text-align:center; color:#555;'>#{team_row['expected_rank']}</td>
                <td style='text-align:center; color:#555;'>#{team_row['actual_rank']}</td>
                <td style='text-align:center;'>{team_row['played']}</td>
                <td style='text-align:center;'>{team_row['gd']}</td>
                <td style='text-align:center;'><b>{team_row['pts']}</b></td>
                <td style='text-align:right; padding-right:15px; font-weight:800; color:{score_color};'>{op_formatted}</td>
            </tr>"""
            
        master_table_html += "</tbody></table></div>"
        st.markdown(master_table_html, unsafe_allow_html=True)

# --- Key Players Section (New) ---
# Loop through the groups again or just use one group for demonstration
# Here, for simplicity, I add it after the first group only
# (you can place it wherever you want, or inside the loop for each group)

# For the example, adding after the first group:
if 'teams_in_group' in locals() and teams_in_group:
    st.markdown('<div class="key-players-banner">', unsafe_allow_html=True)
    st.markdown('<div class="key-players-header">🌟 Key Players</div>', unsafe_allow_html=True)

    active_cards = []
    for team_name in teams_in_group:
        if team_name in GROUP_PLAYERS:
            p = GROUP_PLAYERS[team_name]
            card_html = f"""
            <div class="key-player-card">
                <img src="{p['img_url']}" loading="eager" referrerpolicy="no-referrer">
                <div class="key-player-name">{p['player_name']}</div>
                <div class="key-player-team">{team_name}</div>
            </div>
            """
            active_cards.append(card_html)

    if active_cards:
        html_content = f'<div class="key-players-container">{"".join(active_cards)}</div>'
        components.html(html_content, height=160, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

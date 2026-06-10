import os
import requests
from datetime import datetime
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="Byway World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 30 seconds to keep live scores syncing
st_autorefresh(interval=90 * 1000, key="datarefresh")

# Custom branding & layout safety styles with strict light-mode overrides and Figtree font
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');

        /* Force global app body background, standard text, and Figtree font */
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
            color: #ff7d23 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        
        /* Centered Title Area */
        .title-area {
            text-align: center !important;
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

        /* --- NEXT MATCH BANNER LAYOUT (DYNAMIC COLOURS) --- */
        .match-banner-container {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 15px 0px;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD;
        }

        .banner-top-pane {
            background-color: #111111;
            padding: 10px 20px;
        }

        .next-match-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.15);
            padding: 6px 12px;
            border-radius: 6px;
            display: inline-block;
        }

        .matchup-split-screen {
            display: flex;
            position: relative;
            align-items: center;
        }

        .team-panel {
            width: 50%;
            display: flex;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
            height: 100%;
            min-height: 80px;
        }

        .home-panel {
            justify-content: flex-end;
            padding-right: 45px;
            border-right: 2px solid #FFFFFF;
        }

        .away-panel {
            justify-content: flex-start;
            padding-left: 45px;
        }

        .team-panel-text {
            color: #FFFFFF !important;
            font-size: 20px;
            font-weight: 900 !important;
            text-shadow: 0px 1px 4px rgba(0,0,0,0.8);
            display: flex;
            flex-direction: column; /* Stack name and owner */
            justify-content: center;
        }
        
        .home-panel .team-panel-text {
            align-items: flex-end; /* Align to the right for home team */
        }
        
        .away-panel .team-panel-text {
            align-items: flex-start; /* Align to the left for away team */
        }

        .team-name-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .team-panel-text span.owner-name {
            font-size: 13px;
            font-weight: 400 !important;
            opacity: 0.9;
            color: #FFFFFF !important;
            margin-top: 4px;
        }

        .vs-marker-bubble {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            background-color: #111111;
            color: #FFFFFF !important;
            font-size: 13px;
            font-weight: 900 !important;
            padding: 6px 10px;
            border-radius: 50%;
            border: 2px solid #FFFFFF;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
        }

        .banner-bottom-time {
            background-color: #111111;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        
        .banner-flag {
            width: 32px !important;
            height: 22px !important;
            object-fit: cover !important;
            border-radius: 3px;
            border: 1px solid rgba(255,255,255,0.4);
            display: inline-block;
            vertical-align: middle;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.3);
        }

        .stat-banner-box {
            background: #FFFFFF !important;
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #EAEAEA;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
            height: auto;
            min-height: 50px;
        }
        .stat-banner-box medium {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 800 !important;
            color: #ff7d23 !important;
        }
        .stat-banner-box span {
            font-size: 14px;
            font-weight: 800 !important;
            text-align: right;
            color: #333333 !important;
        }

        /* --- IN-GROUP TEAM PLAYERS ROW --- */
        .group-players-container {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 8px !important; 
            margin-bottom: 0px !important;
            justify-content: center;
        }
        .group-player-card {
            background: #FFFFFF;
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            width: 120px;
            text-align: center;
            padding: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .group-player-card img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            object-fit: cover;
            background: #F5F5F5;
        }
        .group-player-card-name {
            font-size: 11px;
            font-weight: 800 !important;
            color: #333333 !important;
            margin-top: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .group-player-card-team {
            font-size: 9px;
            font-weight: 600 !important;
            color: #ff7d23 !important;
            text-transform: uppercase;
            margin-top: 1px;
        }

        /* Clean Separator Block for Group Rows Grid layout */
        .group-row-spacer {
            margin-bottom: 15px !important;
        }

        /* Responsive Table Canvas Controls */
        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 8px !important;
        }
        
        .custom-dashboard-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
            white-space: nowrap;
        }
        .custom-dashboard-table th {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-weight: 700 !important;
            padding: 6px 6px !important;
            border-bottom: 2px solid #ff7d23;
        }
        .custom-dashboard-table td {
            padding: 6px 6px !important;
            border-bottom: 1px solid #EAEAEA;
            vertical-align: middle;
            background-color: #FFFFFF !important;
            color: #333333 !important;
        }
        
        .fixture-row {
            background-color: #FFFFFF !important;
            padding: 6px 8px !important;
            border-radius: 4px;
            margin-bottom: 3px !important;
            border: 1px solid #EAEAEA;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
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
            color: #ff7d23 !important;
            font-size: 18px;
            font-weight: 800 !important;
            margin-bottom: 4px !important;
            margin-top: 0px !important;
            display: inline-block;
        }

        @media (max-width: 800px) {
            .match-banner-container {
                flex-direction: column;
            }
            .matchup-split-screen {
                flex-direction: column;
                width: 100%;
            }
            .team-panel {
                width: 100% !important;
                justify-content: center !important;
                padding: 15px !important;
                font-size: 16px;
            }
            .home-panel {
                border-right: none !important;
                border-bottom: 2px solid #FFFFFF;
                padding-right: 20px !important;
            }
            .away-panel {
                padding-left: 20px !important;
            }
            .vs-marker-bubble {
                top: auto;
                bottom: -14px;
                left: 50%;
                transform: translateX(-50%);
            }
        }
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
    "Bosnia-Herzegovina": "Izzy 2", "Czechia": "Pablo", "Qatar": "Jess", "Morocco": "Bartek",
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

DEFAULT_LEFT_COLOR = "#ff7d23"
DEFAULT_RIGHT_COLOR = "#ff7d23"

def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except Exception:
        return None

# Fallbacks
next_home = "Mexico"
next_away = "South Africa"
next_home_owner = "(TBC)"
next_away_owner = "(TBC)"
next_date = "11th June @ 20:00"
next_home_flag = ""
next_away_flag = ""

all_matches = []
standings_list = []
master_flat_leaderboard = []
top_performer_text = "N/A"

banner_left_color = DEFAULT_LEFT_COLOR
banner_right_color = DEFAULT_RIGHT_COLOR

if API_TOKEN != "placeholder":
    try:
        # Fetch Standings
        standings_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings"
        standings_res = requests.get(standings_url, headers=HEADERS)
        standings_list = standings_res.json().get("standings", [])
        
        for group in standings_list:
            for row in group.get("table", []):
                t_info = row.get("team", {})
                master_flat_leaderboard.append({
                    "name": t_info.get("name", "Unknown"),
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
        
        if master_flat_leaderboard:
            master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
            for idx, team_item in enumerate(master_flat_leaderboard, start=1):
                name = team_item["name"]
                expected_rank = EXPECTED_RANKINGS.get(name, 25)
                team_item["actual_rank"] = idx
                team_item["expected_rank"] = expected_rank
                team_item["overperformance"] = expected_rank - idx
            
            best_overperformer = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
            op_owner = SWEEPSTAKE_MAPPING.get(best_overperformer["name"], "Unassigned")
            top_performer_text = f"{best_overperformer['name']} ({op_owner})"
        
        # Fetch Matches
        matches_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        matches_res = requests.get(matches_url, headers=HEADERS)
        all_matches = matches_res.json().get("matches", [])
        
        if all_matches:
            upcoming_matches = [m for m in all_matches if m.get("status") in ["TIMED", "SCHEDULED"]]
            if upcoming_matches:
                upcoming_matches.sort(key=lambda x: x.get("utcDate", ""))
                next_m = upcoming_matches[0]
                
                home_team_obj = next_m.get("homeTeam", {})
                away_team_obj = next_m.get("awayTeam", {})
                
                next_home = home_team_obj.get("name", "TBD")
                next_away = away_team_obj.get("name", "TBD")
                
                banner_left_color = TEAM_COLORS.get(next_home, DEFAULT_LEFT_COLOR)
                banner_right_color = TEAM_COLORS.get(next_away, DEFAULT_RIGHT_COLOR)
                
                if banner_left_color == banner_right_color:
                    banner_right_color = "#222222" if banner_left_color != "#222222" else "#555555"

                if home_team_obj.get("crest"):
                    next_home_flag = f'<img src="{home_team_obj.get("crest")}" class="banner-flag">'
                if away_team_obj.get("crest"):
                    next_away_flag = f'<img src="{away_team_obj.get("crest")}" class="banner-flag">'
                
                next_home_owner = f"({SWEEPSTAKE_MAPPING.get(next_home, 'Unassigned')})"
                next_away_owner = f"({SWEEPSTAKE_MAPPING.get(next_away, 'Unassigned')})"
                
                dt_uk = format_to_uk_time(next_m.get("utcDate"))
                if dt_uk:
                    day = dt_uk.day
                    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
                    next_date = dt_uk.strftime(f"{day}{suffix} %B @ %H:%M")
    except Exception:
        pass

# --- HEADER ---
st.markdown("""
    <div class="title-area">
        <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings</p>
    </div>
""", unsafe_allow_html=True)

# --- DYNAMIC MATCHUP BANNER ---
banner_html = (
    '<div class="match-banner-container">'
    '    <div class="banner-top-pane">'
    '        <div class="next-match-title">⏳ Next Match</div>'
    '    </div>'
    '    '
    '    <div class="matchup-split-screen">'
    '        <div class="team-panel home-panel" style="background-color: ' + banner_left_color + ';">'
    '            <div class="team-panel-text">'
    '                <div class="team-name-row">' + next_home_flag + ' <span>' + next_home + '</span></div>'
    '                <span class="owner-name">' + next_home_owner + '</span>'
    '            </div>'
    '        </div>'
    '        '
    '        <div class="vs-marker-bubble">VS</div>'
    '        '
    '        <div class="team-panel away-panel" style="background-color: ' + banner_right_color + ';">'
    '            <div class="team-panel-text">'
    '                <div class="team-name-row"><span>' + next_away + '</span> ' + next_away_flag + '</div>'
    '                <span class="owner-name">' + next_away_owner + '</span>'
    '            </div>'
    '        </div>'
    '    </div>'
    '    '
    '    <div class="banner-bottom-time">🗓️ ' + next_date + '</div>'
    '</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

# --- STATS ROW ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #ff7d23;'>", unsafe_allow_html=True)

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
                                <td style="text-align:center; font-weight: bold; color: #ff7d23 !important;">{row.get("points")}</td>
                            </tr>"""
                        table_html += """
                                </tbody>
                            </table>
                        </div>
                        </div>
                        """
                        st.markdown(table_html, unsafe_allow_html=True)

        # --- OVERPERFORMANCE LEADERBOARD ---
        st.markdown("<hr style='margin:25px 0px; border-top: 2px solid #EAEAEA;'>", unsafe_allow_html=True)
        st.markdown("### 🚀 Overperformance Leaderboard")
        
        # Sort by best overperformance (descending), then actual rank
        overperformance_list = sorted(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]), reverse=True)
        
        op_html = """
        <div class="table-responsive-wrapper">
            <table class="custom-dashboard-table">
                <thead>
                    <tr>
                        <th style="text-align:center;">Rank</th>
                        <th>Team</th>
                        <th>Owner</th>
                        <th style="text-align:center;">Expected Rank</th>
                        <th style="text-align:center;">Actual Rank</th>
                        <th style="text-align:center;">Overperformance</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, t in enumerate(overperformance_list, start=1):
            owner = SWEEPSTAKE_MAPPING.get(t["name"], "Unassigned")
            flag_html = f'<img src="{t["crest"]}" class="flag-img">' if t.get("crest") else ""
            
            # Add poop emoji to exactly rank 48
            rank_display = f"{idx} 💩" if idx == 48 else str(idx)
            
            op_color = "#009739" if t["overperformance"] > 0 else ("#D52B1E" if t["overperformance"] < 0 else "#333333")
            
            op_html += f"""
                <tr>
                    <td style="text-align:center; font-weight:800;">{rank_display}</td>
                    <td>{flag_html} <b>{t["name"]}</b></td>
                    <td>{owner}</td>
                    <td style="text-align:center;">{t["expected_rank"]}</td>
                    <td style="text-align:center;">{t["actual_rank"]}</td>
                    <td style="text-align:center; font-weight:bold; color:{op_color} !important;">
                        {"+" if t["overperformance"] > 0 else ""}{t["overperformance"]}
                    </td>
                </tr>
            """
        op_html += """
                </tbody>
            </table>
        </div>
        """
        st.markdown(op_html, unsafe_allow_html=True)

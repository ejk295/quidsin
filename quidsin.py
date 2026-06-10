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

# Run page auto-refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Add CSS styles for your app + the Key Players section
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');

        /* Global styles */
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
        /* Title styles */
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
        /* Next Match Banner Styles */
        .next-match-banner {
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%) !important;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
            margin: 15px 0;
            display: flex;
            flex-direction: column;
            gap: 10px;
            font-family: 'Figtree', sans-serif !important;
        }
        @media (min-width: 768px) {
            .next-match-banner {
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
        }
        /* Stat banner styles */
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
            color: #006847 !important;
        }
        .stat-banner-box span {
            font-size: 14px;
            font-weight: 800 !important;
            text-align: right;
            color: #333333 !important;
        }

        /* Group table styles */
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
        /* Fixture row styles */
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
        }
        .flag-img {
            vertical-align: middle;
            margin: 0 4px;
            width: 20px !important;
            height: 14px !important;
            object-fit: cover !important;
            display: inline-block;
        }
        /* Group header text */
        .group-header-text {
            color: #FF6B00 !important;
            font-family: 'Figtree', sans-serif !important;
            font-size: 18px;
            font-weight: 800 !important;
            margin-bottom: 8px;
            display: inline-block;
        }
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
            background-color: #006847;
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
            height: 80px;
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
        /* End of styles */
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN", "placeholder")
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Your mappings and data
SWEEPSTAKE_MAPPING = { ... }  # Your existing mapping
EXPECTED_RANKINGS = { ... }    # Your existing expected rankings

# Helper for date formatting
def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except:
        return None

# Defaults
next_home = "None"
next_away = "Scheduled"
next_home_owner = ""
next_away_owner = ""
next_date = ""

all_matches = []
standings_list = []
master_flat_leaderboard = []
top_performer_text = "N/A"

# Fetch data if token available
if API_TOKEN != "placeholder":
    try:
        # Fetch standings
        standings_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings"
        standings_res = requests.get(standings_url, headers=HEADERS)
        standings_list = standings_res.json().get("standings", [])
        # Build leaderboard
        for group in standings_list:
            for row in group.get("table", []):
                t_info = row.get("team", {})
                t_name = t_info.get("name", "Unknown")
                master_flat_leaderboard.append({ ... })  # Your existing code
        # Sort and compute overperformance
        # Fetch next match
        matches_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        matches_res = requests.get(matches_url, headers=HEADERS)
        all_matches = matches_res.json().get("matches", [])
        # Process next match
        # ... (your existing code)
    except:
        pass

# --- HEADER ---
st.markdown("""
    <div class="title-area">
        <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings</p>
    </div>
""", unsafe_allow_html=True)

# --- Next Match Banner ---
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

# --- Stats Row ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #FF6B00;'>", unsafe_allow_html=True)

# --- GROUPS & FIXTURES ---
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
                        st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                        st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)
                        
                        # Render Standings Table
                        # (your existing table code)
                        # ...
                        
                        # Render Fixtures
                        # (your existing fixture code)
                        # ...
                        
                        # --- ADD KEY PLAYERS SECTION HERE ---
                        # Only do it once per group for demonstration
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
                        # --- END Key Players Section ---

# --- OVERPERFORMANCE TABLE ---
# (your existing code for leaderboard)
# ...
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

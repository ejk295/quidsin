import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Byway World Cup Sweepstake", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLING ---
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

        /* --- NEXT MATCH BANNER LAYOUT (KING FAMILY STYLE) --- */
        .match-banner-container {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 15px 0px 30px 0px;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD;
            background-color: #333333; 
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
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%); 
        }

        .away-panel {
            justify-content: flex-start;
            padding-left: 45px;
            background: #222222; 
        }

        .team-panel-text {
            color: #FFFFFF !important;
            font-size: 20px;
            font-weight: 900 !important;
            text-shadow: 0px 1px 4px rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
        }

        .team-panel-text span {
            font-size: 13px;
            font-weight: 400 !important;
            opacity: 0.9;
            color: #FFFFFF !important;
            margin: 0 8px;
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
            margin: 0 10px;
            vertical-align: middle;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.3);
        }

        /* --- STAT BOXES --- */
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
            color: #FF6B00 !important;
        }
        .stat-banner-box span {
            font-size: 14px;
            font-weight: 800 !important;
            text-align: right;
            color: #333333 !important;
        }

        /* --- TABLE STYLES --- */
        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 20px;
            background: #FFFFFF;
            border-radius: 8px;
            border: 1px solid #EAEAEA;
            padding: 10px;
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
            padding: 8px 6px;
            border-bottom: 2px solid #FF6B00;
        }
        .custom-dashboard-table td {
            padding: 8px 6px;
            border-bottom: 1px solid #EAEAEA;
            vertical-align: middle;
            background-color: #FFFFFF !important;
        }

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
            margin: 0px 4px;
            width: 20px !important;
            height: 14px !important;
            object-fit: cover !important;
            display: inline-block;
        }
        .group-header-text {
            color: #FF6B00 !important;
            font-size: 18px;
            font-weight: 800 !important;
            margin-bottom: 8px;
            display: inline-block;
            margin-top: 20px;
        }

        /* --- IN-GROUP TEAM PLAYERS ROW --- */
        .group-players-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px !important; 
            margin-bottom: 15px !important;
            justify-content: flex-start;
        }
        .group-player-card {
            background: #FFFFFF;
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            width: 120px; 
            text-align: center;
            padding: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .group-player-card img {
            width: 100%;
            height: 80px;
            border-radius: 4px;
            object-fit: cover;
            background: #F5F5F5;
            margin-bottom: 5px;
        }
        .group-player-card-name {
            font-size: 12px; 
            font-weight: 800 !important;
            color: #333333 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    </style>
""", unsafe_allow_html=True)

# --- MOCK DATA (REPLACE WITH YOUR REAL DATA) ---
# Replace this entire section with your API calls or CSV loaders
next_home = "France"
next_home_owner = "(Alice)"
next_away = "England"
next_away_owner = "(Bob)"
next_date = "June 11, 2026 - 20:00 BST"

standings_list = [
    {
        "group": "GROUP A",
        "table": [
            {"team": {"name": "France", "crest": "https://crests.football-data.org/773.png"}, "owner": "Alice", "playedGames": 2, "won": 2, "draw": 0, "lost": 0, "points": 6},
            {"team": {"name": "Italy", "crest": "https://crests.football-data.org/784.png"}, "owner": "Charlie", "playedGames": 2, "won": 1, "draw": 0, "lost": 1, "points": 3},
        ],
        "fixtures": [
            {"home": "France", "home_crest": "https://crests.football-data.org/773.png", "away": "Italy", "away_crest": "https://crests.football-data.org/784.png", "score": "2 - 1"}
        ]
    },
    {
        "group": "GROUP B",
        "table": [
            {"team": {"name": "England", "crest": "https://crests.football-data.org/770.png"}, "owner": "Bob", "playedGames": 2, "won": 2, "draw": 0, "lost": 0, "points": 6},
            {"team": {"name": "Spain", "crest": "https://crests.football-data.org/760.png"}, "owner": "Dave", "playedGames": 2, "won": 0, "draw": 1, "lost": 1, "points": 1},
        ],
        "fixtures": [
            {"home": "England", "home_crest": "https://crests.football-data.org/770.png", "away": "Spain", "away_crest": "https://crests.football-data.org/760.png", "score": "v"}
        ]
    }
]

# Database of key players
all_key_players = [
    {"name": "Kylian Mbappé", "team": "France", "img": "https://crests.football-data.org/773.png"},
    {"name": "Antoine Griezmann", "team": "France", "img": "https://crests.football-data.org/773.png"},
    {"name": "Jude Bellingham", "team": "England", "img": "https://crests.football-data.org/770.png"},
    {"name": "Harry Kane", "team": "England", "img": "https://crests.football-data.org/770.png"},
    {"name": "Pedri", "team": "Spain", "img": "https://crests.football-data.org/760.png"},
    {"name": "Federico Chiesa", "team": "Italy", "img": "https://crests.football-data.org/784.png"}
]

# --- HELPER FUNCTION ---
def get_crest(team_name):
    for group in standings_list:
        for row in group.get("table", []):
            if row.get("team", {}).get("name") == team_name:
                return row.get("team", {}).get("crest", "")
    return ""


# --- BRANDING HEADER TITLE ---
st.markdown("""
    <div class="title-area header-container">
        <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings and match updates</p>
    </div>
""", unsafe_allow_html=True)

# --- NEW SPLIT-SCREEN NEXT MATCH BANNER ---
home_crest = get_crest(next_home)
away_crest = get_crest(next_away)

st.markdown(f"""
    <div class="match-banner-container">
        <div class="banner-top-pane">
            <span class="next-match-title">⏳ Next Match</span>
        </div>
        <div class="matchup-split-screen">
            <div class="team-panel home-panel">
                <div class="team-panel-text">
                    {next_home} <span>{next_home_owner}</span>
                    <img src="{home_crest}" class="banner-flag" onerror="this.style.display='none'">
                </div>
            </div>
            <div class="vs-marker-bubble">VS</div>
            <div class="team-panel away-panel">
                <div class="team-panel-text">
                    <img src="{away_crest}" class="banner-flag" onerror="this.style.display='none'">
                    <span>{next_away_owner}</span> {next_away}
                </div>
            </div>
        </div>
        <div class="banner-bottom-time">
            🗓️ {next_date}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- OVERPERFORMANCE LEADERBOARD (MOCK) ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        <div class="stat-banner-box">
            <medium>📈 Top Overperformer</medium>
            <span>Alice (France)</span>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="stat-banner-box">
            <medium>📉 Biggest Underperformer</medium>
            <span>Dave (Spain)</span>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- MAIN DASHBOARD GROUPS LOOP ---
# Creates a 2-column layout for the groups
cols = st.columns(2)

for index, group_data in enumerate(standings_list):
    col = cols[index % 2] # Alternates placing groups in left/right column
    
    with col:
        # Group Header
        group_name = group_data["group"]
        st.markdown(f"<span class='group-header-text'>{group_name}</span>", unsafe_allow_html=True)
        
        # Build Table
        table_html = """
        <div class="table-responsive-wrapper">
            <table class="custom-dashboard-table">
                <thead>
                    <tr>
                        <th>Team</th>
                        <th>Owner</th>
                        <th>P</th>
                        <th>W</th>
                        <th>D</th>
                        <th>L</th>
                        <th>Pts</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        teams_in_group = [] # Keep track of teams for the player filter
        
        for row in group_data["table"]:
            t_name = row["team"]["name"]
            t_crest = row["team"]["crest"]
            owner = row["owner"]
            teams_in_group.append(t_name)
            
            table_html += f"""
                <tr>
                    <td><img src="{t_crest}" class="flag-img"> <b>{t_name}</b></td>
                    <td>{owner}</td>
                    <td>{row['playedGames']}</td>
                    <td>{row['won']}</td>
                    <td>{row['draw']}</td>
                    <td>{row['lost']}</td>
                    <td><b>{row['points']}</b></td>
                </tr>
            """
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Build Fixtures
        st.write("<span style='font-size:12px; font-weight:700; color:#FF6B00;'>📅 Fixtures</span>", unsafe_allow_html=True)
        for fix in group_data["fixtures"]:
            st.markdown(f"""
                <div class="fixture-row">
                    <div><img src="{fix['home_crest']}" class="flag-img"> {fix['home']}</div>
                    <div style="font-weight: 800; background: #FAFAFA; padding: 2px 8px; border-radius: 4px;">{fix['score']}</div>
                    <div>{fix['away']} <img src="{fix['away_crest']}" class="flag-img"></div>
                </div>
            """, unsafe_allow_html=True)
            
        # --- NEW: KEY GROUP PLAYERS SUBSECTION ---
        st.write("<br><span style='font-size:12px; font-weight:700; color:#FF6B00;'>🌟 Key Group Players</span>", unsafe_allow_html=True)
        
        players_html = '<div class="group-players-container">'
        
        # Filter the player database to only show players in this specific group
        group_players = [p for p in all_key_players if p["team"] in teams_in_group]
        
        if not group_players:
            players_html += "<span style='font-size: 12px; color: #888;'>No key players found for this group.</span>"
        else:
            for player in group_players:
                players_html += f"""
                <div class="group-player-card">
                    <img src="{player['img']}" onerror="this.src='https://via.placeholder.com/120x80?text=No+Image'">
                    <div class="group-player-card-name">{player['name']}</div>
                    <div style="font-size:10px; color:#666;">{player['team']}</div>
                </div>
                """
        players_html += '</div>'
        st.markdown(players_html, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)

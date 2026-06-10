import streamlit as st
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="Byway World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 30 seconds to keep live scores syncing
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Custom branding CSS styles
st.markdown("""
    <style>
        .stApp {
            background-color: #FAFAFA;
        }
        h1, h2, h3 {
            color: #FF6B00 !important;
            font-family: 'Arial Black', Gadget, sans-serif;
        }
        .header-container {
            border-bottom: 2px solid #FF6B00;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title-area h1 {
            margin: 0px !important;
            font-size: 36px;
        }
        .title-area p {
            margin: 4px 0px 0px 0px !important;
            color: #555555;
            font-weight: bold;
            font-size: 18px;
        }
        
        /* New Wide Next Match Banner Design */
        .next-match-banner {
            background: linear-gradient(135deg, #FF6B00 0%, #FF8533 100%);
            color: white !important;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
            margin: 15px 0px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .next-match-title {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Arial Black', sans-serif;
            font-weight: bold;
            opacity: 0.9;
        }
        .next-match-teams {
            font-size: 22px;
            font-family: 'Arial Black', sans-serif;
            font-weight: bold;
        }
        .next-match-teams span {
            font-size: 15px;
            font-weight: normal;
            opacity: 0.85;
            font-family: 'Arial', sans-serif;
        }
        .next-match-vs {
            color: #FFF;
            opacity: 0.7;
            margin: 0 15px;
            font-size: 18px;
        }
        .next-match-time {
            font-size: 16px;
            font-family: 'Arial Black', sans-serif;
            background: rgba(25px, 25px, 25px, 0.15);
            padding: 6px 14px;
            border-radius: 6px;
        }

        /* Smaller Side-by-Side Stat Blocks */
        .stat-banner-box {
            background: #FFFFFF;
            color: #333333 !important;
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #EAEAEA;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            height: 60px;
        }
        .stat-banner-box medium {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-family: 'Arial Black', sans-serif;
            font-weight: bold;
            color: #FF6B00;
        }
        .stat-banner-box span {
            font-size: 15px;
            font-weight: bold !important;
            font-family: 'Arial Black', sans-serif;
            text-align: right;
        }

        /* Custom compact match list element */
        .fixture-row {
            background-color: #FFFFFF;
            padding: 6px 10px;
            border-radius: 4px;
            margin-bottom: 4px;
            border: 1px solid #EAEAEA;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        /* Strict Flag Layout Overrides */
        .flag-img {
            vertical-align: middle;
            margin: 0px 6px;
            width: 24px !important;
            height: 16px !important;
            object-fit: cover !important;
            border: none !important;
            box-shadow: none !important;
        }
        /* Aligned header design element overrides */
        .group-header-text {
            color: #FF6B00;
            font-family: 'Arial Black', Gadget, sans-serif;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
import os
API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN", "placeholder")
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Sweepstake Mappings
SWEEPSTAKE_MAPPING = {
    "Mexico": "Evon",
    "South Africa": "Iwan",
    "Canada": "Holly",
    "Switzerland": "Yannis",
    "Argentina": "Alba",
    "France": "Marc",
    "Brazil": "Andy",
    "Spain": "Ciaran",
    "Bosnia-Herzegovina": "Izzy",
    "Czechia": "Pablo",
    "Qatar": "Jess",
    "Morocco": "Bartek",
    "Haiti": "Hatty",
    "Turkey": "Adrienne",
    "Paraguay": "Becca",
    "Germany": "Oliwia",
    "Curaçao": "Justin",
    "Ecuador": "Cat",
    "Japan": "Adem",
    "Belgium": "Mart",
    "Egypt": "Chris",
    "Tunisia": "Jess 2",
    "Netherlands": "Unassigned",
    "Ivory Coast": "Suzie",
    "Australia": "Amy",
    "Cape Verde Islands": "Justin 2",
    "Uruguay": "Paul 2",
    "Sweden": "Kat",
    "Saudi Arabia": "Aurelie",
    "Scotland": "Unassigned",
    "United States": "Neil",
    "Senegal": "Sara",
    "New Zealand": "James",
    "Iran": "Elaine",
    "Iraq": "Paul",
    "Norway": "Claire",
    "Algeria": "Adrienne 2",
    "Austria": "Rich",
    "Jordan": "Maria",
    "Congo DR": "Izzy",
    "Portugal": "Lucy 2",
    "Uzbekistan": "Kat 2",
    "Colombia": "Neil 2",
    "England": "Marijke",
    "Panama": "Lucy",
    "Ghana": "Sam",
    "Croatia": "Kurt",
    "South Korea": "Beau",
}

# Baseline Expected Rankings Map (Cleaned API Name variants handled safely)
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

# Helper to convert UTC time strings safely to UK Local Time (BST/GMT)
def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except Exception:
        return None

# Fallback structures for upcoming matches
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
        
        # Build Master Flat Leaderboard across all groups combined (Internal Performance Calculation Table)
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
        
        # Sort internal performance calculation table: Pts DESC, Won DESC, GD DESC, GF DESC, Alphabetical ASC
        if master_flat_leaderboard:
            master_flat_leaderboard.sort(
                key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"])
            )
            
            # Inject actual position ranking, pull expectations, and compute overperformance values
            for idx, team_item in enumerate(master_flat_leaderboard, start=1):
                name = team_item["name"]
                expected_rank = EXPECTED_RANKINGS.get(name, 25) # Mid-tier safe default if string mapping mismatches
                team_item["actual_rank"] = idx
                team_item["expected_rank"] = expected_rank
                team_item["overperformance"] = expected_rank - idx
            
            # Find the top overperformer based on score (tiebreak defaults to true tournament position rank)
            best_overperformer = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
            op_owner = SWEEPSTAKE_MAPPING.get(best_overperformer["name"], "Unassigned")
            
            # Format display modifier string showing movement score change
            score_prefix = "+" if best_overperformer["overperformance"] > 0 else ""
            top_performer_text = f"{best_overperformer['name']} ({op_owner}) [{score_prefix}{best_overperformer['overperformance']}]"
        
        # Fetch Match Data
        matches_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        matches_res = requests.get(matches_url, headers=HEADERS)
        all_matches = matches_res.json().get("matches", [])
        
        # Logic to extract the absolute next upcoming match
        if all_matches:
            upcoming_matches = [m for m in all_matches if m.get("status") in ["TIMED", "SCHEDULED"]]
            if upcoming_matches:
                upcoming_matches.sort(key=lambda x: x.get("utcDate", ""))
                next_m = upcoming_matches[0]
                
                next_home = next_m.get("homeTeam", {}).get("name", "TBD")
                next_away = next_m.get("awayTeam", {}).get("name", "TBD")
                
                # Fetch Owner assignments
                next_home_owner = f" ({SWEEPSTAKE_MAPPING.get(next_home, 'Unassigned')})"
                next_away_owner = f" ({SWEEPSTAKE_MAPPING.get(next_away, 'Unassigned')})"
                
                dt_uk = format_to_uk_time(next_m.get("utcDate"))
                if dt_uk:
                    day = dt_uk.day
                    if 4 <= day <= 20 or 24 <= day <= 30:
                        suffix = "th"
                    else:
                        suffix = ["st", "nd", "rd"][day % 10 - 1]
                    
                    next_date = dt_uk.strftime(f"{day}{suffix} %B @ %H:%M")
                else:
                    next_date = "TBD"
    except Exception:
        next_home = "API Connection"
        next_away = "Error"
        next_home_owner = ""
        next_away_owner = ""
        next_date = ""

# --- BRANDING HEADER TITLE ---
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
        <div class="next-match-teams">
            {next_home}<span>{next_home_owner}</span> 
            <span class="next-match-vs">v</span> 
            {next_away}<span>{next_away_owner}</span>
        </div>
        <div class="next-match-time">🗓️ {next_date}</div>
    </div>
""", unsafe_allow_html=True)

# --- TRIPLE STATS ROW (PRIZE POT, FAVORITES & OVERPERFORMER) ---
stat_cols = st.columns(3)

with stat_cols[0]:
    st.markdown("""
        <div class="stat-banner-box">
            <medium>💰 Prize Pot</medium>
            <span>£96</span>
        </div>
    """, unsafe_allow_html=True)

with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("Spain", "Unassigned")
    st.markdown(f"""
        <div class="stat-banner-box">
            <medium>⭐ Favourites</medium>
            <span>Spain ({fave_owner})</span>
        </div>
    """, unsafe_allow_html=True)

with stat_cols[2]:
    st.markdown(f"""
        <div class="stat-banner-box">
            <medium>🚀 Overperformer</medium>
            <span>{top_performer_text}</span>
        </div>
    """, unsafe_allow_html=True)

# Divider Line
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
                    
                    teams_in_group = []
                    for row in group_data.get("table", []):
                        teams_in_group.append(row.get("team", {}).get("name"))
                    
                    with row_cols[j]:
                        # --- CONDENSED STANDINGS TABLE HEADER ---
                        t_cols = st.columns([3.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0])
                        
                        t_cols[0].markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)
                        t_cols[1].write("**P**")
                        t_cols[2].write("**W**")
                        t_cols[3].write("**D**")
                        t_cols[4].write("**L**")
                        t_cols[5].write("**GF**")
                        t_cols[6].write("**GA**")
                        t_cols[7].write("**GD**")
                        t_cols[8].write("**Pts**")
                        st.markdown("<hr style='margin:2px 0px; border-top: 1px solid #FF6B00;'>", unsafe_allow_html=True)
                        
                        for row in group_data.get("table", []):
                            team_info = row.get("team", {})
                            team_name = team_info.get("name")
                            team_crest = team_info.get("crest", "")
                            owner = SWEEPSTAKE_MAPPING.get(team_name, "Unassigned")
                            
                            r_cols = st.columns([3.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0])
                            flag_html = f'<img src="{team_crest}" class="flag-img">' if team_crest else ''
                            
                            r_cols[0].markdown(f"{flag_html} **{team_name}** <span style='font-size:11px; color:#666;'>({owner})</span>", unsafe_allow_html=True)
                            r_cols[1].write(str(row.get("playedGames")))
                            r_cols[2].write(str(row.get("won")))
                            r_cols[3].write(str(row.get("draw")))
                            r_cols[4].write(str(row.get("lost")))
                            r_cols[5].write(str(row.get("goalsFor")))
                            r_cols[6].write(str(row.get("goalsAgainst")))
                            r_cols[7].write(str(row.get("goalDifference")))
                            r_cols[8].write(f"**{row.get('points')}**")
                        
                        # --- CHRONOLOGICAL FIXTURES SUBSECTION ---
                        st.write("<span style='font-size:12px; font-weight:bold; color:#FF6B00;'>📅 Group Fixtures & Results</span>", unsafe_allow_html=True)
                        
                        group_fixtures = []
                        for m in all_matches:
                            h_name = m.get("homeTeam", {}).get("name")
                            a_name = m.get("awayTeam", {}).get("name")
                            if h_name in teams_in_group or a_name in teams_in_group:
                                group_fixtures.append(m)
                        
                        if not group_fixtures:
                            st.caption("No fixtures currently listed for this group.")
                        else:
                            group_fixtures.sort(key=lambda x: x.get("utcDate", ""))
                            
                            for match in group_fixtures:
                                m_status = match.get("status")
                                home_t = match.get("homeTeam", {})
                                away_t = match.get("awayTeam", {})
                                
                                h_name = home_t.get("name", "TBD")
                                a_name = away_t.get("name", "TBD")
                                h_crest = home_t.get("crest", "")
                                a_crest = away_t.get("crest", "")
                                
                                h_owner = SWEEPSTAKE_MAPPING.get(h_name, "Unassigned")
                                a_owner = SWEEPSTAKE_MAPPING.get(a_name, "Unassigned")
                                
                                dt_uk = format_to_uk_time(match.get("utcDate"))
                                local_time_str = dt_uk.strftime("%d/%m %H:%M") if dt_uk else "TBD"
                                
                                h_flag = f'<img src="{h_crest}" class="flag-img">' if h_crest else ''
                                a_flag = f'<img src="{a_crest}" class="flag-img">' if a_crest else ''
                                
                                if m_status == "FINISHED":
                                    score_h = match.get("score", {}).get("fullTime", {}).get("home")
                                    score_a = match.get("score", {}).get("fullTime", {}).get("away")
                                    display_score = f"<b>{score_h} - {score_a}</b>"
                                elif m_status in ["IN_PLAY", "PAUSED"]:
                                    score_h = match.get("score", {}).get("fullTime", {}).get("home", 0)
                                    score_a = match.get("score", {}).get("fullTime", {}).get("away", 0)
                                    display_score = f"<span style='color:red; font-weight:bold;'>🔴 {score_h}-{score_a}</span>"
                                else:
                                    display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                
                                st.markdown(f"""
                                    <div class="fixture-row">
                                        <div style="text-align: left; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            {h_flag} <span>{h_name}</span> <span style="font-size:10px; color:#777;">({h_owner})</span>
                                        </div>
                                        <div style="text-align: center; width: 16%; font-size:11px;">
                                            {display_score}
                                        </div>
                                        <div style="text-align: right; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            <span style="font-size:10px; color:#777;">({a_owner})</span> <span>{a_name}</span> {a_flag}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        st.write("<br>", unsafe_allow_html=True)

        # --- SECTION DIVIDER FOR ADVANCED OVERPERFORMANCE LEADERBOARD ---
        st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 3px solid #FF6B00;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overall Sweepstake Overperformance Table</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;'>Ranked by Overperformance metric: (Expected Baseline Seed Rank - Current Performance Position)</p>", unsafe_allow_html=True)
        
        # Sort master list specifically by the overperformance gap score
        # Tiebreaker: actual performance ranking
        master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))
        
        # Centering table inside custom wrapper columns
        m_center_cols = st.columns([1, 10, 1])
        with m_center_cols[1]:
            # Leaderboard Headers
            h_cols = st.columns([0.6, 3.6, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.7])
            h_cols[0].write("**Pos**")
            h_cols[1].write("**Team**")
            h_cols[2].write("**Expected seed**")
            h_cols[3].write("**Actual rank**")
            h_cols[4].write("**Played**")
            h_cols[5].write("**Goal difference**")
            h_cols[6].write("**Pts**")
            h_cols[7].write("") # Blank buffer 
            h_cols[8].write("**Score**")
            st.markdown("<hr style='margin:4px 0px; border-top: 2px solid #FF6B00;'>", unsafe_allow_html=True)
            
            # Populate Computed Rows
            for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
                owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
                flag_html = f'<img src="{team_row["crest"]}" class="flag-img">' if team_row["crest"] else ''
                
                r_cols = st.columns([0.6, 3.6, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.7])
                
                pos_str = f"🚀 {display_idx}" if display_idx == 1 else str(display_idx)
                op_val = team_row["overperformance"]
                op_formatted = f"+{op_val}" if op_val > 0 else str(op_val)
                
                # Highlight text color if overperforming vs underperforming
                score_color = "#107C41" if op_val > 0 else ("#A80000" if op_val < 0 else "#333333")
                
                r_cols[0].write(f"**{pos_str}**")
                r_cols[1].markdown(f"{flag_html} **{team_row['name']}** <span style='font-size:12px; color:#666;'>({owner})</span>", unsafe_allow_html=True)
                r_cols[2].write(f"#{team_row['expected_rank']}")
                r_cols[3].write(f"#{team_row['actual_rank']}")
                r_cols[4].write(str(team_row["played"]))
                r_cols[5].write(str(team_row["gd"]))
                r_cols[6].write(str(team_row["pts"]))
                r_cols[7].write("") 
                r_cols[8].markdown(f"<span style='color:{score_color}; font-weight:bold;'>{op_formatted}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0px; border-top: 1px solid #EAEAEA;'>", unsafe_allow_html=True)

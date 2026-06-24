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
    "Ivory Coast": {"player_name": "Yan Diomande", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/yan-diomande-ivory-coast-forward-profile-full.png"},
    "Bosnia-Herzegovina": {"player_name": "Esmir Bajraktarevic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/esmir-bajraktarevic-bosnia-and-herzegovina-forward-profile-full.png"},
    "Bosnia and Herzegovina": {"player_name": "Esmir Bajraktarevic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/esmir-bajraktarevic-bosnia-and-herzegovina-forward-profile-full.png"},
    "Cape Verde Islands": {"player_name": "Ryan Mendes", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ryan-mendes-cape-verde-midfielder-profile-full.png"},
    "Curaçao": {"player_name": "Juninho Bacuna", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/juninho-bacuna-curacao-midfielder-profile-full.png"},
    "Haiti": {"player_name": "Wilson Isidor", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/wilson-isidor-haiti-forward-profile-full.png"},
    "Congo DR": {"player_name": "Aaron Wan-Bissaka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/aaron-wan-bissaka-dr-congo-defender-profile-full.png"},
    "DR Congo": {"player_name": "Aaron Wan-Bissaka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/aaron-wan-bissaka-dr-congo-defender-profile-full.png"},
    "Ghana": {"player_name": "Antoine Semenyo", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/antoine-semenyo-ghana-forward-profile-full.png"},
    "Algeria": {"player_name": "Riyad Mahrez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/riyad-mahrez-algeria-forward-profile-full.png"},
    "Australia": {"player_name": "Jackson Irvine", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/jackson-irvine-australia-midfielder-profile-full.png"},
    "Canada": {"player_name": "Alphonso Davies", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/alphonso-davies-canada-defender-profile-full.png"},
    "Czechia": {"player_name": "Patrik Schick", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/patrik-schick-czech-republic-forward-profile-full.png"},
    "Austria": {"player_name": "Romano Schmid", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/romano-schmid-austria-midfielder-profile-full.png"},
    "New Zealand": {"player_name": "Chris Wood", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/chris-wood-new-zealand-forward-profile-full.png"},
    "Iraq": {"player_name": "Ali Al-Hamadi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ali-al-hamadi-iraq-forward-profile-full.png"},
    "Jordan": {"player_name": "Ihsan Haddad", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ihsan-haddad-jordan-defender-profile-full.png"},
    "Egypt": {"player_name": "Mohamed Salah", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/mohamed-salah-egypt-forward-profile-full.png"},
    "Ecuador": {"player_name": "Willian Pacho", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/willian-pacho-ecuador-defender-profile-full.png"},
    "Saudi Arabia": {"player_name": "Salem Al-Dawsari", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/salem-al-dawsari-saudi-arabia-forward-profile-full.png"},
    "Belgium": {"player_name": "Jeremy Doku", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/jeremy-doku-belgium-forward-profile-full.png"},
    "Qatar": {"player_name": "Hassan Al-Haydos", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/hassan-al-haydos-qatar-forward-profile-full.png"},
    "Colombia": {"player_name": "Luis Suarez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/luis-suarez-colombia-forward-profile-full.png"},
    "Iran": {"player_name": "Alireza Beiranvand", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/alireza-beiranvand-iran-goalkeeper-profile-full.png"},
    "South Africa": {"player_name": "Mbekezeli Mbokazi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/mbekezeli-mbokazi-south-africa-defender-profile-full.png"},
    "Norway": {"player_name": "Erling Haaland", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/erling-haaland-norway-forward-profile-full.png"},
    "Croatia": {"player_name": "Luka Vuskovic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/luka-vuskovic-croatia-defender-profile-full.png"},
    "Paraguay": {"player_name": "Diego Gomez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/diego-gomez-paraguay-midfielder-profile-full.png"},
    "Panama": {"player_name": "Adalberto Carrasquilla", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/adalberto-carrasquilla-panama-midfielder-profile-full.png"},
    "Japan": {"player_name": "Ritsu Doan", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ritsu-doan-japan-forward-profile-full.png"},
    "Scotland": {"player_name": "Scott McTominay", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/scott-mctominay-scotland-midfielder-profile-full.png"},
    "Tunisia": {"player_name": "Ellyes Skhiri", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ellyes-skhiri-tunisia-midfielder-profile-full.png"},
    "Sweden": {"player_name": "Viktor Gyökeres", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/viktor-gyokeres-sweden-forward-profile-full.png"},
    "Uzbekistan": {"player_name": "Eldor Shomurodov", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/eldor-shomurodov-uzbekistan-forward-profile-full.png"},
    "Mexico": {"player_name": "Gilberto Mora", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/gilberto-mora-mexico-midfielder-profile-full.png"},
    "South Korea": {"player_name": "Son Heung-min", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/son-heung-min-south-korea-forward-profile-full.png"},
    "Morocco": {"player_name": "Yassine Bounou", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/yassine-bounou-morocco-goalkeeper-profile-full.png"},
    "Senegal": {"player_name": "Sadio Mane", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/sadio-mane-senegal-forward-profile-full.png"},
    "Switzerland": {"player_name": "Johan Manzambi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/johan-manzambi-switzerland-midfielder-profile-full.png"},
    "United States": {"player_name": "Christian Pulisic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/christian-pulisic-united-states-forward-profile-full.png"},
    "Uruguay": {"player_name": "Federico Valverde", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/federico-valverde-uruguay-midfielder-profile-full.png"},
    "Turkey": {"player_name": "Kenan Yildiz", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kenan-yildiz-turkey-forward-profile-full.png"}
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
    
    p, span, div, label, small, td, th, b {
        color: #333333;
        font-family: 'Figtree', sans-serif !important;
    }

    .match-banner-wrapper {
        width: 100%;
        margin: 0px 0px 15px 0px;
        box-sizing: border-box;
    }

    .match-banner-container {
        width: 100%;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        overflow: hidden;
        font-family: 'Figtree', sans-serif !important;
        text-align: center;
        border: 1px solid #DDDDDD;
        background-color: #FFFFFF;
    }

    .banner-top-pane {
        background-color: #444444;
        padding: 8px 15px;
    }

    .next-match-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.15);
        padding: 8px 15px;
        border-radius: 6px;
        display: inline-block;
    }

    .inplay-top-pane {
        background-color: #8B0000;
        padding: 8px 15px;
    }
    
    .result-top-pane {
        background-color: #444444;
        padding: 6px 10px;
    }

    .matchup-split-screen {
        display: flex;
        position: relative;
        align-items: center;
        height: 75px;
        width: 100%;
    }

    .team-panel {
        width: 50%;
        display: flex;
        align-items: center;
        padding: 10px 25px;
        box-sizing: border-box;
        height: 100%;
        overflow: hidden;
    }
    
    .home-panel {
        justify-content: flex-end;
        padding-right: 50px;
        border-right: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .away-panel {
        justify-content: flex-start;
        padding-left: 50px;
    }

    .team-panel-text {
        color: #FFFFFF !important;
        font-size: 18px;
        font-weight: 800 !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        white-space: nowrap;
    }

    .team-panel-text span {
        font-size: 13px !important;
        font-weight: 400 !important;
        opacity: 0.95;
        color: #FFFFFF !important;
        margin: 0 6px;
    }

    .mobile-abbrev-text {
        display: none;
    }

    .vs-marker-bubble, .score-bubble, .score-reveal-wrapper {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        white-space: nowrap;
    }

    .vs-marker-bubble {
        background-color: #111111;
        color: #FFFFFF !important;
        font-size: 12px;
        font-weight: 900 !important;
        padding: 5px 9px;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .score-bubble {
        background-color: #444444;
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 900 !important;
        padding: 6px 14px;
        border-radius: 6px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .reveal-toggle-input {
        display: none !important;
    }

    .score-reveal-label {
        background-color: #111111;
        color: #FFFFFF !important;
        font-size: 11px !important;
        font-weight: 900 !important;
        padding: 6px 12px !important;
        border-radius: 6px;
        cursor: pointer;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        user-select: none;
    }

    .reveal-toggle-input:checked ~ .score-reveal-label {
        display: none !important;
    }

    .reveal-toggle-input:checked ~ .score-bubble {
        display: block !important;
    }

    .banner-bottom-time {
        background-color: #444444;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }

    .inplay-bottom-bar {
        background-color: #8B0000;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    .result-bottom-bar {
        background-color: #444444;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    .highlights-btn, .watch-live-btn {
        font-weight: 800 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        text-decoration: none !important;
        padding: 6px 10px;
        border-radius: 2px;
        display: inline-flex !important;
        align-items: center;
        gap: 4px;
        color: #FFFFFF !important;
    }

    .highlights-btn, .watch-live-btn.is-scheduled-btn {
        background-color: #444444 !important;
    }

    .watch-live-btn.is-live-btn {
        background-color: #8b0802 !important;
    }

    .highlights-btn:hover, .watch-live-btn.is-scheduled-btn:hover, .watch-live-btn.is-live-btn:hover {
        background-color: #CC0000 !important;
    }
    
    .banner-flag {
        width: 28px !important;
        height: 19px !important;
        min-width: 28px !important;
        max-width: 28px !important;
        object-fit: cover !important;
        border-radius: 2px;
        border: 1px solid rgba(255,255,255,0.3);
        display: inline-block;
        margin: 0 8px;
        vertical-align: middle;
    }

    .odds-grid-row {
        display: flex;
        width: 100%;
        height: 75px;
        background-color: #FFFFFF;
        align-items: center;
        justify-content: space-around;
        padding: 0 10px;
        box-sizing: border-box;
    }
    .odds-item-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 4px;
        padding: 6px;
        border-radius: 6px;
        background: #FFFDFC;
        border: 1px solid #FFEAD6;
        min-width: 0;
    }
    .odds-item-team {
        font-size: 13px;
        font-weight: 800;
        color: #333333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .odds-item-owner {
        font-size: 10px;
        color: #666666;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
        text-align: center;
    }
    .odds-item-price {
        font-size: 12px;
        font-weight: 900;
        color: #ff7d23;
        margin-top: 4px;
        background: #FFF1E5;
        border-radius: 4px;
        padding: 2px 8px;
    }

    /* Status Indicator Dots */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-left: 6px;
        vertical-align: middle;
    }
    .dot-green { background-color: #28a745; box-shadow: 0 0 4px #28a745; }
    .dot-red { background-color: #dc3545; box-shadow: 0 0 4px #dc3545; }

    @media (max-width: 768px) {
        .team-panel { padding: 10px 8px !important; }
        .home-panel { padding-right: 32px !important; }
        .away-panel { padding-left: 32px !important; }
        .team-panel-text { font-size: 15px !important; }
        .team-panel-text span { font-size: 11px !important; margin: 0 2px !important; }
        .desktop-full-text { display: none !important; }
        .mobile-abbrev-text { display: inline-block !important; }
        .banner-flag { width: 20px !important; height: 14px !important; min-width: 20px !important; max-width: 20px !important; margin: 0 4px !important; }
        .score-bubble, .vs-marker-bubble { font-size: 12px !important; padding: 4px 10px !important; }
        .score-reveal-label { font-size: 9px !important; padding: 4px 8px !important; }
        .odds-item-card:nth-child(n+4) { display: none !important; }
    }
</style>
"""

st.markdown(GLOBAL_STYLE_TOKENS, unsafe_allow_html=True)
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAFA !important;
        }
        h1, h2, h3, h1 span, h2 span, h3 span, h1 p, h2 p, h3 p {
            color: #ff7d23 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        .title-area h1 { margin: 0px !important; font-size: 28px; font-weight: 900 !important; }
        .title-area p { margin: 4px 0px 0px 0px !important; color: #555555 !important; font-weight: 700 !important; font-size: 16px; }
        .stat-banner-box { background: #FFFFFF !important; padding: 12px 20px; border-radius: 8px; border: 2px solid #EAEAEA; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
        .stat-banner-box medium { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 800 !important; color: #ff7d23 !important; }
        .stat-banner-box span { font-size: 14px; font-weight: 800 !important; text-align: right; color: #333333 !important; }
        .group-row-spacer { margin-bottom: 15px !important; }
        .table-responsive-wrapper { width: 100%; overflow-x: auto; margin-bottom: 8px !important; }
        
        .flag-img { 
            vertical-align: middle !important; 
            margin: 0px 4px !important; 
            width: 20px !important; 
            height: 14px !important; 
            min-width: 20px !important;
            max-width: 20px !important;
            object-fit: cover !important; 
            display: inline-block !important; 
        }
        
        .custom-dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; white-space: nowrap; }
        .custom-dashboard-table th { background-color: #FAFAFA !important; color: #333333 !important; font-weight: 700 !important; padding: 6px 6px !important; border-bottom: 2px solid #ff7d23; }
        .custom-dashboard-table td { padding: 6px 6px !important; border-bottom: 1px solid #EAEAEA; vertical-align: middle; background-color: #FFFFFF !important; color: #333333 !important; }
        .custom-dashboard-table td img, .fixture-row img { width: 20px !important; height: 14px !important; min-width: 20px !important; max-width: 20px !important; object-fit: cover !important; }
        
        .fixture-row { background-color: #FFFFFF !important; padding: 6px 8px !important; border-radius: 4px; margin-bottom: 3px !important; border: 1px solid #EAEAEA; font-size: 12px; display: flex; align-items: center; justify-content: space-between; }
        .fixture-row-live { background-color: #FFF5F5 !important; border: 1px solid #FFCCCC !important; }
        .group-header-text { color: #ff7d23 !important; font-size: 18px; font-weight: 800 !important; margin-bottom: 4px !important; margin-top: 0px !important; display: inline-block; }
        
        /* Knockout Bracket Styles */
        .ko-bracket-container { display: flex; flex-direction: column; gap: 10px; background: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #EAEAEA; margin-bottom: 20px; }
        .ko-match-card { background: #FAFAFA; border-left: 4px solid #ff7d23; padding: 8px 12px; border-radius: 4px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
        .ko-match-info { display: flex; flex-direction: column; }
        .ko-match-date { font-size: 11px; color: #ff7d23; font-weight: 700; text-transform: uppercase; }
        .ko-match-teams { font-weight: 700; margin-top: 2px; }
        .ko-match-venue { font-size: 11px; color: #666; }
    </style>
""", unsafe_allow_html=True)

# 3. Core Helper Utility Functions
@st.cache_data(ttl=86400)
def get_cached_team_crests():
    crests = {}
    if API_TOKEN == "placeholder":
        return crests
    try:
        url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/teams"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            teams_data = res.json().get("teams", [])
            for t in teams_data:
                name = t.get("name")
                crest_url = t.get("crest")
                if name and crest_url:
                    crests[name] = crest_url
                    if name == "DR Congo": crests["Congo DR"] = crest_url
                    if name == "Cape Verde": crests["Cape Verde Islands"] = crest_url
                    if name == "Bosnia and Herzegovina": crests["Bosnia-Herzegovina"] = crest_url
    except Exception:
        pass
    return crests

CACHED_CRESTS = get_cached_team_crests()

def get_banner_flag_html(team_name):
    crest_url = CACHED_CRESTS.get(team_name)
    if crest_url:
        return f'<img src="{crest_url}" class="banner-flag" alt="{team_name}">'
    return ''

def get_group_flag_html(team_name):
    crest_url = CACHED_CRESTS.get(team_name)
    if crest_url:
        return f'<img src="{crest_url}" class="flag-img" alt="{team_name}">'
    return ''

def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except Exception:
        return None

def get_live_score(match):
    score_obj = match.get("score", {})
    for target_key in ["fullTime", "regularTime", "halfTime"]:
        s = score_obj.get(target_key, {})
        if s and s.get("home") is not None and s.get("away") is not None:
            return int(s.get("home")), int(s.get("away"))
    return 0, 0

def convert_to_fractional_odds(decimal_odds):
    if decimal_odds <= 1.0:
        return "1/1"
    net_odds = decimal_odds - 1.0
    frac = Fraction(net_odds).limit_denominator(100)
    return f"{frac.numerator}/{frac.denominator}"

# ── MASTER SPREADSHEET SCHEDULE OVERRIDES ENGINE ──
@st.cache_data(ttl=15)
def fetch_spreadsheet_overrides_master():
    override_dict = {}
    try:
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQeLButP4o4374i0KJP_YdOnTW1wN-Wzgqabuulvd1cMVmIuCfFTEM3CjJ4FmFIbBW6FLNDfaB9Hg4w/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(csv_url, header=None)
        if not df.empty:
            for _, row in df.iterrows():
                try:
                    if len(row) < 7:
                        continue
                    home_t = str(row[2]).strip() if pd.notna(row[2]) else ""
                    away_t = str(row[3]).strip() if pd.notna(row[3]) else ""
                    status_str = str(row[4]).strip().lower() if pd.notna(row[4]) else ""
                    h_score = str(row[5]).strip() if pd.notna(row[5]) else "0"
                    a_score = str(row[6]).strip() if pd.notna(row[6]) else "0"
                    h_link = str(row[7]).strip() if (len(row) >= 8 and pd.notna(row[7])) else ""
                    tv_network = str(row[8]).strip() if (len(row) >= 9 and pd.notna(row[8])) else ""

                    if home_t and away_t:
                        lookup_key = f"{home_t.lower()}_v_{away_t.lower()}"
                        override_dict[lookup_key] = {
                            "status": status_str,
                            "homeScore": h_score,
                            "awayScore": a_score,
                            "highlightsUrl": h_link if h_link.lower().startswith("http") else "https://www.youtube.com/@fifa/videos",
                            "tvNetwork": tv_network
                        }
                except Exception:
                    pass
    except Exception:
        pass
    return override_dict

SPREADSHEET_OVERRIDES = fetch_spreadsheet_overrides_master()

# ── THE ODDS API LIVE OUTRIGHTS INGESTION SYSTEM ──
@st.cache_data(ttl=86400)
def fetch_odds_api_favourites():
    favourites = []
    if ODDS_API_TOKEN == "placeholder":
        return [
            {"team": "France", "odds": 5.5}, {"team": "Brazil", "odds": 6.0}, 
            {"team": "England", "odds": 6.5}, {"team": "Argentina", "odds": 7.0}, 
            {"team": "Spain", "odds": 8.0}, {"team": "Germany", "odds": 10.0}
        ]
    try:
        url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup_winner/odds/"
        params = {"apiKey": ODDS_API_TOKEN, "regions": "eu,uk", "markets": "outrights"}
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                bookmakers = data[0].get("bookmakers", [])
                if bookmakers:
                    markets = bookmakers[0].get("markets", [])
                    if markets:
                        outcomes = markets[0].get("outcomes", [])
                        sorted_outcomes = sorted(outcomes, key=lambda x: x.get("price", 999))
                        for item in sorted_outcomes[:6]:
                            raw_name = item.get("name", "Unknown")
                            if raw_name == "USA": raw_name = "United States"
                            favourites.append({
                                "team": raw_name,
                                "odds": item.get("price", 0.0)
                            })
                        return favourites
    except Exception:
        pass
    return [
        {"team": "France", "odds": 5.5}, {"team": "Brazil", "odds": 6.0}, 
        {"team": "England", "odds": 6.5}, {"team": "Argentina", "odds": 7.0}, 
        {"team": "Spain", "odds": 8.0}, {"team": "Germany", "odds": 10.0}
    ]

def build_odds_favourites_banner():
    fav_list = fetch_odds_api_favourites()
    cards_html = ""
    for f in fav_list:
        team_name = f["team"]
        decimal_odds = f["odds"]
        fractional_str = convert_to_fractional_odds(decimal_odds)
        owner = SWEEPSTAKE_MAPPING.get(team_name, "Unassigned")
        crest_url = CACHED_CRESTS.get(team_name, "")
        flag_img_html = f'<img src="{crest_url}" style="width:24px; height:16px; min-width:24px; max-width:24px; object-fit:cover; border-radius:2px; border:1px solid #DDD; margin-right:6px; display:inline-block; vertical-align:middle;">' if crest_url else ""
        
        cards_html += f"""
        <div class="odds-item-card">
            <div class="odds-item-team">{flag_img_html}{team_name}</div>
            <div class="odds-item-owner">({owner})</div>
            <div class="odds-item-price">{fractional_str}</div>
        </div>
        """
        
    return f"""
    {GLOBAL_STYLE_TOKENS}
    <div class="match-banner-wrapper">
        <div class="match-banner-container" style="border-color: #ff7d23;">
            <div class="banner-top-pane" style="background-color: #ff7d23; padding: 6px 15px;">
                <div class="next-match-title" style="background: rgba(255,255,255,0.2); color: #FFFFFF !important; font-size: 11px; padding: 4px 10px;">🔥 Tournament Favourites</div>
            </div>
            <div class="odds-grid-row">
                {cards_html}
            </div>
            <div class="banner-bottom-time" style="background-color: #ff7d23; color: #FFFFFF !important; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; padding: 4px 15px;"></div>
        </div>
    </div>
    """

# ── SINGLE OR COMBINED MATCH BANNER SYSTEM ──
def build_match_banner(matches, is_live=False, is_result=False, match_idx=2):
    if not isinstance(matches, list):
        matches = [matches]
        
    html_out = f"{GLOBAL_STYLE_TOKENS}<div class='match-banner-wrapper'><div class='match-banner-container'>"
    
    # Header pane configuration
    if is_live:
        html_out += '<div class="inplay-top-pane"><div class="next-match-title">🔴 Live Now</div></div>'
    elif is_result:
        html_out += '<div class="result-top-pane"><div class="next-match-title" style="background: rgba(0,0,0,0.2);">✅ Latest Result</div></div>'
    else:
        html_out += '<div class="banner-top-pane"><div class="next-match-title">⏳ Next Match</div></div>'

    # Match layouts
    for idx, match in enumerate(matches):
        home_team_obj = match.get("homeTeam", {})
        away_team_obj = match.get("awayTeam", {})
        h_name = home_team_obj.get("name", "TBD")
        a_name = away_team_obj.get("name", "TBD")
        h_abbrev = COUNTRY_ABBREVIATIONS.get(h_name, h_name[:3].upper())
        a_abbrev = COUNTRY_ABBREVIATIONS.get(a_name, a_name[:3].upper())

        left_color = TEAM_COLORS.get(h_name, DEFAULT_LEFT_COLOR)
        right_color = TEAM_COLORS.get(a_name, DEFAULT_RIGHT_COLOR)
        if left_color == right_color:
            right_color = "#222222" if left_color != "#222222" else "#555555"

        h_flag = get_banner_flag_html(h_name)
        a_flag = get_banner_flag_html(a_name)
        h_owner = f" ({SWEEPSTAKE_MAPPING.get(h_name, 'Unassigned')})"
        a_owner = f" ({SWEEPSTAKE_MAPPING.get(a_name, 'Unassigned')})"

        h_score, a_score = get_live_score(match)
        highlights_url = "https://www.youtube.com/@fifa/videos"
        tv_channel_text = ""
        
        if h_name and a_name:
            lookup_key = f"{h_name.lower()}_v_{a_name.lower()}"
            if lookup_key in SPREADSHEET_OVERRIDES:
                sheet_row = SPREADSHEET_OVERRIDES[lookup_key]
                h_score = sheet_row.get("homeScore", h_score)
                a_score = sheet_row.get("awayScore", a_score)
                highlights_url = sheet_row.get("highlightsUrl", highlights_url)
                tv_channel_text = sheet_row.get("tvNetwork", "")

        normalized_channel = tv_channel_text.lower().strip()

        if is_live:
            centre_bubble = f'<div class="score-bubble">{h_score} – {a_score}</div>'
        elif is_result:
            sub_idx = f"{match_idx}_{idx}"
            centre_bubble = f"""
            <div class="score-reveal-wrapper">
                <input type="checkbox" id="reveal-toggle-{sub_idx}" class="reveal-toggle-input">
                <label for="reveal-toggle-{sub_idx}" class="score-reveal-label">Show</label>
                <div class="score-bubble" style="display: none;">{h_score} – {a_score}</div>
            </div>
            """
        else:
            centre_bubble = '<div class="vs-marker-bubble">VS</div>'

        border_css = "border-bottom: 1px dashed #DDD;" if idx < len(matches) - 1 else ""
        
        html_out += f"""
        <div class="matchup-split-screen" style="{border_css}">
            <div class="team-panel home-panel" style="background-color: {left_color};">
                <div class="team-panel-text">
                    {h_flag} 
                    <span class="desktop-full-text">{h_name}</span>
                    <span class="mobile-abbrev-text">{h_abbrev}</span>
                    <span>{h_owner}</span>
                </div>
            </div>
            {centre_bubble}
            <div class="team-panel away-panel" style="background-color: {right_color};">
                <div class="team-panel-text">
                    <span>{a_owner}</span> 
                    <span class="desktop-full-text">{a_name}</span>
                    <span class="mobile-abbrev-text">{a_abbrev}</span>
                    {a_flag}
                </div>
            </div>
        </div>
        """

    # Bottom Meta Bar Setup
    repr_match = matches[0]
    tv_channel_text = ""
    home_t = repr_match.get("homeTeam", {}).get("name", "")
    away_t = repr_match.get("awayTeam", {}).get("name", "")
    if home_t and away_t:
        lookup_key = f"{home_t.lower()}_v_{away_t.lower()}"
        if lookup_key in SPREADSHEET_OVERRIDES:
            tv_channel_text = SPREADSHEET_OVERRIDES[lookup_key].get("tvNetwork", "")
            highlights_url = SPREADSHEET_OVERRIDES[lookup_key].get("highlightsUrl", "https://www.youtube.com/@fifa/videos")

    normalized_channel = tv_channel_text.lower().strip()

    if is_live:
        if normalized_channel in BROADCAST_BRANDS:
            brand = BROADCAST_BRANDS[normalized_channel]
            html_out += f"""
            <div class="inplay-bottom-bar" style="display: flex; align-items: center; justify-content: center; gap: 15px; padding: 5px 15px;">
                <span style="color: #FFFFFF !important;">⚽ Matches in progress</span>
                <span style="opacity: 0.4; color: #FFFFFF !important;">|</span>
                <a href="{brand['live_url']}" target="_blank" class="watch-live-btn is-live-btn">
                    WATCH LIVE
                    <img src="{brand['logo']}" style="height: 14.5px; width: auto; object-fit: contain; vertical-align: middle; margin-left: 2px;" alt="{tv_channel_text}">
                </a>
            </div>"""
        else:
            suffix = f" | 📺 {tv_channel_text}" if tv_channel_text else ""
            html_out += f'<div class="inplay-bottom-bar">⚽ Match in progress{suffix}</div>'
    elif is_result:
        html_out += f'<div class="result-bottom-bar"><a href="{highlights_url}" target="_blank" class="highlights-btn">📺 SPOILER-FREE HIGHLIGHTS 📺</a></div>'
    else:
        dt_uk = format_to_uk_time(repr_match.get("utcDate"))
        date_str = dt_uk.strftime(f"{dt_uk.day}th %B @ %H:%M") if dt_uk else "TBD"
        
        if normalized_channel in BROADCAST_BRANDS:
            brand = BROADCAST_BRANDS[normalized_channel]
            html_out += f"""
            <div class="banner-bottom-time" style="display: flex; align-items: center; justify-content: center; gap: 15px; padding: 5px 15px;">
                <span style="color: #FFFFFF !important;">🗓️ {date_str}</span>
                <span style="opacity: 0.4; color: #FFFFFF !important;">|</span>
                <a href="{brand['live_url']}" target="_blank" class="watch-live-btn is-scheduled-btn">
                    WATCH LIVE
                    <img src="{brand['logo']}" style="height: 14.5px; width: auto; object-fit: contain; vertical-align: middle; margin-left: 2px;" alt="{tv_channel_text}">
                </a>
            </div>"""
        else:
            suffix = f" | 📺 {tv_channel_text}" if tv_channel_text else ""
            html_out += f'<div class="banner-bottom-time" style="color: #FFFFFF !important;">🗓️ {date_str}{suffix}</div>'

    html_out += "</div></div>"
    return html_out

# ── Data Ingestion Pipeline Routing Engine ──
@st.cache_data(ttl=120)  
def fetch_football_data():
    all_matches = []
    standings_list = []
    if API_TOKEN == "placeholder":
        return all_matches, standings_list
    try:
        s_res = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings", headers=HEADERS, timeout=10)
        if s_res.status_code == 200:
            standings_list = s_res.json().get("standings", [])
        m_res = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches", headers=HEADERS, timeout=10)
        if m_res.status_code == 200:
            all_matches = m_res.json().get("matches", [])
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
    return all_matches, standings_list

all_matches, standings_list = fetch_football_data()

# Head-to-Head Evaluation Engine Matrix for ties
def get_h2h_winner_if_tied(team_a, team_b, matches_pool):
    for m in matches_pool:
        if m.get("status") == "FINISHED":
            ha = m.get("homeTeam", {}).get("name")
            aw = m.get("awayTeam", {}).get("name")
            if {ha, aw} == {team_a, team_b}:
                hs, _ = get_live_score(m)
                _, as_ = get_live_score(m)
                if hs > as_:
                    return ha
                elif as_ > hs:
                    return aw
    return None

# Process Group Standings with requested tie-breakers
processed_standings = {}
third_place_pool = []
all_group_teams_completed = True

for group in standings_list:
    g_name = group.get("group", "Unknown Group")
    table_rows = []
    for row in group.get("table", []):
        t_info = row.get("team", {})
        t_name = t_info.get("name", "Unknown")
        played = row.get("playedGames", 0)
        if played < 3:
            all_group_teams_completed = False
            
        table_rows.append({
            "name": t_name,
            "played": played,
            "won": row.get("won", 0),
            "draw": row.get("draw", 0),
            "lost": row.get("lost", 0),
            "gf": row.get("goalsFor", 0),
            "ga": row.get("goalsAgainst", 0),
            "gd": row.get("goalDifference", 0),
            "pts": row.get("points", 0),
            "crest": t_info.get("crest", "")
        })

    # Sort using tie-breaker framework
    def group_sort_key(item):
        return (-item["pts"], -item["gd"], -item["gf"])

    table_rows.sort(key=group_sort_key)
    
    # H2H Evaluation Override check
    i = 0
    while i < len(table_rows) - 1:
        if table_rows[i]["pts"] == table_rows[i+1]["pts"]:
            winner = get_h2h_winner_if_tied(table_rows[i]["name"], table_rows[i+1]["name"], all_matches)
            if winner == table_rows[i+1]["name"]:
                table_rows[i], table_rows[i+1] = table_rows[i+1], table_rows[i]
        i += 1

    processed_standings[g_name] = table_rows
    if len(table_rows) >= 3:
        third_place_pool.append(table_rows[2])

# Sort third-place teams across entire tournament structure
third_place_pool.sort(key=lambda x: (-x["pts"], -x["gd"], -x["gf"]))
highest_8_third_place = [t["name"] for t in third_place_pool[:8]]

# Build Master Flat Overperformance Board Dataset
master_flat_leaderboard = []
flat_idx = 1
for g_name, rows in processed_standings.items():
    for r in rows:
        master_flat_leaderboard.append(r.copy())

if master_flat_leaderboard:
    master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["gd"], -x["gf"]))
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

    best = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
    op_owner = SWEEPSTAKE_MAPPING.get(best["name"], "Unassigned")
    top_performer_text = f"{best['name']} ({op_owner})"
else:
    top_performer_text = "N/A"

# Match Sorting Categories Ingestion
live_matches, upcoming_matches, finished_matches = [], [], []
for m in all_matches:
    home_team_node = m.get("homeTeam")
    away_team_node = m.get("awayTeam")
    if home_team_node and away_team_node:
        h_name = home_team_node.get("name")
        a_name = away_team_node.get("name")
        if h_name and a_name:
            lookup_key = f"{h_name.lower()}_v_{a_name.lower()}"
            if lookup_key in SPREADSHEET_OVERRIDES:
                sheet_status = SPREADSHEET_OVERRIDES[lookup_key]["status"]
                if "live" in sheet_status: live_matches.append(m)
                elif "finished" in sheet_status or "completed" in sheet_status: finished_matches.append(m)
                else: upcoming_matches.append(m)
                continue

    api_status = m.get("status")
    if api_status in ["IN_PLAY", "PAUSED"]: live_matches.append(m)
    elif api_status == "FINISHED": finished_matches.append(m)
    else: upcoming_matches.append(m)

upcoming_matches = sorted(upcoming_matches, key=lambda x: x.get("utcDate", ""))
finished_matches = sorted(finished_matches, key=lambda x: x.get("utcDate", ""), reverse=True)

# ── HEADER ROW ──
header_cols = st.columns([1, 1], gap="medium")
with header_cols[0]:
    st.markdown("""
        <div class="title-area" style="padding-top: 15px; margin-bottom: 20px;">
            <h1>🏆 BYWAY WORLD CUP SWEEPSTAKE</h1>
            <p>Live standings</p>
        </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    if live_matches:
        first_kickoff = live_matches[0].get("utcDate", "")
        concurrent_live = [m for m in live_matches if m.get("utcDate", "") == first_kickoff]
        payload = build_match_banner(concurrent_live, is_live=True, match_idx=200)
        components.html(payload, height=170, scrolling=False)
    else:
        odds_payload = build_odds_favourites_banner()
        components.html(odds_payload, height=170, scrolling=False)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECONDARY CONTENT ROW ──
hero_cols = st.columns([1, 1], gap="medium")
with hero_cols[0]:
    if upcoming_matches:
        first_kickoff = upcoming_matches[0].get("utcDate", "")
        concurrent_upcoming = [m for m in upcoming_matches if m.get("utcDate", "") == first_kickoff]
        payload = build_match_banner(concurrent_upcoming, is_live=False, match_idx=100)
        components.html(payload, height=170, scrolling=False)
    else:
        st.info("⏳ No matches currently scheduled.")

with hero_cols[1]:
    if finished_matches:
        latest_match = finished_matches[0]
        result_banner_html = build_match_banner([latest_match], is_live=False, is_result=True, match_idx=800)
        components.html(result_banner_html, height=170, scrolling=False)
    else:
        st.info("⚽ No results logged yet for this tournament state.")

# ── STATS ROW ──
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    st.markdown('<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>' + top_performer_text + '</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    if master_flat_leaderboard:
        master_flat_leaderboard.sort(key=lambda x: (x["overperformance"], -x["actual_rank"]))
        underdog = master_flat_leaderboard[0]
        ud_owner = SWEEPSTAKE_MAPPING.get(underdog["name"], "Unassigned")
        st.markdown(f'<div class="stat-banner-box"><medium>💩 Underperformer</medium><span>{underdog["name"]} ({ud_owner})</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="stat-banner-box"><medium>💩 Underperformer</medium><span>N/A</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #ff7d23;'>", unsafe_allow_html=True)

# Set up Auto-Open States
ko_expanded = all_group_teams_completed
group_expanded = not all_group_teams_completed

# ── KNOCKOUT PHASE BLOCK ──
with st.expander("🏅 KNOCKOUT PHASE BRACKET", expanded=ko_expanded):
    st.markdown("<h3 style='margin-top:0px;'>Knockout Phase Matchups</h3>", unsafe_allow_html=True)
    
    ko_matches = [
        {"date": "June 28", "venue": "Inglewood", "teams": "Runner-up Group A vs Runner-up Group B", "match": "Match 73"},
        {"date": "June 29", "venue": "Foxborough", "teams": "Winner Group E vs 3rd Group A/B/C/D/F", "match": "Match 74"},
        {"date": "June 29", "venue": "Guadalupe", "teams": "Winner Group F vs Runner-up Group C", "match": "Match 75"},
        {"date": "June 29", "venue": "Houston", "teams": "Winner Group C vs Runner-up Group F", "match": "Match 76"},
        {"date": "June 30", "venue": "East Rutherford", "teams": "Winner Group I vs 3rd Group C/D/F/G/H", "match": "Match 77"},
        {"date": "June 30", "venue": "Arlington", "teams": "Runner-up Group E vs Runner-up Group I", "match": "Match 78"},
        {"date": "June 30", "venue": "Mexico City", "teams": "Winner Group A vs 3rd Group C/E/F/H/I", "match": "Match 79"},
        {"date": "July 1", "venue": "Santa Clara", "teams": "Winner Group D vs 3rd Group B/E/F/I/J", "match": "Match 81"},
        {"date": "July 1", "venue": "Seattle", "teams": "Winner Group G vs 3rd Group A/E/H/I/J", "match": "Match 82"},
        {"date": "July 1", "venue": "Atlanta", "teams": "Winner Group L vs 3rd Group E/H/I/J/K", "match": "Match 80"},
        {"date": "July 2", "venue": "Toronto", "teams": "Winner Match 75 vs Runner-up Group K", "match": "Match 97"},
        {"date": "July 2", "venue": "Inglewood", "teams": "Winner Group H vs Runner-up Group J", "match": "Match 84"},
        {"date": "July 2", "venue": "Vancouver", "teams": "Winner Group B vs 3rd Group E/F/G/I/J", "match": "Match 85"},
        {"date": "July 3", "venue": "Miami Gardens", "teams": "Winner Match 79 vs Winner Match 80", "match": "Match 99"},
        {"date": "July 3", "venue": "Arlington", "teams": "Winner Match 86 vs Runner-up Group D", "match": "Match 88"},
        {"date": "July 3", "venue": "Kansas City", "teams": "Winner Match 85 vs 3rd Group D/E/I/J/L", "match": "Match 87"},
        {"date": "July 4", "venue": "Philadelphia", "teams": "Winner Match 74 vs Winner Match 77", "match": "Match 89"},
        {"date": "July 4", "venue": "Houston", "teams": "Winner Match 73 vs Winner Match 76", "match": "Match 90"},
        {"date": "July 5", "venue": "East Rutherford", "teams": "Winner Match 78 vs Winner Match 91", "match": "Match 102"},
        {"date": "July 5", "venue": "Mexico City", "teams": "Winner Match 92 vs Winner Match 79", "match": "Match 101"},
        {"date": "July 6", "venue": "Arlington", "teams": "Runner-up Group L vs Winner Match 83", "match": "Match 98"},
        {"date": "July 6", "venue": "Seattle", "teams": "Winner Match 81 vs Winner Match 82", "match": "Match 94"},
        {"date": "July 7", "venue": "Atlanta", "teams": "Winner Match 100 vs Runner-up Group H", "match": "Match 86"},
        {"date": "July 7", "venue": "Vancouver", "teams": "Winner Match 87 vs Winner Match 88", "match": "Match 96"},
        {"date": "July 9", "venue": "Foxborough", "teams": "Winner Match 89 vs Winner Match 90", "match": "Match 91"},
        {"date": "July 10", "venue": "Inglewood", "teams": "Winner Match 83 vs Winner Match 84", "match": "Match 93"},
        {"date": "July 11", "venue": "Miami Gardens", "teams": "Winner Match 91 vs Winner Match 92", "match": "Match 92"},
        {"date": "July 11", "venue": "Kansas City", "teams": "Runner-up Group G vs Winner Match 95", "match": "Match 95"},
        {"date": "July 14", "venue": "Arlington", "teams": "Winner Match 97 vs Winner Match 98", "match": "Match 103"},
        {"date": "July 15", "venue": "Atlanta", "teams": "Winner Match 99 vs Winner Match 100", "match": "Match 104"},
        {"date": "July 18", "venue": "Miami Gardens", "teams": "Loser Match 101 vs Loser Match 102", "match": "Match for Third Place"},
        {"date": "July 19", "venue": "East Rutherford", "teams": "Winner Match 101 vs Winner Match 102", "match": "World Cup Final"}
    ]

    st.markdown("<div class='ko-bracket-container'>", unsafe_allow_html=True)
    for km in ko_matches:
        st.markdown(f"""
            <div class='ko-match-card'>
                <div class='ko-match-info'>
                    <span class='ko-match-date'>📆 {km['date']} – {km['venue']}</span>
                    <span class='ko-match-teams'>{km['teams']}</span>
                </div>
                <div><span class='ko-match-venue' style='font-weight:800; color:#ff7d23;'>{km['match']}</span></div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── GROUPS CANVAS ──
with st.expander("📊 GROUP STAGE TABLES & FIXTURES", expanded=group_expanded):
    if API_TOKEN == "placeholder":
        st.warning("⚠️ Using placeholder API key.")
    else:
        g_keys = list(processed_standings.keys())
        for i in range(0, len(g_keys), 2):
            row_cols = st.columns(2)
            for j in range(2):
                if i + j < len(g_keys):
                    group_name = g_keys[i + j]
                    table_data = processed_standings[group_name]
                    teams_in_group = [row["name"] for row in table_data]

                    with row_cols[j]:
                        st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                        st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)

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
                                        <th style="text-align:center;">GD</th>
                                        <th style="text-align:center;">Pts</th>
                                    </tr>
                                </thead>
                                <tbody>"""
                        
                        for idx, row in enumerate(table_data, start=1):
                            t_name = row["name"]
                            owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                            flag_html = get_group_flag_html(t_name)
                            
                            # Dot Indicator Calculation Logic
                            dot_html = ""
                            if row["played"] == 3:
                                if idx <= 2:
                                    dot_html = "<span class='status-dot dot-green'></span>"
                                elif idx == 3 and t_name in highest_8_third_place:
                                    dot_html = "<span class='status-dot dot-green'></span>"
                                else:
                                    dot_html = "<span class='status-dot dot-red'></span>"

                            table_html += f"""<tr>
                                <td>{flag_html} <b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner}){dot_html}</span></td>
                                <td style="text-align:center;">{row["played"]}</td>
                                <td style="text-align:center;">{row["won"]}</td>
                                <td style="text-align:center;">{row["draw"]}</td>
                                <td style="text-align:center;">{row["lost"]}</td>
                                <td style="text-align:center;">{row["gf"]}</td>
                                <td style="text-align:center;">{row["gd"]}</td>
                                <td style="text-align:center;"><b>{row["pts"]}</b></td>
                            </tr>"""
                        table_html += "</tbody></table></div>"
                        st.markdown(table_html, unsafe_allow_html=True)

                        st.markdown("<div style='margin-bottom:6px;'><span style='font-size:12px; font-weight:700; color:#ff7d23;'>📅 Group Fixtures</span></div>", unsafe_allow_html=True)
                        group_fixtures = [
                            m for m in all_matches
                            if m.get("homeTeam", {}).get("name") in teams_in_group
                            or m.get("awayTeam", {}).get("name") in teams_in_group
                        ]

                        if group_fixtures:
                            group_fixtures.sort(key=lambda x: x.get("utcDate", ""))
                            for match in group_fixtures[:6]:
                                home_t = match.get("homeTeam", {})
                                away_t = match.get("awayTeam", {})
                                h_n = home_t.get("name", "TBD")
                                a_n = away_t.get("name", "TBD")
                                h_owner = SWEEPSTAKE_MAPPING.get(h_n, "Unassigned")
                                a_owner = SWEEPSTAKE_MAPPING.get(a_n, "Unassigned")

                                dt_uk = format_to_uk_time(match.get("utcDate"))
                                local_time_str = dt_uk.strftime("%d/%m %H:%M") if dt_uk else "TBD"

                                h_flg = get_group_flag_html(h_n)
                                a_flg = get_group_flag_html(a_n)

                                lookup_key = f"{h_n.lower()}_v_{a_n.lower()}"
                                if lookup_key in SPREADSHEET_OVERRIDES:
                                    s_row = SPREADSHEET_OVERRIDES[lookup_key]
                                    if "live" in s_row["status"]:
                                        display_score = f"<span style='color:#CC0000; font-weight:800;'>LIVE 🔴 {s_row['homeScore']}-{s_row['awayScore']}</span>"
                                        row_class = "fixture-row fixture-row-live"
                                    elif "finished" in s_row["status"] or "completed" in s_row["status"]:
                                        display_score = f"<b>{s_row['homeScore']} - {s_row['awayScore']}</b>"
                                        row_class = "fixture-row"
                                    else:
                                        display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                        row_class = "fixture-row"
                                else:
                                    m_status = match.get("status")
                                    if m_status == "FINISHED":
                                        h_s, a_s = get_live_score(match)
                                        display_score = f"<b>{h_s} - {a_s}</b>"
                                        row_class = "fixture-row"
                                    elif m_status in ["IN_PLAY", "PAUSED"]:
                                        h_s, a_s = get_live_score(match)
                                        display_score = f"<span style='color:#CC0000; font-weight:800;'>LIVE 🔴 {h_s}-{a_s}</span>"
                                        row_class = "fixture-row fixture-row-live"
                                    else:
                                        display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                        row_class = "fixture-row"

                                st.markdown(f"""
                                    <div class="{row_class}">
                                        <div style="text-align: left; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            {h_flg} <span>{h_n}</span> <span style="font-size:9px; color:#777;">({h_owner})</span>
                                        </div>
                                        <div style="text-align: center; width: 16%; font-size:11px;">
                                            {display_score}
                                        </div>
                                        <div style="text-align: right; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            <span style="font-size:9px; color:#777;">({a_owner})</span> <span>{a_n}</span> {a_flg}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                        # Key Player Profile Cards
                        active_cards = []
                        for team_name in teams_in_group:
                            if team_name in GROUP_PLAYERS:
                                p = GROUP_PLAYERS[team_name]
                                card = f"""
                                <div style="background: #FFFFFF; border: 1px solid #EAEAEA; border-radius: 8px; width: 110px; height: 140px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); text-align: center; margin: 4px;">
                                    <img src="{p['img_url']}" style="width: 100%; height: 90px; object-fit: contain; object-position: top; border-radius: 4px;" loading="eager" referrerpolicy="no-referrer">
                                    <div style="font-size: 10px; font-weight: 800; color: #333; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 2px;">{p['player_name']}</div>
                                    <div style="font-size: 8px; font-weight: 600; color: #ff7d23; text-transform: uppercase; margin-top: 2px;">{team_name}</div>
                                </div>"""
                                active_cards.append(card)

                        if active_cards:
                            st.markdown("<div style='text-align: center; margin-top: 10px;'><span style='font-size:12px; font-weight:700; color:#ff7d23;'>🔑 Key Players</span></div>", unsafe_allow_html=True)
                            full_html = f"""
                            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; width: 100%; font-family: sans-serif; padding: 5px 0;">
                                {"".join(active_cards)}
                            </div>"""
                            components.html(full_html, height=170, scrolling=False)
                        st.markdown('</div>', unsafe_allow_html=True)

        # ── OVERPERFORMANCE LEADERBOARD ──
        st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 2px solid #ff7d23;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overperformance Table</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 13px; margin-bottom: 20px;'>Ranked by overperformance: (Expected Rank - Actual Rank)</p>", unsafe_allow_html=True)

        master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))

        master_table_html = """
        <div class="table-responsive-wrapper">
            <table class="custom-dashboard-table" style="width:100%;">
                <thead>
                    <tr>
                        <th style="width: 100px;">Pos</th>
                        <th>Team</th>
                        <th style="text-align:center;">Expected</th>
                        <th style="text-align:center;">Actual</th>
                        <th style="text-align:center;">P</th>
                        <th style="text-align:center;">GD</th>
                        <th style="text-align:center;">Pts</th>
                        <th style="text-align:right; padding-right:15px;">Score</th>
                    </tr>
                </thead>
                <tbody>"""
        
        for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
            owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
            flag_html = get_group_flag_html(team_row["name"])
            pos_str = "1 🚀" if display_idx == 1 else ("48 💩" if display_idx == 48 else str(display_idx))
            
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

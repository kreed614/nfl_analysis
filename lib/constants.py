#!/usr/bin/env python3

from dataclasses import dataclass
from lib.db_utils import ReadWrite


@dataclass
class Inputs:
    WEEK = 11  # the most recent completed week
    YEAR = 2022
    if WEEK > 17:
        SEASON = 'postseason'
        SEASON_VAL = 3
    else:
        SEASON = 'regular'
        SEASON_VAL = 2
    URL = 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/'


@dataclass
class Files:
    STATS = ReadWrite('./db/stats.json').read()
    BENCHMARKS = ReadWrite('./db/benchmark_stats.json').read()
    DETAILS = ReadWrite('./db/player_details.json').read()
    DEPTH_CHART = ReadWrite('./db/depth_chart.json').read()
    SCHEDULE = ReadWrite('./db/schedule.json').read()
    FILTERED_STATS = ReadWrite('./db/filtered_stats.json').read()
    PROCESSED_STATS = ReadWrite('./db/processed_stats.json').read()
    RESULTS = ReadWrite('./db/results.json').read()
    TIMESTAMPS = ReadWrite('./db/timestamps.json').read()
    INJURIES = ReadWrite('./db/injuries.json').read()


@dataclass
class Lists:
    key_stats = [
        "gamesPlayed", "ESPNRBRating", "stuffYardsLost", "stuffs", "ESPNWRRating",
        "netYardsPerGame", "totalTouchdowns", "rushingAttempts", "yardsPerGame", "receivingFirstDowns",
        "receivingYardsPerGame", "yardsPerReception", "receivingTargets", "ESPNQBRating",
        "fumbles", "interceptionPct", "sacks", "avgGain", "completionPct", "netPassingYardsPerGame",
        "passingTouchdownPct", "totalPointsPerGame", "yardsPerCompletion", "netYardsPerPassAttempt",
        "rushingFirstDowns", "rushingYardsPerGame", "yardsPerRushAttempt", "fumblesForced", "fumblesRecovered",
        "hurries", "passesDefended", "QBHits", "sacks", "totalTackles", "stuffs",
        "interceptionTouchdowns", "interceptions"
    ]

    fantasy_positions = [
        'quarterback', 'running back', 'wide receiver', 'tight end', 'place kicker'
    ]

    defense_positions = [
        "left defensive end", "left defensive tackle", "right defensive tackle",
        "right defensive end", "weakside linebacker", "middle linebacker", "strongside linebacker",
        "right inside linebacker", "left inside linebacker", "nose tackle"
    ]

    secondary_positions = [
        "left cornerback", "strong safety", "free safety", "right cornerback",
    ]

    offense_positions = [
        "wide receiver", "quarterback", "tight end", "running back", "bullback"
    ]

    # maybe incorporate fullback
    skill_positions = [
        'quarterback', 'running back', 'wide receiver', 'tight end'
    ]

    offensive_line = [
        "left tackle", "left guard", "center", "right tackle", "right guard"
    ]

    passing_defense_stats = [
        "QBHits," "sacks", "hurries", "passesDefended", "interceptions"
    ]

    general_defense_stats = [
        "gamesPlayed", "fumblesForced", "fumblesRecovered", "totalTackles", "interceptionTouchdowns"
    ]

    FANTASY_TEAM = [
        "4241479", "15795", "2976212", "3043078", "15807", "4036133", "4035538", "4047650", "3045144", "4038941", "2580216", "3128429", "15920", "4360078"
    ]


@dataclass
class Maps:
    KEY_STATS = {
        'running back': {
            'general': ["RBR", "play_pct"],
            'negative': ["rushing_fumbles_pct", "stuffs_pct"],
            'positive': [
                "yds_per_game", "rushing_yds_per_attempt", "reception_pct",
                "yds_per_reception", "yds_after_catch"
            ]
        },
        'wide receiver': {
            'general': ["WRR", "play_pct"],
            'negative': [],
            'positive': [
                'yds_per_reception', 'yds_per_game', 'yds_after_catch'
            ]
        },
        'tight end': {
            'general': ["RBR", "WRR", "play_pct"],
            'negative': ["rushing_fumbles_pct", "stuffs_pct"],
            'positive': [
                "yds_per_game", "rushing_yds_per_attempt", "reception_pct",
                "yds_per_reception", "yds_after_catch"
            ]
        },
        'quarterback': {
            'general': ["QBR"],
            'negative': ["interception_pct", "stuffs_pct"],
            'positive': [
                "passing_pct", "completion_pct", "passing_yds_per_game",
                "rushing_pct", "rush_yds_per_attempt"
            ]
        },
        'end': {
            "fumblesForced", "fumblesRecovered", "gamesPlayed", "hurries",
            "passesDefended", "QBHits", "sacks", "totalTackles", "stuffs", "interceptionTouchdowns",

        },
        "tackle": {
            "fumblesForced", "fumblesRecovered", "gamesPlayed", "hurries",
            "passesDefended", "QBHits", "sacks", "totalTackles", "stuffs", "interceptionTouchdowns",
        },
        "linebacker": {
            "fumblesForced", "fumblesRecovered", "gamesPlayed", "hurries",
            "passesDefended", "QBHits", "sacks", "totalTackles", "stuffs", "interceptionTouchdowns",
        },
        "cornerback": {
            "interceptions", "interceptionTouchdowns", "totalTackles", "gamesPlayed", "passesDefended", "fumblesForced"
        },
        "safety": {
            "interceptions", "interceptionTouchdowns", "totalTackles", "gamesPlayed", "passesDefended", "fumblesForced"
        },
    }

    ABBR_TEAM = {
        "ARI": "arizona cardinals",
        "SF": "san francisco 49ers",
        "PHI": "philadelphia eagles",
        "WAS": "washington commanders",
        "ATL": "atlanta falcons",
        "TEN": "tennessee titans",
        "LAR": "los angeles rams",
        "PIT": "pittsburgh steelers",
        "NE": "new england patriots",
        "CLE": "cleveland browns",
        "SEA": "seattle seahawks",
        "HOU": "houston texans",
        "LV": "las vegas raiders",
        "LAC": "los angeles chargers",
        "BAL": "baltimore ravens",
        "JAX": "jacksonville jaguars",
        "GB": "green bay packers",
        "NYG": "new york giants",
        "IND": "indianapolis colts",
        "NYJ": "new york jets",
        "CIN": "cincinnati bengals",
        "MIA": "miami dolphins",
        "CAR": "carolina panthers",
        "NO": "new orleans saints",
        "DAL": "dallas cowboys",
        "DEN": "denver broncos",
        "TB": "tampa bay buccaneers",
        "CHI": "chicago bears",
        "KC": "kansas city chiefs",
        "BUF": "buffalo bills",
        "MIN": "minnesota vikings",
        "DET": "detroit lions"
    }

    NAME_TEAM = {
        "bills": "buffalo bills",
        "rams": "los angeles rams",
        "saints": "new orleans saints",
        "falcons": "atlanta falcons",
        "49ers": "san francisco 49ers",
        "bears": "chicago bears",
        "steelers": "pittsburgh steelers",
        "bengals": "cincinnati bengals",
        "eagles": "philadelphia eagles",
        "lions": "detroit lions",
        "patriots": "new england patriots",
        "dolphins": "miami dolphins",
        "ravens": "baltimore ravens",
        "jets": "new york jets",
        "jaguars": "jacksonville jaguars",
        "commanders": "washington commanders",
        "browns": "cleveland browns",
        "panthers": "carolina panthers",
        "colts": "indianapolis colts",
        "texans": "houston texans",
        "giants": "new york giants",
        "titans": "tennessee titans",
        "packers": "green bay packers",
        "vikings": "minnesota vikings",
        "chiefs": "kansas city chiefs",
        "cardinals": "arizona cardinals",
        "raiders": "las vegas raiders",
        "chargers": "los angeles chargers",
        "buccaneers": "tampa bay buccaneers",
        "cowboys": "dallas cowboys",
        "broncos": "denver broncos",
        "seahawks": "seattle seahawks",
    }

    CITY_TEAM = {
        "arizona": "arizona cardinals",
        "san francisco": "san francisco 49ers",
        "philadelphia": "philadelphia eagles",
        "washington": "washington commanders",
        "atlanta": "atlanta falcons",
        "tennessee": "tennessee titans",
        "l.a. rams": "los angeles rams",
        "pittsburgh": "pittsburgh steelers",
        "new england": "new england patriots",
        "cleveland": "cleveland browns",
        "seattle": "seattle seahawks",
        "houston": "houston texans",
        "las vegas": "las vegas raiders",
        "l.a. chargers": "los angeles chargers",
        "baltimore": "baltimore ravens",
        "jacksonville": "jacksonville jaguars",
        "green bay": "green bay packers",
        "n.y. giants": "new york giants",
        "indianapolis": "indianapolis colts",
        "n.y. jets": "new york jets",
        "cincinnati": "cincinnati bengals",
        "miami": "miami dolphins",
        "carolina": "carolina panthers",
        "new orleans": "new orleans saints",
        "dallas": "dallas cowboys",
        "denver": "denver broncos",
        "tampa bay": "tampa bay buccaneers",
        "chicago": "chicago bears",
        "kansas city": "kansas city chiefs",
        "buffalo": "buffalo bills",
        "minnesota": "minnesota vikings",
        "detroit": "detroit lions"
    }

    TEAM_CITY = {
        "arizona cardinals": "arizona",
        "san francisco 49ers": "san francisco",
        "philadelphia eagles": "philadelphia",
        "washington commanders": "washington",
        "atlanta falcons": "atlanta",
        "tennessee titans": "tennessee",
        "los angeles rams": "l.a. rams",
        "pittsburgh steelers": "pittsburgh",
        "new england patriots": "new england",
        "cleveland browns": "cleveland",
        "seattle seahawks": "seattle",
        "houston texans": "houston",
        "las vegas raiders": "las vegas",
        "los angeles chargers": "l.a. chargers",
        "baltimore ravens": "baltimore",
        "jacksonville jaguars": "jacksonville",
        "green bay packers": "green bay",
        "new york giants": "n.y. giants",
        "indianapolis colts": "indianapolis",
        "new york jets": "n.y. jets",
        "cincinnati bengals": "cincinnati",
        "miami dolphins": "miami",
        "carolina panthers": "carolina",
        "new orleans saints": "new orleans",
        "dallas cowboys": "dallas",
        "denver broncos": "denver",
        "tampa bay buccaneers": "tampa bay",
        "chicago bears": "chicago",
        "kansas city chiefs": "kansas city",
        "buffalo bills": "buffalo",
        "minnesota vikings": "minnesota",
        "detroit lions": "detroit"
    }

    TEAM_IDS = {
        'atlanta falcons': 1,
        'buffalo bills': 2,
        'chicago bears': 3,
        'cincinnati bengals': 4,
        'cleveland browns': 5,
        'dallas cowboys': 6,
        'denver broncos': 7,
        'detroit lions': 8,
        'green bay packers': 9,
        'tennessee titans': 10,
        'indianapolis colts': 11,
        'kansas city chiefs': 12,
        'las vegas raiders': 13,
        'los angeles rams': 14,
        'miami dolphins': 15,
        'minnesota vikings': 16,
        'new england patriots': 17,
        'new orleans saints': 18,
        'new york giants': 19,
        'new york jets': 20,
        'philadelphia eagles': 21,
        'arizona cardinals': 22,
        'pittsburgh steelers': 23,
        'los angeles chargers': 24,
        'san francisco 49ers': 25,
        'seattle seahawks': 26,
        'tampa bay buccaneers': 27,
        'washington commanders': 28,
        'carolina panthers': 29,
        'jacksonville jaguars': 30,
        'baltimore ravens': 33,
        'houston texans': 34
    }

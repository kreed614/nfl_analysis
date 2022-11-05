#!/usr/bin/env python3

from typing import Dict
from lib.constants import Inputs, Files, Lists
from lib.db_utils import GetData


def schedule(data: str) -> Dict:
    """Formats the raw HTML pulled from the CBS sports weekend
    schedule. Sorts through each day and parses out the teams
    playing in each match. 

    Args:
        data (str): raw HTML from CBS sports

    Returns:
        Dict: Each day in the weekend contains a list of lists for 
        each match that day. Each match is a list containing a pair of 
        city names. NOTE: This can be mapped to the CITY_FULL map in 
        lib.constants to provide eachfull team name. 
    """

    match_ups = []
    for day in data:
        date = day.text.split('\n')[2].strip()
        games_table = day.find_next('tbody')
        games = games_table.find_all('tr')
        for game in games:
            teams = game.find_all('span', class_='TeamName')
            if Inputs.SEASON == 'regular':
                match_ups.append([date, teams[0].text, teams[1].text])
            elif Inputs.SEASON == 'postseason':
                match_ups.append([date, teams[0].text.split(
                    '\n')[-1].strip(), teams[1].text.split('\n')[-1].strip()])
        dates = set([day[0] for day in match_ups])
        match_dict = {date: [] for date in dates}

    for match in match_ups:
        match_dict[match[0]].append([match[1].lower(), match[2].lower()])

    return match_dict


def depth_chart(data: Dict) -> Dict:
    """Sorts through the positions in a team's depth chart or organize
    dictionaries in the order of position -> depth -> athlete details. 
    Athlete details include: name, status, injury date, and ESPN ID.

    Args:
        data (Dict): an object containing the entire query for a team's
        depth chart (refer to mocks/raw_depth_chart.json)

    Returns:
        Dict: each team's formatted depth chart
        {
            "position a": {
                "1": {
                    "name": athlete's first and last name,
                    "status": the health status of the athlete,
                    "injury date": if hurt, date of the injury,
                    "id": the ESPN ID for the athlete
                },
                "2": {...}
            }, 
            "position b": {...}
        }
    """

    depth_chart = {}
    for items in data['items']:
        for position in items.get('positions'):
            position_name = items['positions'][position]['position'].get(
                'displayName')
            depth_chart[position_name] = {}
            for athlete in items['positions'][position]['athletes']:
                player = GetData(athlete['athlete']['$ref']
                                 ).query()
                status = 'healthy'
                date = 'n/a'
                if player.get("injuries"):
                    status = player["injuries"][0].get('status')
                    date = player["injuries"][0].get('date')

                depth_chart[position_name][str(athlete['rank'])] = {
                    "name": player.get("displayName").lower(),
                    "status": status,
                    "injury date": date,
                    "id": player.get("id")
                }
    return depth_chart


def player_details(data: Dict, team: str) -> Dict:
    """Sorts through each team's depth chart to build a similar
    dictionary, but with keys at the athlete level instead of the
    team level.

    Args:
        data (Dict): the depth chart for each team (see the return value
        of depth_chart() for reference)
        team (str): the team the athlete plays on

    Returns:
        Dict: The key details of each player
        {
            "athlete1 id": {
                "name": athletes first and last name,
                "team": team name passed into the function,
                "position": position played,
                "depth": order in the team's depth chart, 
                "status": health status,
                "injury date": if injured, date of injury
            }, 
            "athlete2 id": {...},
        }
    """
    player_details = {}
    for position in data:
        for rank in data[position]:
            player_details[data[position][rank]['id']] = {
                "name": data[position][rank]['name'],
                "team": team,
                "position": position.lower(),
                "depth": rank,
                "status": data[position][rank]['status'],
                "injury_date": data[position][rank]['injury date'],
            }
    return player_details


def stats(data: Dict) -> Dict:
    """Formats the data provided by ESPN on every stat for an individual 
    athlete into an easily digestible dictionary.

    Args:
        data (Dict): an object containing the entire query for an athlete's
        stats (refer to mocks/raw_stats.json). 

    Returns:
        Dict: stat (str), value (float) pairs for each stat associated with the
        athlete (refer to mocks/stats.json).
    """
    stats = {}
    for i in range(len(data['splits']['categories'])):
        for j in range(len(data['splits']['categories'][i]['stats'])):
            stat_name = data['splits']['categories'][i]['stats'][j]['name']
            stat_value = data['splits']['categories'][i]['stats'][j]['value']
            stats[stat_name] = stat_value
    return stats


def results(data: dict) -> Dict:
    """Formats the results of a single game

    Args:
        data (dict): an object containing the entire query for a game's
        results (refer to mocks/raw_results.json).

    Returns:
        Dict: details of each team and their performance during the game
        {
            'opponent': the opposing team in the game,
            'home_away': if the team was playing at home or on the road,
            'linescores': the team's points scored each quarter,
            'score': the total amount of points scored in the game,
            'records': the overall, home and away records for that team
        }
    """
    results = {}
    competitors = data.get('competitors')
    count = 1
    for competitor in competitors:
        team = competitor['team'].get('displayName').lower()
        opponent = competitors[count]['team'].get(
            'displayName').lower()
        home_away = competitor.get('homeAway')
        score = competitor.get('score')
        records = {
            'overall': competitor['records'][0].get('summary'),
            'home': competitor['records'][1].get('summary'),
            'away': competitor['records'][2].get('summary')
        }
        linescores = competitor.get('linescores')

        results[team] = {
            'opponent': opponent,
            'home_away': home_away,
            'linescores': linescores,
            'score': score,
            'records': records
        }
        count = 0

    return results

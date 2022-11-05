#!/usr/bin/env python3

from lib.db_utils import GetData, ReadWrite
from lib.constants import Inputs, Maps, Files
import update.data_formatting as formatter
import datetime
import sys


def update_schedule() -> None:
    """Scrapes the cbs sports website to get the correct schedule for the week's
    game that is defined in lib.constants.
    """
    url = f'https://www.cbssports.com/nfl/schedule/{Inputs.YEAR}/{Inputs.SEASON}/{Inputs.WEEK}/'
    ReadWrite('db/schedule.json',
              formatter.schedule(GetData(url).scrape().find_all('h4'))).write()


def update_depth_chart() -> None:
    """Sorts through the positions on each team to populate athletes
    and their ESPN player ID into a depth chart based on their position rank.
    """
    depth_charts = {}
    teams = Maps.TEAM_IDS
    progress = [0, len(teams)]
    for team in teams:
        progress[0] += 1
        sys.stdout.write(
            f"{progress[0]} out of {progress[1]} team depth charts complete \r")
        sys.stdout.flush()
        url = f'{Inputs.URL}2022/teams/{teams.get(team)}/depthcharts'
        depth_charts[team] = formatter.depth_chart(
            GetData(url).query())
    ReadWrite('db/depth_chart.json', depth_charts).write()


def update_player_details() -> None:
    """Sorts through the depth chart to build a separate dictionary that maps
    an ESPN ID directly to that athlete's details.
    """
    player_details = {}
    for team in Files.DEPTH_CHART:
        player_details[team] = formatter.player_details(
            Files.DEPTH_CHART[team], team)
    ReadWrite('./db/player_details.json', player_details).write()


def update_stats() -> None:
    """Sorts through each athlete to get the latest stats based on the 
    season to date. 
    """
    stats = {}
    athletes = Files.DETAILS
    progress = [0, len(athletes)]
    for athlete in athletes:
        progress[0] += 1
        sys.stdout.write(
            f"Stat updates {'{0:.2g}'.format((progress[0] / progress[1]) * 100)}% complete \r")
        sys.stdout.flush()
        url = f'{Inputs.URL}{Inputs.YEAR}/types/{Inputs.SEASON_VAL}/athletes/{athlete}/statistics/0'
        data = GetData(url).query()
        if data:
            stats[athlete] = formatter.stats(data)
    ReadWrite('db/stats.json', stats).write()
    ReadWrite(
        f'db/{Inputs.YEAR}_stats/week_{Inputs.WEEK - 1}.json', stats).write()


def update_results():
    """Sorts through each game of week and formatters the results
    """
    data = GetData(
        'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard').query()
    results = Files.RESULTS
    for event in data['events']:
        competitions = event['competitions']
        for competition in competitions:
            result = formatter.results(competition)
            for team in result:
                if results[team][str(Inputs.WEEK - 1)]:
                    raise Exception(
                        f"Can't overwrite week {Inputs.WEEK - 1} results")
                results[team][str(Inputs.WEEK - 1)] = result[team]
    ReadWrite('./db/results.json', results).write()
    print(f"Week {Inputs.WEEK - 1} updated")


def time_check():
    """A quick time check to make sure the update module isn't being run 
    outside of Monday night (after the evening game) or on Tuesday. This prevents
    incomplete data from being updated or data being overwritten. 

    Raises:
        Exception: exits the update module outside of when stats can be updated
    """
    time = datetime.datetime.now()
    if (time.day != 0 and time.hour < 21) or time.day != 1:
        raise Exception(
            f"Can't update outside of Monday evening or Tuesday")


def main():
    """To Run: python3 -m update.main
        Run this on Monday after the game or Tuesday before results are 
        overwritten by ESPN
    """
    time_check()
    update_results()
    print(f"Week {Inputs.WEEK - 1} updated")
    update_schedule()
    print(f"week {Inputs.WEEK} schedule updated")
    update_depth_chart()
    print("Depth Chart is updated")
    update_stats()
    print('Stats are updated')
    update_player_details()
    print('Player details are updated')


if __name__ == "__main__":
    main()

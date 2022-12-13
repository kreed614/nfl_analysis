#!/usr/bin/env python3

from lib.db_utils import ReadWrite, GetData
from lib.constants import Maps, Lists, Files, Inputs
import update.data_formatting as formatter
import process.data_processing as process
import pandas as pd
import sys
import datetime


def filter_stats() -> None:
    """Iterates through all the current stats for each player and 
    filters them into a select, more manageable amount of stats
    """

    details = Files.DETAILS
    stats = Files.STATS
    filtered_stats = {}
    for player in stats:
        if not details.get(player):
            continue
        team = details[player]['team']
        position = details[player]['position']
        filtered_stats[player] = process.filter_stats(
            stats.get(player), position, team)
    ReadWrite('./db/filtered_stats.json', filtered_stats).write()
    Files.TIMESTAMPS['filtered_stats'] = str(datetime.datetime.today())
    print("Stats filtered")


def process_stats() -> None:
    """Iterates through a team's depth chart and uses each players
    filtered stats to aggregate a team's overall performance
    """
    stats = Files.FILTERED_STATS
    depth_charts = Files.DEPTH_CHART
    details = Files.DETAILS
    processed_stats = Files.PROCESSED_STATS
    processed_stats[str(Inputs.WEEK)] = {}
    for team in depth_charts:
        ps = process.ProcessStats(team, stats)
        for position in depth_charts[team]:
            for depth in depth_charts[team][position]:
                id = depth_charts[team][position][depth].get('id')
                if details.get(id):
                    status = details[id].get('status')
                else:
                    continue
                if not stats.get(id) or (status != 'healthy' and status != 'questionable'):
                    continue
                if position in ['tight end', 'running back']:
                    ps.set_rushing(id)
                elif position in ['tight end', 'wide receiver']:
                    ps.set_receiving(id)
                elif position == 'quarterback' and depth == "1":
                    ps.set_quarterback(id)
                elif position in Lists.secondary_positions or Lists.defense_positions:
                    ps.set_passing_defense(id)
                    ps.set_rushing_defense(id)
        processed_stats[str(Inputs.WEEK)
                        ][team] = ps.get_processed_stats()
    ReadWrite('./db/processed_stats.json', processed_stats).write()
    Files.TIMESTAMPS['processed_stats'] = str(datetime.datetime.today())
    print("Stats processed")


def rank_teams() -> None:
    """Iterates through the processed stats to sort and rank each team 
    by their performance in each metric
    """
    metrics = ["quarterback", "receiving", "rushing",
               "passing_defense", "rushing_defense"]
    stats = Files.PROCESSED_STATS.get(str(Inputs.WEEK))
    stat_dict = {}
    for metric in metrics:
        stat_dict[metric] = {}
        stat_array = []
        for team in stats:
            stat_array.append([stats[team].get(metric), team])

        stat_array.sort(key=lambda stat_array: stat_array[0])
        n = 32
        for stat in stat_array:
            stat_dict[metric][stat[1]] = {
                "rank": n, "stat": stat[0]}
            n -= 1

    ReadWrite("./db/weekly_ranks.json", stat_dict).write()
    Files.TIMESTAMPS['weekly_ranks'] = str(datetime.datetime.today())
    print("Teams ranked")


def process_injuries() -> None:
    """Iterates through each player's details to check their injury 
    status and creates a new dataset containing all the information 
    around that player's injury
    """
    def update_db():
        # Get latest depth chart info
        depth_charts = {}
        teams = Maps.TEAM_IDS
        progress = [0, len(teams)]
        for team in teams:
            progress[0] += 1
            sys.stdout.write(
                f"{progress[0]} out of {progress[1]} team depth charts complete \t\r")
            sys.stdout.flush()
            url = f'{Inputs.URL}2022/teams/{teams.get(team)}/depthcharts'
            depth_charts[team] = formatter.depth_chart(
                GetData(url).query())
        ReadWrite('db/depth_chart.json', depth_charts).write()
        Files.TIMESTAMPS['depth_chart'] = str(datetime.datetime.today())

        # Get latest player details
        player_details = {}
        for team in depth_charts:
            for position in depth_charts.get(team):
                for rank in depth_charts[team][position]:
                    player_details[depth_charts[team][position][rank].get('id')] = formatter.player_details(
                        data=depth_charts[team][position][rank], team=team, position=position, rank=rank)
        ReadWrite('./db/player_details.json', player_details).write()
        Files.TIMESTAMPS['player_details'] = str(datetime.datetime.today())

    # check run time config to see if data is recent
    update_time = datetime.datetime.strptime(
        Files.TIMESTAMPS['depth_chart'], '%Y-%m-%d %H:%M:%S.%f')

    # check to see if the data is older than 1 day
    if datetime.datetime.today() > update_time + datetime.timedelta(days=1):
        print("Depth chart and player details out of date")
        update_db()
        print("Depth chart and player details updated")
        ReadWrite('./db/timestamps.json', Files.TIMESTAMPS).write()

    details = Files.DETAILS
    injuries = {}
    progress = [0, len(details)]
    for player in details:
        progress[0] += 1
        sys.stdout.write(
            f"Injury updates {'{0:.2g}'.format((progress[0] / progress[1]) * 100)}% complete \t\r")
        sys.stdout.flush()
        if details[player]['status'] != 'healthy':
            additional_info = GetData(
                details[player].get('ref')).query()
            if additional_info.get('details'):
                body_part = additional_info['details'].get('type')
                return_date = additional_info['details'].get('returnDate')
                status = additional_info['details']['fantasyStatus'].get(
                    'description').lower()
            else:
                body_part = None
                return_date = None
                status = None
            comments = additional_info.get('longComment')
            injuries[player] = {
                "name": details[player].get('name'),
                "team": details[player].get('team'),
                "position": details[player].get('position'),
                "depth": details[player].get('depth'),
                "status": status,
                "injury_date": details[player].get('injury_date').split('T')[0],
                "body_part": body_part,
                "return_date": return_date,
                "comments": comments,
            }

    ReadWrite('./db/injuries.json', injuries).write()
    Files.TIMESTAMPS['injuries'] = str(datetime.datetime.today())
    print("Injuries processed")


def process_defense_performance() -> None:
    """Iterates through each team's results week over week to 
    find the difference in rushing and passing yards between 
    weeks to calculate the average and total
    """
    defense_performances = {}
    results = Files.RESULTS
    depth_chart = Files.DEPTH_CHART

    # iterate through each team in the results file
    for team in results:
        performances = []
        # iterate through each week's results for that team
        for week in results[team]:
            # skip week 4 since there are no stats for week 3
            if week == "4":
                continue

            # get the opponent from that game
            opponent = results[team][week].get('opponent')
            # create StatDelta object for that week
            stat_deltas = process.StatDeltas(week)

            for position in depth_chart[opponent]:
                for depth in depth_chart[opponent][position]:
                    id = depth_chart[opponent][position][depth].get('id')
                    stat_deltas.set_rushing(id)
                    stat_deltas.set_receiving(id)
            # append that week's object to the list
            performances.append(stat_deltas.get_stat_deltas())

        df = pd.DataFrame(performances)
        defense_performances[team] = {
            'rushing': {
                'average': df['rushing'].mean(),
                'std': df['rushing'].std(),
                'total': df['rushing'].sum(),
            },
            'passing': {
                'average': df['receiving'].mean(),
                'std': df['receiving'].std(),
                'total': df['receiving'].sum(),
            }
        }

    ReadWrite('./db/defense_performance.json', defense_performances).write()
    Files.TIMESTAMPS['defense_performance'] = str(datetime.datetime.today())
    print("Defense performance processed")


def process_benchmarks() -> None:
    """Iterates through the filtered stats to sort each player's stats
    by position and then calculates to find the 90th percentile for 
    each stat
    """
    # BUG: this keeps breaking because for some reason, the filtered stats
    # function needs to run twice. The first time, there are stats that exist there
    # after the depth chart changes and they are no longer playing with a team

    stats = Files.FILTERED_STATS
    details = Files.DETAILS

    # A dictionary containing lists for each player's value for each stat
    stats_by_position = {}
    for player in stats:
        # avoid low outliers by omitting any player deeper than 3rd string
        if stats.get(player) and int(details[player].get('depth')) < 4:
            if not stats_by_position.get(details[player].get('position')):
                stats_by_position[details[player].get('position')] = []
            stats_by_position[details[player]
                              ['position']].append(stats[player])

    # a dictionary with the 90th percentile value for each stat
    benchmarks = {}
    for position in stats_by_position:
        df = pd.DataFrame(stats_by_position[position])
        if not df.empty:
            benchmarks[position] = {}
            for col in df:
                data = df[col].dropna()
                benchmarks[position][col] = data.quantile(q=0.9)

    ReadWrite('./db/benchmark_stats.json', benchmarks).write()
    Files.TIMESTAMPS['benchmarks'] = str(datetime.datetime.today())
    print("Benchmarks processed")


def identify_top_athletes() -> None:
    """References the benchmark stats to compare players against the 
    90th percentile for each stat and then creates a new dataset to 
    list those players and the stats they are elite in. This also includes
    negative stats, so "top athletes" is a bit of a misnomber
    """
    stats = Files.FILTERED_STATS
    benchmarks = Files.BENCHMARKS
    details = Files.DETAILS
    top_athletes = {}
    for player in stats:
        for stat in stats[player]:
            if not top_athletes.get(stat):
                top_athletes[stat] = {}
            benchmark = benchmarks[details[player].get('position')][stat]
            player_stat = stats[player][stat]
            if stats[player].get(stat) and player_stat > benchmark:
                top_athletes[stat][player] = {"name": details[player].get(
                    'name'), "position": details[player].get('position'), "stat": player_stat}

    ReadWrite('./db/top_athletes.json', top_athletes).write()
    Files.TIMESTAMPS['top_athletes'] = str(datetime.datetime.today())
    print("Top athletes identified")


def process_offensive_line_performance() -> None:
    """Quanitfies the effectiveness of the offensive line through the 
    amount of rush yards gained by the offense and sacks on the qb
    """
    o_line_performance = ReadWrite(
        './db/offensive_line_performance.json').read()

    # Won't overwrite
    if o_line_performance.get(str(Inputs.WEEK)):
        return None

    o_line_performance[str(Inputs.WEEK)] = {}

    # Reference the static depth chart updated at the beginning of the week
    # so any mid week changes aren't reflected
    depth_chart = ReadWrite(
        f'./db/{Inputs.YEAR}_depth_charts/week_{Inputs.WEEK}.json').read()

    for team in depth_chart:
        # continue if the team didn't have a game that week
        if not Files.RESULTS[team].get(str(Inputs.WEEK)):
            continue
        opponent = Files.RESULTS[team][str(Inputs.WEEK)].get('opponent')

        o_line_performance[str(Inputs.WEEK)][team] = {}
        sd = process.StatDeltas(Inputs.WEEK)

        # populate first string offensive linemen
        offensive_lineman = {}
        for position in depth_chart.get(team):
            if position in Lists.offensive_line:
                offensive_lineman[position] = depth_chart[team][position]["1"].get(
                    'id')

            # get team's rushing performance
            for depth in depth_chart[team][position]:
                sd.set_rushing(depth_chart[team][position][depth].get('id'))

        # get sacks on QB
        for position in depth_chart[opponent]:
            if position in Lists.defense_positions:
                for depth in depth_chart[opponent][position]:
                    sd.set_sacks(depth_chart[opponent]
                                 [position][depth].get('id'))

        stat_deltas = sd.get_stat_deltas()
        o_line_performance[str(Inputs.WEEK)][team] = {
            'offensive_lineman': offensive_lineman,
            'offense_rushing': stat_deltas.get('rushing'),
            'qb_sacks': stat_deltas.get('sacks')
        }

    ReadWrite('./db/offensive_line_performance.json',
              o_line_performance).write()
    print("Offensive Line performance processed")


def main():
    """Use this module to process the stats that are added through the 
    update module. This condenses the massive amount of stats and aggregates
    them into somethng more manageable while also providing new datasets 
    that can be used for analysis
    """
    process_injuries()
    filter_stats()
    process_benchmarks()
    identify_top_athletes()
    process_stats()
    process_offensive_line_performance()
    process_defense_performance()
    rank_teams()

    ReadWrite('./db/timestamps.json', Files.TIMESTAMPS).write()


if __name__ == "__main__":
    main()

from lib.constants import Files, Lists
from lib.db_utils import ReadWrite
from typing import Dict, Tuple


class ProcessStats:
    """_summary_
    """

    def __init__(self, team, stats):
        self.processed_stats = {
            'quarterback': 0,
            'receiving': 0,
            'rushing': 0,
            'passing_defense': 0,
            'rushing_defense': 0,
        }
        self.stats = stats
        self.team = team

    def _get_stat(self, stat: str, id: str) -> float:
        """_summary_

        Args:
            stat (str): _description_
            id (str): _description_

        Returns:
            float: _description_
        """
        if not self.stats.get(id):
            return 0.0
        elif self.stats[id].get(stat):
            return self.stats[id].get(stat)
        else:
            return 0.0

    def set_rushing(self, id) -> None:
        """_summary_

        Args:
            stats (Dict): _description_
        """
        impact = self._get_stat('rushing_yds_per_game', id)
        negative_probability = self._get_stat(
            'rushing_fumbles_pct', id) + self._get_stat('stuffs_pct', id)
        self.processed_stats['rushing'] += impact - \
            (impact * negative_probability)

    def set_receiving(self, id) -> None:
        """_summary_

        Args:
            stats (Dict): _description_
            team (str): _description_
        """
        qb_id = Files.DEPTH_CHART[self.team]['quarterback']["1"]['id']
        interception_pct = self._get_stat('interception_pct', qb_id)
        impact = self._get_stat('receiving_yds_per_game', id)
        negative_probability = (self._get_stat(
            'play_pct', id) * interception_pct)
        self.processed_stats['receiving'] += impact - \
            (impact * negative_probability)

    def set_quarterback(self, id) -> None:
        """_summary_

        Args:
            stats (Dict): _description_
        """
        impact = self._get_stat('passing_yds_per_game', id) + \
            self._get_stat('rush_yds_per_game', id)
        negative_probability = self._get_stat(
            "stuffs_pct", id) + self._get_stat("interception_pct", id)
        self.processed_stats['quarterback'] = impact - \
            (impact * negative_probability)

    def set_passing_defense(self, id) -> None:
        """_summary_

        Args:
            stats (Dict): _description_
        """
        self.processed_stats['passing_defense'] += sum([self._get_stat(
            stat, id) for stat in ['interceptions', 'sacks', 'qb_hits', 'passes_defended']])

    def set_rushing_defense(self, id) -> None:
        """_summary_

        Args:
            stats (Dict): _description_
        """
        self.processed_stats['rushing_defense'] += sum([self._get_stat(
            stat, id) for stat in ['fumbles', 'tackles', 'tackles_for_loss', 'stuffs']])

    def get_processed_stats(self) -> Dict:
        """Getter function for the values calculated in each setter method

        Returns:
            Dict: the aggregated values for a team's quarterback, rushing and receiving 
            offense + rushing and passing defense
        """
        return self.processed_stats


class StatDeltas:
    def __init__(self, week):
        self.stat0 = ReadWrite(
            f'./db/2022_stats/week_{int(week) - 1}.json').read()
        self.stat1 = ReadWrite(f'./db/2022_stats/week_{week}.json').read()
        self.stat_deltas = {
            'rushing': 0,
            'receiving': 0,
            'sacks': 0,
        }

    def _get_delta(self, stats):
        # played both games
        if stats[0] and stats[1]:
            return stats[0] - stats[1]
        # only played recent week
        elif stats[0] and not stats[1]:
            return stats[0]
        # didn't play recent week
        else:
            return 0

    def set_rushing(self, id):
        if self.stat0.get(id) and self.stat1.get(id):
            delta = self._get_delta([self.stat1[id].get(
                "rushingYards"), self.stat0[id].get("rushingYards")])
            self.stat_deltas['rushing'] += delta

    def set_receiving(self, id):
        if self.stat0.get(id) and self.stat1.get(id):
            delta = self._get_delta([self.stat1[id].get(
                "receivingYards"), self.stat0[id].get("receivingYards")])
            self.stat_deltas['receiving'] += delta

    def set_sacks(self, id):
        if self.stat0.get(id) and self.stat1.get(id):
            delta = self._get_delta([self.stat1[id].get(
                "sacks"), self.stat0[id].get("sacks")])
            self.stat_deltas['sacks'] += delta

    def get_stat_deltas(self):
        return self.stat_deltas


def filter_stats(stats: Dict, position: str, team: str) -> Dict:
    """_summary_

    Args:
        stats (Dict): _description_
        position (str): _description_
        team (str): _description_

    Returns:
        Dict: _description_
    """
    try:
        qb_total_plays = Files.STATS[Files.DEPTH_CHART[team]
                                     ['quarterback']["1"]['id']].get('totalOffensivePlays')
    except KeyError:
        qb_total_plays = 0

    targets = stats.get('receivingTargets') if stats.get(
        'receivingTargets') else 0
    rushes = stats.get('rushingAttempts') if stats.get(
        'rushingAttempts') else 0

    def validate(a, b):
        # Checks against division by 0 or None
        try:
            return a/b
        except Exception:
            return 0

    def get_quarterback():
        return {
            'QBR': stats.get('QBR'),
            'passing_pct': validate(stats.get('passingAttempts'), stats.get('totalOffensivePlays')),
            'completion_pct': validate(stats.get('completions'), stats.get('passingAttempts')),
            'interception_pct': validate(stats.get('interceptionPct'), 100),
            'passing_yds_per_game': validate(stats.get('passingYards'), stats.get('gamesPlayed')),
            'rushing_pct': validate(stats.get('rushingAttempts'), stats.get('totalOffensivePlays')),
            'rush_yds_per_attempt': validate(stats.get('rushingYards'), stats.get('rushingAttempts')),
            'rush_yds_per_game': validate(stats.get('rushingYards'), stats.get('gamesPlayed')),
            'stuffs_pct': validate(stats.get('stuffs'), stats.get('rushingAttempts'))
        }

    def get_running_back():
        return {
            'RBR': stats.get('ESPNRBRating'),
            'play_pct': validate((targets + rushes), qb_total_plays),
            'yds_per_game': stats.get('yardsPerGame'),
            'rushing_yds_per_game': validate(stats.get('rushingYards'), stats.get('gamesPlayed')),
            'rushing_yds_per_attempt': validate(stats.get('rushingYards'), stats.get('rushingAttempts')),
            'rushing_fumbles_pct': validate(stats.get('rushingFumbles'), stats.get('rushingAttempts')),
            'stuffs_pct': validate(stats.get('stuffs'), stats.get('rushingAttempts')),
            'reception_pct': validate(stats.get('receptions'), stats.get('receivingTargets')),
            'yds_per_reception': validate(stats.get('receivingYards'), stats.get('receptions')),
            'yds_after_catch': validate(stats.get('receivingYardsAfterCatch'), stats.get('receptions'))
        }

    def get_wide_receiver():
        return {
            'WRR': stats.get('ESPNWRRating'),
            'play_pct': validate(targets, qb_total_plays),
            'reception_pct': validate(stats.get('receptions'), stats.get('receivingTargets')),
            'yds_per_reception': validate(stats.get('receivingYards'), stats.get('receptions')),
            'receiving_yds_per_game': validate(stats.get('receivingYards'), stats.get('gamesPlayed')),
            'yds_per_game': stats.get('yardsPerGame'),
            'yds_after_catch': validate(stats.get('receivingYardsAfterCatch'), stats.get('receptions'))
        }

    def get_tight_end():
        return {
            'RBR': stats.get('ESPNRBRating'),
            'WRR': stats.get('ESPNWRRating'),
            'play_pct': validate((targets + rushes), qb_total_plays),
            'yds_per_game': stats.get('yardsPerGame'),
            'receiving_yds_per_game': validate(stats.get('receivingYards'), stats.get('gamesPlayed')),
            'rushing_yds_per_game': validate(stats.get('rushingYards'), stats.get('gamesPlayed')),
            'rushing_yds_per_attempt': validate(stats.get('rushingYards'), stats.get('rushingAttempts')),
            'rushing_fumbles_pct': validate(stats.get('rushingFumbles'), stats.get('rushingAttempts')),
            'stuffs_pct': validate(stats.get('stuffs'), stats.get('rushingAttempts')),
            'reception_pct': validate(stats.get('receptions'), stats.get('receivingTargets')),
            'yds_per_reception': validate(stats.get('receivingYards'), stats.get('receptions')),
            'yds_after_catch': validate(stats.get('receivingYardsAfterCatch'), stats.get('receptions'))
        }

    def get_secondary():
        return {
            "fumbles": validate(stats.get("fumblesForced"), stats.get("gamesPlayed")),
            "tackles": validate(stats.get("totalTackles"), stats.get("gamesPlayed")),
            "interceptions": validate(stats.get("interceptions"), stats.get("gamesPlayed")),
            "passes_defended": validate(stats.get("passesDefended"), stats.get("gamesPlayed")),
        }

    def get_defense():
        return {
            "fumbles": validate(stats.get("fumblesForced"), stats.get("gamesPlayed")),
            "tackles": validate(stats.get("totalTackles"), stats.get("gamesPlayed")),
            "interceptions": validate(stats.get("interceptions"), stats.get("gamesPlayed")),
            "passes_defended": validate(stats.get("passesDefended"), stats.get("gamesPlayed")),
            "sacks": validate(stats.get("sacks"), stats.get("gamesPlayed")),
            "qb_hits": validate(stats.get("QBHits"), stats.get("gamesPlayed")),
            "tackles_for_loss": validate(stats.get("tacklesForLoss"), stats.get("gamesPlayed")),
            "stuffs": validate(stats.get("stuffs"), stats.get("gamesPlayed")),
        }

    if position == 'quarterback':
        return get_quarterback()
    elif position == 'running back':
        return get_running_back()
    elif position == 'wide receiver':
        return get_wide_receiver()
    elif position == 'tight end':
        return get_tight_end()
    elif position in Lists.secondary_positions:
        return get_secondary()
    elif position in Lists.defense_positions:
        return get_defense()
    else:
        return {}

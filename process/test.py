import unittest
import process.data_processing as process
from lib.db_utils import ReadWrite
from lib.constants import Lists


class TestProcessing(unittest.TestCase):

    def test_process_set_quarterback(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position == 'quarterback' and depth == "1":
                    ps.set_quarterback(id)
        test = ps.get_processed_stats().get('quarterback')
        expected = 201.03663910627367
        self.assertEqual(test, expected)

    def test_process_set_receiving(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in ['tight end', 'wide receiver']:
                    ps.set_receiving(id)
        test = ps.get_processed_stats().get('receiving')
        expected = 169.25833333333335
        self.assertEqual(test, expected)

    def test_process_set_rushing(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in ['tight end', 'running back']:
                    ps.set_rushing(id)
        test = ps.get_processed_stats().get('rushing')
        expected = 172.08822588307623
        self.assertEqual(test, expected)

    def test_process_set_rushing_defense(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in Lists.secondary_positions or position in Lists.defense_positions:
                    ps.set_rushing_defense(id)
        test = ps.get_processed_stats().get('rushing_defense')
        expected = 78.99007936507935
        self.assertEqual(test, expected)

    def test_process_set_passing_defense(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in Lists.secondary_positions or position in Lists.defense_positions:
                    ps.set_passing_defense(id)
        test = ps.get_processed_stats().get('passing_defense')
        expected = 11.906746031746032
        self.assertEqual(test, expected)

    def test_delta_set_rushing(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        stats = ReadWrite('./process/mocks/filtered_stats.json').read()
        ps = process.ProcessStats('atlanta falcons', stats)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in Lists.secondary_positions or position in Lists.defense_positions:
                    ps.set_rushing(id)
        test = ps.get_processed_stats().get('rushing')
        expected = 13.512157287157288
        self.assertEqual(test, expected)

    def test_delta_set_rushing(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        sd = process.StatDeltas(7)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in ['tight end', 'running back']:
                    sd.set_rushing(id)
        test = sd.get_stat_deltas().get('rushing')
        expected = 76.0
        self.assertEqual(test, expected)

    def test_delta_set_receiving(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        sd = process.StatDeltas(7)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in ['tight end', 'wide receiver']:
                    sd.set_receiving(id)
        test = sd.get_stat_deltas().get('receiving')
        expected = 124.0
        self.assertEqual(test, expected)

    def test_delta_set_sacks(self):
        depth_charts = ReadWrite('./process/mocks/depth_chart.json').read()
        sd = process.StatDeltas(7)
        for position in depth_charts:
            for depth in depth_charts[position]:
                id = depth_charts[position][depth].get('id')
                if position in Lists.defense_positions:
                    sd.set_sacks(id)
        test = sd.get_stat_deltas().get('sacks')
        expected = 3.0
        self.assertEqual(test, expected)

    def test_filter_stats(self):
        details = ReadWrite('./process/mocks/player_details.json').read()
        stats = ReadWrite('./process/mocks/week_6.json').read()
        test = {}
        for player in stats:
            if not details.get(player):
                continue
            team = details[player]['team']
            position = details[player]['position']
            test[player] = process.filter_stats(
                stats.get(player), position, team)
        expected = ReadWrite('./process/mocks/filtered_stats.json').read()
        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main()

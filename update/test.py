#!/usr/bin/env python3

import unittest
import update.data_formatting as format
from lib.db_utils import GetData, ReadWrite


class TestUpdates(unittest.TestCase):

    def test_schedule(self):
        url = 'https://www.cbssports.com/nfl/schedule/2022/regular/4/'
        test = format.schedule(
            GetData(url).scrape().find_all('h4'))
        expected = ReadWrite('./update/mocks/schedule.json').read()
        self.assertEqual(test, expected)

    def test_depth_chart(self):
        data = ReadWrite('./update/mocks/raw_depth_chart.json').read()
        test = format.depth_chart(data)
        expected = ReadWrite('./update/mocks/depth_chart.json').read()
        self.assertEqual(test, expected)

    def test_player_details(self):
        test = {}
        data = ReadWrite('./update/mocks/depth_chart.json').read()
        for position in data:
            for rank in data[position]:
                test[data[position][rank].get('id')] = format.player_details(
                    data=data[position][rank], team="atlanta falcons", position=position, rank=rank)
        expected = ReadWrite('./update/mocks/player_details.json').read()
        self.assertEqual(test, expected)

    def test_stats(self):
        data = ReadWrite('./update/mocks/raw_stats.json').read()
        test = format.stats(data)
        expected = ReadWrite('./update/mocks/stats.json').read()
        self.assertEqual(test, expected)

    def test_results(self):
        data = ReadWrite('./update/mocks/raw_results.json').read()
        test = format.results(data)
        expected = ReadWrite('./update/mocks/results.json').read()
        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main()

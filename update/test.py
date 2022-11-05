#!/usr/bin/env python3

import unittest
import update.data_formatting as format
from lib.db_utils import GetData, ReadWrite


class TestUpdates(unittest.TestCase):

    def test_schedule(self):
        url = 'https://www.cbssports.com/nfl/schedule/2022/regular/4/'
        test = format.schedule(
            GetData(url).scrape().find_all('h4'))
        expected = ReadWrite('./mocks/schedule.json').read()
        self.assertEqual(test, expected)

    def test_depth_chart(self):
        data = ReadWrite('./mocks/raw_depth_chart.json').read()
        test = format.depth_chart(data)
        expected = ReadWrite('./mocks/depth_chart.json').read()
        self.assertEqual(test, expected)

    def test_player_details(self):
        data = ReadWrite('./mocks/depth_chart.json').read()
        test = format.player_details(data, 'atlanta falcons')
        expected = ReadWrite('./mocks/player_details.json').read()
        self.assertEqual(test, expected)

    def test_stats(self):
        data = ReadWrite('./mocks/raw_stats.json').read()
        test = format.stats(data)
        expected = ReadWrite('./mocks/stats.json').read()
        self.assertEqual(test, expected)

    def test_results(self):
        data = ReadWrite('./mocks/raw_results.json').read()
        test = format.results(data)
        expected = ReadWrite('./mocks/results.json').read()
        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main()

import logging
from unittest import TestCase
from random import randint

import log_config
import tub_utils
from tub_utils import STEP_RATE

log_config.prepare_logging(logging.INFO)

class TestHeatCalc(TestCase):
    def test_same_result_1(self):
        heating = tub_utils.CalcHeatTime_iterate(36, 38, 350, 40, 9.5 * 60)
        self.assertEqual(heating.start_time, 440, "start_time incorrect")
        self.assertEqual(heating.time_to_heat, 130, "time_to_heat incorrect")

    def test_same_result_2(self):
        heating = tub_utils.CalcHeatTime_algebra(36, 38, 350, 40, 9.5 * 60)
        self.assertAlmostEqual(heating.start_time, 440, delta=STEP_RATE)
        self.assertAlmostEqual(heating.time_to_heat, 130, delta=STEP_RATE)

    def test_random_results(self):
        for i in range(1000):
            start_time = 22 * 60 # 22:00
            start_temp = randint(22, 38)
            target_temp = randint(30, 40)
            cool_rate = randint(160, 400)
            heat_rate = randint(30, 60)
            time_left = 9.5 * 60  # 07:30 tomorrow
            logging.info(f"Trying: {start_temp}->{target_temp} at {cool_rate}/{heat_rate}")
            it_heating = tub_utils.CalcHeatTime_iterate(start_temp, target_temp, cool_rate, heat_rate, time_left)
            al_heating = tub_utils.CalcHeatTime_algebra(start_temp, target_temp, cool_rate, heat_rate, time_left)
            if (it_heating.start_time is None):
                try:
                    self.assertEqual(al_heating.start_time, None)
                except:
                    self.assertAlmostEqual(al_heating.start_time, time_left, delta=STEP_RATE)
            elif (al_heating.start_time is None):
                try:
                    self.assertEqual(al_heating.start_time, None)
                except:
                    self.assertAlmostEqual(al_heating.start_time, time_left, delta=STEP_RATE)
            else:
                self.assertAlmostEqual(it_heating.start_time, al_heating.start_time, delta=STEP_RATE)
                self.assertAlmostEqual(it_heating.time_to_heat, al_heating.time_to_heat, delta=STEP_RATE)
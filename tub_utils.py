import logging

# ---------------------------------------------------------------------------

ECO_MINS    = 7 * 60
STEP_RATE   = 10  # minutes per iteration for calculating heat time

from typing import NamedTuple

class tub_heating(NamedTuple):
    start_time: int
    time_to_heat: int

def CalcHeatTime_iterate(start_temp, target_temp, cool_rate, heat_rate, time_left):
    logging.info("calculating start and duration (iterative)")
    time_to_heat = 0
    tracked_temp = float(start_temp)
    target_temp = float(target_temp)
    logging.debug(f"Temp now = {tracked_temp}")
    start_time = 0
    logging.debug(f"target temperature {target_temp} in {time_left} minutes")

    while (start_time + time_to_heat) < time_left:
        # walk forwards from now until the time to start heating is reached
        start_time += STEP_RATE
        tracked_temp -= STEP_RATE / cool_rate
        time_to_heat = int((target_temp - tracked_temp) * heat_rate)
        logging.debug(f"temp after {start_time} minutes = {tracked_temp:.1f}; {time_to_heat} mins heating needed")

    if time_to_heat > 0:
        if time_to_heat > ECO_MINS: time_to_heat = ECO_MINS
        start_time = time_left - time_to_heat
        logging.debug(f"Setting timer to start in {start_time} minutes; heat for {time_to_heat} minutes")
    elif time_to_heat <= 0:
        # -ve heating time - indicates will still be > target temperature after cooling
        start_time = None
        time_to_heat= None
        logging.debug(f"temperature ({start_temp}) projected to end at {tracked_temp:.1f} - over setpoint {target_temp}")

    return tub_heating(start_time, time_to_heat)

# ---------------------------------------------------------------------------

def CalcHeatTime_algebra(start_temp, target_temp, cool_rate, heat_rate, time_left):
    logging.info("calculating start and duration (algebraic)")
    time_to_heat = 0
    tracked_temp = float(start_temp)
    target_temp = float(target_temp)
    cool_rate = 1.0 / float(cool_rate)
    heat_rate = 1.0 / float(heat_rate)
    logging.debug(f"Temp now = {tracked_temp}")
    start_time = 0
    logging.debug(f"target temperature {target_temp} in {time_left} minutes")

    # From symbolab.com/solver: heat_time = (Tend - Tstart + cool_rate * total_time) /  (heat_rate + cool_rate)
    # (See my Google sheet "Hot Hub Heating Timer")

    time_to_heat = int((target_temp - tracked_temp + cool_rate * time_left) / (heat_rate + cool_rate))

    if time_to_heat > 0:
        if time_to_heat > ECO_MINS: time_to_heat = ECO_MINS
        start_time = time_left - time_to_heat
        logging.debug(f"Setting timer to start in {start_time:.1f} minutes; heat for {time_to_heat:.1f} minutes")
        return tub_heating(int(start_time), int(time_to_heat))
    elif time_to_heat <= 0:
        # -ve heating time - indicates will still be > target temperature after cooling
        start_time = None
        time_to_heat= None
        logging.debug(f"current temperature ({start_temp}) projected to remain over target {target_temp}")
        return tub_heating(None, None)


# ---------------------------------------------------------------------------

CalcHeatTime = CalcHeatTime_algebra

# ---------------------------------------------------------------------------

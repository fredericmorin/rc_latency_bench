#!/bin/env python3
"""
Mesure end to end remote control lantency

requirements:
pip3 install saleae
"""

import time
import os
import logging

import saleae

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s"
)
current_dir = os.path.dirname(os.path.abspath(__file__))
tmp_file_fullpath = os.path.join(current_dir, "tmp_dshot_export")
output_file_fullpath = os.path.join(current_dir, "result.txt")
log.info(f'Will tmp export dshot analyzer results to "{tmp_file_fullpath}"')

# saleae config
s = saleae.Saleae()
s.set_sample_rate((4000000, 0))  # 4MHz
s.set_capture_pretrigger_buffer_size(1000000)  # minimum possible value.
s.set_capture_seconds(0.2)  # in s. Reaction typically happens within 50ms
# find dshot analyser and find it analyser index for later
dshot_analysers = list(filter(lambda a: a[0] == "Dshot", s.get_analyzers()))
assert dshot_analysers
_, dshot_analyser_index = dshot_analysers[0]

# misc config
max_wait = 5  # in s


def mesure_dshot_latency_after_trigger():
    # not sure why this is needed but couldnt get consistent reading without it
    s.reset_active_channels()
    s.close_all_tabs()

    # do capture
    s.capture_start()
    time_waited = 0
    while time_waited < max_wait and not s.is_processing_complete():
        time.sleep(0.1)  # should not take more than 1 sec
        time_waited += 0.1
    if not s.is_processing_complete():  # timeout
        log.warning(
            "Timed out while waiting for capture to complete. Missing triggers?"
        )
        s.capture_stop()
        return
    time.sleep(0.2)

    # export dshot data
    s.export_analyzer(dshot_analyser_index, tmp_file_fullpath)

    # have to sleep here because saleae takes some time to
    #  write to the file yet pretend the request was fulfilled :(
    #  I got corrupted file data before without the delay
    time.sleep(0.1)

    # parse dshot data and find reaction time
    with open(tmp_file_fullpath) as tmp_file:
        line = next(tmp_file)  # skip first line
        running_sum = 0
        read_count = 0
        for line in tmp_file:
            try:
                t, dshot_value = line.split(",")
            except ValueError:
                log.error(line)
                raise
            t = float(t)
            if t < 0:
                continue
            dshot_value = int(dshot_value.strip(" '\n"))

            # do some basic filtering on data
            if read_count < 20:
                running_sum += dshot_value
                read_count += 1
            elif read_count == 20:
                running_sum += dshot_value
                read_count += 1
                avg_value = float(running_sum) / read_count
                offset = abs(avg_value - 160)  # 160 = ~5.5% motor idle
                if offset > 10:
                    raise ValueError(f"avg_value of {avg_value} is out of norm")
                log.debug(f"Avg value used: {avg_value}")
            else:
                avg_value = float(running_sum) / read_count
                if abs(avg_value - dshot_value) > 10:
                    return t
                running_sum += dshot_value
                read_count += 1
    return None


with open(output_file_fullpath, "a") as f:
    f.write("================\n")
    for i in range(500):
        try:
            latency = mesure_dshot_latency_after_trigger()
        except s.CommandNAKedError:
            # not sure why but it randomly fails sometimes... :(
            log.warning("CommandNAKedError")
        except ValueError as exc:
            log.warning(exc)
        else:
            if latency is None:
                log.warning("Could not get latency")
            else:
                log.info(f"Mesured latency: {latency}")
                f.write(f"{latency}\n")

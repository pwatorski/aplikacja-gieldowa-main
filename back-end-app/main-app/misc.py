from datetime import timedelta, datetime
import random

def dane_z_nikad(steps:int=100, end:datetime=None, step_time:timedelta=None, beg_val:int=400, 
    stringify=True, fluctuation=100, as_tuples:bool=False):
    if not step_time:
        step_time = timedelta(hours=1)
    if not end:
        end = datetime.now()
    begin = end-step_time*steps
    data = []
    value = beg_val
    for e in range(steps):
        value = max(100, value + (random.random() * 2 - 1)**5 * fluctuation)
        if stringify:
            data.append((begin.strftime('%d-%m-%Y %H:%M:00'), value))
        else:
            data.append((begin, value))
        begin += step_time
    if as_tuples:
        return data
    return {t[0]: t[1] for t in data}
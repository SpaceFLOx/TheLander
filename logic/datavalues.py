from adwin.ADwin import ADwin
from logic.config import *


class DataValues:
    MAX_SEQUENCE_LEN = 1 * 1000 # max historic datapoints to store per selected FPAR index

    def __init__(self, adw: ADwin):
        self.adw = adw
        # contains only selected values for fpar ids def in config
        self.reset_queues()

    def reset_queues(self):
        self.queues: list[list[float]] = []# initialize []
        for _ in range(len(GLOBAL_ADWIN_FPAR.values())):
            self.queues.append([0] * DataValues.MAX_SEQUENCE_LEN)

    def add_new_vals_to_queue(self):
        fpar = self.adw.Get_FPar_All()
        if fpar[GLOBAL_ADWIN_FPAR["TIME_ADWIN"]] == 0:
            self.reset_queues()
            return
        for q_index, (fpar_name, fpar_index) in enumerate(GLOBAL_ADWIN_FPAR.items()):
            # q_index is the index in thq queue[], e.g. 0 = temperature, 1 = ...
            # fpar_index is the index in the 80 fpars, e.g. for temperature = 61
            self.queues[q_index].append(float(fpar[fpar_index]))
            self.queues[q_index] = self.queues[q_index][-DataValues.MAX_SEQUENCE_LEN:] # cuts old ones

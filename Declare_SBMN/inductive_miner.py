# Instalar a biblioteca necessária
# !pip install pm4py

# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.statistics.variants.log import get as variants_filter
from pm4py.util import xes_constants as xes
from collections import defaultdict
import statistics
from datetime import datetime, timedelta
import random

# log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/MINIMETAL/metalmec_log.xes"  # ajuste
# log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/ComputerRepair_2/log_sintetico_multimodelo.xes"  # ajuste
log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS4/ITIL/BPIC14-PreProcessed-Filtered.xes"  # ajuste
log = xes_importer.apply(log_path)

parameters = {'pm4py:param:noise_threshold': 0.15}

tree = inductive_miner.apply(log, parameters=parameters)
print("Process Tree:", tree)
net, initial_marking, final_marking = pt_converter.apply(tree)

gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.view(gviz)

# converte para bpmn
bpmn_model = pm4py.convert_to_bpmn(tree)
pm4py.view_bpmn(bpmn_model)
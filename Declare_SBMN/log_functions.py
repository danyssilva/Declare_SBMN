from collections import defaultdict
from typing import List, Dict, Tuple, Set
from Declare4Py.D4PyEventLog import D4PyEventLog


def extract_traces_from_log(event_log: D4PyEventLog) -> List[List[str]]:
    """
    Extract the traces from the event log as lists of activities.
    
    Args:
        event_log: D4Py event log
        
    Returns:
        List of traces, where each trace is a list of activity names
    """
    traces = []
    for trace in event_log.log:
        activity_sequence = []
        for event in trace:
            activity_name = event.get('concept:name', '')
            if activity_name:
                activity_sequence.append(activity_name)
        
        traces.append(activity_sequence)
    
    return traces
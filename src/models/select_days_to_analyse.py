import numpy as np
import pandas as pd
from datetime import timedelta

def appendDaysInRange(days_to_analyse, start_date, end_date, day_type):
    num_of_days = (end_date - start_date).days
    if np.isnan(num_of_days):
        return days_to_analyse
    for day in range(num_of_days + 1):
        days_to_analyse = days_to_analyse.append({"local_date": start_date + timedelta(days = day), "day_type": day_type}, ignore_index=True)
    return days_to_analyse

days_before_surgery = int(snakemake.params["days_before_surgery"])
days_in_hospital = str(snakemake.params["days_in_hospital"])
days_after_discharge = int(snakemake.params["days_after_discharge"])
participant_info = pd.read_csv(snakemake.input["participant_info"], parse_dates=["surgery_date", "discharge_date"])
days_to_analyse = pd.DataFrame(columns = ["local_date", "day_type"])

try:
    surgery_date, discharge_date = participant_info["surgery_date"].iloc[0].date(), participant_info["discharge_date"].iloc[0].date()
except:
    pass
else:
    start_date = surgery_date - timedelta(days = days_before_surgery)
    end_date = discharge_date + timedelta(days = days_after_discharge)

    # days before surgery: -1; in hospital: 0; after discharge: 1
    days_to_analyse = appendDaysInRange(days_to_analyse, start_date, surgery_date - timedelta(days = 1), -1)
    if days_in_hospital == "T":
        days_to_analyse = appendDaysInRange(days_to_analyse, surgery_date, discharge_date, 0)
    days_to_analyse = appendDaysInRange(days_to_analyse, discharge_date + timedelta(days = 1), end_date, 1)
    
days_to_analyse.to_csv(snakemake.output[0], index=False)

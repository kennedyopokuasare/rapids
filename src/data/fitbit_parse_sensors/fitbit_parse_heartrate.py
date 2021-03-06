import json
import pandas as pd
from datetime import datetime


HR_SUMMARY_COLUMNS = ("device_id",
                        "local_date",
                        "heartrate_daily_restinghr",
                        "heartrate_daily_caloriesoutofrange",
                        "heartrate_daily_caloriesfatburn",
                        "heartrate_daily_caloriescardio",
                        "heartrate_daily_caloriespeak")

HR_INTRADAY_COLUMNS = ("device_id",
                        "heartrate", "heartrate_zone",
                        "local_date_time", "local_date", "local_month", "local_day",
                        "local_day_of_week", "local_time", "local_hour", "local_minute", 
                        "local_day_segment")

def parseHeartrateZones(heartrate_data):
    # Get the range of heartrate zones: outofrange, fatburn, cardio, peak
    # refer to: https://help.fitbit.com/articles/en_US/Help_article/1565

    heartrate_fitbit_data = json.loads(heartrate_data["fitbit_data"].iloc[0])["activities-heart"][0]
    # API Version X: not sure the exact version
    if "heartRateZones" in heartrate_fitbit_data:
        heartrate_zones = heartrate_fitbit_data["heartRateZones"]
    # API VERSION Y: not sure the exact version
    elif "value" in heartrate_fitbit_data:
        heartrate_zones = heartrate_fitbit_data["value"]["heartRateZones"]
    else:
        raise ValueError("Heartrate zone are stored in an unkown format, this could mean Fitbit's heartrate API changed")
    
    heartrate_zones_range = {}
    for hrzone in heartrate_zones:
        heartrate_zones_range[hrzone["name"].lower().replace(" ", "")] = [hrzone["min"], hrzone["max"]]
    return heartrate_zones_range

def parseHeartrateSummaryData(record_summary, device_id, curr_date):
    # API Version X: not sure the exact version
    if "heartRateZones" in record_summary:
        heartrate_zones = record_summary["heartRateZones"]
        d_resting_heartrate = record_summary["value"] if "value" in record_summary else None
    # API VERSION Y: not sure the exact version
    elif "value" in record_summary:
        heartrate_zones = record_summary["value"]["heartRateZones"]
        d_resting_heartrate = record_summary["value"]["restingHeartRate"] if "restingHeartRate" in record_summary["value"] else None
    else:
        ValueError("Heartrate zone are stored in an unkown format, this could mean Fitbit's heartrate API changed")
    
    if "caloriesOut" in heartrate_zones[0]:
        d_calories_outofrange = heartrate_zones[0]["caloriesOut"]
        d_calories_fatburn = heartrate_zones[1]["caloriesOut"]
        d_calories_cardio = heartrate_zones[2]["caloriesOut"]
        d_calories_peak = heartrate_zones[3]["caloriesOut"]
    else:
        d_calories_outofrange, d_calories_fatburn, d_calories_cardio, d_calories_peak = None, None, None, None
    
    row_summary = (device_id,
                    curr_date,
                    d_resting_heartrate,
                    d_calories_outofrange,
                    d_calories_fatburn,
                    d_calories_cardio,
                    d_calories_peak)
    return row_summary




def parseHeartrateIntradayData(records_intraday, dataset, device_id, curr_date, heartrate_zones_range, HOUR2EPOCH):
    for data in dataset:
        d_time = datetime.strptime(data["time"], '%H:%M:%S').time()
        d_datetime = datetime.combine(curr_date, d_time)
        d_hr =  data["value"]

        # Get heartrate zone by range: min <= heartrate < max
        d_hrzone = None
        for hrzone, hrrange in heartrate_zones_range.items():
            if d_hr >= hrrange[0] and d_hr < hrrange[1]:
                d_hrzone = hrzone
                break

        row_intraday = (device_id,
                        d_hr, d_hrzone,
                        d_datetime, d_datetime.date(), d_datetime.month, d_datetime.day,
                        d_datetime.weekday(), d_datetime.time(), d_datetime.hour, d_datetime.minute,
                        HOUR2EPOCH[d_datetime.hour])

        records_intraday.append(row_intraday)
    return records_intraday


def parseHeartrateData(heartrate_data, HOUR2EPOCH):
    if heartrate_data.empty:
        return pd.DataFrame(columns=HR_SUMMARY_COLUMNS), pd.DataFrame(columns=HR_INTRADAY_COLUMNS)
    device_id = heartrate_data["device_id"].iloc[0]
    records_summary, records_intraday = [], []

    heartrate_zones_range = parseHeartrateZones(heartrate_data)

    # Parse JSON into individual records
    for record in heartrate_data.fitbit_data:
        record = json.loads(record)  # Parse text into JSON
        curr_date = datetime.strptime(record["activities-heart"][0]["dateTime"], "%Y-%m-%d")

        record_summary = record["activities-heart"][0]
        row_summary = parseHeartrateSummaryData(record_summary, device_id, curr_date)
        records_summary.append(row_summary)

        dataset = record["activities-heart-intraday"]["dataset"]
        records_intraday = parseHeartrateIntradayData(records_intraday, dataset, device_id, curr_date, heartrate_zones_range, HOUR2EPOCH)

    return pd.DataFrame(data=records_summary, columns=HR_SUMMARY_COLUMNS), pd.DataFrame(data=records_intraday, columns=HR_INTRADAY_COLUMNS)

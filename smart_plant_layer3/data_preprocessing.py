import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def preprocess_sensor_data(data_dict):
    df = pd.DataFrame([data_dict])
    df = df.fillna(np.nan)
    df.loc[(df["temperature"] < 0) | (df["temperature"] > 50), "temperature"] = np.nan
    df.loc[(df["humidity"] < 0) | (df["humidity"] > 100), "humidity"] = np.nan
    df.loc[(df["soilMoisture"] < 0) | (df["soilMoisture"] > 100), "soilMoisture"] = np.nan
    df.loc[(df["lightLevel"] < 0) | (df["lightLevel"] > 1000), "lightLevel"] = np.nan
    df = df.apply(lambda x: x.fillna(x.mean()))
    scaler = MinMaxScaler()
    normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    return normalized.iloc[0].to_dict()

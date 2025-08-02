import pandas as pd

df = pd.read_csv("iata-icao.csv")

def icaotolonlat(icao:str):
    row = df[df["icao"] == icao.upper()]
    if not row.empty:
        lat = row["latitude"].iloc[0]
        lon = row["longitude"].iloc[0]
        return {"lat": float(lat), "lon": float(lon)}
    return {"lat": None, "lon": None}

print(icaotolonlat("ellx"))
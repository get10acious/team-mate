import os
import pandas as pd
from weaviate import Client
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
client = Client(WEAVIATE_URL)
# auth_client_secret=auth) Pass auth if logging to cloud instance


df = pd.read_csv("/Users/adakibet/cosmology/platform/refined.csv")
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
print(df.shape)
df.dropna(subset=["date"], inplace=True)
print(df.shape)
for index, row in df.iterrows():
    nan_cols = row.index[row.isnull()].tolist()
    for col in nan_cols:
        row[col] = ""

    client.data_object.create(
        {
            "title": row["title"],
            "company": row["company"],
            "company_link": row["company_link"],
            "location": row["location"],
            "date_posted": row["date"],
            "apply_link": row["apply_link"],
            "post_link": row["post_link"],
            "seniority_level": row["seniority_level"],
            "employment_type": row["employmnet_type"],
            "description": row["description"],
        },
        "JobPosting",
    )

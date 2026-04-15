import pandas as pd
import streamlit as st

@st.cache_data
def load_data(df):
    df = df.fillna("")
    df["search_blob"] = (
        df["Brand"] + " " + df["Vehicle"] + " " +
        df["OE Part Number"] + " " +
        df["Manufacturing Part Number"] + " " +
        df["Description"]
    ).str.lower()
    return df

def search(df, query):
    query = query.lower()
    return df[df["search_blob"].str.contains(query)].head(20)

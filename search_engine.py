import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

def search(query):
    df = load_data()
    query = query.lower()

    return df[df.apply(lambda row: query in str(row).lower(), axis=1)]

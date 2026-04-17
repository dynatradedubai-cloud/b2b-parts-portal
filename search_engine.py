import pandas as pd
import streamlit as st


# =============================
# PREPARE DATA (FAST)
# =============================
@st.cache_data
def prepare_search(df):

    df = df.fillna("")

    # Combine searchable fields
    df["search_blob"] = (
        df["Brand"].astype(str) + " " +
        df["Vehicle"].astype(str) + " " +
        df["OE Part Number"].astype(str) + " " +
        df["Manufacturing Part Number"].astype(str) + " " +
        df["Description"].astype(str)
    ).str.lower()

    return df


# =============================
# FAST SEARCH
# =============================
def search_parts(df, query):

    if not query:
        return df.head(20)

    query_words = query.lower().split()

    mask = pd.Series(True, index=df.index)

    for word in query_words:
        mask &= df["search_blob"].str.contains(word, regex=False)

    return df[mask].head(20)


# =============================
# SUGGESTIONS
# =============================
def get_suggestions(df, query):

    if not query:
        return []

    query = query.lower()

    matches = df[
        df["search_blob"].str.contains(query, regex=False)
    ]

    return matches["Description"].head(5).tolist()

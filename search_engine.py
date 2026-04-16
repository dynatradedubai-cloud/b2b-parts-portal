import streamlit as st
import pandas as pd
import re

# =============================
# PREPARE DATA (CACHE)
# =============================

@st.cache_data
def prepare_search(df):
    df = df.fillna("")

    # Create combined search column
    df["search_blob"] = (
        df["Brand"].astype(str) + " " +
        df["Vehicle"].astype(str) + " " +
        df["OE Part Number"].astype(str) + " " +
        df["Manufacturing Part Number"].astype(str) + " " +
        df["Description"].astype(str)
    ).str.lower()

    return df

# =============================
# TOKENIZE QUERY
# =============================

def tokenize(query):
    return re.split(r"\s+", query.lower().strip())

# =============================
# MULTI-KEYWORD SEARCH
# =============================

def search_parts(df, query, limit=20):
    if not query:
        return pd.DataFrame()

    tokens = tokenize(query)

    mask = pd.Series(True, index=df.index)

    for token in tokens:
        mask &= df["search_blob"].str.contains(token, na=False)

    results = df[mask]

    return results.head(limit)

# =============================
# AUTO SUGGESTIONS
# =============================

def get_suggestions(df, query, limit=5):
    if not query:
        return []

    query = query.lower()

    matches = df[df["search_blob"].str.contains(query, na=False)]

    suggestions = matches["Description"].dropna().unique().tolist()

    return suggestions[:limit]

import streamlit as st
import pandas as pd
import re
from difflib import SequenceMatcher

# =============================
# PREPARE DATA (FAST SEARCH)
# =============================

@st.cache_data
def prepare_search(df):
    df = df.fillna("")

    df["search_blob"] = (
        df["Brand"].astype(str) + " " +
        df["Vehicle"].astype(str) + " " +
        df["OE Part Number"].astype(str) + " " +
        df["Manufacturing Part Number"].astype(str) + " " +
        df["Description"].astype(str)
    ).str.lower()

    return df


# =============================
# TOKENIZER
# =============================

def tokenize(query):
    return re.split(r"\s+", query.lower().strip())


# =============================
# MULTI-KEYWORD SEARCH
# =============================

def multi_keyword_search(df, query, limit=20):
    tokens = tokenize(query)

    mask = pd.Series(True, index=df.index)

    for token in tokens:
        mask = mask & df["search_blob"].str.contains(token, na=False)

    return df[mask].head(limit)


# =============================
# FUZZY SEARCH (FALLBACK)
# =============================

def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()


def fuzzy_search(df, query, threshold=0.6, limit=20):
    query = query.lower()

    scores = df["search_blob"].apply(lambda x: fuzzy_match(query, x))

    return df[scores > threshold].head(limit)


# =============================
# MAIN SEARCH FUNCTION
# =============================

def search_parts(df, query):
    if not query:
        return pd.DataFrame()

    results = multi_keyword_search(df, query)

    if results.empty:
        results = fuzzy_search(df, query)

    return results


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

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
from difflib import SequenceMatcher

def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()

def fuzzy_search(df, query, threshold=0.6):
    query = query.lower()

    scores = df["search_blob"].apply(lambda x: fuzzy_match(query, x))
    return df[scores > threshold].head(20)

def search_parts(df, query):
    results = multi_keyword_search(df, query)

    if results.empty:
        results = fuzzy_search(df, query)

    return results

lang = st.selectbox("🌍", ["en", "ar"], index=0)
st.session_state.lang = lang

def render_notifications():
    st.markdown("### 🔔 Notifications")

    import os
    files = os.listdir("data")

    for f in files:
        if "campaign" in f:
            with open(f"data/{f}", "rb") as file:
                st.download_button(f"📄 {f}", file)

import streamlit as st

is_mobile = st.session_state.get("mobile", False)

for i, row in results.iterrows():

    if is_mobile:
        with st.container():
            st.markdown(f"""
            **{row['Description']}**  
            Brand: {row['Brand']}  
            Price: {row['Price']} AED  
            """)
    else:
        # existing desktop table layout
        pass

from security import log_event

if results.empty:
    log_event("user", f"NOT FOUND: {query}")

from database import load_encrypted_file
users = load_encrypted_file("users")

if users is not None:
    user_row = users[users["Username"] == user]

    if user_row.empty:
        st.error("User not found")
        return

    if user_row.iloc[0].get("Blocked", False):
        st.error("User is blocked")
        return

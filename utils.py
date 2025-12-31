# utils.py
import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection
import config as cfg  # config.py 임포트

def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=cfg.SHEET_URL, ttl=0)
        if df.empty or len(df.columns) < len(cfg.COLUMNS): 
            return pd.DataFrame(columns=cfg.COLUMNS)
        
        missing_cols = set(cfg.COLUMNS) - set(df.columns)
        for c in missing_cols: df[c] = ""
        
        df = df[cfg.COLUMNS].fillna("")
        df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
        df = df.astype({c: str for c in df.columns if c != '평점'})
        return df
    except Exception as e:
        return pd.DataFrame(columns=cfg.COLUMNS)

def save_data(df):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(spreadsheet=cfg.SHEET_URL, data=df)
    except Exception as e:
        st.error(f"저장 실패: {e}")

def extract_url(text):
    if not isinstance(text, str): return ""
    match = re.search(r'(https?://\S+)', text)
    if match: return match.group(1)
    return text

def get_unique_values(df, column, defaults=[]):
    if column in df.columns:
        existing = set()
        for item in df[column].unique():
            if item:
                existing.update([x.strip() for x in str(item).split(',')])
        return sorted(list(existing.union(defaults)))
    return sorted(defaults)

def aggregate_reviews(df):
    if df.empty: return df
    grouped = df.groupby('식당명').agg({
        '카테고리': 'first', '메뉴키워드': 'first', '분위기키워드': 'first',
        '가격대': 'first', '거리': 'first', '최대수용인원': 'first',
        '전화번호': 'first', '네이버지도URL': 'first', '휴무일': 'first',
        '평점': 'mean', '한줄평': lambda x: list(x), '작성자': lambda x: list(x)
    }).reset_index()
    grouped['평점'] = grouped['평점'].round(1)
    return grouped
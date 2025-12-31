# utils.py
import streamlit as st
import pandas as pd
import re
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import config as cfg  # config.py 임포트

def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # worksheet 인자 추가 (기본값: 첫번째 시트)
        df = conn.read(spreadsheet=cfg.SHEET_URL, worksheet=cfg.WORKSHEET_NAME_LIST, ttl=0)
        
        if df.empty or len(df.columns) < len(cfg.COLUMNS): 
            return pd.DataFrame(columns=cfg.COLUMNS)
        
        missing_cols = set(cfg.COLUMNS) - set(df.columns)
        for c in missing_cols: df[c] = ""
        
        df = df[cfg.COLUMNS].fillna("")
        df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
        df = df.astype({c: str for c in df.columns if c != '평점'})
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
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

# [신규] 식사 기록 로드
def load_history():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=cfg.SHEET_URL, worksheet=cfg.WORKSHEET_NAME_HISTORY, ttl=0)
        
        if df.empty: return pd.DataFrame(columns=cfg.COLUMNS_HISTORY)
        
        # 필수 컬럼 보장
        missing_cols = set(cfg.COLUMNS_HISTORY) - set(df.columns)
        for c in missing_cols: df[c] = ""
        return df[cfg.COLUMNS_HISTORY].fillna("")
    except Exception:
        st.error(f"히스토리 로드 실패: {e}") 
        return pd.DataFrame(columns=cfg.COLUMNS_HISTORY)
# 2. 맛집 리스트 저장 (기존 함수 수정)
def save_data(df):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(spreadsheet=cfg.SHEET_URL, worksheet=cfg.WORKSHEET_NAME_LIST, data=df)
    except Exception as e:
        st.error(f"저장 실패: {e}")

def add_history_row(new_row_dict):
    # 1. 어디에 쓸 건지 주소부터 출력 (터미널 확인용)
    print("\n---------------------------------------------------")
    print(f"🔥 [DEBUG] 쓰기 시도 중...")
    print(f"🎯 타겟 시트 URL: {cfg.SHEET_URL}")
    print(f"🎯 타겟 탭 이름: {cfg.WORKSHEET_NAME_HISTORY}")

    # 2. 기존 데이터 로드
    df = load_history()
    print(f"📂 기존 데이터 개수: {len(df)}개")

    # 3. 데이터 합치기
    new_df = pd.DataFrame([new_row_dict])
    updated_df = pd.concat([df, new_df], ignore_index=True)
    
    # [중요] 데이터 타입 강제 변환 (숫자/날짜 깨짐 방지)
    updated_df = updated_df.astype(str)
    
    print(f"📝 저장할 데이터 개수: {len(updated_df)}개")
    print(f"💾 데이터 미리보기:\n{updated_df.tail(1)}")

    # 4. 강제 쓰기 및 캐시 삭제
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 시트 업데이트 수행
        conn.update(
            spreadsheet=cfg.SHEET_URL, 
            worksheet=cfg.WORKSHEET_NAME_HISTORY, 
            data=updated_df
        )
        
        # 캐시 날리기 (매우 중요)
        st.cache_data.clear()
        print("✅ [SUCCESS] 업데이트 명령 실행 완료 (에러 없음)")
        print("---------------------------------------------------\n")
        return True

    except Exception as e:
        print(f"❌ [FAIL] 저장 중 치명적 에러 발생: {e}")
        st.error(f"저장 시스템 에러: {e}")
        return False
    

import streamlit as st
import pandas as pd
import os
import random

# 1. 데이터 파일 관리 (CSV를 간이 DB로 사용)
CSV_FILE = 'lunch_data.csv'

def load_data():
    if not os.path.exists(CSV_FILE):
        # 초기 더미 데이터 생성
        df = pd.DataFrame(columns=['식당명', '카테고리', '가격대', '거리(분)', '특징', '네이버지도URL'])
        df.to_csv(CSV_FILE, index=False)
        return df
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# 2. 메인 앱 설정
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋")
st.title("🍱 우리 팀 점심 추천 에이전트 (PoC)")

# 데이터 로드
df = load_data()

# 3. 사이드바: 데이터 등록 (관리 기능)
with st.sidebar:
    st.header("📝 맛집 데이터 등록")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("식당 이름")
        category = st.selectbox("카테고리", ["한식", "중식", "일식", "양식", "분식/기타"])
        price = st.selectbox("가격대", ["1만원 이하", "1~2만원", "2만원 이상"])
        distance = st.slider("회사에서의 거리 (도보 분)", 1, 30, 5)
        tags = st.text_input("특징/태그 (쉼표로 구분)", placeholder="매운, 조용한, 해장")
        
        submitted = st.form_submit_button("등록하기")
        if submitted and name:
            # 네이버 지도 검색 URL 자동 생성
            naver_url = f"https://map.naver.com/v5/search/{name}"
            
            new_data = pd.DataFrame({
                '식당명': [name],
                '카테고리': [category],
                '가격대': [price],
                '거리(분)': [distance],
                '특징': [tags],
                '네이버지도URL': [naver_url]
            })
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success(f"'{name}' 등록 완료!")
            st.rerun() # 데이터 갱신을 위해 리로드

# 4. 메인 화면: 에이전트 인터페이스 (검색 및 추천)
tab1, tab2 = st.tabs(["🔍 추천 받기 (Agent)", "📊 전체 리스트 관리"])

with tab1:
    st.subheader("오늘의 점심 조건을 알려주세요!")
    
    # 자연어 이해 대신 직관적인 필터링 UI (PoC 단계)
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.multiselect("먹고 싶은 종류 (비워두면 전체)", df['카테고리'].unique())
    with col2:
        max_dist = st.slider("최대 이동 거리 (분)", 0, 30, 15)
    
    keyword = st.text_input("특정 키워드 검색 (예: 해장, 조용한)")

    if st.button("🚀 점심 장소 추천해 줘!", type="primary"):
        # 필터링 로직 (Rule-based Agent)
        results = df.copy()
        
        if filter_category:
            results = results[results['카테고리'].isin(filter_category)]
        
        results = results[results['거리(분)'] <= max_dist]
        
        if keyword:
            results = results[results['특징'].str.contains(keyword, na=False) | results['식당명'].str.contains(keyword, na=False)]
        
        # 결과 출력
        if not results.empty:
            # 추천 알고리즘: 랜덤으로 1~3개 추천 (Top-K)
            recommendations = results.sample(n=min(3, len(results)))
            
            st.success(f"총 {len(results)}개의 후보 중 {len(recommendations)}곳을 추천합니다!")
            
            for _, row in recommendations.iterrows():
                with st.expander(f"🍽️ **{row['식당명']}** ({row['카테고리']})", expanded=True):
                    st.write(f"- 💰 가격: {row['가격대']}")
                    st.write(f"- 🚶 거리: 도보 {row['거리(분)']}분")
                    st.write(f"- 🏷️ 특징: {row['특징']}")
                    st.markdown(f"[📍 네이버 지도로 보기]({row['네이버지도URL']})")
        else:
            st.error("조건에 맞는 식당이 없습니다. 조건을 조금 넓혀보세요! 😭")

with tab2:
    st.dataframe(df)
    st.caption("※ 데이터는 'lunch_data.csv' 파일에 자동 저장됩니다.")
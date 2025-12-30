import streamlit as st
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# 1. 설정 및 기본 데이터 정의
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋", layout="wide")

# [중요] 구글 시트 주소 (공유 권한을 '제한됨'으로 하고 봇 이메일만 초대하면 URL 공개돼도 안전함)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1_WvbJhPTbxU5c4hMwv9ak-G78jajBD-ZIrzvqxvgDTI/edit?usp=sharing"

COLUMNS = [
    '식당명', '카테고리', '메뉴키워드', '분위기키워드', 
    '가격대', '거리', '최대수용인원', 
    '전화번호', '네이버지도URL', 
    '예약필수여부', '웨이팅정도', '휴무일', 
    '추천인', '평점', '한줄평'
]

COMMON_MENUS = ["김치찌개", "된장찌개", "제육볶음", "돈가스", "파스타", "짜장면", "짬뽕", "삼겹살", "국밥", "샌드위치", "샐러드", "회/초밥"]
COMMON_VIBES = ["조용한", "깔끔한", "시끌벅적한", "노포감성", "빨리나옴", "혼밥가능", "회식추천", "손님접대", "가성비", "비오는날", "해장"]
DISTANCE_MAP = {"도보 5분 이내": 1, "도보 10분 이내": 2, "차량 이동": 3}

# -----------------------------------------------------------------------------
# 2. 헬퍼 함수
# -----------------------------------------------------------------------------
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        if df.empty or len(df.columns) < len(COLUMNS):
            return pd.DataFrame(columns=COLUMNS)
        
        missing_cols = set(COLUMNS) - set(df.columns)
        for c in missing_cols:
            df[c] = ""
            
        df = df[COLUMNS]
        df = df.fillna("")
        # 평점 계산을 위해 숫자형 변환 시도 (에러나면 0.0)
        df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
        df = df.astype({c: str for c in df.columns if c != '평점'}) # 평점 빼고 다 문자열
        
        return df
    except Exception as e:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(spreadsheet=SHEET_URL, data=df)
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

# -----------------------------------------------------------------------------
# 3. 데이터 통합 로직 (Aggregation)
# -----------------------------------------------------------------------------
def aggregate_reviews(df):
    """같은 식당 이름끼리 묶어서 평점 평균과 리뷰를 합칩니다."""
    if df.empty: return df
    
    # 식당명 기준으로 그룹화
    grouped = df.groupby('식당명').agg({
        '카테고리': 'first', # 첫 번째 값 유지
        '메뉴키워드': 'first',
        '분위기키워드': 'first',
        '가격대': 'first',
        '거리': 'first',
        '최대수용인원': 'first',
        '전화번호': 'first',
        '네이버지도URL': 'first',
        '휴무일': 'first',
        '평점': 'mean', # 평점은 평균!
        '한줄평': lambda x: list(x), # 리뷰는 리스트로 묶기
        '추천인': lambda x: list(x)  # 추천인도 리스트로
    }).reset_index()
    
    # 평점 반올림 (0.5 단위처럼 보이게 소수점 1자리)
    grouped['평점'] = grouped['평점'].round(1)
    return grouped

# -----------------------------------------------------------------------------
# 4. 팝업: 맛집 등록
# -----------------------------------------------------------------------------
@st.dialog("맛집 등록하기 📝")
def popup_register():
    st.caption("필요한 정보만 빠르게 터치해서 등록하세요!")
    with st.form("reg_form", clear_on_submit=True):
        st.markdown("##### 🏪 식당 기본 정보")
        col1, col2 = st.columns(2)
        name = col1.text_input("식당 이름 (필수)")
        category = col2.selectbox("카테고리", ["한식", "중식", "일식", "양식", "아시안", "분식/기타"])
        
        st.markdown("##### 🏷️ 키워드 선택")
        menu_tags = st.multiselect("🥘 메뉴 키워드", COMMON_MENUS)
        vibe_tags = st.multiselect("✨ 분위기 키워드", COMMON_VIBES)
        
        st.markdown("##### ⚙️ 이용 정보")
        c1, c2 = st.columns(2)
        price = c1.selectbox("가격대", ["1만원 미만", "1~1.5만원", "1.5~2만원", "2만원 이상"])
        distance = c2.select_slider("회사 거리", options=["도보 5분 이내", "도보 10분 이내", "차량 이동"])
        st.write("👥 **최대 수용 인원**")
        capacity = st.radio("인원 선택", ["2명", "4명", "6명", "8명", "단체가능"], horizontal=True)

        st.markdown("##### 📞 상세 정보")
        r1, r2, r3 = st.columns(3)
        phone = r1.text_input("전화번호")
        reservation = r2.selectbox("예약 정보", ["예약 불필요", "예약 가능", "예약 필수", "현장 대기"])
        waiting = r3.selectbox("평소 웨이팅", ["없음", "보통", "심함"])
        off_days = st.multiselect("휴무일", ["월", "화", "수", "목", "금", "토", "일"])
        raw_link = st.text_area("네이버 지도 링크", height=70, placeholder="공유 텍스트 붙여넣기")

        st.markdown("##### ⭐ 나의 평가")
        # [수정됨] 0.5점 단위 슬라이더
        rating = st.slider("별점", 1.0, 5.0, 3.0, 0.5)
        comment = st.text_input("한줄평")
        recommender = st.text_input("추천인")

        if st.form_submit_button("등록 완료", type="primary", use_container_width=True):
            if not name:
                st.error("식당 이름은 필수입니다!")
            else:
                final_link = extract_url(raw_link)
                new_row = {
                    '식당명': name, '카테고리': category, 
                    '메뉴키워드': ",".join(menu_tags), '분위기키워드': ",".join(vibe_tags),
                    '가격대': price, '거리': distance, '최대수용인원': capacity, 
                    '전화번호': phone, '네이버지도URL': final_link, 
                    '예약필수여부': reservation, '웨이팅정도': waiting, '휴무일': ",".join(off_days), 
                    '추천인': recommender, '평점': rating, '한줄평': comment
                }
                df = load_data()
                # concat 시 평점 타입 문제 방지를 위해 DataFrame 생성 후 병합
                new_df = pd.DataFrame([new_row])
                updated_df = pd.concat([df, new_df], ignore_index=True)
                save_data(updated_df)
                st.toast(f"'{name}' 등록 성공!", icon="✅")
                st.rerun()

# -----------------------------------------------------------------------------
# 5. 메인 화면
# -----------------------------------------------------------------------------
menu = st.sidebar.radio("메뉴", ["🔍 점심 추천 (Agent)", "📊 데이터 관리"])

if menu == "🔍 점심 추천 (Agent)":
    st.title("🤖 오늘 점심 뭐 먹지?")
    raw_df = load_data()
    
    if raw_df.empty:
        st.info("데이터가 없습니다.")
    else:
        # [핵심] 보여줄 때는 데이터를 통합(Aggregation)해서 보여줌
        df = aggregate_reviews(raw_df)
        
        with st.container(border=True):
            st.subheader("🎯 조건 선택")
            c1, c2, c3 = st.columns(3)
            cat_opts = ["전체"] + get_unique_values(df, '카테고리')
            s_cat = c1.selectbox("카테고리", cat_opts)
            s_dist = c2.select_slider("최대 이동 거리", options=["도보 5분 이내", "도보 10분 이내", "차량 이동(전체)"], value="도보 10분 이내")
            s_people = c3.selectbox("인원", ["상관없음", "4명 이하", "5~8명", "단체"])

            st.write("🔑 **키워드 검색**")
            all_menu = get_unique_values(df, '메뉴키워드', COMMON_MENUS)
            all_vibe = get_unique_values(df, '분위기키워드', COMMON_VIBES)
            k1, k2 = st.columns(2)
            s_menu = k1.multiselect("메뉴", all_menu)
            s_vibe = k2.multiselect("분위기", all_vibe)
            
            if st.button("추천 받기 🚀", type="primary", use_container_width=True):
                result = df.copy()
                if s_cat != "전체": result = result[result['카테고리'] == s_cat]
                u_lvl = DISTANCE_MAP.get(s_dist, 3)
                result['d_lvl'] = result['거리'].map(DISTANCE_MAP).fillna(3)
                if "차량" not in s_dist: result = result[result['d_lvl'] <= u_lvl]
                if s_menu: result = result[result['메뉴키워드'].apply(lambda x: any(k in str(x) for k in s_menu))]
                if s_vibe: result = result[result['분위기키워드'].apply(lambda x: any(k in str(x) for k in s_vibe))]

                if result.empty: st.warning("조건에 맞는 곳이 없어요.")
                else:
                    st.success(f"{len(result)}곳 발견!")
                    # 결과 카드 출력
                    for i, r in result.iterrows():
                        # 평균 별점 표시
                        avg_score = r['평점']
                        review_count = len(r['한줄평'])
                        
                        with st.expander(f"🍽️ **{r['식당명']}** ({r['카테고리']}) ⭐{avg_score} ({review_count}명 평가)"):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.write(f"**🥘 메뉴:** {r['메뉴키워드']} | **✨ 특징:** {r['분위기키워드']}")
                                st.caption(f"📍 {r['거리']} | 💰 {r['가격대']} | 📞 {r['전화번호']}")
                                
                                # [핵심] 여러 명의 리뷰 보여주기
                                st.divider()
                                st.markdown("**🗣️ 팀원들의 한줄평**")
                                for comment, person in zip(r['한줄평'], r['추천인']):
                                    if comment: # 내용이 있을 때만
                                        st.write(f"- {comment} (by {person})")
                                    
                            with c2:
                                if r['네이버지도URL']: st.link_button("지도", r['네이버지도URL'])

elif menu == "📊 데이터 관리":
    st.title("📝 맛집 데이터 관리")
    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("➕ 맛집 등록", type="primary"): popup_register()
    
    # 관리 페이지에서는 '날것의 데이터(Raw Data)'를 그대로 보여줘야 수정이 가능함
    df = load_data()
    st.markdown("⚠️ **주의:** 여기서는 개별 등록 건이 모두 보입니다. 수정 후 **[변경사항 저장]**을 눌러주세요.")
    
    # [수정됨] warning 해결을 위해 use_container_width 제거하고 width 설정 권장 (보통 기본값이면 충분)
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", 
        column_config={
            "네이버지도URL": st.column_config.LinkColumn(),
            "평점": st.column_config.NumberColumn(min_value=1, max_value=5, step=0.5)
        }
    )
    if st.button("💾 변경사항 저장하기", type="primary"):
        save_data(edited_df)
        st.success("저장 완료!")
        st.rerun()
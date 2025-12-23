import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -----------------------------------------------------------------------------
# 1. 설정 및 데이터 컬럼 정의
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋", layout="wide")

# 관리할 데이터 항목 (구글 시트 헤더와 동일하게 구성)
COLUMNS = [
    # (1) 기본 정보
    '식당명', '카테고리', '가격대', '거리(분)', '최대수용인원', '네이버지도URL',
    # (2) 운영 정보
    '예약필수여부', '웨이팅정도', '대표메뉴', '휴무일',
    # (3) 평가 정보
    '추천인', '평점(5점만점)', '상황_날씨', '한줄평'
]

CSV_FILE = 'lunch_data_v2.csv'

# -----------------------------------------------------------------------------
# 2. 데이터 연결 계층 (Google Sheets + CSV Fallback)
# -----------------------------------------------------------------------------
def load_data():
    """구글 시트 연결을 시도하고, 실패하면 로컬 CSV를 사용합니다."""
    try:
        # Streamlit Cloud 배포 시 secrets에 gsheets 정보가 있으면 시트 연동
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="맛집리스트", ttl="10m") # 10분 캐시
        # 필수 컬럼이 없으면 생성
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    except Exception:
        # 로컬 모드 또는 설정 전
        if not os.path.exists(CSV_FILE):
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(CSV_FILE, index=False)
            return df
        return pd.read_csv(CSV_FILE)

def save_new_row(new_row_data):
    """새로운 데이터를 저장합니다."""
    df = load_data()
    new_df = pd.DataFrame([new_row_data])
    updated_df = pd.concat([df, new_df], ignore_index=True)
    
    try:
        # 구글 시트 저장 시도
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(worksheet="맛집리스트", data=updated_df)
        st.toast("구글 시트에 저장되었습니다!", icon="☁️")
    except:
        # 로컬 CSV 저장
        import os
        updated_df.to_csv(CSV_FILE, index=False)
        st.toast("로컬 CSV에 저장되었습니다. (구글 시트 미연동)", icon="💾")

# -----------------------------------------------------------------------------
# 3. UI 컴포넌트: 등록 팝업 (Dialog)
# -----------------------------------------------------------------------------
@st.dialog("맛집 등록하기 📝")
def popup_register():
    st.caption("팀원들을 위해 알고 있는 맛집 정보를 입력해주세요!")
    
    with st.form("reg_form", clear_on_submit=True):
        # 섹션 1: 기본 정보
        st.markdown("##### 1. 기본 정보")
        col1, col2 = st.columns(2)
        name = col1.text_input("식당 이름 (필수)")
        category = col2.selectbox("음식 카테고리", ["한식", "중식", "일식", "양식", "아시안", "분식/기타"])
        
        col3, col4 = st.columns(2)
        price = col3.selectbox("1인당 평균 가격", ["1만원 미만", "1~1.5만원", "1.5~2만원", "2만원 이상"])
        distance = col4.number_input("회사 거리 (도보 분)", min_value=0, max_value=60, value=5)
        
        # 섹션 2: 운영 정보
        st.markdown("##### 2. 운영 정보")
        menu = st.text_input("대표 메뉴 (예: 김치찌개, 돈가스)")
        col5, col6, col7 = st.columns(3)
        capacity = col5.number_input("최대 수용 인원", min_value=1, value=4)
        reservation = col6.selectbox("예약 여부", ["예약 불필요", "예약 가능", "예약 필수", "현장 대기만 가능"])
        waiting = col7.selectbox("평소 웨이팅", ["없음", "보통(10분)", "심함(20분↑)"])
        off_day = st.multiselect("휴무일 (방문 불가)", ["월", "화", "수", "목", "금", "토", "일"])
        
        # 섹션 3: 평가 및 링크
        st.markdown("##### 3. 평가 및 링크")
        tags = st.multiselect("추천 상황/태그", ["비오는날", "해장", "조용함", "빨리나옴", "회식가능", "손님접대"])
        rating = st.slider("종합 점수", 1, 5, 3)
        comment = st.text_area("한줄평 및 꿀팁", placeholder="예: 11시 반에 가야 줄 안서요.")
        recommender = st.text_input("추천인 (본인 이름)")
        naver_link = st.text_input("네이버 지도 링크", placeholder="https://naver.me/xxxxx (복사 붙여넣기)")

        submitted = st.form_submit_button("등록 완료")
        
        if submitted:
            if not name:
                st.error("식당 이름은 필수입니다!")
            else:
                row = {
                    '식당명': name, '카테고리': category, '가격대': price, '거리(분)': distance,
                    '최대수용인원': capacity, '네이버지도URL': naver_link,
                    '예약필수여부': reservation, '웨이팅정도': waiting, '대표메뉴': menu,
                    '휴무일': ",".join(off_day) if off_day else "",
                    '추천인': recommender, '평점(5점만점)': rating,
                    '상황_날씨': ",".join(tags) if tags else "",
                    '한줄평': comment
                }
                save_new_row(row)
                st.rerun()

# -----------------------------------------------------------------------------
# 4. 메인 화면 구성
# -----------------------------------------------------------------------------
menu = st.sidebar.radio("메뉴 선택", ["🔍 점심 추천 (Agent)", "📊 데이터 관리 (List)"])

# [페이지 1] 점심 추천 에이전트
if menu == "🔍 점심 추천 (Agent)":
    st.title("🤖 오늘 점심 뭐 먹지?")
    st.markdown("상황에 맞는 최적의 식당을 찾아드립니다.")

    # 필터링 섹션
    with st.container(border=True):
        st.subheader("조건 설정")
        col1, col2, col3 = st.columns(3)
        with col1:
            f_cat = st.multiselect("카테고리", ["한식", "중식", "일식", "양식", "아시안", "분식/기타"])
        with col2:
            f_people = st.number_input("오늘 인원 (명)", min_value=1, value=4)
        with col3:
            f_weather = st.selectbox("오늘 날씨/상황", ["상관없음", "비오는날", "해장", "조용함", "빨리나옴"])
        
        f_max_dist = st.slider("최대 이동 거리 (분)", 5, 30, 10)
    
    if st.button("🚀 추천 시작", type="primary", use_container_width=True):
        df = load_data()
        
        # 1. 인원 필터
        result = df[pd.to_numeric(df['최대수용인원'], errors='coerce').fillna(99) >= f_people]
        # 2. 거리 필터
        result = result[pd.to_numeric(result['거리(분)'], errors='coerce').fillna(0) <= f_max_dist]
        # 3. 카테고리 필터
        if f_cat:
            result = result[result['카테고리'].isin(f_cat)]
        # 4. 상황/태그 필터 (부분 일치 검색)
        if f_weather != "상관없음":
            result = result[result['상황_날씨'].str.contains(f_weather, na=False)]
            
        if result.empty:
            st.warning("조건에 맞는 식당이 없습니다 😭 조건을 조금 완화해 보세요.")
        else:
            # 추천 로직: 평점순 정렬 후 상위 3개 중 랜덤 or 그냥 랜덤
            st.balloons()
            st.success(f"총 {len(result)}개의 맛집을 찾았습니다!")
            
            for i, row in result.iterrows():
                with st.expander(f"🏅 {row['식당명']} ({row['카테고리']}) - ⭐{row['평점(5점만점)']}", expanded=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**메뉴:** {row['대표메뉴']} | **가격:** {row['가격대']}")
                        st.write(f"**특징:** {row['상황_날씨']}")
                        st.info(f"💡 {row['한줄평']}")
                    with c2:
                        if row['네이버지도URL']:
                            st.link_button("네이버 지도 🔗", row['네이버지도URL'])
                        else:
                            st.caption("지도 링크 없음")

# [페이지 2] 데이터 관리 및 등록
elif menu == "📊 데이터 관리 (List)":
    st.title("맛집 리스트 관리")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("등록된 모든 맛집 데이터를 확인하고 수정합니다.")
    with col2:
        if st.button("➕ 맛집 등록", type="primary", use_container_width=True):
            popup_register() # 팝업 호출
            
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)
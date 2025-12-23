import streamlit as st
import pandas as pd
import re # 링크 추출용
import os
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# 1. 설정 및 기본 데이터
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋", layout="wide")

COLUMNS = [
    '식당명', '카테고리', '가격대', '거리', '최대수용인원', 
    '네이버지도URL', '예약필수여부', '웨이팅정도', '대표메뉴', 
    '휴무일', '추천인', '평점', '태그', '한줄평'
]

# 파일명을 고정하여 데이터 유실 방지
CSV_FILE = 'lunch_db.csv' 

# 기본 태그 목록
DEFAULT_TAGS = ["비오는날", "해장", "조용함", "빨리나옴", "회식가능", "손님접대", "가성비", "혼밥가능"]

# 거리 정렬 맵핑
DISTANCE_MAP = {"도보 5분 이내": 1, "도보 10분 이내": 2, "차량 이동": 3}

# -----------------------------------------------------------------------------
# 2. 헬퍼 함수 (데이터 로드/저장 - 인코딩 수정됨)
# -----------------------------------------------------------------------------
def load_data():
    """구글 시트에서 데이터를 불러옵니다."""
    # 연결 객체 생성 (secrets.toml 정보를 자동으로 읽음)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    try:
        # 데이터 읽기 (ttl=0은 캐시 없이 항상 최신 데이터 로드)
        df = conn.read(ttl=0)
        
        # 만약 빈 시트라면 컬럼 생성
        if df.empty or len(df.columns) < len(COLUMNS):
            df = pd.DataFrame(columns=COLUMNS)
            
        # 필요한 컬럼만 선택하고 결측치 처리
        # (시트에는 잡다한 데이터가 있을 수 있으니 정리)
        missing_cols = set(COLUMNS) - set(df.columns)
        for c in missing_cols:
            df[c] = ""
        df = df[COLUMNS]
        
        return df
    except Exception as e:
        st.error(f"구글 시트 연결 오류: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    """구글 시트에 데이터를 저장합니다."""
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # 데이터프레임 전체를 시트에 덮어쓰기
        conn.update(data=df)
        # st.toast("구글 시트 저장 완료!", icon="☁️") # 너무 자주 뜨면 주석 처리
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")

def extract_url(text):
    """링크 텍스트에서 URL만 추출"""
    if not isinstance(text, str): return ""
    match = re.search(r'(https?://\S+)', text)
    if match:
        return match.group(1)
    return text

def get_all_tags(df):
    """저장된 태그와 기본 태그 합치기"""
    existing_tags = set()
    if '태그' in df.columns:
        for tag_str in df['태그'].dropna():
            if tag_str:
                existing_tags.update([t.strip() for t in tag_str.split(',')])
    return sorted(list(existing_tags.union(DEFAULT_TAGS)))

# -----------------------------------------------------------------------------
# 3. 팝업: 맛집 등록 (Dialog)
# -----------------------------------------------------------------------------
@st.dialog("맛집 등록하기 📝")
def popup_register():
    df = load_data()
    all_tags = get_all_tags(df)
    
    st.caption("공유받은 텍스트를 그대로 붙여넣어도 링크만 인식합니다!")
    
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("식당 이름 (필수)")
        category = col2.selectbox("음식 카테고리", ["한식", "중식", "일식", "양식", "아시안", "분식/기타"])
        
        col3, col4 = st.columns(2)
        price = col3.selectbox("1인당 평균 가격", ["1만원 미만", "1~1.5만원", "1.5~2만원", "2만원 이상"])
        distance = col4.radio("회사 거리", ["도보 5분 이내", "도보 10분 이내", "차량 이동"], horizontal=True)
        
        col5, col6 = st.columns(2)
        capacity = col5.selectbox("최대 수용 인원 (테이블)", ["2명", "4명", "6명", "8명", "제한없음(단체가능)"])
        waiting = col6.selectbox("평소 웨이팅", ["없음", "보통", "심함"])

        raw_link = st.text_area("네이버 지도 링크", placeholder="예: [네이버지도] 덕수파스타... https://naver.me/...")
        
        selected_tags = st.multiselect("추천 태그 (선택)", all_tags)
        new_tag = st.text_input("태그 직접 추가 (엔터 키 입력)", placeholder="목록에 없으면 여기에 입력하세요")
        
        rating = st.radio("나의 별점", [1, 2, 3, 4, 5], index=2, horizontal=True, format_func=lambda x: "⭐"*x)
        comment = st.text_input("한줄평")
        recommender = st.text_input("추천인")

        submitted = st.form_submit_button("등록 완료")
        
        if submitted:
            if not name:
                st.error("식당 이름은 필수입니다!")
            else:
                final_link = extract_url(raw_link)
                final_tags = selected_tags
                if new_tag:
                    final_tags.append(new_tag)
                
                new_row = {
                    '식당명': name, '카테고리': category, '가격대': price, 
                    '거리': distance, '최대수용인원': capacity, 
                    '네이버지도URL': final_link, '예약필수여부': "", 
                    '웨이팅정도': waiting, '대표메뉴': "", '휴무일': "",
                    '추천인': recommender, '평점': rating,
                    '태그': ",".join(final_tags), '한줄평': comment
                }
                
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(updated_df)
                st.toast(f"'{name}' 등록 성공!", icon="✅")
                st.rerun()

# -----------------------------------------------------------------------------
# 4. 메인 화면
# -----------------------------------------------------------------------------
menu = st.sidebar.radio("메뉴", ["🔍 점심 추천 (Agent)", "📊 데이터 관리"])

# [검색/추천 페이지]
if menu == "🔍 점심 추천 (Agent)":
    st.title("🤖 오늘 점심 뭐 먹지?")
    
    df = load_data()
    if df.empty:
        st.warning("데이터가 없습니다. 사이드바 메뉴에서 [데이터 관리] > [맛집 등록]을 먼저 해주세요!")
    else:
        with st.container(border=True):
            st.subheader("🔍 조건 검색")
            c1, c2, c3 = st.columns(3)
            
            # 카테고리 검색 (전체 추가)
            cat_options = ["전체"] + sorted(list(df['카테고리'].unique()))
            s_cat = c1.selectbox("카테고리", cat_options)
            
            s_dist = c2.selectbox("최대 이동 거리", ["도보 5분 이내", "도보 10분 이내", "차량 이동(전체)"], index=1)
            s_keyword = c3.multiselect("원하는 분위기/태그", get_all_tags(df))
            
            if st.button("추천 받기 🎲", type="primary", use_container_width=True):
                result = df.copy()
                
                # 1. 카테고리 필터
                if s_cat != "전체":
                    result = result[result['카테고리'] == s_cat]
                
                # 2. 거리 필터 (포함 관계 적용)
                user_dist_level = DISTANCE_MAP.get(s_dist, 3) 
                result['dist_lvl'] = result['거리'].map(DISTANCE_MAP).fillna(1) 
                if "차량" not in s_dist:
                    result = result[result['dist_lvl'] <= user_dist_level]

                # 3. 태그 필터
                if s_keyword:
                    mask = result['태그'].apply(lambda x: any(k in str(x) for k in s_keyword))
                    result = result[mask]
                
                if result.empty:
                    st.error("조건에 맞는 식당이 없습니다.")
                else:
                    st.success(f"총 {len(result)}곳을 찾았습니다!")
                    
                    for i, row in result.iterrows():
                        with st.expander(f"🍽️ **{row['식당명']}** ({row['카테고리']}) {'⭐'*int(row['평점'])}"):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"- 🚶 **거리:** {row['거리']} | 💰 **가격:** {row['가격대']}")
                                st.write(f"- 👥 **인원:** {row['최대수용인원']}")
                                if row['태그']:
                                    st.caption(f"🏷️ {row['태그']}")
                                st.info(f"🗣️ {row['한줄평']}")
                            with col_b:
                                if row['네이버지도URL']:
                                    st.link_button("지도 보기 🗺️", row['네이버지도URL'])

# [관리 페이지]
elif menu == "📊 데이터 관리":
    st.title("맛집 리스트 관리")
    col1, col2 = st.columns([4,1])
    with col2:
        if st.button("➕ 맛집 등록", type="primary"):
            popup_register()
            
    df = load_data()
    
    st.markdown("데이터를 직접 수정하거나 삭제할 수 있습니다. (체크박스 선택 후 Del 키)")
    # 데이터 에디터 (행 추가/삭제 허용 옵션 켬)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("변경사항 저장하기"):
        save_data(edited_df)
        st.success("데이터가 안전하게(UTF-8-SIG) 저장되었습니다!")
        st.rerun()


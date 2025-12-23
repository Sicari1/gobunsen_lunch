import streamlit as st
import pandas as pd
import re # 링크 추출을 위한 정규표현식 라이브러리

# -----------------------------------------------------------------------------
# 1. 설정 및 기본 데이터
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋", layout="wide")

COLUMNS = [
    '식당명', '카테고리', '가격대', '거리', '최대수용인원', 
    '네이버지도URL', '예약필수여부', '웨이팅정도', '대표메뉴', 
    '휴무일', '추천인', '평점', '태그', '한줄평'
]

CSV_FILE = 'lunch_data_v3.csv'

# 기본 태그 목록 (초기값)
DEFAULT_TAGS = ["비오는날", "해장", "조용함", "빨리나옴", "회식가능", "손님접대", "가성비", "혼밥가능"]

# 거리 정렬을 위한 맵핑 (검색 로직용)
DISTANCE_MAP = {"도보 5분 이내": 1, "도보 10분 이내": 2, "차량 이동": 3}

# -----------------------------------------------------------------------------
# 2. 헬퍼 함수 (데이터 로드/저장/링크파싱)
# -----------------------------------------------------------------------------
def load_data():
    import os
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return df
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def extract_url(text):
    """
    네이버 지도 공유 텍스트에서 https:// 링크만 추출합니다.
    """
    if not isinstance(text, str): return ""
    # https://naver.me/xxxxx 또는 일반 https 링크 추출 패턴
    match = re.search(r'(https?://\S+)', text)
    if match:
        return match.group(1)
    return text # 링크가 없으면 입력값 그대로 반환 (혹은 빈 문자열)

def get_all_tags(df):
    """
    기존 데이터에 있는 태그들과 기본 태그들을 합쳐서 중복 없이 반환합니다.
    """
    existing_tags = set()
    if '태그' in df.columns:
        for tag_str in df['태그'].dropna():
            if tag_str:
                existing_tags.update([t.strip() for t in tag_str.split(',')])
    
    # 기본 태그와 합치기
    all_tags = sorted(list(existing_tags.union(DEFAULT_TAGS)))
    return all_tags

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
        
        # 수정됨: 선택형 입력
        col3, col4 = st.columns(2)
        price = col3.selectbox("1인당 평균 가격", ["1만원 미만", "1~1.5만원", "1.5~2만원", "2만원 이상"])
        distance = col4.radio("회사 거리", ["도보 5분 이내", "도보 10분 이내", "차량 이동"], horizontal=True)
        
        # 수정됨: 인원 선택형
        col5, col6 = st.columns(2)
        capacity = col5.selectbox("최대 수용 인원 (테이블)", ["2명", "4명", "6명", "8명", "제한없음(단체가능)"])
        waiting = col6.selectbox("평소 웨이팅", ["없음", "보통", "심함"])

        # 수정됨: 링크 파싱용 텍스트 에리어
        raw_link = st.text_area("네이버 지도 링크 (공유 텍스트 붙여넣기)", 
                              placeholder="예: [네이버지도] 덕수파스타... https://naver.me/...")
        
        # 수정됨: 태그 (선택 + 직접입력)
        selected_tags = st.multiselect("추천 태그 (선택)", all_tags)
        new_tag = st.text_input("태그 직접 추가 (엔터 키 입력)", placeholder="목록에 없으면 여기에 입력하세요")
        
        # 수정됨: 점수 (1~5점 선택)
        rating = st.radio("나의 별점", [1, 2, 3, 4, 5], index=2, horizontal=True, format_func=lambda x: "⭐"*x)
        
        comment = st.text_input("한줄평")
        recommender = st.text_input("추천인")

        submitted = st.form_submit_button("등록 완료")
        
        if submitted:
            if not name:
                st.error("식당 이름은 필수입니다!")
            else:
                # 데이터 전처리
                final_link = extract_url(raw_link) # 링크 추출
                
                final_tags = selected_tags
                if new_tag:
                    final_tags.append(new_tag) # 새 태그 추가
                
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
                st.toast(f"'{name}' 등록 성공! 링크가 자동으로 추출되었습니다.", icon="✅")
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
        st.warning("데이터가 없습니다. 먼저 맛집을 등록해주세요!")
    else:
        with st.container(border=True):
            st.subheader("🔍 조건 검색")
            c1, c2, c3 = st.columns(3)
            
            # 1. 카테고리 (전체 포함)
            cat_options = ["전체"] + list(df['카테고리'].unique())
            s_cat = c1.selectbox("카테고리", cat_options)
            
            # 2. 거리 (로직 포함)
            # 5분 선택 -> 5분만 / 10분 선택 -> 5분+10분 / 차량 -> 전체
            s_dist = c2.selectbox("최대 이동 거리", ["도보 5분 이내", "도보 10분 이내", "차량 이동(전체)"], index=1)
            
            # 3. 태그 검색
            s_keyword = c3.multiselect("원하는 분위기/태그", get_all_tags(df))
            
            if st.button("추천 받기 🎲", type="primary", use_container_width=True):
                result = df.copy()
                
                # 필터 1: 카테고리
                if s_cat != "전체":
                    result = result[result['카테고리'] == s_cat]
                
                # 필터 2: 거리 (레벨 비교)
                # 선택한 거리의 레벨보다 작거나 같은(가까운) 곳은 모두 포함
                # 예: 사용자가 '10분(Lv 2)' 선택 -> '5분(Lv 1)'과 '10분(Lv 2)' 모두 통과
                user_dist_level = DISTANCE_MAP.get(s_dist, 3) 
                
                # 데이터에 있는 거리 텍스트를 숫자로 변환하여 비교
                # (데이터가 비어있으면 기본적으로 포함시킴)
                result['dist_lvl'] = result['거리'].map(DISTANCE_MAP).fillna(1) 
                
                if "차량" not in s_dist: # 차량 선택시 거리 필터 무시 (전체)
                    result = result[result['dist_lvl'] <= user_dist_level]

                # 필터 3: 태그 (교집합 검색)
                if s_keyword:
                    # 하나라도 포함되면 결과에 나옴
                    mask = result['태그'].apply(lambda x: any(k in str(x) for k in s_keyword))
                    result = result[mask]
                
                # 결과 출력
                if result.empty:
                    st.error("조건에 맞는 식당이 없습니다.")
                else:
                    st.success(f"총 {len(result)}곳을 찾았습니다!")
                    
                    # 추천 결과 카드
                    for i, row in result.iterrows():
                        with st.expander(f"🍽️ **{row['식당명']}** ({row['카테고리']}) {'⭐'*int(row['평점'])}"):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"- **거리:** {row['거리']} | **가격:** {row['가격대']}")
                                st.write(f"- **인원:** {row['최대수용인원']}")
                                if row['태그']:
                                    st.caption(f"🏷️ {row['태그']}")
                                st.info(f"🗣️ {row['한줄평']}")
                            with col_b:
                                if row['네이버지도URL']:
                                    st.link_button("지도 보기 🗺️", row['네이버지도URL'])
                                else:
                                    st.write("(링크 없음)")

# [관리 페이지]
elif menu == "📊 데이터 관리":
    st.title("맛집 리스트 관리")
    col1, col2 = st.columns([4,1])
    with col2:
        if st.button("➕ 맛집 등록", type="primary"):
            popup_register()
            
    df = load_data()
    
    # 데이터 에디터 (수정/삭제 가능)
    st.markdown("데이터를 직접 수정하거나 삭제할 수 있습니다. (체크박스 선택 후 Del 키 혹은 휴지통 아이콘)")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    # 변경사항 저장 버튼
    if st.button("변경사항 저장하기"):
        save_data(edited_df)
        st.success("데이터가 저장되었습니다!")
        st.rerun()

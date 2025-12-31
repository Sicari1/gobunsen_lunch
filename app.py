# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_tags import st_tags

# 모듈 임포트
import config as cfg
import utils
import llm_agent

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🍱 우리 팀 점심 에이전트", page_icon="😋", layout="wide")

# -----------------------------------------------------------------------------
# 2. 팝업 UI (맛집/카페 등록)
# -----------------------------------------------------------------------------
@st.dialog("맛집/카페 등록하기 📝")
def popup_register():
    st.caption("필요한 정보만 빠르게 터치해서 등록하세요!")
    
    # [유형 선택] 식당 vs 카페
    type_selection = st.radio("유형 선택", ["식당 🍚", "카페 ☕"], horizontal=True)
    
    # 선택된 유형에 따라 카테고리 및 추천 메뉴 키워드 변경
    if type_selection == "식당 🍚":
        curr_categories = cfg.OPT_CATEGORY_FOOD
        curr_menus = cfg.COMMON_MENUS_FOOD
    else:
        curr_categories = cfg.OPT_CATEGORY_CAFE
        curr_menus = cfg.COMMON_MENUS_CAFE

    col1, col2 = st.columns(2)
    name = col1.text_input("상호명 (필수)")
    category = col2.selectbox("카테고리", curr_categories)
    
    st.markdown("##### 🏷️ 키워드 (검색하거나, 입력 후 Enter)")
    
    c_k1, c_k2 = st.columns(2)
    with c_k1:
        menu_tags = st_tags(
            label='메뉴/대표음료',
            text='입력 후 엔터',
            value=[],
            suggestions=curr_menus,
            maxtags=10,
            key='tags_menu_input'
        )
    with c_k2:
        vibe_tags = st_tags(
            label='분위기',
            text='특징 입력 후 엔터',
            value=[],
            suggestions=cfg.COMMON_VIBES,
            maxtags=10,
            key='tags_vibe_input'
        )

    c1, c2 = st.columns(2)
    price = c1.selectbox("가격대", cfg.OPT_PRICE)
    distance = c2.select_slider("회사 거리", options=cfg.OPT_DISTANCE)
    capacity = st.radio("인원 선택", cfg.OPT_CAPACITY, horizontal=True)

    r1, r2, r3 = st.columns(3)
    phone = r1.text_input("전화번호")
    reservation = r2.selectbox("예약 정보", cfg.OPT_RESERVATION)
    waiting = r3.selectbox("평소 웨이팅", cfg.OPT_WAITING)
    off_days = st.multiselect("휴무일", cfg.OPT_DAYS)
    raw_link = st.text_area("네이버 지도 링크", height=70)

    rating = st.slider("별점", 1.0, 5.0, 3.0, 0.5)
    comment = st.text_input("한줄평")
    recommender = st.text_input("작성자")

    st.markdown("---")
    
    if st.button("등록 완료", type="primary", use_container_width=True):
        if not name:
            st.error("상호명은 필수입니다!")
        else:
            final_link = utils.extract_url(raw_link)
            str_menus = ",".join(menu_tags)
            str_vibes = ",".join(vibe_tags)
            new_row = {
                '식당명': name, '카테고리': category, 
                '메뉴키워드': str_menus, '분위기키워드': str_vibes,
                '가격대': price, '거리': distance, '최대수용인원': capacity, 
                '전화번호': phone, '네이버지도URL': final_link, 
                '예약필수여부': reservation, '웨이팅정도': waiting, '휴무일': ",".join(off_days), 
                '작성자': recommender, '평점': rating, '한줄평': comment
            }
            df = utils.load_data()
            new_df = pd.DataFrame([new_row])
            updated_df = pd.concat([df, new_df], ignore_index=True)
            utils.save_data(updated_df)
            st.toast(f"'{name}' 등록 성공!", icon="✅")
            st.rerun()

# -----------------------------------------------------------------------------
# 3. 메인 화면 구성
# -----------------------------------------------------------------------------
menu = st.sidebar.radio("메뉴", ["🔍 점심/카페 추천", "💬 AI 상담소 (New)", "📅 식사 기록", "📊 데이터 관리"])

# 3-1. 점심/카페 추천
if menu == "🔍 점심/카페 추천":
    st.title("🤖 오늘 어디 가지?")
    raw_df = utils.load_data()
    
    if raw_df.empty:
        st.info("데이터가 없습니다. 먼저 데이터를 등록해주세요.")
    else:
        df = utils.aggregate_reviews(raw_df)
        
        with st.container(border=True):
            search_mode = st.radio("검색 모드", ["식사 하기 🍚", "카페 가기 ☕"], horizontal=True)
            if search_mode == "식사 하기 🍚":
                target_cats = cfg.OPT_CATEGORY_FOOD + ["분식/기타"]
                target_menus = cfg.COMMON_MENUS_FOOD
            else:
                target_cats = cfg.OPT_CATEGORY_CAFE
                target_menus = cfg.COMMON_MENUS_CAFE

            st.subheader("🎯 조건 선택")
            c1, c2, c3 = st.columns(3)
            available_cats_in_db = utils.get_unique_values(df, '카테고리')
            filtered_opts = [c for c in available_cats_in_db if c in target_cats]
            if not filtered_opts: filtered_opts = target_cats

            s_cat = c1.selectbox("카테고리", ["전체"] + filtered_opts)
            s_dist = c2.select_slider("최대 이동 거리", options=["도보 5분 이내", "도보 10분 이내", "차량 이동(전체)"], value="도보 10분 이내")
            s_people = c3.selectbox("인원", ["상관없음", "4명 이하", "5~8명", "단체"])

            df_mode_filtered = df[df['카테고리'].isin(target_cats)]
            all_menu = utils.get_unique_values(df_mode_filtered, '메뉴키워드', target_menus)
            all_vibe = utils.get_unique_values(df, '분위기키워드', cfg.COMMON_VIBES)
            
            k1, k2 = st.columns(2)
            s_menu = k1.multiselect("🥘 메뉴/음료", all_menu)
            s_vibe = k2.multiselect("✨ 분위기", all_vibe)
            
            if st.button("추천 받기 🚀", type="primary", use_container_width=True):
                result = df.copy()
                if s_cat == "전체": result = result[result['카테고리'].isin(target_cats)]
                else: result = result[result['카테고리'] == s_cat]
                
                u_lvl = cfg.DISTANCE_MAP.get(s_dist, 3)
                result['d_lvl'] = result['거리'].map(cfg.DISTANCE_MAP).fillna(3)
                if "차량" not in s_dist: result = result[result['d_lvl'] <= u_lvl]
                
                if s_menu: result = result[result['메뉴키워드'].apply(lambda x: any(k in str(x) for k in s_menu))]
                if s_vibe: result = result[result['분위기키워드'].apply(lambda x: any(k in str(x) for k in s_vibe))]

                if result.empty: 
                    st.warning("조건에 맞는 곳이 없어요.")
                else:
                    st.success(f"{len(result)}곳 발견!")
                    
                    # [신규] 최근 먹은 기록 확인을 위해 history 로드
                    history_df = utils.load_history()
                    recent_eats = []
                    if not history_df.empty:
                        # 오늘 날짜 기준 최근 7일
                        recent_eats = history_df['식당명'].tolist()[-10:] # 간단하게 최근 10개만

                    for i, r in result.iterrows():
                        avg_score = r['평점']
                        review_count = len(r['한줄평'])
                        
                        # 최근에 먹은 곳이면 뱃지 표시
                        visit_badge = " (⚠️최근 방문)" if r['식당명'] in recent_eats else ""
                        
                        with st.expander(f"🍽️ **{r['식당명']}**{visit_badge} ({r['카테고리']}) ⭐{avg_score}"):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.write(f"**🥘** {r['메뉴키워드']} | **✨** {r['분위기키워드']}")
                                st.caption(f"📍 {r['거리']} | 💰 {r['가격대']}")
                                st.divider()
                                
                                # [신규] '오늘 이거 먹음' 버튼
                                col_btn, col_info = st.columns([1, 2])
                                with col_btn:
                                    if st.button(f"😋 오늘 이거 먹음!", key=f"eat_{i}"):
                                        today = datetime.now().strftime("%Y-%m-%d")
                                        # 기록 저장 로직
                                        log_data = {
                                            "날짜": today,
                                            "식당명": r['식당명'],
                                            "카테고리": r['카테고리'],
                                            "메뉴": r['메뉴키워드'], # 대표메뉴로 저장
                                            "작성자": "팀원", # 기본값
                                            "평점": str(avg_score),
                                            "비고": "추천 통해 방문"
                                        }
                                        if utils.add_history_row(log_data):
                                            st.cache_data.clear() # 캐시 강제 삭제
                                            st.toast(f"📅 [{today}] '{r['식당명']}' 저장 완료! (기록 탭 확인)", icon="💾")
                                        else:
                                            st.error("저장 실패: 구글 시트의 'history' 탭을 확인하세요.")

                            with c2:
                                if r['네이버지도URL']: st.link_button("지도 보기", r['네이버지도URL'])

# 3-2. AI 상담소
elif menu == "💬 AI 상담소 (New)":
    st.title("🧠 AI 점심 상담소")
    st.caption(f"Powered by OpenAI {cfg.MODEL_NAME} + 🔍 검색 기능")
    
    raw_df = utils.load_data()
    history_df = utils.load_history() # 히스토리 로드

    if raw_df.empty:
        st.error("데이터가 없어서 상담할 수 없습니다.")
    else:
        df = utils.aggregate_reviews(raw_df)
        
        # [신규] 최근 식사 기록 텍스트화
        history_text = "아직 기록된 식사가 없습니다."
        if not history_df.empty:
            recent = history_df.tail(7) # 최근 7건
            history_list = [f"- {row['날짜']}: {row['식당명']} ({row['메뉴']})" for _, row in recent.iterrows()]
            history_text = "\n".join(history_list)

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "안녕하세요! 날씨 검색도 가능합니다. (예: '오늘 날씨 어때? 메뉴 추천해줘')"}
            ]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("질문을 입력하세요..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                try:
                    with st.spinner("생각 중... (날씨 검색 및 기록 확인) ⚡"):
                        agent = llm_agent.get_agent(df)
                        
                        # [핵심] 시스템 프롬프트에 '오늘 날짜'와 '식사 기록' 주입
                        today_str = datetime.now().strftime("%Y년 %m월 %d일")
                        system_prefix = (
                            f"너는 스마트한 점심 추천 봇이야. 오늘은 {today_str}이야.\n"
                            f"사용자가 날씨를 물어보면 검색 도구를 써서 확인해.\n\n"
                            f"[최근 우리 팀 식사 기록]\n{history_text}\n\n"
                            f"위 기록을 참고해서 최근에 먹은 메뉴는 피해서 추천해줘. 한국어로 대답해."
                        )
                        
                        response = agent.invoke(f"{system_prefix}\n질문: {prompt}")
                        result_text = response["output"]
                        st.write(result_text)
                        st.session_state.messages.append({"role": "assistant", "content": result_text})
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# 3-3. 식사 기록 (신규 탭)
elif menu == "📅 식사 기록":
    st.title("📅 우리 팀 식사 캘린더")
    
    history_df = utils.load_history()
    
    if history_df.empty:
        st.info("아직 기록된 식사가 없습니다. '추천' 탭에서 '오늘 이거 먹음' 버튼을 눌러보세요!")
    else:
        # 상단 통계
        c1, c2, c3 = st.columns(3)
        c1.metric("총 식사 횟수", f"{len(history_df)}회")
        
        # 가장 많이 간 곳
        top_place = history_df['식당명'].mode()
        top_place_name = top_place[0] if not top_place.empty else "-"
        c2.metric("최애 식당", top_place_name)
        
        # 최근 방문
        last_date = history_df['날짜'].iloc[-1] if not history_df.empty else "-"
        c3.metric("마지막 식사일", last_date)
        
        st.divider()
        st.subheader("📋 전체 기록")
        # 최신순 정렬해서 보여주기
        st.dataframe(history_df.sort_values(by="날짜", ascending=False), use_container_width=True)

# 3-4. 데이터 관리 (기존 유지)
elif menu == "📊 데이터 관리":
    st.title("📝 데이터 관리")
    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("➕ 맛집/카페 등록", type="primary"): 
            popup_register()
    
    df = utils.load_data()
    existing_writers = utils.get_unique_values(df, '작성자')
    ALL_CATS = cfg.OPT_CATEGORY_FOOD + cfg.OPT_CATEGORY_CAFE
    
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", 
        column_config={
            "카테고리": st.column_config.SelectboxColumn(options=ALL_CATS, required=True),
            "가격대": st.column_config.SelectboxColumn(options=cfg.OPT_PRICE, required=True),
            "거리": st.column_config.SelectboxColumn(options=cfg.OPT_DISTANCE, required=True),
            "최대수용인원": st.column_config.SelectboxColumn(options=cfg.OPT_CAPACITY, required=True),
            "예약필수여부": st.column_config.SelectboxColumn(options=cfg.OPT_RESERVATION),
            "웨이팅정도": st.column_config.SelectboxColumn(options=cfg.OPT_WAITING),
            "네이버지도URL": st.column_config.LinkColumn(display_text="링크"),
            "전화번호": st.column_config.TextColumn(width="medium"),
            "한줄평": st.column_config.TextColumn(width="large"),
            "평점": st.column_config.SelectboxColumn(label="평점", width="small", options=cfg.OPT_RATING, required=True),
            "작성자": st.column_config.SelectboxColumn(label="작성자", width="medium", options=existing_writers),
            "휴무일": st.column_config.SelectboxColumn(label="휴무일", width="small", options=cfg.OPT_DAYS),
            "메뉴키워드": st.column_config.TextColumn(label="메뉴 (자유입력)", width="medium"),
            "분위기키워드": st.column_config.TextColumn(label="분위기 (자유입력)", width="medium"),
        }
    )
    if st.button("💾 변경사항 저장하기", type="primary"):
        utils.save_data(edited_df)
        st.success("저장 완료!")
        st.rerun()
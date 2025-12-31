# config.py
import streamlit as st

# 기본 설정
SHEET_URL = "https://docs.google.com/spreadsheets/d/1_WvbJhPTbxU5c4hMwv9ak-G78jajBD-ZIrzvqxvgDTI/edit?usp=sharing"
MODEL_NAME = "gpt-4o"

# 데이터 컬럼 정의
COLUMNS = [
    '식당명', '카테고리', '메뉴키워드', '분위기키워드', 
    '가격대', '거리', '최대수용인원', 
    '전화번호', '네이버지도URL', 
    '예약필수여부', '웨이팅정도', '휴무일', 
    '작성자', '평점', '한줄평'
]

# 식사 관련 상수
OPT_CATEGORY_FOOD = ["한식", "중식", "일식", "양식", "아시안", "분식/기타"]
COMMON_MENUS_FOOD = ["김치찌개", "된장찌개", "제육볶음", "돈가스", "파스타", "짜장면", "짬뽕", "삼겹살", "국밥", "샌드위치", "샐러드", "회/초밥"]

# 카페 관련 상수
OPT_CATEGORY_CAFE = ["카페", "베이커리", "디저트 전문", "브런치"]
COMMON_MENUS_CAFE = ["아메리카노", "라떼", "아인슈페너", "케이크", "스콘", "빙수", "소금빵", "크로플", "휘낭시에", "티(Tea)"]

# 공통 상수
OPT_PRICE = ["1만원 미만", "1~1.5만원", "1.5~2만원", "2만원 이상"]
OPT_DISTANCE = ["도보 5분 이내", "도보 10분 이내", "차량 이동"]
OPT_CAPACITY = ["2명", "4명", "6명", "8명", "단체가능"]
OPT_RESERVATION = ["예약 불필요", "예약 가능", "예약 필수", "현장 대기"]
OPT_WAITING = ["없음", "보통", "심함"]
OPT_DAYS = ["월", "화", "수", "목", "금", "토", "일", "연중무휴"]
OPT_RATING = [x * 0.5 for x in range(1, 11)]

COMMON_VIBES = ["조용한", "깔끔한", "시끌벅적한", "노포감성", "빨리나옴", "혼밥가능", "회식추천", "손님접대", "가성비", "비오는날", "해장", "감성적인"]
DISTANCE_MAP = {"도보 5분 이내": 1, "도보 10분 이내": 2, "차량 이동": 3}
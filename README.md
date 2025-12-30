# 🍱 우리 팀 점심 추천 에이전트 (Lunch Recommendation Agent)

매일 점심 메뉴를 고민하는 팀원들을 위한 **데이터 기반 + AI 점심 추천 서비스**입니다.
구글 스프레드시트로 맛집 데이터를 관리하고, Streamlit 웹앱을 통해 규칙 기반 필터링과 AI 상담 기능을 제공합니다.

## 🚀 주요 기능

### 1. 🔍 규칙 기반 추천 (Rule-based)
- **정밀한 필터링:** 카테고리, 거리, 인원, 가격대 등 조건에 맞는 식당을 찾아줍니다.
- **키워드 검색:** '김치찌개', '조용한' 등 메뉴나 분위기 키워드로 검색이 가능합니다.
- **리뷰 통합:** 팀원들이 남긴 여러 개의 한줄평과 별점을 통합해서 보여줍니다.

### 2. 🧠 AI 점심 상담소 (AI Chatbot)
- **OpenAI (GPT-4o-mini) 연동:** 자연어로 질문하면 AI가 데이터를 분석해 답변합니다.
- **사용 예시:**
  - "비 오는 날 가기 좋은 얼큰한 국물 요리집 추천해줘"
  - "평점 4.5 이상이고 웨이팅 없는 곳 있어?"

### 3. 📝 데이터 관리 (Data Management)
- **손쉬운 등록:** 웹 UI에서 터치 몇 번으로 맛집을 등록하고 구글 시트에 저장합니다.
- **실시간 수정:** 등록된 정보를 표(Data Editor)에서 더블클릭으로 바로 수정할 수 있습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend:** Streamlit
- **Data:** Google Sheets (via `streamlit-gsheets`)
- **AI/LLM:** LangChain, OpenAI API (`gpt-4o-mini`)
- **Deployment:** Streamlit Cloud

---

## ⚙️ 설치 및 실행 방법 (Local)

1. **레포지토리 클론**
   ```bash
   git clone [https://github.com/Sicari1/gobunsen_lunch.git](https://github.com/Sicari1/gobunsen_lunch.git)
   cd gobunsen_lunch
   ```

2. **라이브러리 설치**
```bash
pip install -r requirements.txt
   ```

3. **앱 실행**
```bash
streamlit run app.py
```

---

## 📂 프로젝트 구조

```text
gobunsen_lunch/
├── app.py              # 메인 애플리케이션 코드
├── requirements.txt    # 필요 라이브러리 목록
├── .gitignore          # 깃 업로드 제외 설정
└── README.md           # 프로젝트 설명서

```
```
# 🍱 우리 팀 점심 에이전트 (Lunch Recommendation Agent)

매일 점심 메뉴를 고르느라 고민하는 팀원들을 위해 개발된 **AI 기반 점심 메뉴 추천 및 맛집 데이터 관리 서비스**입니다.
구글 시트(Google Sheets)를 데이터베이스로 사용하여 팀원 누구나 데이터를 쉽게 관리할 수 있으며, Streamlit Cloud를 통해 언제 어디서나 접속할 수 있습니다.

## 🌟 주요 기능 (Features)

### 1. 🤖 점심 메뉴 추천 (Agent)

* **조건 검색:** 카테고리(한식/중식 등), 거리, 가격대, 인원 수에 따른 필터링.
* **키워드 매칭:** 먹고 싶은 메뉴(예: 김치찌개)나 분위기(예: 조용한, 노포감성) 태그 기반 검색.
* **리뷰 통합:** 같은 식당에 대해 여러 팀원이 남긴 평점(평균 계산)과 한줄평을 모아서 보여줍니다.
* **편의성:** 네이버 지도 링크 바로가기 제공.

### 2. 📝 맛집 데이터 관리 (Data Management)

* **간편 등록:** 식당 이름, 위치, 키워드 등을 터치 몇 번으로 쉽게 등록하는 팝업 UI 제공.
* **실시간 수정:** 엑셀 같은 표(Data Editor)에서 더블 클릭으로 데이터 수정 가능.
* *오타 방지를 위한 드롭다운(선택지) 제공.*


* **클라우드 동기화:** 수정 후 [저장] 버튼을 누르면 구글 시트에 즉시 반영.

---

## 🛠 기술 스택 (Tech Stack)

* **Language:** Python 3.9+
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Database:** Google Sheets (via `st-gsheets-connection`)
* **Version Control:** Git & GitHub
* **Hosting:** Streamlit Community Cloud

---

## 🚀 개발 및 배포 가이드 (Workflow)

이 프로젝트는 안정적인 운영을 위해 **`main` (배포용)** 브랜치와 **`develop` (개발용)** 브랜치를 분리하여 운영합니다.

### 1. 기능 개발 및 수정 (Develop)

새로운 기능을 추가하거나 코드를 수정할 때는 항상 `develop` 브랜치에서 작업합니다.

```bash
# 1. 개발 브랜치로 이동
git checkout develop

# 2. 코드 수정 후 로컬 테스트
streamlit run app.py

# 3. 변경사항 저장 및 업로드
git add .
git commit -m "작업 내용 요약 (예: UI 개선)"
git push origin develop

```

### 2. 배포 및 업데이트 (Merge to Main)

`develop`에서 테스트가 끝난 코드를 실제 서버(`main`)에 반영하는 방법입니다.

```bash
# 1. 메인 브랜치로 이동
git checkout main

# 2. 개발 내용을 메인으로 합치기
git merge develop

# 3. GitHub에 업로드 (자동 배포됨)
git push origin main

```

> **Note:** `git push origin main`을 실행하면 Streamlit Cloud가 변경사항을 감지하고 약 1~2분 뒤에 웹사이트를 자동으로 업데이트합니다.

---

## 📖 사용 방법 (User Guide)

### 1. 맛집 등록하기

1. 사이드바 메뉴에서 **[📊 데이터 관리]** 탭 클릭.
2. **[➕ 맛집 등록]** 버튼 클릭.
3. 식당 정보 입력 (키워드, 거리, 평점 등).
4. **[등록 완료]** 버튼 클릭 (자동으로 구글 시트에 저장됨).

### 2. 데이터 수정하기 (엑셀처럼)

1. **[📊 데이터 관리]** 탭의 표(Table) 확인.
2. 수정하고 싶은 셀을 **더블 클릭**.
3. 드롭다운 목록에서 선택하거나 텍스트 수정.
* *주의: 메뉴/분위기 키워드는 드롭다운 선택 시 기존 내용이 덮어씌워지므로, 여러 개 입력 시 직접 타이핑 권장.*


4. 수정이 끝나면 표 하단의 **[💾 변경사항 저장하기]** 버튼을 반드시 클릭해야 반영됨.

### 3. 로컬 실행 (내 컴퓨터에서 돌리기)

개발을 위해 내 컴퓨터에서 실행하려면 `secrets.toml` 설정이 필요합니다.

1. **필수 라이브러리 설치:**
```bash
pip install -r requirements.txt

```


2. **Secrets 설정:**
* `.streamlit/secrets.toml` 파일을 생성하고 구글 시트 연결 정보(API Key)를 입력해야 합니다. (보안상 GitHub에 올리지 않음)


3. **실행:**
```bash
streamlit run app.py

```



---

## 📂 프로젝트 구조 (Structure)

```text
📦 gobunsen_lunch
 ├── 📄 app.py              # 메인 애플리케이션 코드 (UI, 로직 포함)
 ├── 📄 requirements.txt    # 필요한 파이썬 라이브러리 목록
 ├── 📄 .gitignore          # Git 업로드 제외 파일 목록 (보안 중요)
 ├── 📂 .streamlit          # (로컬용) 설정 폴더
 │    └── 📄 secrets.toml   # (로컬용) API 키 저장소 (절대 공유 금지)
 └── 📄 README.md           # 프로젝트 설명서

```

---

## ⚠️ 주의사항 (Security & Caution)

1. **보안 (Secrets):** `secrets.toml` 파일이나 `.json` 키 파일은 **절대로 GitHub에 업로드하지 마세요.** 해킹의 위험이 있습니다.
2. **데이터 백업:** 구글 시트의 데이터는 중요하므로, 주기적으로 시트 자체를 복제하여 백업해두는 것을 권장합니다.
3. **동시 수정:** 여러 명이 동시에 '데이터 관리' 탭에서 [저장]을 누르면 충돌이 날 수 있습니다. 데이터 수정은 한 명씩 하는 것이 안전합니다.
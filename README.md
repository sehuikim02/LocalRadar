# 📡 로컬레이더 (LocalRadar)
> **광고 없는 동네 찐맛집·신상 카페 스펙 분석 대시보드**  
> 네이버 블로그 검색 직접 크롤링 + Google Gemini 2.5 Flash Structured Outputs

---

## 🌟 프로젝트 소개
로컬레이더(LocalRadar)는 범람하는 블로그 대가성 광고/체험단 포스팅을 인공지능으로 걸러내고, 실제 방문객의 '내돈내산' 찐후기만을 바탕으로 **주차, 웨이팅, 대표 메뉴, 솔직한 장단점**을 일목요연하게 비교해 주는 로컬 탐색 지원 대시보드입니다.

---

## 🛠 실행 방법

### 1. 사전 준비 (환경 변수 설정)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 본인의 Google Gemini API 키를 입력합니다. (루트의 `.env.example` 참고)

```env
GEMINI_API_KEY="your_gemini_api_key_here"
```

### 2. 가상환경 세팅 및 패키지 설치
```bash
# 가상환경 생성 (선택 사항)
python -m venv venv
# 가상환경 활성화 (Windows)
.\venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 3. Streamlit 앱 실행
```bash
streamlit run app.py
```
실행 후 브라우저가 자동으로 열리며, 열리지 않을 경우 콘솔에 표시된 `http://localhost:8501` 주소로 접속합니다.

---

## 📂 프로젝트 문서 (`docs/`)
과제 평가 및 개발 분석에 필요한 상세 문서 4종이 `docs/` 폴더에 구비되어 있습니다:
- [`docs/PRD.md`](docs/PRD.md) : 제품 요구사항 정의서 (기획 배경, 아키텍처, JSON 스키마, 기능 명세)
- [`docs/CHECKLIST.md`](docs/CHECKLIST.md) : 개발 및 배포 점검 체크리스트
- [`docs/TEST_LIST.md`](docs/TEST_LIST.md) : 10개 핵심 시나리오 기능 및 예외 테스트 결과서
- [`docs/PPT_OUTLINE.md`](docs/PPT_OUTLINE.md) : 10장 슬라이드 발표 자료 구성안

import os
import re
import json
import time
import urllib.parse
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# ----------------------------------------------------
# 1. 페이지 기본 설정 및 감각적인 에디토리얼 테마 CSS
# ----------------------------------------------------
st.set_page_config(
    page_title="로컬레이더 (LocalRadar) | 로컬 큐레이션 매거진",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 감각적인 웜 아이보리 + 코랄 오렌지 매거진 테마 주입
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 전체 폰트 및 기본 배경 (눈이 편안한 웜 아이보리) */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
        background-color: #FAF9F6 !important;
        color: #1E1E1E !important;
    }

    /* 메인 컨테이너 최대 너비 및 여백 최적화 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px !important;
    }

    /* 사이드바 스타일링: 깨끗한 화이트 배경 + 세련된 보더 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAE6DF !important;
        min-width: 390px !important;
        max-width: 450px !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding: 2rem 1.6rem !important;
    }

    /* 사이드바 헤더 및 뱃지 */
    .sidebar-brand-badge {
        display: inline-block;
        background: #FFF0EB;
        color: #FF5A36;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1E1E1E;
        letter-spacing: -0.02em;
        margin-bottom: 0.3rem;
    }
    .sidebar-subtitle {
        font-size: 0.88rem;
        color: #71717A;
        line-height: 1.4;
        margin-bottom: 1.8rem;
    }

    /* 텍스트 입력 필드 고도화 */
    [data-testid="stTextInput"] input {
        background-color: #FAFAFA !important;
        border: 1px solid #E4E4E7 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #18181B !important;
        transition: all 0.2s ease;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #FF5A36 !important;
        box-shadow: 0 0 0 3px rgba(255, 90, 54, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* 사이드바 스캔 CTA 버튼: 코랄 그라데이션 + 3D 그림자 + 호버 */
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B4A 0%, #FF451A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.2rem !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 6px 18px rgba(255, 69, 26, 0.28) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(255, 69, 26, 0.38) !important;
        background: linear-gradient(135deg, #FF7B5C 0%, #FF3D10 100%) !important;
    }

    /* 상단 히어로 배너 (Hero Magazine Card) */
    .hero-banner {
        background: linear-gradient(135deg, #FFF6F3 0%, #FFF0EB 60%, #FFE9E2 100%);
        border: 1px solid #FCDDD4;
        border-radius: 20px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(255, 90, 54, 0.06);
    }
    .hero-banner::after {
        content: "LOCAL RADAR";
        position: absolute;
        right: -20px;
        bottom: -25px;
        font-size: 4.8rem;
        font-weight: 900;
        color: rgba(255, 90, 54, 0.05);
        letter-spacing: 0.02em;
        pointer-events: none;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFFFFF;
        color: #FF5A36;
        border: 1px solid #FFD8CE;
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(255, 90, 54, 0.08);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #18181B;
        letter-spacing: -0.03em;
        line-height: 1.25;
        margin-bottom: 0.6rem;
    }
    .hero-desc {
        font-size: 1.05rem;
        color: #52525B;
        line-height: 1.6;
        max-width: 680px;
        margin-bottom: 1.2rem;
    }
    .hero-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 12px;
        border: 1px solid #E4E4E7;
        font-size: 0.82rem;
        color: #3F3F46;
        font-weight: 600;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }

    /* 프로그레스 바 커스텀 */
    [data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #FF6B4A 0%, #FF451A 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 10px rgba(255, 69, 26, 0.35) !important;
    }
    [data-testid="stProgress"] > div > div > div {
        background-color: #EAE6DF !important;
        border-radius: 10px !important;
        height: 10px !important;
    }
    [data-testid="stProgress"] p {
        font-weight: 700 !important;
        color: #FF451A !important;
        font-size: 0.95rem !important;
    }

    /* 스탯 KPI 매거진 카드 */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #EFECE6;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
    }
    .stat-card-accent-1 { border-top: 4px solid #3B82F6; }
    .stat-card-accent-2 { border-top: 4px solid #FF5A36; background: #FFFDFD; }
    .stat-card-accent-3 { border-top: 4px solid #10B981; }
    .stat-label {
        font-size: 0.88rem;
        font-weight: 600;
        color: #71717A;
        margin-bottom: 0.4rem;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #18181B;
        letter-spacing: -0.02em;
    }
    .stat-sub {
        font-size: 0.78rem;
        color: #A1A1AA;
        margin-top: 0.3rem;
    }

    /* 상권 브리핑 카드 */
    .briefing-box {
        background: #FFFFFF;
        border: 1px solid #FFE4DC;
        border-left: 5px solid #FF5A36;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin: 1.6rem 0;
        box-shadow: 0 4px 16px rgba(255, 90, 54, 0.04);
    }
    .briefing-title {
        font-size: 1rem;
        font-weight: 800;
        color: #FF5A36;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .briefing-text {
        font-size: 0.98rem;
        color: #27272A;
        line-height: 1.65;
    }

    /* 핫플 TOP 10 큐레이션 카드 (호버 애니메이션) */
    .hotspot-card {
        background: #FFFFFF;
        border: 1px solid #EFECE6;
        border-radius: 16px;
        padding: 1.3rem;
        height: 100%;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hotspot-card:hover {
        transform: translateY(-4px);
        border-color: #FF5A36;
        box-shadow: 0 10px 25px rgba(255, 90, 54, 0.12);
    }
    .hotspot-badge {
        display: inline-block;
        background: #F4F4F5;
        color: #71717A;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .hotspot-name {
        font-size: 1.15rem;
        font-weight: 800;
        color: #18181B;
        margin-bottom: 0.4rem;
    }
    .hotspot-desc {
        font-size: 0.82rem;
        color: #71717A;
        line-height: 1.5;
        margin-bottom: 1rem;
        flex-grow: 1;
    }

    /* 베스트 픽 카드 스타일링 */
    .best-card {
        background: #FFFFFF;
        border: 1px solid #EFECE6;
        border-radius: 18px;
        padding: 1.6rem;
        height: 100%;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.04);
        position: relative;
        transition: all 0.25s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .best-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.07);
    }
    .best-card-first {
        border: 2px solid #FF5A36 !important;
        box-shadow: 0 8px 26px rgba(255, 90, 54, 0.1) !important;
    }
    .ribbon-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #FF5A36;
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }
    .normal-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #F4F4F5;
        color: #3F3F46;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }
    .best-place-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #18181B;
        margin-bottom: 0.6rem;
        line-height: 1.3;
    }
    .best-menu-box {
        background: #FAFAFA;
        border: 1px solid #F4F4F5;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        font-size: 0.85rem;
        color: #27272A;
        margin-bottom: 0.8rem;
    }
    .best-reason {
        font-size: 0.88rem;
        color: #52525B;
        line-height: 1.6;
        margin-bottom: 1.2rem;
        flex-grow: 1;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 전국 핫플 TOP 10 데이터 및 헬퍼 정의
# ----------------------------------------------------
def get_gemini_api_key(user_input_key: str = "") -> str:
    """
    API 키 우선순위 로직:
    1순위: 사이드바 사용자 직접 입력값
    2순위: st.secrets.get("GEMINI_API_KEY") (Streamlit Cloud, 로컬 파일 부재 시 예외 안전 처리)
    3순위: os.getenv("GEMINI_API_KEY") (.env 로컬 환경변수)
    """
    if user_input_key and user_input_key.strip():
        return user_input_key.strip()

    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and str(key).strip():
                return str(key).strip()
    except Exception:
        pass

    env_key = os.getenv("GEMINI_API_KEY", "")
    return env_key.strip() if env_key else ""

def build_naver_map_url(region: str, place_name: str) -> str:
    """
    네이버 지도 검색 URL을 안정적으로 생성.
    가게명에 붙은 지역명, 블로그 수식어 등을 정제하여 네이버 지도에서 정확히 검색되도록 보정.
    """
    p_name = place_name.strip()
    p_name = re.sub(r"\[.*?\]|\(.*?\)", "", p_name).strip()
    clean_name = re.sub(r"^(울산|서울|부산|대구|대전|광주|제주|강릉|전주|수원|인천|경주)\s*", "", p_name)
    clean_name = re.sub(r"\s*(맛집|카페|베이커리|본점|직영점|내돈내산|추천)$", "", clean_name).strip()
    target_name = clean_name if len(clean_name) >= 2 else p_name

    reg_parts = region.split()
    sub_region = reg_parts[-1] if reg_parts else region

    query_str = f"{sub_region} {target_name}"
    return f"https://map.naver.com/p/search/{urllib.parse.quote(query_str)}"

HOTSPOTS = [
    {"name": "서울 성수동", "category": "TREND SPOT", "desc": "트렌디한 팝업스토어와 감성 팩토리 카페의 성지"},
    {"name": "부산 전포동", "category": "CAFE STREET", "desc": "골목마다 숨겨진 감성 디저트 카페와 힙한 맛집"},
    {"name": "울산 삼산동", "category": "HOT DOWNTOWN", "desc": "울산의 메인 번화가, 최신 트렌드 맛집 밀집 지역"},
    {"name": "대구 동성로", "category": "BAKERY & FOOD", "desc": "대구 중심가, 개성 넘치는 베이커리와 로컬 맛집"},
    {"name": "대전 은행동", "category": "LOCAL VIBE", "desc": "성심당 거리부터 으능정이 감성 카페까지"},
    {"name": "제주 애월읍", "category": "OCEAN SUNSET", "desc": "에메랄드빛 오션뷰와 힐링 선셋 카페 라인업"},
    {"name": "강릉 안목해변", "category": "COFFEE COAST", "desc": "푸른 동해 바다를 바라보는 명품 커피거리"},
    {"name": "전주 객리단길", "category": "MODERN HANOK", "desc": "한옥과 모던의 조화, 개성 가득한 감성 골목"},
    {"name": "광주 동명동", "category": "VINTAGE ALLEY", "desc": "주택 개조 감성 카페와 맛있는 식당들의 아지트"},
    {"name": "수원 행궁동", "category": "HERITAGE WALK", "desc": "수원화성 성곽길 따라 펼쳐진 감성 공방 & 행리단길"}
]

PURPOSE_OPTIONS = [
    "주차편함", "카공/노트북", "조용한/대화하기좋은", "웨이팅적음",
    "데이트/분위기", "가성비", "디저트/커피맛집", "혼밥/혼술가능",
    "부모님/가족모임", "단체회식/모임", "뷰맛집/야경", "로컬노포/현지인맛집",
    "애견동반", "신상오픈"
]

# ----------------------------------------------------
# 3. 웹 크롤링 모듈: 네이버 블로그 검색 직접 스크래핑
# ----------------------------------------------------
def crawl_naver_blog_reviews(region: str, category: str, display_count: int):
    """
    네이버 블로그 검색 탭을 직접 크롤링하여 블로그 제목, 요약 텍스트, 원문 URL을 추출.
    클래스명 변경에 유연하도록 a[href*='blog.naver.com'] 기반 상위 카드 컨테이너를 탐색.
    """
    query = f"{region} {category} 내돈내산"
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.naver.com/",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            return None, f"네이버 검색 페이지 응답 오류 (상태 코드: {response.status_code})"

        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        seen_urls = set()

        for a in soup.find_all("a"):
            href = a.get("href") or ""
            match = re.match(r"https?://blog\.naver\.com/([^/]+)/(\d+)", href)
            if not match:
                continue

            post_url = match.group(0)
            if post_url in seen_urls:
                continue

            anchor_title = a.get_text(" ", strip=True).replace("새 창 열림", "").strip()

            curr = a
            card = None
            for _ in range(7):
                curr = curr.parent
                if not curr:
                    break
                sibling_count = len(curr.find_next_siblings()) + len(curr.find_previous_siblings())
                if curr.name == "li" or sibling_count >= 5:
                    card = curr
                    break
                if any(cls in ["view_wrap", "detail_box", "total_wrap"] for cls in (curr.get("class") or [])):
                    card = curr
                    break

            if not card:
                card = a.parent.parent.parent if (a.parent and a.parent.parent) else a

            lines = [re.sub(r"\s+", " ", line).strip() for line in card.get_text("\n", strip=True).split("\n")]
            filtered_lines = [
                l for l in lines
                if l and l not in ["새 창 열림", "Keep에 저장", "Keep에 바로가기"] and not re.match(r"^\d+$", l)
            ]

            title = anchor_title if anchor_title else "제목 없음"
            desc_candidates = [l for l in filtered_lines if len(l) > 20 and l != title]
            desc = " ".join(desc_candidates) if desc_candidates else " ".join(filtered_lines)

            seen_urls.add(post_url)
            articles.append({
                "title": title,
                "description": desc[:400],
                "link": post_url
            })

            if len(articles) >= display_count:
                break

        if not articles:
            return None, "네이버 검색 결과에서 블로그 후기를 찾지 못했습니다. 검색어나 지역명을 확인해 보세요."

        return articles, None

    except Exception as e:
        return None, f"웹 크롤링 중 오류가 발생했습니다: {str(e)}"

# ----------------------------------------------------
# 4. Google Gemini AI 분석 모듈 (Structured Outputs)
# ----------------------------------------------------
def analyze_reviews_with_gemini(reviews: list, target_query: str, purposes: list, api_key: str):
    """google-genai SDK를 활용하여 광고 필터링 및 찐후기 JSON 분석 (v1beta)"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None, "google-genai 패키지가 설치되어 있지 않습니다. `pip install google-genai`를 실행해 주세요."

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

    purpose_str = ", ".join(purposes) if purposes else "전반적인 가성비 및 분위기"

    full_prompt = f"""당신은 로컬 맛집 및 신상 카페의 실제 후기(내돈내산)를 감별하는 전문 분석가 AI '로컬레이더(LocalRadar)'입니다.
전달받은 웹 크롤링된 블로그 글(제목, 요약 본문, 원문 링크) 목록을 면밀히 분석하여 다음 규칙에 따라 엄격한 JSON을 출력하십시오:

[핵심 분석 규칙]
1. 협찬, 제품/서비스 제공, 원고료 지원, 기자단, 체험단 등 대가성 광고/홍보성 글은 철저히 제외하고 'filtered_ads' 카운트를 증가시킵니다.
2. 동일한 가게에 대한 후기가 여러 개 있을 경우 하나로 병합하여 종합적으로 분석합니다.
3. [중요-가게명 추출]: place_name은 반드시 실존하는 사업자 상호명(가게 본래의 이름, 예: '오드밀', '바틱', '휩커피', '런던베이글뮤지엄')만 정확하게 추출해야 합니다. '지역', '내돈내산', '카페', '맛집', 메뉴명(버터케이크 등)이나 수식어구가 가게명으로 잘못 지정되지 않도록 엄격히 정제하십시오.
4. area_briefing: 수집된 후기들을 종합하여 해당 지역 상권의 전반적인 특징, 주차/웨이팅 분위기, 추천 방문 팁을 친절하고 통찰력 있는 2~3문장으로 요약 작성합니다.
5. 방문 목적(사용자 선택 목적: {purpose_str})에 얼마나 잘 부합하는지 평가합니다.
6. 상위 추천(top_picks)은 최대 3개까지 선정하며, 상황에 맞는 맞춤형 배지(예: '🏆 주차·웨이팅 최적', '✨ 데이트/분위기 1위', '☕ 디저트 끝판왕' 등)와 구체적 이유를 제시합니다.
7. 각 가게(places)에 대해 주차, 웨이팅, 장점, 주의점(단점)을 솔직하게 요약합니다. 언급이 없으면 '정보 없음'으로 표기합니다.
8. tags는 핵심 특징 키워드 2~3개를 '#'을 포함한 형태로 작성합니다 (예: ["#주차편함", "#소금빵맛집"]).
9. source_url은 해당 가게와 연관된 블로그 중 가장 신뢰할 만한 원문 링크를 1개 넣습니다.

반드시 정해진 JSON 스키마를 준수하십시오.

[검색 지역 및 유형]: {target_query}
[사용자 선택 방문 목적]: {purpose_str}

[크롤링된 블로그 후기 목록]:
{json.dumps(reviews, ensure_ascii=False, indent=2)}

위 후기들을 바탕으로 광고를 필터링하고 실제 방문객의 찐후기를 분석하여 요구된 JSON 형식으로 반환해 주세요.
"""

    json_schema = {
        "type": "OBJECT",
        "properties": {
            "summary_metrics": {
                "type": "OBJECT",
                "properties": {
                    "total_analyzed": {"type": "INTEGER"},
                    "filtered_ads": {"type": "INTEGER"},
                    "valid_places_count": {"type": "INTEGER"}
                },
                "required": ["total_analyzed", "filtered_ads", "valid_places_count"]
            },
            "area_briefing": {"type": "STRING"},
            "top_picks": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "badge": {"type": "STRING"},
                        "place_name": {"type": "STRING"},
                        "reason": {"type": "STRING"},
                        "signature_menu": {"type": "STRING"}
                    },
                    "required": ["badge", "place_name", "reason", "signature_menu"]
                }
            },
            "places": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "place_name": {"type": "STRING"},
                        "signature_menu": {"type": "STRING"},
                        "waiting_info": {"type": "STRING"},
                        "parking_info": {"type": "STRING"},
                        "pros": {"type": "STRING"},
                        "cons": {"type": "STRING"},
                        "tags": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "source_url": {"type": "STRING"}
                    },
                    "required": ["place_name", "signature_menu", "waiting_info", "parking_info", "pros", "cons", "tags", "source_url"]
                }
            }
        },
        "required": ["summary_metrics", "area_briefing", "top_picks", "places"]
    }

    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = None

    for model_name in candidate_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json",
                        response_schema=json_schema,
                    )
                )
                parsed_result = json.loads(response.text)
                return parsed_result, None
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    time.sleep(1.5)
                    continue
                else:
                    break

    return None, f"Gemini 분석 중 일시적 서버 과부하가 발생했습니다: {last_error}"

# ----------------------------------------------------
# 5. 상태 초기화 및 핫플 빠른 스캔 전환 처리
# ----------------------------------------------------
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "current_search_label" not in st.session_state:
    st.session_state["current_search_label"] = ""
if "location_input_box" not in st.session_state:
    st.session_state["location_input_box"] = "울산 삼산동"
if "trigger_scan" not in st.session_state:
    st.session_state["trigger_scan"] = False

if "pending_region" in st.session_state:
    st.session_state["location_input_box"] = st.session_state["pending_region"]
    del st.session_state["pending_region"]

# ----------------------------------------------------
# 6. 사이드바 UI (큐레이션 컨트롤 패널)
# ----------------------------------------------------
with st.sidebar:
    if st.session_state["analysis_result"] is not None:
        if st.button("← 핫플 TOP 10 매거진 홈", use_container_width=True):
            st.session_state["analysis_result"] = None
            st.session_state["trigger_scan"] = False
            st.rerun()
        st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    st.markdown("<span class='sidebar-brand-badge'>AI Curation Filter</span>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>탐색 조건 설정</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-subtitle'>원하는 지역과 취향을 선택하면 광고를 걷어낸 찐스펙만 분석합니다.</div>", unsafe_allow_html=True)

    # 1) 지역명 입력
    location_input = st.text_input(
        "📍 탐색 지역명",
        key="location_input_box",
        placeholder="예: 서울 성수동, 부산 전포동, 울산 삼산동",
        help="시/군/구 및 읍/면/동이나 대표 상권명을 입력하세요."
    )

    st.markdown("<div style='margin-bottom: 1.6rem;'></div>", unsafe_allow_html=True)

    # 2) 장소 유형 선택
    place_type = st.radio(
        "🍽️ 카테고리",
        options=["카페", "맛집", "혼밥/술집"],
        index=0,
        horizontal=True
    )

    st.markdown("<div style='margin-bottom: 1.6rem;'></div>", unsafe_allow_html=True)

    # 3) 방문 목적 필터
    purposes = st.multiselect(
        "🎯 방문 목적 & 취향 (다중 선택)",
        options=PURPOSE_OPTIONS,
        default=["데이트/분위기", "디저트/커피맛집"]
    )

    st.markdown("<div style='margin-bottom: 1.6rem;'></div>", unsafe_allow_html=True)

    # 4) 분석할 블로그 수
    blog_count = st.slider(
        "📑 수집 후기 표본 수",
        min_value=10,
        max_value=25,
        value=15,
        step=1,
        help="수집할 블로그 글의 개수입니다. 많을수록 분석 신뢰도가 높아집니다."
    )

    st.markdown("<div style='margin-bottom: 1.6rem;'></div>", unsafe_allow_html=True)

    # 5) API 키 입력 (선택 사항: 1순위 직접 입력 오버라이드)
    custom_gemini_key = st.text_input(
        "🔑 Gemini API Key (선택)",
        type="password",
        placeholder="직접 입력 시 우선 적용됩니다",
        help="미입력 시 Streamlit Cloud Secrets 또는 .env 파일의 키가 자동으로 사용됩니다."
    )

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # 6) 메인 스캔 버튼 (CTA)
    manual_scan_button = st.button("📡 로컬레이더 스캔 시작", type="primary", use_container_width=True)

# API 키 확정 (1순위 사용자 직접입력 -> 2순위 st.secrets -> 3순위 .env)
gemini_api_key = get_gemini_api_key(custom_gemini_key)

# ----------------------------------------------------
# 7. 상단 히어로 배너 (Hero Magazine Header)
# ----------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-tag">✨ LOCAL CURATION RADAR</div>
    <div class="hero-title">동네 찐후기만 골라 담는<br><span style="color: #FF5A36;">로컬레이더</span> 매거진</div>
    <div class="hero-desc">대가성 협찬과 광고는 인공지능이 깨끗하게 걸러내고, 실제 방문객의 내돈내산 경험에서 주차·웨이팅·장단점 핵심 스펙만 큐레이션합니다.</div>
    <div class="hero-status-pill">
        <span class="status-dot"></span>
        <span>광고 필터링 엔진 활성화 · <b>Gemini 2.5 Flash</b> 실시간 연동</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 스캔 트리거 확인
should_run_scan = manual_scan_button or st.session_state["trigger_scan"]
if should_run_scan:
    st.session_state["trigger_scan"] = False

    target_region = st.session_state.get("location_input_box", "").strip()
    if not gemini_api_key:
        st.error("⚠️ `GEMINI_API_KEY`가 설정되어 있지 않습니다. 사이드바에 직접 입력하거나, Streamlit Cloud의 Secrets 또는 로컬의 `.env` 파일을 확인해 주세요.")
    elif not target_region:
        st.warning("⚠️ 지역명을 입력해 주세요.")
    else:
        st.session_state["current_search_label"] = f"{target_region} · {place_type}"

        progress_bar = st.progress(0, text="📡 로컬레이더 가동 준비 중... (0%)")

        with st.status(f"🔍 '{target_region}' 찐후기 크롤링 및 AI 큐레이션 진행 중...", expanded=True) as status:
            progress_bar.progress(15, text="1️⃣ 네이버 블로그 검색 탭 크롤링 중... (15%)")
            st.write(f"1️⃣ 네이버 블로그 검색 탭 접속 (검색어: `{target_region} {place_type} 내돈내산`)")

            reviews, err = crawl_naver_blog_reviews(
                region=target_region,
                category=place_type,
                display_count=blog_count
            )

            if err:
                progress_bar.empty()
                status.update(label="❌ 블로그 크롤링 실패", state="error", expanded=True)
                st.error(err)
            elif not reviews:
                progress_bar.empty()
                status.update(label="⚠️ 수집된 후기가 없습니다.", state="error", expanded=True)
                st.info("검색 결과가 없습니다. 지역명이나 장소 유형을 확인해 주세요.")
            else:
                progress_bar.progress(50, text=f"✅ 블로그 {len(reviews)}건 수집 완료! Gemini AI 분석 준비 중... (50%)")
                st.write(f"✅ 네이버 블로그 {len(reviews)}건 본문 요약 데이터 추출 완료.")
                
                progress_bar.progress(70, text="2️⃣ Gemini 2.5 Flash 광고 필터링 및 찐스펙 분석 중... (70%)")
                st.write("2️⃣ Gemini 2.5 Flash 기반 대가성 포스팅 필터링 및 찐스펙 정형화 중...")

                result, gemini_err = analyze_reviews_with_gemini(
                    reviews=reviews,
                    target_query=f"{target_region} {place_type}",
                    purposes=purposes,
                    api_key=gemini_api_key
                )

                if gemini_err:
                    progress_bar.empty()
                    status.update(label="❌ AI 분석 실패", state="error", expanded=True)
                    st.error(gemini_err)
                else:
                    progress_bar.progress(100, text="🎉 큐레이션 완료! 결과 대시보드를 생성합니다. (100%)")
                    status.update(label="🎉 로컬레이더 큐레이션 완료!", state="complete", expanded=False)
                    st.session_state["analysis_result"] = result
                    st.session_state["searched_region"] = target_region
                    progress_bar.empty()

# ----------------------------------------------------
# 8. 화면 분기: 분석 결과 화면 vs 랜딩 뷰 (핫플 TOP 10)
# ----------------------------------------------------
if st.session_state["analysis_result"]:
    res = st.session_state["analysis_result"]
    metrics = res.get("summary_metrics", {})
    area_briefing = res.get("area_briefing", "")
    top_picks = res.get("top_picks", [])
    places = res.get("places", [])
    current_reg = st.session_state.get("searched_region", st.session_state.get("location_input_box", "지역"))

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"### 📊 큐레이션 리포트 : <span style='color: #FF5A36;'>{st.session_state['current_search_label']}</span>", unsafe_allow_html=True)

    # 1) 컬러 포인트 라인이 들어간 3개 미니 스탯 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card stat-card-accent-1">
            <div class="stat-label">수집된 후기 표본</div>
            <div class="stat-value">{metrics.get('total_analyzed', 0)} <span style="font-size:1.1rem; font-weight:600;">건</span></div>
            <div class="stat-sub">네이버 블로그 최신 내돈내산 포스팅</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card stat-card-accent-2">
            <div class="stat-label" style="color: #FF5A36;">🚫 걸러낸 협찬·광고</div>
            <div class="stat-value" style="color: #FF5A36;">{metrics.get('filtered_ads', 0)} <span style="font-size:1.1rem; font-weight:600;">건</span></div>
            <div class="stat-sub">원고료/체험단 등 대가성 글 감지 차단</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card stat-card-accent-3">
            <div class="stat-label">엄선된 로컬 플레이스</div>
            <div class="stat-value">{metrics.get('valid_places_count', len(places))} <span style="font-size:1.1rem; font-weight:600;">곳</span></div>
            <div class="stat-sub">실제 방문객 찐후기 기반 추천 매장</div>
        </div>
        """, unsafe_allow_html=True)

    # 2) AI 상권 요약 브리핑 카드
    if area_briefing:
        st.markdown(f"""
        <div class="briefing-box">
            <div class="briefing-title">💡 로컬레이더 AI 상권 브리핑</div>
            <div class="briefing-text">{area_briefing}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3) 상황별 베스트 Pick TOP 3 (1위 카드 강조 & 액션 버튼)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 🏆 에디터 추천 베스트 Pick TOP 3")
    st.caption("선택하신 방문 목적과 취향 조건에 가장 부합하는 상위 3곳의 핵심 정보입니다.")

    if top_picks:
        pick_cols = st.columns(min(len(top_picks), 3))
        for idx, pick in enumerate(top_picks[:3]):
            with pick_cols[idx]:
                pick_name = pick.get("place_name", "가게명").strip()
                pick_map_url = build_naver_map_url(current_reg, pick_name)
                is_first = (idx == 0)
                card_class = "best-card best-card-first" if is_first else "best-card"
                badge_class = "ribbon-badge" if is_first else "normal-badge"
                badge_text = pick.get('badge', '✨ 추천')

                st.markdown(f"""
                <div class="{card_class}">
                    <div>
                        <div class="{badge_class}">{badge_text}</div>
                        <div class="best-place-title">{pick_name}</div>
                        <div class="best-menu-box">🍴 <b>대표 메뉴</b> : {pick.get('signature_menu', '정보 없음')}</div>
                        <div class="best-reason">💡 <b>선정 이유</b><br>{pick.get('reason', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("📍 네이버 지도에서 바로 확인", pick_map_url, use_container_width=True)
    else:
        st.info("선정된 상위 추천 장소가 없습니다.")

    # 4) 전체 가게 스펙 비교표 및 실시간 태그 필터링
    st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 전체 로컬 플레이스 스펙 비교표")
    if places:
        all_tags = set()
        for p in places:
            p_tags = p.get("tags", [])
            if isinstance(p_tags, list):
                for t in p_tags:
                    if t and t.startswith("#"):
                        all_tags.add(t)

        sorted_tags = sorted(list(all_tags))

        selected_tags = []
        if sorted_tags:
            st.markdown("🏷️ **특징 태그 칩으로 빠른 필터링**")
            if hasattr(st, "pills"):
                selected_tags = st.pills("원하는 태그를 선택하세요", options=sorted_tags, selection_mode="multi", label_visibility="collapsed")
            else:
                selected_tags = st.multiselect("원하는 태그를 선택하세요", options=sorted_tags)

        df_data = []
        for p in places:
            p_tags = p.get("tags", []) if isinstance(p.get("tags"), list) else []
            tags_str = " ".join(p_tags) if p_tags else str(p.get("tags", ""))

            if selected_tags:
                if not any(sel in p_tags for sel in selected_tags):
                    continue

            p_name = p.get("place_name", "").strip()
            map_url = build_naver_map_url(current_reg, p_name)

            df_data.append({
                "가게명": p_name,
                "지도 위치": map_url,
                "대표 메뉴": p.get("signature_menu", "정보 없음"),
                "웨이팅 정보": p.get("waiting_info", "정보 없음"),
                "주차 정보": p.get("parking_info", "정보 없음"),
                "핵심 장점": p.get("pros", ""),
                "아쉬운 점 (단점)": p.get("cons", ""),
                "특징 태그": tags_str,
                "후기 원문": p.get("source_url", "")
            })

        if df_data:
            df = pd.DataFrame(df_data)

            col_btn, _ = st.columns([1, 4])
            with col_btn:
                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 비교표 CSV 다운로드",
                    data=csv,
                    file_name=f"local_radar_{current_reg}_{place_type}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "가게명": st.column_config.TextColumn("가게명", width="medium"),
                    "지도 위치": st.column_config.LinkColumn("지도 위치", display_text="지도 보기", width="small"),
                    "대표 메뉴": st.column_config.TextColumn("대표 메뉴", width="small"),
                    "웨이팅 정보": st.column_config.TextColumn("웨이팅 정보", width="medium"),
                    "주차 정보": st.column_config.TextColumn("주차 정보", width="medium"),
                    "핵심 장점": st.column_config.TextColumn("핵심 장점", width="large"),
                    "아쉬운 점 (단점)": st.column_config.TextColumn("아쉬운 점 (단점)", width="large"),
                    "특징 태그": st.column_config.TextColumn("특징 태그", width="medium"),
                    "후기 원문": st.column_config.LinkColumn("후기 원문", display_text="원문 보러가기", width="small")
                }
            )
        else:
            st.info("선택하신 태그에 해당하는 매장이 없습니다. 다른 태그를 선택해 보세요.")
    else:
        st.info("표시할 가게 정보가 없습니다.")

else:
    # ----------------------------------------------------
    # 랜딩 뷰: 🔥 요즘 뜨는 전국 핫플 TOP 10 매거진 큐레이션
    # ----------------------------------------------------
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔥 요즘 뜨는 전국 핫플 TOP 10 빠른 스캔")
    st.caption("궁금한 핫플레이스를 클릭하면 네이버 블로그 찐후기 크롤링 및 AI 분석이 즉시 시작됩니다.")

    row1 = HOTSPOTS[:5]
    row2 = HOTSPOTS[5:]

    cols1 = st.columns(5)
    for idx, spot in enumerate(row1):
        with cols1[idx]:
            st.markdown(f"""
            <div class="hotspot-card">
                <div>
                    <span class="hotspot-badge">{spot['category']}</span>
                    <div class="hotspot-name">📍 {spot['name']}</div>
                    <div class="hotspot-desc">{spot['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📡 바로 스캔", key=f"btn_spot_{idx}", use_container_width=True):
                st.session_state["pending_region"] = spot["name"]
                st.session_state["trigger_scan"] = True
                st.rerun()

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    cols2 = st.columns(5)
    for idx, spot in enumerate(row2):
        with cols2[idx]:
            st.markdown(f"""
            <div class="hotspot-card">
                <div>
                    <span class="hotspot-badge">{spot['category']}</span>
                    <div class="hotspot-name">📍 {spot['name']}</div>
                    <div class="hotspot-desc">{spot['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📡 바로 스캔", key=f"btn_spot_{idx+5}", use_container_width=True):
                st.session_state["pending_region"] = spot["name"]
                st.session_state["trigger_scan"] = True
                st.rerun()

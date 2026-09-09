import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import pytz

# 페이지 기본 설정
st.set_page_config(
    page_title="박스오피스 조회 앱",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. API 데이터 호출 함수 (캐시 적용)
# -----------------------------------------------------------------------------
# ttl=3600: 선택한 날짜에 대해 1시간 동안 API를 다시 부르지 않고 캐시된 데이터를 사용합니다.
@st.cache_data(ttl=3600)
def fetch_daily_box_office(api_key: str, target_date: str):
    """
    KOBIS API를 호출하여 해당 날짜의 일별 박스오피스 데이터를 가져오는 함수
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        # API 요청 (타임아웃 10초)
        response = requests.get(url, params=params, timeout=10)
        
        # HTTP 상태 코드가 200이 아닌 경우
        if response.status_code != 200:
            return None, f"서버 통신 실패 (HTTP 상태 코드: {response.status_code})"
            
        data = response.json()
        
        # API 응답 내 faultInfo(인증 오류 등)가 있는 경우
        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 오류가 발생했습니다.")
            return None, f"API 오류 발생: {message}"
            
        # 박스오피스 리스트 추출
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])
        
        # 영화 목록이 비어 있는 경우
        if not daily_list:
            return None, "그날은 아직 집계 전입니다."
            
        return daily_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 요청 중 에러가 발생했습니다: {e}"
    except Exception as e:
        return None, f"데이터 처리 중 에러가 발생했습니다: {e}"


# -----------------------------------------------------------------------------
# 2. 날짜 선택 및 API 키 설정
# -----------------------------------------------------------------------------
# 한국 시간 기준 '어제' 날짜 계산 (선택 가능한 최신 날짜)
seoul_tz = pytz.timezone("Asia/Seoul")
now_korea = datetime.datetime.now(seoul_tz)
yesterday = (now_korea - datetime.timedelta(days=1)).date()

# 사이드바에서 조회할 날짜를 달력으로 선택 (최대 날짜는 '어제')
st.sidebar.header("🗓️ 날짜 선택")
selected_date = st.sidebar.date_input(
    label="조회할 날짜를 골라주세요",
    value=yesterday,
    max_value=yesterday,
    min_value=datetime.date(2004, 1, 1)  # KOBIS 제공 최소 연도 기준
)

# API 요청용 날짜 문자열 (YYYYMMDD)
target_dt_str = selected_date.strftime("%Y%m%d")
# 화면 표시용 날짜 문자열
formatted_date_str = selected_date.strftime("%Y년 %m월 %d일")

# Streamlit Secrets에서 API 키 불러오기
api_key = st.secrets.get("KOBIS_KEY")

# -----------------------------------------------------------------------------
# 3. 메인 UI 화면 구성 및 데이터 불러오기
# -----------------------------------------------------------------------------
st.title("🎬 일별 박스오피스")
st.subheader(f"📅 조회 기준일: {formatted_date_str}")

# Secrets에 KOBIS_KEY가 없으면 안내 후 중단
if not api_key:
    st.error("⚠️ Secrets에 'KOBIS_KEY'가 설정되어 있지 않습니다.")
    st.info("""
    **확인 방법:**
    1. 로컬 실행 시: `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = "발급받은키"`를 입력했는지 확인하세요.
    2. Streamlit Cloud 배포 시: App Settings -> Secrets 메뉴에서 `KOBIS_KEY`를 추가해 주세요.
    """)
    st.stop()

# API 데이터 불러오기
with st.spinner("박스오피스 데이터를 가져오는 중입니다..."):
    raw_data, error_message = fetch_daily_box_office(api_key, target_dt_str)

# 데이터 호출 실패 또는 오류/목록 없음 처리
if error_message:
    # 영화 목록이 비어 있는 특수한 상황("그날은 아직 집계 전입니다.")
    if error_message == "그날은 아직 집계 전입니다.":
        st.info(f"ℹ️ {error_message}")
    else:
        st.error(f"❌ 데이터를 불러올 수 없습니다.\n\n**오류 내용:** {error_message}")
        st.warning("""
        💡 **확인해 보세요:**
        - Secrets에 입력한 **KOBIS_KEY**가 올바른지 확인해 주세요.
        - KOBIS 홈페이지에서 키 발급 상태를 확인해 주세요.
        - 네트워크 연결 상태를 확인해 주세요.
        """)
    st.stop()

# -----------------------------------------------------------------------------
# 4. 데이터 가공 (문자열 -> 숫자 변환 및 텍스트 가공)
# -----------------------------------------------------------------------------
df = pd.DataFrame(raw_data)

# 숫자 변환 대상 컬럼
numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 순위(rank) 기준으로 정렬
df = df.sort_values(by="rank").reset_index(drop=True)

# 1. 누적관객 100만 명 이상 영화명 옆에 트로피 이모지(🏆) 추가
def format_movie_name(row):
    name = row["movieNm"]
    if row["audiAcc"] >= 1_000_000:
        return f"{name} 🏆"
    return name

df["display_movieNm"] = df.apply(format_movie_name, axis=1)

# 2. 순위 증감(rankInten) 화살표 가공 함수 (양수: 🔺 red, 음수: 🔻 blue)
def format_rank_change(val):
    if val > 0:
        return f"🔺 {int(val)}"
    elif val < 0:
        return f"🔻 {int(abs(val))}"
    else:
        return "-"

df["rank_change"] = df["rankInten"].apply(format_rank_change)

# -----------------------------------------------------------------------------
# 5. 1위 영화 지표 카드 (Metric)
# -----------------------------------------------------------------------------
if not df.empty:
    top_1 = df.iloc[0]
    st.markdown("---")
    st.markdown(f"### 🥇 1위 영화: **{top_1['display_movieNm']}**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("일일 관객수", f"{top_1['audiCnt']:,} 명")
    with col2:
        st.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
    with col3:
        st.metric("스크린수", f"{top_1['scrnCnt']:,} 개")
    st.markdown("---")

# -----------------------------------------------------------------------------
# 6. 상위 5개 영화 일일 관객수 막대그래프
# -----------------------------------------------------------------------------
st.write("### 📊 관객수 상위 5개 영화")
top_5_df = df.head(5).copy()

fig = px.bar(
    top_5_df,
    x="display_movieNm",
    y="audiCnt",
    text="audiCnt",
    labels={"display_movieNm": "영화명", "audiCnt": "일일 관객수(명)"},
    title="상위 5위 관객수 비교"
)
fig.update_traces(texttemplate="%{text:,}명", textposition="outside")
fig.update_layout(xaxis_title="", yaxis_title="관객수", height=400)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. 전체 박스오피스 순위표 (Table)
# -----------------------------------------------------------------------------
st.write("### 📋 박스오피스 전체 순위")

# 표출용 DataFrame 구성
display_df = df[["rank", "rank_change", "display_movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "순위증감", "영화명", "개봉일", "일일 관객수", "누적 관객수", "스크린수"]

# 순위 증감 컬럼 색상 지정을 위한 스타일 함수
def color_rank_change(val):
    if "🔺" in str(val):
        return "color: red; font-weight: bold;"
    elif "🔻" in str(val):
        return "color: blue; font-weight: bold;"
    return ""

# 데이터프레임 스타일 적용 및 포맷팅
styled_df = display_df.style.map(color_rank_change, subset=["순위증감"]).format({
    "순위": "{:}위",
    "일일 관객수": "{:,.0f}명",
    "누적 관객수": "{:,.0f}명",
    "스크린수": "{:,.0f}개"
})

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)

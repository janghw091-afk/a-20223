import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import pytz

# Page configuration
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. API 데이터 호출 함수 (캐시 적용)
# -----------------------------------------------------------------------------
# ttl=3600: 같은 날짜 데이터 요청 시 1시간(3600초) 동안 API를 다시 호출하지 않고 저장된 결과를 사용합니다.
@st.cache_data(ttl=3600)
def fetch_daily_box_office(api_key: str, target_date: str):
    """
    KOBIS API를 호출하여 일별 박스오피스 데이터를 가져오는 함수
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        # API 요청 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)
        
        # HTTP 상태 코드가 200이 아닌 경우 예외 발생
        if response.status_code != 200:
            return None, f"서버 통신 실패 (HTTP 상태 코드: {response.status_code})"
            
        data = response.json()
        
        # API 응답 내 faultInfo(인증 오류 등)가 있는지 확인
        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 오류가 발생했습니다.")
            return None, f"API 오류 발생: {message}"
            
        # 박스오피스 리스트 추출
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])
        
        # 목록이 비어있는 경우 처리
        if not daily_list:
            return None, "해당 날짜의 박스오피스 데이터가 비어 있습니다."
            
        return daily_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 요청 중 에러가 발생했습니다: {e}"
    except Exception as e:
        return None, f"데이터 처리 중 에러가 발생했습니다: {e}"


# -----------------------------------------------------------------------------
# 2. 날짜 및 API 키 설정
# -----------------------------------------------------------------------------
# 배포 서버 시계와 상관없이 한국 시간(Asia/Seoul) 기준 '어제' 날짜 계산
seoul_tz = pytz.timezone("Asia/Seoul")
now_korea = datetime.datetime.now(seoul_tz)
yesterday = now_korea - datetime.timedelta(days=1)
target_dt_str = yesterday.strftime("%Y%m%d")      # API 요청용 (예: 20260908)
formatted_date_str = yesterday.strftime("%Y년 %m월 %d일") # 화면 표시용

# Streamlit Secrets에서 API 키 불러오기
api_key = st.secrets.get("KOBIS_KEY")

# -----------------------------------------------------------------------------
# 3. 메인 UI 화면 구성
# -----------------------------------------------------------------------------
st.title("🎬 어제의 박스오피스")
st.subheader(f"📅 기준일: {formatted_date_str} (한국 시간 기준)")

# API 키가 secrets.toml에 설정되어 있지 않은 경우 예외 처리
if not api_key:
    st.error("⚠️ Secrets에 'KOBIS_KEY'가 설정되어 있지 않습니다.")
    st.info("""
    **확인 방법:**
    1. 로컬 실행 시: `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = "발급받은키"`를 입력했는지 확인하세요.
    2. Streamlit Cloud 배포 시: App Settings -> Secrets 메뉴에서 `KOBIS_KEY`를 추가해 주세요.
    """)
    st.stop()

# 데이터 불러오기 실행
with st.spinner("박스오피스 데이터를 가져오는 중입니다..."):
    raw_data, error_message = fetch_daily_box_office(api_key, target_dt_str)

# 데이터 호출에 실패하거나 오류가 발생한 경우 안내 메시지 출력
if error_message:
    st.error(f"❌ 데이터를 불러올 수 없습니다.\n\n**오류 내용:** {error_message}")
    st.warning("""
    💡 **확인해 보세요:**
    - Secrets에 입력한 **KOBIS_KEY**가 올바른지 확인해 주세요.
    - KOBIS 홈페이지에서 일일 데이터 제공 시간 및 키 발급 상태를 확인해 주세요.
    - 네트워크 연결 상태를 확인해 주세요.
    """)
    st.stop()

# -----------------------------------------------------------------------------
# 4. 데이터 가공 (문자열 -> 숫자 변환)
# -----------------------------------------------------------------------------
df = pd.DataFrame(raw_data)

# API 응답값이 모두 문자열이므로 수치형 데이터로 변환
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 순위(rank) 기준으로 정렬
df = df.sort_values(by="rank").reset_index(drop=True)

# -----------------------------------------------------------------------------
# 5. 1위 영화 지표 카드 (Metric)
# -----------------------------------------------------------------------------
if not df.empty:
    top_1 = df.iloc[0]
    st.markdown("---")
    st.markdown(f"### 🥇 어제 1위 영화: **{top_1['movieNm']}**")
    
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

# 막대그래프 생성 (Plotly)
fig = px.bar(
    top_5_df,
    x="movieNm",
    y="audiCnt",
    text="audiCnt",
    labels={"movieNm": "영화명", "audiCnt": "일일 관객수(명)"},
    title="상위 5위 관객수 비교"
)
# 그래프 내부 텍스트 콤마 규격 적용 및 레이아웃 설정
fig.update_traces(texttemplate="%{text:,}명", textposition="outside")
fig.update_layout(xaxis_title="", yaxis_title="관객수", height=400)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. 전체 박스오피스 순위표 (Table)
# -----------------------------------------------------------------------------
st.write("### 📋 박스오피스 전체 순위")

# 표에 출력할 컬럼명 변경 및 정리
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "일일 관객수", "누적 관객수", "스크린수"]

# 숫자 포맷 지정 (천 단위 쉼표 추가)
st.dataframe(
    display_df.style.format({
        "순위": "{:}위",
        "일일 관객수": "{:,.0f}명",
        "누적 관객수": "{:,.0f}명",
        "스크린수": "{:,.0f}개"
    }),
    use_container_width=True,
    hide_index=True
)

import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (타이틀 및 레이아웃)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 KOBIS 박스오피스 데이터 분석")


# -------------------------------------------------------------------
# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 캐싱(저장)합니다.
# 앱이 새로고침되어도 매번 재다운로드하지 않아 속도가 빨라집니다.
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(값이 없는 데이터)가 있는 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 기준일자 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드
df = load_data()


# -------------------------------------------------------------------
# [3. 영화 선택 기능]
# 누적관객수가 높은 순서대로 중복 없는 영화 목록을 만듭니다.
# -------------------------------------------------------------------
# 영화별 최대 누적관객수를 구해 내림차순 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"].max().sort_values(ascending=False).index
)

st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox("영화 선택", movie_order)


# -------------------------------------------------------------------
# [4. 구역 분할 및 선그래프 그리기]
# 앞으로 다른 그래프를 추가하기 쉽도록 구역(Container)을 나눕니다.
# -------------------------------------------------------------------
# 구역 1: 일별 관객수 변화 그래프
with st.container():
    st.subheader(f"📊 [{selected_movie}] 일별 관객수 추이")

    # 선택된 영화의 데이터만 필터링
    movie_df = df[df["영화명"] == selected_movie]

    # Plotly 선그래프 생성
    fig = px.line(
        movie_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 기준일자별 해당일관객수",
        labels={"기준일자": "날짜", "해당일관객수": "일일 관객수"},
        markers=True,  # 데이터 지점에 점 표시
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # [5. 기타] 알 수 있는 것 문구 자리
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

st.divider()  # 구역 구분을 위한 구분선

# 구역 2: 추후 추가될 그래프를 위한 공간
with st.container():
    st.subheader("📈 추가 분석 그래프 (예정)")
    st.caption("여기에 새로운 차트나 분석 항목을 계속 추가할 수 있습니다.")

    # 추가 그래프 예시 문구 자리
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

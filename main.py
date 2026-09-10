import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (타이틀 및 넓은 레이아웃 적용)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 KOBIS 박스오피스 데이터 분석")


# -------------------------------------------------------------------
# [1. 데이터 불러오기]
# @st.cache_data 데코레이터: 불러온 데이터를 메모리에 저장해두어
# 새로고침할 때마다 다시 다운로드하지 않고 빠르게 앱을 실행합니다.
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 값)가 포함된 행을 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 문자열에서 datetime(날짜) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 기준일자 오름차순(과거->최근)으로 데이터 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로딩 실행
df = load_data()


# -------------------------------------------------------------------
# [3. 영화 선택 기능]
# 중복 없는 영화 이름 목록을 만들고, 누적관객수가 높은 순서대로 정렬합니다.
# -------------------------------------------------------------------
# 영화별 maximum 누적관객수를 구해 내림차순 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"].max().sort_values(ascending=False).index
)

st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox("영화 선택", movie_order)

# 사용자가 사이드바에서 선택한 영화의 데이터만 추출
movie_df = df[df["영화명"] == selected_movie]


# -------------------------------------------------------------------
# [4. 구역 1: 일별 관객수 변화 (선 그래프 - px.line)]
# -------------------------------------------------------------------
with st.container():
    st.subheader(f"📊 [{selected_movie}] 일별 관객수 추이")

    # Plotly 선 그래프 생성
    fig_line = px.line(
        movie_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 기준일자별 해당일관객수",
        labels={"기준일자": "날짜", "해당일관객수": "일일 관객수"},
        markers=True,  # 데이터 위치에 점 표시
    )

    # 스트림릿에 그래프 표시
    st.plotly_chart(fig_line, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

# 구역 구분을 위한 구분선
st.divider()


# -------------------------------------------------------------------
# [5. 구역 2: 누적 관객수 변화 (영역 차트 - px.area)]
# -------------------------------------------------------------------
with st.container():
    st.subheader(f"📈 [{selected_movie}] 누적 관객수 성장 추이 (영역 차트)")

    # Plotly 영역 차트 생성 (px.area)
    fig_area = px.area(
        movie_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}'의 기준일자별 누적관객수",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수"},
    )

    # 스트림릿에 영역 차트 표시
    st.plotly_chart(fig_area, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

st.divider()


# -------------------------------------------------------------------
# [6. 구역 3: 누적관객수 TOP 5 영화 비교 (다중 선 그래프)]
# -------------------------------------------------------------------
with st.container():
    st.subheader("🏆 누적관객수 TOP 5 영화 비교 (다중 선 그래프)")

    # 1. 전체 데이터에서 누적관객수가 가장 높은 상위 5개 영화명 추출
    top5_movies = movie_order[:5]

    # 2. 상위 5개 영화에 해당하는 데이터만 필터링
    top5_df = df[df["영화명"].isin(top5_movies)]

    # 3. 다중 선 그래프 생성 (color="영화명"을 주어 영화별 색상 및 범례 분리)
    fig_multi_line = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="누적관객수 상위 5개 영화의 기준일자별 누적관객수 추이 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수", "영화명": "영화 제목"},
    )

    # 스트림릿에 다중 선 그래프 표시
    st.plotly_chart(fig_multi_line, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# [6. 구역 3: 20일 이상 상위권 유지 영화 중 TOP 5 비교 (다중 선 그래프)]
# -------------------------------------------------------------------
with st.container():
    st.subheader("🏆 TOP 10 유지 20일 이상 영화 중 누적관객수 TOP 5 비교")

    # 1. 영화별 TOP 10 차트 등재 일수(행 수) 집계
    movie_counts = df.groupby("영화명")["기준일자"].count()

    # 2. 등장 일수가 20일 이상인 영화 목록 추출
    long_running_movies = movie_counts[movie_counts >= 20].index

    # 3. 20일 이상 등장한 영화들만 필터링한 데이터셋 생성
    filtered_df = df[df["영화명"].isin(long_running_movies)]

    # 4. 해당 영화들 중 최대 누적관객수 기준으로 상위 5개 영화명 선택
    top5_long_running = (
        filtered_df.groupby("영화명")["누적관객수"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    # 5. 상위 5개 영화의 데이터만 필터링
    top5_df = filtered_df[filtered_df["영화명"].isin(top5_long_running)]

    # 6. 다중 선 그래프 생성 (color="영화명"으로 각 영화별 색상 및 범례 표기)
    fig_multi_line = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 등재 영화 중 누적관객수 상위 5개 영화의 누적관객수 추이",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수", "영화명": "영화 제목"},
    )

    # 스트림릿에 다중 선 그래프 표시
    st.plotly_chart(fig_multi_line, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

st.divider()


# -------------------------------------------------------------------
# [7. 구역 4: 전체 박스오피스 총 관객수 및 7일 이동평균선 (Plotly go)]
# -------------------------------------------------------------------
with st.container():
    st.subheader("📉 전체 박스오피스 일일 총 관객수 및 7일 이동평균선")

    # 1. 기준일자별 TOP10 영화의 해당일관객수 총합 계산
    daily_total = df.groupby("기준일자")["해당일관객수"].sum().reset_index()

    # 2. 7일 이동평균선 컬럼 생성 (rolling window 사용)
    daily_total["7일_이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7).mean()
    )

    # 3. 커스텀 그래픽을 위해 plotly.graph_objects 사용
    fig_ma = go.Figure()

    # 원본 일일 총 관객수 선 (연하게 표시)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일일 총 관객수 (원본)",
            line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
        )
    )

    # 7일 이동평균선 (진하게 표시)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#FF4B4B", width=3),
        )
    )

    # 레이아웃 옵션 설정
    fig_ma.update_layout(
        title="기준일자별 TOP10 전체 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="총 관객수",
        hovermode="x unified",
    )

    # 스트림릿에 이동평균선 그래프 표시
    st.plotly_chart(fig_ma, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

st.divider()


# -------------------------------------------------------------------
# [8. 구역 5: 전체 박스오피스 월별 관객수 합계 (막대 그래프 - px.bar)]
# -------------------------------------------------------------------
with st.container():
    st.subheader("📅 전체 박스오피스 월별 총 관객수 (막대 그래프)")

    # 1. daily_total 데이터프레임을 연-월(YYYY-MM) 단위로 재그룹화하여 합산
    daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

    # 연월 기준으로 관객수 총합 계산
    monthly_total = (
        daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
    )

    # 2. Plotly 막대 그래프 생성 (px.bar)
    fig_bar = px.bar(
        monthly_total,
        x="연월",
        y="해당일관객수",
        title="연-월별 TOP10 전체 관객수 합계",
        labels={"연월": "연월 (YYYY-MM)", "해당일관객수": "월간 총 관객수"},
        text_auto=".2s",
    )

    # 막대 디자인 커스텀
    fig_bar.update_traces(
        marker_color="#2E86C1",
        textposition="outside",
    )

    # 스트림릿에 막대 그래프 표시
    st.plotly_chart(fig_bar, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

st.divider()


# -------------------------------------------------------------------
# [9. 구역 6: 월(주차) × 요일별 캘린더 히트맵 (px.density_heatmap)]
# -------------------------------------------------------------------
with st.container():
    st.subheader("🗓️ 월(주차) × 요일별 관객수 분포 (캘린더 히트맵)")

    # 1. 캘린더 피처 생성 (월-주차, 요일)
    # dt.floor('MS')를 사용하여 해당 월의 첫 날 날짜를 구하고 주차를 계산합니다.
    first_day_of_month_weekday = daily_total["기준일자"].dt.floor("MS").dt.weekday

    daily_total["월_주차"] = (
        daily_total["기준일자"].dt.strftime("%Y-%m")
        + " "
        + (
            (daily_total["기준일자"].dt.day + first_day_of_month_weekday) // 7
            + 1
        ).astype(str)
        + "주차"
    )

    # 요일 이름 컬럼 생성 (월요일 ~ 일요일)
    weekday_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    daily_total["요일_코드"] = daily_total["기준일자"].dt.weekday
    daily_total["요일"] = daily_total["요일_코드"].apply(
        lambda x: weekday_kr[x]
    )

    # 날짜를 yyyy-mm-dd 형태의 문자열로 저장 (마우스 호버 툴팁용)
    daily_total["날짜_str"] = daily_total["기준일자"].dt.strftime("%Y-%m-%d")

    # 2. 히트맵 생성 (x축: 요일, y축: 월_주차, z: 관객수 합계)
    fig_heatmap = px.density_heatmap(
        daily_total,
        x="요일",
        y="월_주차",
        z="해당일관객수",
        histfunc="sum",
        title="월(주차) 및 요일별 일일 관객수 히트맵",
        labels={
            "요일": "요일",
            "월_주차": "월 및 주차",
            "해당일관객수": "일일 총 관객수",
        },
        category_orders={"요일": weekday_kr},  # 요일을 월~일 순서로 고정
        color_continuous_scale="Reds",  # 관객수가 많을수록 진한 빨간색
        hover_data={
            "날짜_str": True,  # yyyy-mm-dd 날짜 표기
            "요일": True,
            "월_주차": True,
            "해당일관객수": ":,d",  # 천 단위 쉼표 서식
        },
    )

    # 툴팁 레이블 수정
    fig_heatmap.update_traces(
        hovertemplate=(
            "<b>날짜: %{customdata[0]}</b><br>"
            "요일: %{x}<br>"
            "주차: %{y}<br>"
            "총 관객수: %{z:,}명<extra></extra>"
        )
    )

    # 레이아웃 조절 (y축을 위에서 아래로 순차 배치)
    fig_heatmap.update_layout(yaxis=dict(autorange="reverse"))

    # 스트림릿에 히트맵 표시
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # 알 수 있는 것 문구 작성 공간
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 분석 내용을 작성하세요.)")

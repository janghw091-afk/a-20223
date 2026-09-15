import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre: 세로막대 기호(|)로 여러 개 적힌 경우 첫 번째 장르만 추출
    if 'genre' in df.columns:
        df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if x and x != 'nan' else '기타')
        
    return df

df = load_data()

# 앱 제목 및 데이터 소개
st.title("🎬 영화 데이터 - 분포와 관계")
st.markdown("박스오피스 10위권에 진입했던 주요 영화 216편의 데이터 분석 및 시각화 앱입니다.")

st.divider()

# -----------------------------------------------------------------------------
# 1. 장르별 영화 편수 분포 (도넛 그래프)
# -----------------------------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화 수']

# 플롯리 도넛 그래프 생성
fig_donut = px.pie(
    genre_counts, 
    values='영화 수', 
    names='장르',
    hole=0.4,
    title='장르별 영화 편수 비중',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# 마우스 호버시 편수와 비율 표기 설정
fig_donut.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}'
)

fig_donut.update_layout(
    margin=dict(t=50, b=20, l=20, r=20),
    legend_title_text='장르'
)

# 그래프 출력
st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 설명 박스 구역
with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 영화 중 특정 주요 장르(예: 드라마, 액션 등)의 비중이 과반 이상을 차지하며, 극장에 걸리는 흥행권 영화들의 장르 쏠림 현상과 최선호 장르 구성을 한눈에 파악할 수 있습니다.")

st.divider()

# -----------------------------------------------------------------------------
# 2. 주요 변수 간 관계 분석 (산점도 그래프)
# -----------------------------------------------------------------------------
st.header("2. 개봉 첫 주 관객과 총 관객 수의 관계")

if 'first_week_audi' in df.columns and 'total_audi' in df.columns:
    fig_scatter = px.scatter(
        df,
        x='first_week_audi',
        y='total_audi',
        color='genre',
        hover_data=['movieNm'],
        title='개봉 첫 주 관객 vs 총 관객 수',
        labels={'first_week_audi': '개봉 첫 주 관객 수', 'total_audi': '총 관객 수', 'genre': '장르'},
        opacity=0.8
    )
    fig_scatter.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.container():
        st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객 수가 많을수록 최종 총 관객 수 역시 비례하여 증가하는 강한 양의 상관관계를 보이며, 초기 흥행 여세가 최종 실적을 크게 좌우함을 알 수 있습니다.")

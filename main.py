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
    
    # genre: 세로막대 기호(|)로 분리된 장르 중 첫 번째 장르만 추출
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
# 2. 장르 및 영화별 총 관객 수 분포 (트리맵 그래프)
# -----------------------------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객 수 분포")

# 플롯리 트리맵 그래프 생성 (계층: 전체 장르 -> 장르 -> 영화명, 크기: 총 관객 수)
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), 'genre', 'movieNm'],
    values='total_audi',
    title='장르 및 영화별 총 관객 수 (칸 크기: 총 관객 수)',
    color='genre',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# 마우스 호버시 영화명/장르 및 총 관객 수 표기
fig_treemap.update_traces(
    hovertemplate='<b>영화/그룹:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명'
)

fig_treemap.update_layout(
    margin=dict(t=50, b=20, l=20, r=20)
)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 설명 박스 구역
with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 장르 내에서도 어떤 영화가 흥행을 주도했는지 한눈에 비교할 수 있으며, 전체 총 관객 수에서 각 영화와 장르가 차지하는 상대적 기여도 및 비중을 파악할 수 있습니다.")

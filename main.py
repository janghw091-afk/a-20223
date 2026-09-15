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

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화 수']

fig_donut = px.pie(
    genre_counts, 
    values='영화 수', 
    names='장르',
    hole=0.4,
    title='장르별 영화 편수 비중',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_donut.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}'
)

fig_donut.update_layout(
    margin=dict(t=50, b=20, l=20, r=20),
    legend_title_text='장르'
)

st.plotly_chart(fig_donut, use_container_width=True)

with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 영화 중 특정 주요 장르(예: 드라마, 액션 등)의 비중이 과반 이상을 차지하며, 극장에 걸리는 흥행권 영화들의 장르 쏠림 현상과 최선호 장르 구성을 한눈에 파악할 수 있습니다.")

st.divider()

# -----------------------------------------------------------------------------
# 2. 장르 및 영화별 총 관객 수 분포 (트리맵 그래프)
# -----------------------------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객 수 분포")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), 'genre', 'movieNm'],
    values='total_audi',
    title='장르 및 영화별 총 관객 수 (칸 크기: 총 관객 수)',
    color='genre',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_treemap.update_traces(
    hovertemplate='<b>영화/그룹:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명'
)

fig_treemap.update_layout(
    margin=dict(t=50, b=20, l=20, r=20)
)

st.plotly_chart(fig_treemap, use_container_width=True)

with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 장르 내에서도 어떤 영화가 흥행을 주도했는지 한눈에 비교할 수 있으며, 전체 총 관객 수에서 각 영화와 장르가 차지하는 상대적 기여도 및 비중을 파악할 수 있습니다.")

st.divider()

# -----------------------------------------------------------------------------
# 3. 총 관객 수 분포 (히스토그램)
# -----------------------------------------------------------------------------
st.header("3. 총 관객 수 분포")

# 히스토그램 생성
fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title='총 관객 수(total_audi) 히스토그램',
    labels={'total_audi': '총 관객 수 (명)', 'count': '영화 수'},
    color_discrete_sequence=['#4C78A8']
)

fig_hist.update_traces(
    hovertemplate='<b>관객 수 구간:</b> %{x}<br><b>영화 수:</b> %{y}편'
)

fig_hist.update_layout(
    yaxis_title="영화 수",
    margin=dict(t=50, b=20, l=20, r=20)
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 관객 수 많은 영화 데이터 자동 추출
top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

# 그래프 설명 및 분석 결과 표기
with st.container():
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 관객 수가 상대적으로 낮은 구간(약 100만~200만 명 이하)에 빽빽하게 집중되어 있는 반면, 대형 흥행작은 극소수에 불과함을 알 수 있습니다. 참고로 가장 관객이 많은 영화는 **'{top_movie_name}'** (총 {top_movie_audi:,.0f}명)입니다.")

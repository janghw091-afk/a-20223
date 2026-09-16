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

top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

with st.container():
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 관객 수가 상대적으로 낮은 하위 구간(약 100만~200만 명 이하)에 빽빽하게 밀집되어 있는 반면, 대형 흥행작은 극소수에 불과합니다. 참고로 이번 데이터셋에서 가장 관객 수가 많은 영화는 **'{top_movie_name}'** (총 {top_movie_audi:,.0f}명)입니다.")

st.divider()

# -----------------------------------------------------------------------------
# 4. 개봉일 스크린수와 총 관객 수의 관계 (산점도)
# -----------------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객 수의 관계")

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    hover_data={'first_scrn': ':,', 'total_audi': ':,', 'genre': True},
    title='개봉일 스크린수(first_scrn) vs 총 관객 수(total_audi)',
    labels={
        'first_scrn': '개봉일 스크린수 (개)',
        'total_audi': '총 관객 수 (명)',
        'genre': '장르'
    },
    opacity=0.8,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_scatter.update_traces(
    marker=dict(size=9),
    hovertemplate='<b>%{hovertext}</b><br>장르: %{customdata[0]}<br>개봉일 스크린수: %{x:,}개<br>총 관객 수: %{y:,}명'
)

fig_scatter.update_layout(
    margin=dict(t=50, b=20, l=20, r=20),
    legend_title_text='장르'
)

st.plotly_chart(fig_scatter, use_container_width=True)

with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수가 확보될수록 최종 총 관객 수도 증가하는 대체적인 우상향 경향성을 보이며, 초기의 상영관 확보(스크린수)가 흥행 성공에 유리한 고지를 점하는 데 중요한 요소임을 알 수 있습니다.")

st.divider()

# -----------------------------------------------------------------------------
# 5. 주요 장르별 총 관객 수 분포 (박스플롯)
# -----------------------------------------------------------------------------
st.header("5. 주요 장르별 총 관객 수 분포 (10편 이상 장르)")

# 영화 수 10편 이상인 장르만 필터링
genre_counts_series = df['genre'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df['genre'].isin(major_genres)]

# 박스플롯 생성 (이상치 점에 영화명 표기)
fig_box = px.box(
    df_filtered,
    x='genre',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    hover_data={'total_audi': ':,', 'genre': False},
    points='outliers',
    title='10편 이상 개봉 장르별 총 관객 수(total_audi) 상자 그림',
    labels={'genre': '장르', 'total_audi': '총 관객 수 (명)'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_box.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>총 관객 수: %{y:,}명'
)

fig_box.update_layout(
    showlegend=False,
    margin=dict(t=50, b=20, l=20, r=20)
)

st.plotly_chart(fig_box, use_container_width=True)

# 그래프 설명 박스 구역
with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 영화 편수가 많은 주요 장르 간의 관객 수 중위수와 편차를 한눈에 비교할 수 있으며, 상자 밖의 아웃라이어(이상치) 점들을 통해 일반적인 흥행 범주를 뛰어넘은 초대형 흥행작을 쉽게 식별할 수 있습니다.")

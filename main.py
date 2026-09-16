import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 최다 제작 영화 장르 분석",
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
        
    # nation 결측치 및 빈값 처리
    if 'nation' in df.columns:
        df['nation'] = df['nation'].fillna('기타').astype(str).str.strip()
        df['nation'] = df['nation'].apply(lambda x: '기타' if x == 'nan' or x == '' else x)
        
    return df

df = load_data()

st.title("🎬 상위 10개 제작 국가별 최다 제작 장르")
st.markdown("전체 영화 데이터 중 영화를 가장 많이 만든 상위 10개 국가와 각 국가에서 가장 많이 제작된 대표 장르를 보여줍니다.")

st.divider()

# -----------------------------------------------------------------------------
# 상위 10개 국가별 최다 제작 장르 추출 및 시각화
# -----------------------------------------------------------------------------

# 1. 영화를 가장 많이 만든 상위 10개 국가 추출
top10_nations = df['nation'].value_counts().head(10).index
df_top10 = df[df['nation'].isin(top10_nations)]

# 2. 각 국가별로 가장 많이 제작된 장르 1개씩만 추출
top_genre_per_nation = (
    df_top10.groupby(['nation', 'genre'])
    .size()
    .reset_index(name='편수')
    .sort_values(['nation', '편수'], ascending=[True, False])
    .groupby('nation')
    .head(1)
    .reset_index(drop=True)
)

# 3. 국가 순서를 전체 영화 제작 순위에 맞게 정렬
top_genre_per_nation['nation'] = pd.Categorical(top_genre_per_nation['nation'], categories=top10_nations, ordered=True)
top_genre_per_nation = top_genre_per_nation.sort_values('nation').reset_index(drop=True)

# 4. 가로 막대 그래프 생성 (막대 안에 장르 이름 표시)
fig = px.bar(
    top_genre_per_nation,
    x='편수',
    y='nation',
    color='genre',
    orientation='h',
    text='genre',
    title='상위 10개 영화 제작 국가별 최다 제작 장르 및 편수',
    labels={'nation': '제작 국가', '편수': '해당 장르 제작 편수 (개)', 'genre': '최다 제작 장르'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig.update_traces(
    textposition='auto',
    hovertemplate='<b>국가:</b> %{y}<br><b>최다 제작 장르:</b> %{text}<br><b>편수:</b> %{x}편'
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),  # 1위 국가가 상단에 위치하도록 정렬
    margin=dict(t=50, b=20, l=20, r=20),
    legend_title_text='장르'
)

st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.info("💡 **그래프 설명:** 상위 10개 국가별로 가장 많이 제작된 대표 장르 1개와 해당 장르의 제작 편수를 직관적으로 비교할 수 있습니다.")

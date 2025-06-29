# CSS 스타일 추가
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc
import pandas as pd

def add_custom_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px 10px 0px 0px;
        color: black;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.2);
        color: black;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.7), rgba(238, 90, 36, 0.7));
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 10px 0;
        color: black;
        text-align: center;
    }
    
    .ranking-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
        border: 1px solid #f39c12;
    }
    
    .gold { background: linear-gradient(135deg, #ffd700, #ffed4e); }
    .silver { background: linear-gradient(135deg, #c0c0c0, #e5e5e5); }
    .bronze { background: linear-gradient(135deg, #cd7f32, #daa520); }
    
    .trophy-icon {
        font-size: 2em;
        margin-right: 10px;
    }
    
    .medal-icon {
        font-size: 1.5em;
        margin-right: 8px;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: black;
        border-radius: 25px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

def create_gamified_ranking_plot(ranking_df, selected_country, column_name, title, x_label):
    """게임화된 랭킹 차트 생성"""
    
    # 상위 20개 국가 선택
    top_20_countries = ranking_df.head(20)
    
    # selected_country가 상위 20개에 있는지 확인
    selected_country_in_top20 = selected_country in top_20_countries['country'].values
    
    if not selected_country_in_top20:
        selected_country_data = ranking_df[ranking_df['country'] == selected_country]
        if not selected_country_data.empty:
            plot_data = pd.concat([top_20_countries, selected_country_data])
            plot_data = plot_data.reset_index(drop=True)
            selected_idx = plot_data[plot_data['country'] == selected_country].index[0]
            plot_data = pd.concat([plot_data.drop(selected_idx), plot_data.loc[selected_idx:selected_idx]]).reset_index(drop=True)
        else:
            plot_data = top_20_countries
    else:
        plot_data = top_20_countries
    
    plot_data = plot_data.sort_values(by=column_name, ascending=True)
    
    # 메달 색상 정의 (상위 3개에 메달 색상 적용)
    colors = []
    for i in range(len(plot_data)):
        if i == len(plot_data)-1:  # 1등(맨 위)
            colors.append('#FFD700')
        elif i == len(plot_data)-2:  # 2등
            colors.append('#C0C0C0')
        elif i == len(plot_data)-3:  # 3등
            colors.append('#CD7F32')
        elif plot_data.iloc[i]['country'] == selected_country:
            colors.append('#FF6B6B')
        else:
            colors.append('#87CEEB')
    
    # Plotly 차트 생성
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=plot_data['country'],
        x=plot_data[column_name],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1),
            pattern=dict(
                shape="",
                size=10,
                solidity=0.2
            )
        ),
        text=[f"{val:,.0f}" if column_name == 'total_runners' else f"{val:.2f}" for val in plot_data[column_name]],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>' +
                      f'{x_label}: %{{x:,.0f}}<br>' +
                      '<extra></extra>',
        name=''
    ))
    
    
    # 메달 아이콘도 인덱스 기준 len-1, len-2, len-3에 부여
    annotations = []
    for i, (idx, row) in enumerate(plot_data.iterrows()):
        if i == len(plot_data)-1:
            medal = '🥇'
        elif i == len(plot_data)-2:
            medal = '🥈'
        elif i == len(plot_data)-3:
            medal = '🥉'
        else:
            medal = None
        if medal:
            annotations.append(dict(
                x=row[column_name] * 0.05,
                y=row['country'],
                text=medal,
                showarrow=False,
                font=dict(size=20),
                xanchor='left',
                yanchor='middle'
            ))
        elif row['country'] == selected_country:
            annotations.append(dict(
                x=row[column_name] * 0.05,
                y=row['country'],
                text='🎯',
                showarrow=False,
                font=dict(size=20),
                xanchor='left',
                yanchor='middle'
            ))
    
    fig.update_layout(
        title=dict(
            text=f"🏆 {title}",
            font=dict(size=20, color='black'),
            x=0.1
        ),
        xaxis=dict(
            title=dict(text=x_label, font=dict(color='black')),
            tickfont=dict(color='black'),
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            tickfont=dict(color='black'),
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        showlegend=False,
        annotations=annotations,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_animated_metric_card(label, value, unit="", icon=""):
    """애니메이션 메트릭 카드 생성"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5em; margin-bottom: 10px;">{icon} {label}</div>
        <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 5px;">{value:,.0f} {unit}</div>
    </div>
    """, unsafe_allow_html=True)
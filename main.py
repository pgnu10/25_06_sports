import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'Malgun Gothic'
from src.preprocessor import preprocess_data
from src.design import add_custom_css, create_animated_metric_card, create_gamified_ranking_plot

def draw_dashboard():
    # CSS 스타일 적용
    add_custom_css()
    
    @st.cache_data
    def load_data(data):
        path = f'./data/processed/{data}.csv'
        if not os.path.exists(path):
            df = preprocess_data(data)
        else:
            df = pd.read_csv(path)
        return df
    
    # Streamlit 설정
    st.set_page_config(page_title="🏃‍♂️ Running Dashboard", layout="wide")
    st.title("🏃‍♂️ Running Dashboard")
    
    # 탭 구성
    TAB1, TAB2, TAB3 = st.tabs(["📊 전체 데이터 요약", "🧑‍🤝‍🧑 성별/연령대별 지표", "🏆 랭킹 대시보드"])
    
    with TAB1:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: black; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                📊 전체 데이터 요약
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        running_Y_M_stats = load_data('running_Y_M_stats')
        distance_duration_df = load_data('distance_duration_df')
        
        # 게임화된 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_animated_metric_card("총 러너 수", running_Y_M_stats['total_runners'].sum(), "명", "👥")
        with col2:
            create_animated_metric_card("평균 속도", running_Y_M_stats['speed_per_hour'].mean(), "km/h", "⚡")
        with col3:
            create_animated_metric_card("평균 거리", running_Y_M_stats['distance'].mean(), "km", "🏃")
        with col4:
            create_animated_metric_card("평균 시간", running_Y_M_stats['duration'].mean(), "분", "⏱️")
        
        col2, col3 = st.columns(2)
        with col2:
            crosstab_data = pd.crosstab(
                running_Y_M_stats['age_group'],
                running_Y_M_stats['gender'],
                values=running_Y_M_stats['total_runners'],
                aggfunc='sum'
            ).fillna(0).reset_index()

            # 데이터 melt로 변환 (Plotly용)
            crosstab_melt = crosstab_data.melt(id_vars='age_group', var_name='gender', value_name='total_runners')

            # Plotly bar chart (stacked)
            fig_gender_age = px.bar(
                crosstab_melt,
                x='age_group',
                y='total_runners',
                color='gender',
                barmode='group',  # 'stack'도 가능
                color_discrete_map={'M': '#3498db', 'F': '#e74c3c'},
                labels={'age_group': '연령대', 'total_runners': '러너 수', 'gender': '성별'},
                title='성별/연령대별 러너 수'
            )
            fig_gender_age.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='black'),
                title_font=dict(size=18, color='black'),
                xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
                yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
                legend=dict(title='성별', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            fig_gender_age.update_traces(marker_line_color='black', marker_line_width=1, textfont_color='black')
            st.plotly_chart(fig_gender_age, use_container_width=True)
        with col3:
            x_list, y_list = [], []
            for idx, row in distance_duration_df.iterrows():
                x_list.extend([row['distance']] * int(row['count']))
                y_list.extend([row['duration']] * int(row['count']))

            plt.figure(figsize=(8, 6))
            plt.hexbin(x_list, y_list, gridsize=60, cmap='turbo', bins='log')
            plt.xlabel('Distance (km)')
            plt.ylabel('Duration (min)')
            plt.title('Running Distance x Running Duration')
            plt.colorbar(label='log10(Count)')
            plt.tight_layout()
            st.pyplot(plt)
            plt.close()

    with TAB2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: black; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🧑‍🤝‍🧑 성별/연령대별 지표
            </h1>
        </div>
        """, unsafe_allow_html=True)
        # 성별과 연령대 필터 추가
        st.markdown("### 성별/연령대 설정")
        # 필터를 컬럼으로 배치
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            # 성별 필터
            gender_options = ["전체"] + sorted(running_Y_M_stats['gender'].unique().tolist())
            selected_gender = st.selectbox("성별 선택", gender_options)
        
        with filter_col2:
            # 연령대 필터
            age_options = ["전체"] + sorted(running_Y_M_stats['age_group'].unique().tolist())
            selected_age = st.selectbox("연령대 선택", age_options)
        
        # 필터링된 데이터 생성
        filtered_stats = running_Y_M_stats.copy()
        
        if selected_gender != "전체":
            filtered_stats = filtered_stats[filtered_stats['gender'] == selected_gender]
            
        if selected_age != "전체":
            filtered_stats = filtered_stats[filtered_stats['age_group'] == selected_age]
        
        # 필터링된 데이터로 메트릭 업데이트
        if len(filtered_stats) > 0:
            col_1, col_2 = st.columns(2)
            with col_1:
                st.metric(label=f"총 러너 수", value=f"{filtered_stats['total_runners'].sum():,d} 명")
                st.metric(label=f"평균 러닝 속도", value=f"{filtered_stats['speed_per_hour'].mean():.2f} km/h")
            with col_2:
                st.metric(label=f"평균 러닝 거리", value=f"{filtered_stats['distance'].mean():.2f} km")
                st.metric(label=f"평균 러닝 시간", value=f"{filtered_stats['duration'].mean():.2f} 분")
        else:
            st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

        monthly_summary = filtered_stats.groupby(['year', 'month']).agg(
            total_runners=('total_runners', 'sum'),
            distance=('distance', 'mean'),
            speed_per_hour=('speed_per_hour', 'mean'),
            duration=('duration', 'mean')
        ).reset_index()
        monthly_summary['date'] = monthly_summary['year'].astype(str) + '-' + monthly_summary['month'].astype(str)
        col4, col5, col6 = st.columns(3)

        with col4:
            fig1 = px.line(monthly_summary, x='date', y='total_runners', title="월별 총 러너 수", 
                           labels={'date': '년도-월', 'total_runners': '총 러너 수'},
                           line_shape='spline')  # 부드러운 곡선으로 변경
            fig1.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.line(monthly_summary, x='date', y='duration', title="월별 평균 러닝 시간 (분)",
                           labels={'date': '년도-월', 'duration': '평균 시간 (분)'},
                           line_shape='spline')
            fig2.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig2, use_container_width=True)

        with col5:
            fig3 = px.line(monthly_summary, x='date', y='distance', title="월별 평균 거리 (km)",
                           labels={'date': '년도-월', 'distance': '평균 거리 (km)'},
                           line_shape='spline')
            fig3.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.line(monthly_summary, x='date', y='speed_per_hour', title="월별 평균 속도 (km/h)",
                           labels={'date': '년도-월', 'speed_per_hour': '평균 속도 (km/h)'},
                           line_shape='spline')
            fig4.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig4, use_container_width=True)

        with col6:
            # 요일별 평균 러너 수 Plotly
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_dist_df = filtered_stats.groupby('weekday')['total_runners'].mean().reset_index()
            weekday_dist_df['weekday'] = pd.Categorical(weekday_dist_df['weekday'], categories=weekday_order, ordered=True)
            weekday_dist_df = weekday_dist_df.sort_values('weekday')

            fig_weekday = px.bar(
                weekday_dist_df,
                x='weekday',
                y='total_runners',
                color='total_runners',
                color_continuous_scale='Blues',
                title='요일별 평균 러너 수',
                labels={'weekday': '요일', 'total_runners': '평균 러너 수'},
                text_auto='.0f'
            )
            fig_weekday.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='black'),
                title_font=dict(size=18, color='black'),
                xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
                yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'))
            )
            fig_weekday.update_traces(marker_line_color='black', marker_line_width=1)
            st.plotly_chart(fig_weekday, use_container_width=True)

            # 국가별 평균 속도 Plotly
            top_countries = filtered_stats.groupby('country')['speed_per_hour'].mean().reset_index()
            top_countries = top_countries.sort_values(by='speed_per_hour', ascending=True).head(10)

            fig_speed = px.bar(
                top_countries,
                x='speed_per_hour',
                y='country',
                orientation='h',
                color='speed_per_hour',
                color_continuous_scale='Viridis_r',
                title='국가별 평균 속도 (Top 10)',
                labels={'speed_per_hour': '평균 속도 (km/h)', 'country': '국가'},
                text_auto='.2f'
            )
            fig_speed.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='black'),
                title_font=dict(size=18, color='black'),
                xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
                yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'))
            )
            fig_speed.update_traces(marker_line_color='black', marker_line_width=1)
            st.plotly_chart(fig_speed, use_container_width=True)

    with TAB3:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: black; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🏆 랭킹 대시보드
            </h1>
            <p style="color: black; font-size: 1.2em; opacity: 0.9;">
                전 세계 러너들과 함께하는 건강한 경쟁!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        running_W_ranking = load_data('running_W_ranking')
               
        country_options = sorted(running_W_ranking['country'].unique().tolist())
        selected_country = st.selectbox(
            "(앱 사용자 국가 자동 선택)", 
            country_options, 
            index=country_options.index("United States") if "United States" in country_options else 0
        )
        
        date_options = [x.split('-')[0] + '년 ' + x.split('-')[1] + '주차' for x in running_W_ranking['year_week'].unique()]
        selected_date = st.selectbox("주별 선택 (Default: 최근 주)", date_options, index=len(date_options)-1)
        selected_date = selected_date.split('년 ')[0] + '-' + selected_date.split('년 ')[1].split('주차')[0]
        filtered_stats = running_W_ranking[running_W_ranking['year_week'] == selected_date]
        
        # 국가별 집계
        ranking_df = filtered_stats.groupby('country').agg({
            'total_runners': 'sum',
            'distance': 'mean',
            'duration': 'mean'
        }).reset_index().sort_values(by='total_runners', ascending=False)
        
        st.markdown("""
        <div class="ranking-card">
            <h3 style="color: #2c3e50; margin-bottom: 15px;">🏅 지난 주 랭킹</h3>
            <p style="color: #7f8c8d; font-size: 0.9em;">1회 1Km 이상 러닝한 사람을 대상으로 집계합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fig1 = create_gamified_ranking_plot(
                ranking_df=ranking_df,
                selected_country=selected_country,
                column_name='total_runners',
                title='러너 수 랭킹 (Top 20)',
                x_label='Active Users'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            fig2 = create_gamified_ranking_plot(
                ranking_df=ranking_df,
                selected_country=selected_country,
                column_name='distance',
                title='평균 러닝 거리 랭킹 (Top 20)',
                x_label='Distance (km)'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        with col3:
            fig3 = create_gamified_ranking_plot(
                ranking_df=ranking_df,
                selected_country=selected_country,
                column_name='duration',
                title='평균 러닝 시간 랭킹 (Top 20)',
                x_label='Duration (min)'
            )
            st.plotly_chart(fig3, use_container_width=True)

def main():

    draw_dashboard()

if __name__ == "__main__":
    main()
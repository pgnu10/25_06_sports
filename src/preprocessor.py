import pandas as pd
import numpy as np

def preprocess_data(data):
    # 데이터 로드
    df = pd.concat([pd.read_csv('./data/raw/run_ww_2019_d.csv', index_col=0), 
                    pd.read_csv('./data/raw/run_ww_2020_d.csv', index_col=0)]).reset_index(drop=True)
    
    # 전처리
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce') # NA 처리
    # 파생변수 생성
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['week'] = df['datetime'].dt.isocalendar().week.astype('int')

    df['weekday'] = df['datetime'].dt.day_name()
    df['speed_per_hour'] = df['distance'] / df['duration'] * 60 # 시간당 속도

    # 이상치 처리
    df = df[~((df['distance'] >= 150) # 달린 거리가 150Km를 넘거나 (마라톤 연속 3회)
            | (df['duration'] >= 1200) # 달린 시간이 1200분을 넘거나 (20시간)
            | (df['speed_per_hour'] >= 50))] # 속도가 시간당 50Km를 넘거나 (우사인 볼트 최고 순간 시속 44km)
            # 그러면 제외한다

    # 운동했을 때 분포를 보기 위해 거리와 시간이 0인 경우 제외
    df = df[(df['distance'] > 0) & (df['duration'] > 0)]

    # 통계 데이터 만들기
    running_Y_M_stats = df.groupby(['year', 'month','gender','age_group','weekday','country']).agg({
        'distance': 'mean',
        'duration': 'mean', 
        'speed_per_hour': 'mean',
        'athlete': 'nunique'
    }).reset_index().rename(columns={'athlete': 'total_runners'})
    # 저장
    running_Y_M_stats.to_csv("./data/processed/running_Y_M_stats.csv", index=False)

    # 거리x시간 분포 데이터 만들기
    distance_duration_df = data_compression(df, 'distance', 'duration', x_bins=100, y_bins=100)
    # 저장
    distance_duration_df.to_csv("./data/processed/distance_duration_df.csv", index=False)

    # 주별 랭킹 데이터 만들기
    df['year_week'] = df['year'].astype(str) + '-' + df['week'].astype(str)
    ## active user = 1회에 1km 이상 러닝한 사람
    running_W_ranking = df[df['distance'] > 1].groupby(['country', 'year_week']).agg({
        'athlete': 'nunique',
        'distance': 'mean',
        'duration': 'mean',
    }).reset_index().rename(columns={'athlete': 'total_runners'})
    
    # year_week를 datetime으로 변환하여 올바른 시간 순서로 정렬
    running_W_ranking['year_week_dt'] = pd.to_datetime(running_W_ranking['year_week'] + '-1', format='%Y-%W-%w')
    running_W_ranking = running_W_ranking.sort_values('year_week_dt').reset_index(drop=True)
    running_W_ranking = running_W_ranking.drop('year_week_dt', axis=1)
    running_W_ranking.to_csv("./data/processed/running_W_ranking.csv", index=False)

    if data == 'running_Y_M_stats':
        return running_Y_M_stats
    elif data == 'distance_duration_df':
        return distance_duration_df
    elif data == 'running_W_ranking':
        return running_W_ranking


def data_compression(df, x_col='distance', y_col='duration', 
                        x_bins=100, y_bins=100, min_count=1):
    H, xedges, yedges = np.histogram2d(
        df[x_col], df[y_col], 
        bins=[x_bins, y_bins]
    )
    compressed_data = []
    for i in range(x_bins):
        for j in range(y_bins):
            count = H[i, j]
            if count >= min_count:
                x_center = (xedges[i] + xedges[i+1]) / 2
                y_center = (yedges[j] + yedges[j+1]) / 2
                compressed_data.append({
                    'distance': x_center,
                    'duration': y_center,
                    'count': count
                })
    return pd.DataFrame(compressed_data)


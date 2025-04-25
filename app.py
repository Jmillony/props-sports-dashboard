import pandas as pd
import plotly.express as px
import streamlit as st
from pybaseball import statcast
from datetime import date, timedelta
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="Props-Style Sports Dashboard", layout="wide")

# --- MLB TAB ---
tabs = st.tabs(["⚾ MLB Dashboard", "🏀 NBA Dashboard"])

with tabs[0]:
    st.title("⚾ MLB Player Statcast Dashboard")

    # Fetch yesterday's statcast data
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    mlb_data = statcast(start_dt=yesterday, end_dt=yesterday)

    # Sidebar Filters
    st.sidebar.header("MLB Filters")
    players_mlb = st.sidebar.multiselect("Select Players:", options=mlb_data['player_name'].unique(), default=mlb_data['player_name'].unique())
    date_range = st.sidebar.date_input("Select Date Range:", [mlb_data['game_date'].min(), mlb_data['game_date'].max()])
    pitch_mix = st.sidebar.multiselect("Select Pitch Types:", options=mlb_data['pitch_type'].dropna().unique(), default=mlb_data['pitch_type'].dropna().unique())
    pitcher_hand = st.sidebar.selectbox("Pitcher Throws:", options=['All', 'L', 'R'], index=0)
    batter_hand = st.sidebar.selectbox("Batter Stands:", options=['All', 'L', 'R'], index=0)

    # Apply Filters
    filtered_mlb = mlb_data[
        (mlb_data['player_name'].isin(players_mlb)) &
        (pd.to_datetime(mlb_data['game_date']) >= pd.to_datetime(date_range[0])) &
        (pd.to_datetime(mlb_data['game_date']) <= pd.to_datetime(date_range[1])) &
        (mlb_data['pitch_type'].isin(pitch_mix))
    ]

    if pitcher_hand != 'All':
        filtered_mlb = filtered_mlb[filtered_mlb['p_throws'] == pitcher_hand]

    if batter_hand != 'All':
        filtered_mlb = filtered_mlb[filtered_mlb['stand'] == batter_hand]

    # Group stats by player
    player_summary = filtered_mlb.groupby('player_name').agg({
        'release_speed': 'mean',
        'launch_angle': 'mean',
        'launch_speed': 'mean',
        'barrel': 'sum'
    }).reset_index()

    # Visuals
    fig_velo = px.bar(player_summary, x='player_name', y='release_speed', title='Average Pitch Velocity')
    fig_angle = px.bar(player_summary, x='player_name', y='launch_angle', title='Average Launch Angle')
    fig_exit = px.bar(player_summary, x='player_name', y='launch_speed', title='Average Exit Velocity')
    fig_barrels = px.bar(player_summary, x='player_name', y='barrel', title='Total Barrels')

    st.plotly_chart(fig_velo)
    st.plotly_chart(fig_angle)
    st.plotly_chart(fig_exit)
    st.plotly_chart(fig_barrels)

    # Download CSV
    csv = filtered_mlb.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered MLB Data", data=csv, file_name='filtered_statcast_data.csv', mime='text/csv')

    st.caption("MLB Data Source: Statcast via pybaseball")

# --- NBA TAB ---
with tabs[1]:
    st.title("🏀 NBA Player Game Log Dashboard")

    # NBA Player Search
    nba_player_name = st.text_input("Enter NBA Player Name:", value="LeBron James")
    nba_season = st.selectbox("Select Season", options=["2024-25", "2023-24", "2022-23"])

    # NBA Player Data Fetch
    nba_players = players.get_players()
    player_dict = {p['full_name']: p['id'] for p in nba_players}

    if nba_player_name in player_dict:
        with st.spinner("Fetching NBA stats..."):
            player_id = player_dict[nba_player_name]
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=nba_season)
            df_nba = gamelog.get_data_frames()[0]
            time.sleep(1)

        df_nba['GAME_DATE'] = pd.to_datetime(df_nba['GAME_DATE'])
        df_nba.sort_values('GAME_DATE', ascending=True, inplace=True)

        st.subheader(f"{nba_player_name} - Game Log ({nba_season})")
        st.dataframe(df_nba[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'FG3M', 'STL', 'BLK']])

        # Visualizations
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.line(df_nba, x='GAME_DATE', y='PTS', title='Points Over Time'))
        with col2:
            st.plotly_chart(px.bar(df_nba, x='GAME_DATE', y='AST', title='Assists Per Game'))

        # Download CSV
        csv_nba = df_nba.to_csv(index=False).encode('utf-8')
        st.download_button("Download NBA Player Data", data=csv_nba, file_name=f"{nba_player_name.replace(' ', '_')}_game_log.csv", mime='text/csv')
    else:
        st.warning("Player not found. Please check the spelling.")

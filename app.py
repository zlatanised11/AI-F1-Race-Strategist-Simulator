import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import OpenF1Client
from utils.styling import apply_dark_theme, apply_team_dark_style, get_team_style, get_plotly_theme
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
api_client = OpenF1Client()

# Apply dark theme
st.markdown(apply_dark_theme(), unsafe_allow_html=True)

def parse_f1_datetime(dt_str):
    """Robust F1 datetime parser"""
    try:
        return pd.to_datetime(dt_str, format='ISO8601')
    except:
        try:
            return pd.to_datetime(dt_str, format='mixed')
        except:
            return pd.to_datetime(dt_str, errors='coerce')

def main():
    st.title("🏎️ Formula 1 Team Strategy Analyzer")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Session Selection")
        selected_year = st.selectbox("Season", [2023, 2024], index=0)
        
        meetings = api_client.get_meetings(selected_year)
        meeting_names = [m['meeting_name'] for m in meetings]
        selected_meeting_name = st.selectbox("Grand Prix", meeting_names)
        selected_meeting = next(m for m in meetings if m['meeting_name'] == selected_meeting_name)
        
        sessions = api_client.get_sessions(selected_meeting['meeting_key'])
        session_names = [s['session_name'] for s in sessions]
        selected_session_name = st.selectbox("Session", session_names)
        selected_session = next(s for s in sessions if s['session_name'] == selected_session_name)
        
        drivers = api_client.get_drivers(selected_session['session_key'])
        teams = sorted(list(set([d['team_name'] for d in drivers])))
        selected_team = st.selectbox("Team", teams)
        
        team_drivers = [d for d in drivers if d['team_name'] == selected_team]
        driver_options = {f"{d['driver_number']} - {d['full_name']}": d['driver_number'] for d in team_drivers}
        selected_driver_label = st.selectbox("Driver", list(driver_options.keys()))
        selected_driver = driver_options[selected_driver_label]
        
        selected_driver_details = next(d for d in team_drivers if d['driver_number'] == selected_driver)
        st.image(selected_driver_details['headshot_url'], width=100)
    
    # Apply team styling
    st.markdown(apply_team_dark_style(selected_team), unsafe_allow_html=True)
    
    # Header
    team_style = get_team_style(selected_team)
    st.markdown(
        f"""
        <div class="team-header">
            <h2 style="margin:0;padding:0;color:{team_style['text']};">
                {selected_team} - {selected_driver_label}
            </h2>
            <p style="margin:0;padding:0;color:{team_style['text']};">
                {selected_session_name} - {selected_meeting_name} {selected_year}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Get all relevant data
    with st.spinner("Loading session data..."):
        # Get tire stint data
        stints = api_client.get_stints(selected_session['session_key'], selected_driver)
        
        # Get position data
        positions = api_client.get_position_data(selected_session['session_key'], selected_driver)
        
        # Get weather data
        weather = api_client.get_weather(selected_meeting['meeting_key'])
        
        # Get lap data
        laps = api_client.get_laps(selected_session['session_key'], selected_driver)

    # Tire Strategy Analysis
    st.subheader("🔄 Tire Strategy")
    if stints:
        stints_df = pd.DataFrame(stints)
        stints_df['stint_length'] = stints_df['lap_end'] - stints_df['lap_start'] + 1
        
        fig = px.bar(
            stints_df,
            x='stint_number',
            y='stint_length',
            color='compound',
            labels={'stint_number': 'Stint Number', 'stint_length': 'Laps', 'compound': 'Tire Compound'},
            color_discrete_map={
                'SOFT': '#FF3333',
                'MEDIUM': '#FFD700',
                'HARD': '#FFFFFF',
                'INTERMEDIATE': '#43B1CD',
                'WET': '#0066CC'
            },
            title="Tire Stint Analysis"
        )
        fig.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Stint details
        st.write("**Stint Details:**")
        st.dataframe(stints_df[['stint_number', 'compound', 'lap_start', 'lap_end', 'tyre_age_at_start']])
    else:
        st.warning("No tire stint data available for this session")

    # Position Chart
    st.subheader("📈 Position Changes")
    if positions:
        pos_df = pd.DataFrame(positions)
        pos_df['date'] = pos_df['date'].apply(parse_f1_datetime)
        
        session_start = parse_f1_datetime(selected_session['date_start'])
        pos_df['time_into_session'] = (pos_df['date'] - session_start).dt.total_seconds() / 60
        
        fig = px.line(
            pos_df,
            x='time_into_session',
            y='position',
            markers=True,
            title="Position Throughout Session",
            labels={'time_into_session': 'Minutes into session', 'position': 'Position'}
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No position data available for this session")

    # Weather Data
    st.subheader("🌤️ Weather Conditions")
    if weather:
        weather_df = pd.DataFrame(weather)
        weather_df['date'] = weather_df['date'].apply(parse_f1_datetime)
        
        # Select relevant weather metrics
        weather_metrics = ['air_temperature', 'track_temperature', 'humidity', 'rainfall']
        
        # Plot weather data
        fig = px.line(
            weather_df,
            x='date',
            y=weather_metrics,
            title="Weather Conditions During Session",
            labels={'value': 'Measurement', 'variable': 'Metric'}
        )
        fig.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Weather stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Air Temp", f"{weather_df['air_temperature'].max():.1f}°C")
        with col2:
            st.metric("Max Track Temp", f"{weather_df['track_temperature'].max():.1f}°C")
        with col3:
            st.metric("Max Humidity", f"{weather_df['humidity'].max():.1f}%")
    else:
        st.warning("No weather data available for this session")

    # Lap Time Analysis
    st.subheader("⏱️ Lap Time Performance")
    if laps:
        laps_df = pd.DataFrame(laps)
        laps_df = laps_df[laps_df['lap_duration'].notna()]
        
        if not laps_df.empty:
            fig = px.line(
                laps_df,
                x='lap_number',
                y='lap_duration',
                title="Lap Times Throughout Session",
                labels={'lap_number': 'Lap Number', 'lap_duration': 'Lap Time (s)'}
            )
            fig.update_layout(**get_plotly_theme()['layout'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Lap time stats
            fastest_lap = laps_df['lap_duration'].min()
            avg_lap = laps_df['lap_duration'].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Fastest Lap", f"{fastest_lap:.3f}s")
            with col2:
                st.metric("Average Lap", f"{avg_lap:.3f}s")
        else:
            st.warning("No valid lap time data available")
    else:
        st.warning("No lap data available for this session")

if __name__ == "__main__":
    main()
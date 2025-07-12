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
        # Get position data
        positions = api_client.get_position_data(selected_session['session_key'], selected_driver)
        
        # Get weather data
        weather = api_client.get_weather(selected_meeting['meeting_key'])
        
        # Get lap data
        laps = api_client.get_laps(selected_session['session_key'], selected_driver)
        
        # Get radio messages
        radio_messages = api_client.get_team_radio(selected_session['session_key'], selected_driver)

    # Position Chart vs Lap Number
    st.subheader("📈 Position Changes")
    if positions and laps:
        pos_df = pd.DataFrame(positions)
        pos_df['date'] = pos_df['date'].apply(parse_f1_datetime)
        
        laps_df = pd.DataFrame(laps)
        laps_df['date_start'] = laps_df['date_start'].apply(parse_f1_datetime)
        
        # Clean data - remove rows with null dates
        pos_df = pos_df.dropna(subset=['date'])
        laps_df = laps_df.dropna(subset=['date_start', 'lap_number'])
        
        if not pos_df.empty and not laps_df.empty:
            # Merge position data with lap numbers
            merged_df = pd.merge_asof(
                pos_df.sort_values('date'),
                laps_df[['date_start', 'lap_number']].sort_values('date_start'),
                left_on='date',
                right_on='date_start',
                direction='nearest'
            )
            
            # Remove any rows where merge didn't work
            merged_df = merged_df.dropna(subset=['lap_number'])
            
            if not merged_df.empty:
                fig = px.line(
                    merged_df,
                    x='lap_number',
                    y='position',
                    markers=True,
                    title="Position by Lap Number",
                    labels={'lap_number': 'Lap Number', 'position': 'Position'}
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Could not merge position and lap data")
        else:
            st.warning("Not enough valid position or lap data available")
    else:
        st.warning("No position or lap data available for this session")

    # Weather Data
    st.subheader("🌤️ Weather Conditions")
    if weather:
        weather_df = pd.DataFrame(weather)
        weather_df['date'] = weather_df['date'].apply(parse_f1_datetime)
        
        # Plot weather data
        fig = px.line(
            weather_df,
            x='date',
            y=['air_temperature', 'track_temperature'],
            title="Temperature Trends",
            labels={'value': 'Temperature (°C)', 'variable': 'Metric'}
        )
        fig.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No weather data available for this session")

    # Radio Messages
    st.subheader("📻 Team Radio Messages")
    if radio_messages:
        radio_df = pd.DataFrame(radio_messages)
        radio_df['date'] = radio_df['date'].apply(parse_f1_datetime)
        radio_df = radio_df.sort_values('date')
        
        # Display radio messages with basic info
        for idx, row in radio_df.iterrows():
            with st.expander(f"📻 Message {idx+1} - {row['date'].strftime('%H:%M:%S')}", expanded=False):
                st.audio(row['recording_url'])
                st.write(f"**Timestamp:** {row['date'].strftime('%H:%M:%S')}")
    else:
        st.warning("No radio messages available for this session")

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
                title="Lap Times",
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
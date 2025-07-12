import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import OpenF1Client
from utils.gpt_helper import GPTHelper
from utils.styling import apply_team_style, get_team_style
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
api_client = OpenF1Client()
gpt_helper = GPTHelper()

# App configuration
st.set_page_config(
    page_title="F1 Team Radio Analyzer",
    page_icon="🏎️",
    layout="wide"
)

def main():
    st.title("Formula 1 Team Radio Analyzer")
    st.markdown("Analyze team radio communications with AI-powered insights")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        selected_year = st.selectbox("Season", [2023, 2024], index=0)
        
        # Get meetings for selected year
        meetings = api_client.get_meetings(selected_year)
        meeting_names = [m['meeting_name'] for m in meetings]
        selected_meeting_name = st.selectbox("Grand Prix", meeting_names)
        selected_meeting = next(m for m in meetings if m['meeting_name'] == selected_meeting_name)
        
        # Get sessions for selected meeting
        sessions = api_client.get_sessions(selected_meeting['meeting_key'])
        session_names = [s['session_name'] for s in sessions]
        selected_session_name = st.selectbox("Session", session_names)
        selected_session = next(s for s in sessions if s['session_name'] == selected_session_name)
        
        # Get drivers for selected session
        drivers = api_client.get_drivers(selected_session['session_key'])
        teams = sorted(list(set([d['team_name'] for d in drivers])))
        selected_team = st.selectbox("Team", teams)
        
        # Filter drivers by team
        team_drivers = [d for d in drivers if d['team_name'] == selected_team]
        driver_options = {f"{d['driver_number']} - {d['full_name']}": d['driver_number'] for d in team_drivers}
        selected_driver_label = st.selectbox("Driver", list(driver_options.keys()))
        selected_driver = driver_options[selected_driver_label]
        
        # Get selected driver details
        selected_driver_details = next(d for d in team_drivers if d['driver_number'] == selected_driver)
        
        # Display driver info
        st.image(selected_driver_details['headshot_url'], width=100)
        st.caption(f"Team: {selected_team}")
        st.caption(f"Country: {selected_driver_details['country_code']}")
    
    # Apply team styling
    st.markdown(apply_team_style(selected_team), unsafe_allow_html=True)
    
    # Team header
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
    
    # Get radio messages
    radio_messages = api_client.get_team_radio(selected_session['session_key'], selected_driver)
    
    if not radio_messages:
        st.warning("No radio messages found for this driver/session.")
        return
    
    # Process radio messages
    radio_df = pd.DataFrame(radio_messages)
    radio_df['date'] = pd.to_datetime(radio_df['date'])
    radio_df = radio_df.sort_values('date')
    
    # Calculate time since session start
    session_start = pd.to_datetime(selected_session['date_start'])
    radio_df['time_into_session'] = (radio_df['date'] - session_start).dt.total_seconds() / 60
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Radio Messages", len(radio_df))
    with col2:
        st.metric("First Message", radio_df['date'].min().strftime('%H:%M:%S'))
    with col3:
        st.metric("Last Message", radio_df['date'].max().strftime('%H:%M:%S'))
    
    # Timeline visualization
    st.subheader("Radio Message Timeline")
    fig = px.scatter(
        radio_df,
        x='time_into_session',
        y=[1] * len(radio_df),
        color_discrete_sequence=[team_style['primary']],
        labels={'time_into_session': 'Minutes into session'},
        height=200
    )
    fig.update_yaxes(visible=False)
    fig.update_traces(marker=dict(size=12))
    st.plotly_chart(fig, use_container_width=True)
    
    # Radio messages list
    st.subheader("Radio Messages")
    
    for idx, row in radio_df.iterrows():
        with st.expander(f"📻 Radio {idx+1} - {row['date'].strftime('%H:%M:%S')}", expanded=False):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.audio(row['recording_url'])
                
                # Get telemetry data at time of radio
                telemetry = api_client.get_car_data_at_time(
                    selected_session['session_key'],
                    selected_driver,
                    row['date'].isoformat()
                )
                
                if telemetry:
                    telemetry = telemetry[0]
                    st.caption(f"Speed: {telemetry.get('speed', 'N/A')} km/h")
                    st.caption(f"Gear: {telemetry.get('n_gear', 'N/A')}")
                    st.caption(f"RPM: {telemetry.get('rpm', 'N/A')}")
            
            with col2:
                # Placeholder for actual transcription
                # In a production app, you'd use Whisper API to transcribe the audio
                placeholder_text = "Driver message about car performance and strategy"
                
                # Generate AI summary
                with st.spinner("Generating AI summary..."):
                    summary = gpt_helper.summarize_radio(placeholder_text)
                    st.write(f"**AI Summary:** {summary}")
                
                # Sentiment analysis
                sentiment = gpt_helper.analyze_sentiment(placeholder_text)
                sentiment_color = {
                    "Positive": "green",
                    "Neutral": "orange",
                    "Negative": "red"
                }.get(sentiment, "gray")
                
                st.markdown(f"**Sentiment:** :{sentiment_color}[{sentiment}]")

if __name__ == "__main__":
    main()
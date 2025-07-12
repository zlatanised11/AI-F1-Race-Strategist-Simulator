import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.api_client import OpenF1Client
from utils.gpt_helper import GPTHelper
from utils.styling import apply_dark_theme, apply_team_dark_style, get_team_style, get_plotly_theme
from utils.analysis import RaceAnalyzer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
api_client = OpenF1Client()
gpt_helper = GPTHelper()
analyzer = RaceAnalyzer()

# Apply dark theme
st.markdown(apply_dark_theme(), unsafe_allow_html=True)

def _find_lap_number(timestamp, laps_df):
    """Helper function to find lap number for a given timestamp"""
    if not isinstance(timestamp, pd.Timestamp) or laps_df.empty:
        return None
    
    laps_df = laps_df.copy()
    laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], format='ISO8601', errors='coerce')
    
    for _, lap in laps_df.iterrows():
        if pd.notna(lap['date_start']) and lap['date_start'] <= timestamp:
            return lap['lap_number']
    return None

def parse_f1_datetime(dt_str):
    """Robust F1 datetime parser that handles all known formats"""
    try:
        return pd.to_datetime(dt_str, format='ISO8601')
    except:
        try:
            return pd.to_datetime(dt_str, format='mixed')
        except:
            return pd.to_datetime(dt_str, errors='coerce')  # returns NaT if parsing fails

def main():
    st.title("🏎️ Formula 1 Team Radio Analyzer")
    st.markdown("Analyze team radio communications with AI-powered insights")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Session Selection")
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
    
    # Apply team styling with dark theme
    st.markdown(apply_team_dark_style(selected_team), unsafe_allow_html=True)
    
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
    
    # Get all data for the session
    with st.spinner("Loading session data..."):
        # Get ALL radio messages first, then filter (more reliable)
        all_radio = api_client.get_all_team_radio(selected_session['session_key'])
        radio_messages = [msg for msg in all_radio if msg['driver_number'] == selected_driver]
        
        # Get additional data
        laps = api_client.get_laps(selected_session['session_key'], selected_driver)
        positions = api_client.get_position_data(selected_session['session_key'], selected_driver)
        session_data = api_client.get_session_data(selected_session['session_key'])
    
    # Display comprehensive race summary
    st.subheader("📊 Comprehensive Race Analysis")
    with st.expander("View Detailed Race Summary", expanded=True):
        if radio_messages and laps and positions:
            summary = analyzer.generate_race_summary(
                {
                    **selected_driver_details,
                    'meeting_name': selected_meeting_name,
                    'session_name': selected_session_name
                },
                radio_messages,
                laps,
                positions
            )
            st.write(summary)
        else:
            st.warning("""
            ⚠️ Insufficient data to generate comprehensive race summary
            - Try selecting a different session or check back later
            - Race sessions typically have more data available
            """)
    
    # Metrics row
    st.subheader("📈 Session Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Radio Messages", len(radio_messages))
    with col2:
        st.metric("Laps Completed", len(laps) if laps else 0)
    with col3:
        fastest_lap = min([lap['lap_duration'] for lap in laps if isinstance(lap.get('lap_duration'), (int, float))], default=0)
        st.metric("Fastest Lap", f"{fastest_lap:.3f}s" if fastest_lap else "N/A")
    with col4:
        final_pos = positions[-1]['position'] if positions else "N/A"
        st.metric("Final Position", final_pos)
    
    # Position chart
    if positions:
        st.subheader("📉 Position Changes")
        pos_df = pd.DataFrame(positions)
        
        # Parse datetime with our robust function
        pos_df['date'] = pos_df['date'].apply(parse_f1_datetime)
        
        # Calculate time since session start
        session_start = parse_f1_datetime(selected_session['date_start'])
        pos_df['time_into_session'] = (pos_df['date'] - session_start).dt.total_seconds() / 60
        
        # Create the plot
        fig = px.line(
            pos_df,
            x='time_into_session',
            y='position',
            markers=True,
            labels={'time_into_session': 'Minutes into session', 'position': 'Position'},
            color_discrete_sequence=[team_style['primary']],
            title=f"Position Changes During {selected_session_name}"
        )
        
        # Configure plot appearance
        fig.update_yaxes(autorange="reversed", title="Position")
        fig.update_xaxes(title="Minutes Into Session")
        fig.update_layout(
            **get_plotly_theme()['layout'],
            hovermode="x unified",
            height=400
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced radio message display
    st.subheader("📻 Radio Messages Analysis")
    st.info(f"Found {len(radio_messages)} radio messages for this session")
    
    if not radio_messages:
        st.warning("No radio messages found for this driver/session.")
        return
    
    radio_df = pd.DataFrame(radio_messages)
    radio_df['date'] = radio_df['date'].apply(parse_f1_datetime)
    radio_df = radio_df.sort_values('date')
    
    # Add position at time of radio
    if positions:
        positions_df = pd.DataFrame(positions)
        positions_df['date'] = positions_df['date'].apply(parse_f1_datetime)
        radio_df = pd.merge_asof(
            radio_df.sort_values('date'),
            positions_df[['date', 'position']].sort_values('date'),
            on='date',
            direction='nearest'
        )
    
    # Add lap number
    if laps:
        laps_df = pd.DataFrame(laps)
        laps_df['date_start'] = laps_df['date_start'].apply(parse_f1_datetime)
        radio_df['lap_number'] = radio_df['date'].apply(
            lambda x: _find_lap_number(x, laps_df)
        )
    
    # Display each message with enhanced context
    for idx, row in radio_df.iterrows():
        with st.expander(
            f"📻 Message {idx+1} - Lap {row.get('lap_number', '?')} - Pos {row.get('position', '?')} - {row['date'].strftime('%H:%M:%S')}",
            expanded=False
        ):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.audio(row['recording_url'])
                
                # Show telemetry context
                telemetry = api_client.get_car_data_at_time(
                    selected_session['session_key'],
                    selected_driver,
                    row['date'].isoformat()
                )
                
                if telemetry:
                    telemetry = telemetry[0]
                    st.markdown("""
                    <div class="metric-container">
                        <h4>Telemetry at Time of Message</h4>
                    """, unsafe_allow_html=True)
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.metric("Speed", f"{telemetry.get('speed', 'N/A')} km/h")
                        st.metric("Gear", telemetry.get('n_gear', 'N/A'))
                    with cols[1]:
                        st.metric("RPM", telemetry.get('rpm', 'N/A'))
                        st.metric("Throttle", f"{telemetry.get('throttle', 'N/A')}%")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                # Generate AI analysis
                with st.spinner("Analyzing message..."):
                    # In production, use actual audio transcription here
                    placeholder_text = f"Radio message during {selected_session_name} at {row['date'].time()}"
                    
                    analysis = analyzer.analyze_radio_message(
                        placeholder_text,
                        {
                            'lap_number': row.get('lap_number'),
                            'position': row.get('position'),
                            'session_name': selected_session_name,
                            'team_name': selected_team
                        }
                    )
                    
                    st.write(f"**Summary:** {analysis['summary']}")
                    
                    sentiment_emoji = {
                        "Positive": "✅",
                        "Neutral": "➖",
                        "Negative": "❌"
                    }.get(analysis['sentiment'], "🔘")
                    
                    st.write(f"**Sentiment:** {sentiment_emoji} {analysis['sentiment']}")
                    st.write(f"**Analysis:** {analysis['analysis']}")

if __name__ == "__main__":
    main()
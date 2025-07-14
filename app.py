import streamlit as st

import pandas as pd
import plotly.express as px
from utils.api_client import OpenF1Client
from utils.styling import apply_dark_theme, apply_team_dark_style, get_team_style, get_plotly_theme
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
import openai

st.set_page_config(
    page_title="F1 Stats",  # Change this to your desired title
    page_icon="🏎️",                     # Optional: Set an emoji or image as favicon
    layout="wide"                       # Optional: Keeps the layout wide
)
# Load environment variables
load_dotenv()

# Initialize client
api_client = OpenF1Client()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_compound_color(compound):
    """Return color for each tire compound"""
    return {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFD700',
        'HARD': '#BFBFBF',
        'INTERMEDIATE': '#43B649',
        'WET': '#0066CC'
    }.get(compound, '#CCCCCC')

def color_compound(val):
    """Helper function to color compound cells"""
    color = get_compound_color(val)
    text_color = 'black' if val == 'HARD' else 'white'
    return f'background-color: {color}; color: {text_color}'

def calculate_position_changes(positions: list) -> int:
    """Calculate total number of position changes"""
    if not positions:
        return 0
    changes = 0
    prev_pos = positions[0]['position']
    for pos in positions[1:]:
        if pos['position'] != prev_pos:
            changes += abs(pos['position'] - prev_pos)
            prev_pos = pos['position']
    return changes

def transcribe_audio(audio_url):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = "radio_message.mp3"
        
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        return transcript
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None

def parse_f1_datetime(dt_str):
    """Robust F1 datetime parser"""
    try:
        return pd.to_datetime(dt_str, format='ISO8601')
    except:
        try:
            return pd.to_datetime(dt_str, format='mixed')
        except:
            return pd.to_datetime(dt_str, errors='coerce')
        
def display_radio_messages(selected_session, selected_driver, radio_messages):
    if not radio_messages:
        st.warning("No radio messages available for this session")
        return
    
    # Create DataFrame and process timestamps
    radio_df = pd.DataFrame(radio_messages)
    radio_df['date'] = radio_df['date'].apply(parse_f1_datetime)
    radio_df = radio_df.sort_values('date')
    radio_df['lap_number'] = "?"  # Initialize with default value
    
    # Get lap data for this driver
    laps = api_client.get_laps(selected_session['session_key'], selected_driver)
    if laps:
        laps_df = pd.DataFrame(laps)
        
        # Convert and clean lap data
        laps_df['date_start'] = laps_df['date_start'].apply(parse_f1_datetime)
        laps_df = laps_df.dropna(subset=['date_start', 'lap_duration'])
        laps_df = laps_df.sort_values('lap_number')
        
        # Match radio messages to laps
        for idx, radio_row in radio_df.iterrows():
            radio_time = radio_row['date']
            
            for _, lap_row in laps_df.iterrows():
                try:
                    lap_start = lap_row['date_start']
                    lap_duration = lap_row['lap_duration']
                    
                    # Skip if we have invalid lap data
                    if pd.isna(lap_duration):
                        continue
                        
                    lap_end = lap_start + pd.Timedelta(seconds=float(lap_duration))
                    
                    if lap_start <= radio_time <= lap_end:
                        radio_df.at[idx, 'lap_number'] = int(lap_row['lap_number'])
                        break
                        
                except (TypeError, ValueError):
                    continue
    
    # Display each radio message
    for idx, row in radio_df.iterrows():
        if 'transcriptions' not in st.session_state:
            st.session_state.transcriptions = {}
        if 'ai_summaries' not in st.session_state:
            st.session_state.ai_summaries = {}
        
        with st.expander(f"📻 Lap {row['lap_number']} - {row['date'].strftime('%H:%M:%S')}", expanded=False):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.audio(row['recording_url'])
            
            with col2:
                if idx not in st.session_state.transcriptions:
                    if st.button("Transcribe", key=f"transcribe_{idx}"):
                        with st.spinner("Transcribing..."):
                            transcription = transcribe_audio(row['recording_url'])
                            if transcription:
                                st.session_state.transcriptions[idx] = transcription
                                summary_prompt = f"Summarize this F1 team radio message in 1-2 sentences: {transcription}"
                                ai_summary = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are an F1 analyst summarizing team radio communications."},
                                        {"role": "user", "content": summary_prompt}
                                    ],
                                    max_tokens=100
                                ).choices[0].message.content
                                st.session_state.ai_summaries[idx] = ai_summary
                
                transcription = st.session_state.transcriptions.get(idx, "")
                st.text_area("Message", transcription, height=100, key=f"msg_{idx}",disabled=True)
                
                if idx in st.session_state.ai_summaries:
                    st.text_area("AI Summary", 
                               st.session_state.ai_summaries[idx], 
                               height=68, 
                               key=f"sum_{idx}",disabled=True)

def main():
    st.title("🏎️ Formula 1 Team Strategy Analyzer")
    
    # Initialize session state
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'fetched_data' not in st.session_state:
        st.session_state.fetched_data = {}
    
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
        
        # Submit button that updates session state
        if st.button("Submit Analysis Request"):
            st.session_state.submitted = True
            # Clear previous data when new submission is made
            st.session_state.fetched_data = {}
            
            # Get all relevant data only when submitted
            with st.spinner("Loading session data..."):
                st.session_state.fetched_data['positions'] = api_client.get_position_data(selected_session['session_key'], selected_driver)
                st.session_state.fetched_data['weather'] = api_client.get_weather(selected_meeting['meeting_key'])
                st.session_state.fetched_data['laps'] = api_client.get_laps(selected_session['session_key'], selected_driver)
                st.session_state.fetched_data['radio_messages'] = api_client.get_team_radio(selected_session['session_key'], selected_driver)
                st.session_state.fetched_data['pit_data'] = api_client.get_pit_data(selected_session['session_key'], selected_driver)
                st.session_state.fetched_data['stints'] = api_client.get_stints(selected_session['session_key'], selected_driver)
                st.session_state.fetched_data['driver_details'] = selected_driver_details
        
        # Reset button
        if st.button("Reset All"):
            st.session_state.submitted = False
            st.session_state.fetched_data = {}
            st.experimental_rerun()
    
    # Check submission state
    if not st.session_state.submitted:
        st.info("Please select your analysis parameters and click 'Submit Analysis Request'")
        return
    
    # Access data from session state
    positions = st.session_state.fetched_data.get('positions', [])
    weather = st.session_state.fetched_data.get('weather', [])
    laps = st.session_state.fetched_data.get('laps', [])
    radio_messages = st.session_state.fetched_data.get('radio_messages', [])
    pit_data = st.session_state.fetched_data.get('pit_data', [])
    stints = st.session_state.fetched_data.get('stints', [])
    selected_driver_details = st.session_state.fetched_data.get('driver_details', {})
    
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
    
    # Comprehensive Race Summary
    st.subheader("🏁 Race Summary")
    if st.button("Generate Comprehensive Race Analysis"):
        with st.spinner("Analyzing race data..."):
            summary_data = {
                "driver_name": selected_driver_details['full_name'],
                "team": selected_team,
                "session": selected_session_name,
                "total_laps": len(laps) if laps else 0,
                "final_position": positions[-1]['position'] if positions else "N/A",
                "position_changes": calculate_position_changes(positions) if positions else 0,
                "fastest_lap": min([lap['lap_duration'] for lap in laps if isinstance(lap.get('lap_duration'), (int, float))], default=0),
                "tire_strategy": [{"stint": s['stint_number'], "compound": s['compound'], "laps": s['lap_end'] - s['lap_start'] + 1} for s in stints] if stints else [],
                "weather_changes": len(weather) > 1 if weather else False,
                "radio_messages_count": len(radio_messages)
            }
            
            prompt = f"""
            Create a comprehensive race summary for {summary_data['driver_name']} ({summary_data['team']}) 
            during the {summary_data['session']} session.
            
            Key data:
            - Total laps: {summary_data['total_laps']}
            - Final position: {summary_data['final_position']}
            - Position changes: {summary_data['position_changes']}
            - Fastest lap: {summary_data['fastest_lap']:.3f}s
            - Tire strategy: {summary_data['tire_strategy']}
            - Weather changes: {summary_data['weather_changes']}
            - Radio messages: {summary_data['radio_messages_count']}
            
            Provide a detailed analysis covering:
            1. Overall performance assessment
            2. Tire strategy effectiveness
            3. Position change patterns
            4. Key moments from radio communications
            5. Weather impact (if relevant)
            """
            
            race_summary = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert F1 analyst. Provide detailed race summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            ).choices[0].message.content
            
            st.markdown("### Full Race Analysis")
            st.write(race_summary)

    # Position Chart vs Lap Number
    st.subheader("📈 Position Changes")
    if positions and laps:
        pos_df = pd.DataFrame(positions)
        pos_df['date'] = pos_df['date'].apply(parse_f1_datetime)
        
        laps_df = pd.DataFrame(laps)
        laps_df['date_start'] = laps_df['date_start'].apply(parse_f1_datetime)
        
        pos_df = pos_df.dropna(subset=['date'])
        laps_df = laps_df.dropna(subset=['date_start', 'lap_number'])
        
        if not pos_df.empty and not laps_df.empty:
            merged_df = pd.merge_asof(
                pos_df.sort_values('date'),
                laps_df[['date_start', 'lap_number']].sort_values('date_start'),
                left_on='date',
                right_on='date_start',
                direction='nearest'
            )
            
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

    # Lap Time Performance

    if "Race" in selected_session_name:
        st.subheader("⏱️ Lap Time Performance")
        if laps:
            laps_df = pd.DataFrame(laps)
            laps_df = laps_df[laps_df['lap_duration'].notna()]
            
            if not laps_df.empty:
                # Get pit data from session state
                pit_data = st.session_state.fetched_data.get('pit_data', [])
                
                # Mark pit laps
                pit_laps = []
                if pit_data:
                    pit_df = pd.DataFrame(pit_data)
                    pit_laps = pit_df['lap_number'].unique().tolist()
                    # Add pit stop indicator column
                    laps_df['is_pit'] = laps_df['lap_number'].isin(pit_laps)
                
                # Create plot
                fig = px.line(
                    laps_df,
                    x='lap_number',
                    y='lap_duration',
                    title="Lap Times",
                    labels={'lap_number': 'Lap Number', 'lap_duration': 'Lap Time (s)'},
                    height=500
                )
                
                # Highlight pit stops if they exist
                if pit_laps:
                    pit_lap_data = laps_df[laps_df['is_pit']]
                    fig.add_trace(px.scatter(
                        pit_lap_data,
                        x='lap_number',
                        y='lap_duration',
                        color_discrete_sequence=['red'],
                        hover_data={'is_pit': True}
                    ).data[0])
                    
                    for _, pit in pit_df.iterrows():
                        fig.add_annotation(
                            x=pit['lap_number'],
                            y=laps_df[laps_df['lap_number'] == pit['lap_number']]['lap_duration'].values[0],
                            text=f"Pit: {pit['pit_duration']:.2f}s",
                            showarrow=True,
                            arrowhead=1,
                            yshift=10
                        )
                
                fig.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Show tire strategy table separately if stints exist
                if stints:
                    st.subheader("🔄 Tire Strategy")
                    stint_df = pd.DataFrame(stints)
                    
                    # Calculate fastest lap per stint
                    stint_fastest = []
                    for _, stint in stint_df.iterrows():
                        stint_laps = laps_df[
                            (laps_df['lap_number'] >= stint['lap_start']) & 
                            (laps_df['lap_number'] <= stint['lap_end'])
                        ]
                        fastest = stint_laps['lap_duration'].min()
                        stint_fastest.append(fastest)
                    
                    stint_df['fastest_lap'] = stint_fastest
                    
                    # Prepare table data
                    strategy_table = []
                    for _, stint in stint_df.iterrows():
                        strategy_table.append({
                            "Laps": f"{stint['lap_start']}-{stint['lap_end']}",
                            "Compound": stint['compound'],
                            "Stint Length": stint['lap_end'] - stint['lap_start'] + 1,
                            "Fastest Lap": f"{stint['fastest_lap']:.3f}s",
                        })
                    
                    # Display styled table
                    st.dataframe(
                        pd.DataFrame(strategy_table).style.applymap(
                            color_compound, 
                            subset=['Compound']
                        )
                    )
                
                # Show performance metrics (excluding pit laps)
                normal_laps = laps_df[~laps_df['lap_number'].isin(pit_laps)] if pit_laps else laps_df
                fastest_lap = normal_laps['lap_duration'].min()
                avg_lap = normal_laps['lap_duration'].mean()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fastest Lap", f"{fastest_lap:.3f}s" + (" (excl. pits)" if pit_laps else ""))
                with col2:
                    st.metric("Average Lap", f"{avg_lap:.3f}s" + (" (excl. pits)" if pit_laps else ""))
            
            else:
                st.warning("No valid lap time data available")
        else:
            st.warning("No lap data available for this session")

    # Radio Messages with Transcription and AI Summary
    st.subheader("📻 Team Radio Messages")
    radio_messages = st.session_state.fetched_data.get('radio_messages', [])
    display_radio_messages(selected_session, selected_driver, radio_messages)

if __name__ == "__main__":
    main()
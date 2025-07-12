import streamlit as st
from utils.api_client import OpenF1Client
import pandas as pd
import plotly.express as px

api_client = OpenF1Client()

def show_advanced_view():
    st.title("Advanced Team Radio Analysis")
    
    # Get session from query params
    query_params = st.experimental_get_query_params()
    session_key = query_params.get("session_key", [None])[0]
    driver_number = query_params.get("driver_number", [None])[0]
    
    if not session_key or not driver_number:
        st.warning("Please select a driver from the main page to view advanced analysis")
        return
    
    # Get radio messages
    radio_messages = api_client.get_team_radio(session_key, int(driver_number))
    if not radio_messages:
        st.warning("No radio messages found for this driver/session.")
        return
    
    # Process data
    radio_df = pd.DataFrame(radio_messages)
    radio_df['date'] = pd.to_datetime(radio_df['date'])
    radio_df = radio_df.sort_values('date')
    
    # Message frequency analysis
    st.subheader("Message Frequency")
    radio_df['hour'] = radio_df['date'].dt.hour
    freq_df = radio_df.groupby('hour').size().reset_index(name='count')
    
    fig = px.bar(
        freq_df,
        x='hour',
        y='count',
        labels={'hour': 'Hour of Day', 'count': 'Number of Messages'},
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Lap comparison
    st.subheader("Radio Messages by Lap")
    laps = api_client.get_laps(session_key, int(driver_number))
    if laps:
        laps_df = pd.DataFrame(laps)
        st.dataframe(laps_df[['lap_number', 'lap_duration', 'is_pit_out_lap']])
    
    st.subheader("Raw Data")
    st.dataframe(radio_df)

if __name__ == "__main__":
    show_advanced_view()
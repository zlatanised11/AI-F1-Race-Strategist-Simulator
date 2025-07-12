import requests
import pandas as pd
from datetime import datetime
from functools import lru_cache

class OpenF1Client:
    BASE_URL = "https://api.openf1.org/v1"
    
    @lru_cache(maxsize=128)
    def get_meetings(self, year: int) -> list:
        url = f"{self.BASE_URL}/meetings?year={year}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @lru_cache(maxsize=128)
    def get_sessions(self, meeting_key: int) -> list:
        url = f"{self.BASE_URL}/sessions?meeting_key={meeting_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @lru_cache(maxsize=128)
    def get_drivers(self, session_key: int) -> list:
        url = f"{self.BASE_URL}/drivers?session_key={session_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @lru_cache(maxsize=128)
    def get_team_radio(self, session_key: int, driver_number: int = None) -> list:
        url = f"{self.BASE_URL}/team_radio?session_key={session_key}"
        if driver_number:
            url += f"&driver_number={driver_number}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @lru_cache(maxsize=128)
    def get_car_data_at_time(self, session_key: int, driver_number: int, timestamp: str) -> list:
        url = f"{self.BASE_URL}/car_data?session_key={session_key}&driver_number={driver_number}&date={timestamp}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @lru_cache(maxsize=128)
    def get_laps(self, session_key: int, driver_number: int) -> list:
        url = f"{self.BASE_URL}/laps?session_key={session_key}&driver_number={driver_number}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
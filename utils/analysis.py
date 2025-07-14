import pandas as pd
from datetime import datetime
from utils.gpt_helper import GPTHelper

class RaceAnalyzer:
    def __init__(self):
        self.gpt = GPTHelper()
    
    def generate_race_summary(self, driver_data: dict, radio_messages: list, 
                            laps: list, positions: list) -> str:
        """Generate comprehensive race summary using all available data"""
        # Prepare data
        radio_count = len(radio_messages)
        lap_count = len(laps)
        position_changes = self._calculate_position_changes(positions)
        
        # Get fastest lap
        fastest_lap = min([lap['lap_duration'] for lap in laps if isinstance(lap.get('lap_duration'), (int, float))], default=0)
        
        # Get final position
        final_position = positions[-1]['position'] if positions else "N/A"
        
        # Prepare prompt
        prompt = f"""
        Generate a comprehensive race summary for driver {driver_data['full_name']} ({driver_data['team_name']}).

        Session Details:
        - Event: {driver_data.get('meeting_name', 'Unknown')}
        - Session: {driver_data.get('session_name', 'Unknown')}

        Key Statistics:
        - Total radio messages: {radio_count}
        - Total laps completed: {lap_count}
        - Fastest lap time: {fastest_lap:.3f} seconds
        - Position changes: {position_changes}
        - Final position: {final_position}

        Provide a detailed 3-5 paragraph summary covering:
        1. Race performance overview and key statistics
        2. Analysis of radio communications and team strategy
        3. Position changes throughout the race
        4. Notable incidents or highlights
        5. Overall assessment of driver's performance

        Write in a professional motorsport commentary style.
        """
        
        return self.gpt.generate_race_summary(prompt)
    
    def _calculate_position_changes(self, positions: list) -> int:
        if not positions:
            return 0
        changes = 0
        prev_pos = positions[0]['position']
        for pos in positions[1:]:
            if pos['position'] != prev_pos:
                changes += abs(pos['position'] - prev_pos)
                prev_pos = pos['position']
        return changes
    
    def analyze_radio_message(self, message: str, context: dict) -> dict:
        """Analyze a single radio message with context"""
        prompt = f"""
        Create a concise one-paragraph race summary for {selected_driver_details['full_name']} ({selected_team}) 
        during the {selected_session_name} at {selected_meeting_name} {selected_year}.

        Include these key details in a flowing narrative:
        - Started {positions[0]['position'] if positions else 'N/A'}th, finished {positions[-1]['position'] if positions else 'N/A'}th
        - Made {calculate_position_changes(positions)} position changes
        - Fastest lap: {min([lap['lap_duration'] for lap in laps if isinstance(lap.get('lap_duration'), (int, float))], default=0):.3f}s
        - Tire strategy: {[f"Stint {s['stint_number']} ({s['compound']} x{s['lap_end']-s['lap_start']+1} laps)" for s in stints] if stints else 'No data'}
        - {len(radio_messages)} team radio messages exchanged
        - Weather: {'changed' if len(weather) > 1 else 'stable'} conditions

        Focus on the most impactful moments and overall performance assessment.
        Write in a professional motorsport commentary style.
        Keep it to one tight paragraph (4-5 sentences max).
        """
        
        return {
            'summary': self.gpt.summarize_text(message),
            'sentiment': self.gpt.analyze_sentiment(message),
            'analysis': self.gpt.summarize_text(prompt, max_tokens=200)
        }
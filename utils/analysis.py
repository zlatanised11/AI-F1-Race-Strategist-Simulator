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
        Analyze this Formula 1 team radio message with the given context:

        Message: {message}

        Context:
        - Lap: {context.get('lap_number', 'Unknown')}
        - Position: {context.get('position', 'Unknown')}
        - Session: {context.get('session_name', 'Unknown')}
        - Team: {context.get('team_name', 'Unknown')}

        Provide analysis covering:
        1. Key information conveyed
        2. Likely purpose/strategy
        3. Urgency level (Low/Medium/High)
        4. Suggested team response
        """
        
        return {
            'summary': self.gpt.summarize_text(message),
            'sentiment': self.gpt.analyze_sentiment(message),
            'analysis': self.gpt.summarize_text(prompt, max_tokens=200)
        }
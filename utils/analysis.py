import pandas as pd
from datetime import datetime
from utils.gpt_helper import GPTHelper

class RaceAnalyzer:
    def __init__(self):
        self.gpt = GPTHelper()
    
    def generate_race_summary(self, driver_data: dict, radio_messages: list, 
                            laps: list, positions: list, stints: list, 
                            selected_session: dict) -> str:
        """Generate statistical race summary using measurable API data"""
        # Prepare data
        radio_count = len(radio_messages)
        lap_count = len(laps)
        position_changes = self._calculate_position_changes(positions)
        fastest_lap = min([lap['lap_duration'] for lap in laps if isinstance(lap.get('lap_duration'), (int, float))], default=0)
        final_position = positions[-1]['position'] if positions else "N/A"
        start_position = positions[0]['position'] if positions else "N/A"

        # Calculate tire strategy metrics
        tire_strategy = []
        if stints:
            for stint in stints:
                stint_laps = [lap for lap in laps 
                            if stint['lap_start'] <= lap['lap_number'] <= stint['lap_end']]
                avg_speed = sum(lap.get('speed', 0) for lap in stint_laps) / len(stint_laps) if stint_laps else 0
                fastest_lap_stint = min([lap.get('lap_duration', 0) for lap in stint_laps], default=0)
                tire_strategy.append({
                    'compound': stint['compound'],
                    'laps': f"{stint['lap_start']}-{stint['lap_end']}",
                    'avg_speed': f"{avg_speed:.1f} km/h",
                    'fastest': f"{fastest_lap_stint:.3f}s"
                })

        # Calculate overall speed (excluding pit laps)
        pit_laps = [pit['lap_number'] for pit in (st.session_state.fetched_data.get('pit_data', []))]
        racing_laps = [lap for lap in laps if lap.get('lap_number') not in pit_laps]
        avg_speed = sum(lap.get('speed', 0) for lap in racing_laps) / len(racing_laps) if racing_laps else 0

        # Prepare prompt
        prompt = f"""
        Generate a concise 3-paragraph statistical race summary for {driver_data['full_name']} using only measurable performance data.

        Key Metrics:
        - Position: {start_position} → {final_position} ({position_changes} position changes)
        - Laps: {lap_count}/{selected_session.get('total_laps', 'N/A')} completed
        - Fastest lap: {fastest_lap:.3f}s (vs session best: {selected_session.get('best_lap_time', 'N/A')})
        - Average speed: {avg_speed:.1f} km/h (racing laps only)
        - Radio messages: {radio_count}

        Tire Performance:
        {chr(10).join(
            f"{s['compound']}: {s['laps']} laps | Avg: {s['avg_speed']} | Fastest: {s['fastest']}"
            for s in tire_strategy
        ) if tire_strategy else 'No tire data available'}

        Structure:
        1. Position changes and race outcome statistics
        2. Lap time and speed performance metrics
        3. Tire strategy effectiveness based on stint data

        Include only verifiable data from the API. No subjective assessments.
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
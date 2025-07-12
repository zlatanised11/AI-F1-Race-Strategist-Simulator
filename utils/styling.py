TEAM_COLORS = {
    "Red Bull Racing": {"primary": "#3671C6", "secondary": "#1E41FF", "text": "#FFFFFF"},
    "Mercedes": {"primary": "#6CD3BF", "secondary": "#00D2BE", "text": "#000000"},
    "Ferrari": {"primary": "#F91536", "secondary": "#DC0000", "text": "#FFFFFF"},
    "McLaren": {"primary": "#F58020", "secondary": "#FF8700", "text": "#000000"},
    "Aston Martin": {"primary": "#358C75", "secondary": "#006F62", "text": "#FFFFFF"},
    "Alpine": {"primary": "#2293D1", "secondary": "#0090FF", "text": "#FFFFFF"},
    "Williams": {"primary": "#37BEDD", "secondary": "#005AFF", "text": "#FFFFFF"},
    "AlphaTauri": {"primary": "#5E8FAA", "secondary": "#2B4562", "text": "#FFFFFF"},
    "Alfa Romeo": {"primary": "#C92D4B", "secondary": "#900000", "text": "#FFFFFF"},
    "Haas F1 Team": {"primary": "#B6BABD", "secondary": "#FFFFFF", "text": "#000000"},
}

def get_team_style(team_name: str) -> dict:
    return TEAM_COLORS.get(team_name, {"primary": "#000000", "secondary": "#666666", "text": "#FFFFFF"})

def apply_team_style(team_name: str):
    style = get_team_style(team_name)
    return f"""
    <style>
        .team-header {{
            background-color: {style['primary']};
            color: {style['text']};
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }}
        .stRadio > div > label {{
            color: {style['primary']};
            font-weight: bold;
        }}
        .stButton>button {{
            background-color: {style['primary']};
            color: {style['text']};
            border: none;
        }}
        .stButton>button:hover {{
            background-color: {style['secondary']};
            color: {style['text']};
        }}
    </style>
    """
DARK_THEME = {
    "bg": "#0E1117",        # Dark background
    "text": "#FAFAFA",      # Light text
    "secondary": "#262730", # Darker elements
    "base": "#0E1117",      # Base color
    "font": "sans serif",
    "plot_bg": "#1E1E1E",   # Plot background
    "plot_text": "#FFFFFF", # Plot text
    "sidebar_bg": "#0A0C10" # Darker sidebar
}

TEAM_COLORS = {
    "Red Bull Racing": {
        "primary": "#3671C6",
        "secondary": "#1E41FF",
        "text": "#FFFFFF",
        "dark": "#1E41FF",
        "sidebar": "#0F1A3C"
    },
    "Mercedes": {
        "primary": "#6CD3BF",
        "secondary": "#00D2BE",
        "text": "#000000",
        "dark": "#00D2BE",
        "sidebar": "#003831"
    },
    "Ferrari": {
        "primary": "#F91536",
        "secondary": "#DC0000",
        "text": "#FFFFFF",
        "dark": "#DC0000",
        "sidebar": "#3C0000"
    },
    "McLaren": {
        "primary": "#F58020",
        "secondary": "#FF8700",
        "text": "#000000",
        "dark": "#FF8700",
        "sidebar": "#3A2600"
    },
    "Aston Martin": {
        "primary": "#358C75",
        "secondary": "#006F62",
        "text": "#FFFFFF",
        "dark": "#006F62",
        "sidebar": "#00302A"
    },
    "Alpine": {
        "primary": "#2293D1",
        "secondary": "#0090FF",
        "text": "#FFFFFF",
        "dark": "#0063B2",
        "sidebar": "#002D4D"
    },
    "Williams": {
        "primary": "#37BEDD",
        "secondary": "#005AFF",
        "text": "#FFFFFF",
        "dark": "#005AFF",
        "sidebar": "#001A4D"
    },
    "AlphaTauri": {
        "primary": "#5E8FAA",
        "secondary": "#2B4562",
        "text": "#FFFFFF",
        "dark": "#2B4562",
        "sidebar": "#0F1A2E"
    },
    "Alfa Romeo": {
        "primary": "#C92D4B",
        "secondary": "#900000",
        "text": "#FFFFFF",
        "dark": "#900000",
        "sidebar": "#2A0000"
    },
    "Haas F1 Team": {
        "primary": "#B6BABD",
        "secondary": "#FFFFFF",
        "text": "#000000",
        "dark": "#787878",
        "sidebar": "#2A2A2A"
    },
}

def get_team_style(team_name: str) -> dict:
    return TEAM_COLORS.get(team_name, {
        "primary": "#000000",
        "secondary": "#666666",
        "text": "#FFFFFF",
        "dark": "#333333",
        "sidebar": "#0A0C10"
    })

def apply_dark_theme():
    return f"""
    <style>
        :root {{
            --primary-color: {DARK_THEME['bg']};
            --background-color: {DARK_THEME['bg']};
            --secondary-background-color: {DARK_THEME['secondary']};
            --text-color: {DARK_THEME['text']};
            --font: {DARK_THEME['font']};
        }}
        
        /* Main app styling */
        .stApp {{
            background-color: {DARK_THEME['bg']};
            color: {DARK_THEME['text']};
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {DARK_THEME['sidebar_bg']} !important;
        }}
        
        [data-testid="stSidebar"] .st-cb, 
        [data-testid="stSidebar"] .st-cc, 
        [data-testid="stSidebar"] .st-cd {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Input elements */
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select,
        .stNumberInput>div>div>input {{
            background-color: {DARK_THEME['secondary']};
            color: {DARK_THEME['text']};
            border-color: #444;
        }}
        
        /* Containers */
        .css-1aumxhk {{
            background-color: {DARK_THEME['base']};
            border-color: #444;
        }}
        
        /* Borders */
        .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak {{
            border-color: #444 !important;
        }}
        
        /* Text elements */
        .st-cb, .st-cc, .st-cd {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Dataframes */
        .stDataFrame {{
            background-color: {DARK_THEME['secondary']};
        }}
        
        /* Alerts */
        .stAlert {{
            background-color: {DARK_THEME['secondary']};
        }}
        
        /* Metrics */
        .stMetric {{
            background-color: {DARK_THEME['secondary']};
            border-radius: 0.5rem;
            padding: 1rem;
        }}
        .stMetric > div > div {{
            color: {DARK_THEME['text']} !important;
        }}
        .stMetric > div > div:last-child {{
            color: #AAA !important;
        }}
        
        /* Expanders */
        .st-emotion-cache-1hynsf2 {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Markdown text */
        .stMarkdown {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Selectbox labels */
        .stSelectbox label {{
            color: {DARK_THEME['text']} !important;
        }}
    </style>
    """

def apply_team_dark_style(team_name):
    style = get_team_style(team_name)
    dark_style = style.get("dark", style['primary'])
    sidebar_style = style.get("sidebar", DARK_THEME['sidebar_bg'])
    
    return f"""
    <style>
        /* Team header */
        .team-header {{
            background: linear-gradient(90deg, {DARK_THEME['secondary']} 0%, {dark_style} 100%);
            color: {style['text']};
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border-left: 5px solid {dark_style};
        }}
        
        /* Sidebar theming */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_style} !important;
        }}
        
        /* Sidebar buttons */
        .stButton>button {{
            background-color: {style['primary']} !important;
            color: {style['text']} !important;
            border: 1px solid {style['secondary']} !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            margin: 0.25rem 0 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton>button:hover {{
            background-color: {style['secondary']} !important;
            border-color: {style['primary']} !important;
        }}
        
        /* Radio buttons */
        .stRadio > div > label {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Expanders */
        .st-expander {{
            background-color: {DARK_THEME['secondary']};
            border-color: {dark_style};
            margin-bottom: 1rem;
        }}
        
        /* Fix for all text in sidebar */
        [data-testid="stSidebar"] * {{
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Make select boxes more readable */
        .stSelectbox>div>div>select {{
            background-color: {DARK_THEME['secondary']} !important;
            color: {DARK_THEME['text']} !important;
        }}
        
        /* Style the submit button specifically */
        div[data-testid="stSidebar"] .stButton>button {{
            background-color: {style['primary']} !important;
            color: {style['text']} !important;
            font-weight: bold !important;
            border: 2px solid {style['secondary']} !important;
        }}

        /* Dropdown/Select Box Styling - Minimal changes to match team colors */
        .stSelectbox > div > div {{
            background-color: {DARK_THEME['secondary']} !important;
            border-color: {style['primary']} !important;
        }}
        
        .stSelectbox > div > div > select {{
            background-color: {DARK_THEME['secondary']} !important;
            color: {DARK_THEME['text']} !important;
            border-color: {style['primary']} !important;
        }}
        
        .stSelectbox > div > div > svg {{
            color: {style['primary']} !important;
        }}
        
        .stSelectbox > div > div > div > div {{
            background-color: {DARK_THEME['secondary']} !important;
            color: {DARK_THEME['text']} !important;
            border-color: {style['primary']} !important;
        }}
        
        .stSelectbox > div > div > div > div > div:hover {{
            background-color: {style['primary']} !important;
            color: {style['text']} !important;
        }}
        
        /* Keep existing label styling */
        .stSelectbox label {{
            color: {DARK_THEME['text']} !important;
        }}
    </style>
    """

def get_plotly_theme():
    return {
        'layout': {
            'plot_bgcolor': '#FFFFFF',  # White plot area
            'paper_bgcolor': '#FFFFFF', # White outer area
            'font': {'color': '#000000'},  # Change text to black
            'xaxis': {
                'gridcolor': '#CCC',
                'linecolor': '#999',
                'zerolinecolor': '#999'
            },
            'yaxis': {
                'gridcolor': '#CCC',
                'linecolor': '#999',
                'zerolinecolor': '#999'
            }
        }
    }

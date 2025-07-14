# 🏎️ F1 Race Strategy Analyzer [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-zlatanised.streamlit.app/) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

An AI-powered dashboard for analyzing Formula 1 race strategies, team radio communications, and performance metrics using real racing data.

## 🌟 Features

- **Session Analysis**: Compare qualifying vs race performance  
- **Tire Strategies**: Visualize stint lengths and compound choices  
- **Position Tracking**: Lap-by-lap position changes  
- **Team Radio AI**:  
  - Automatic transcription of radio messages  
  - AI-generated summaries of key communications  
- **Weather Integration**: Track temperature impact on performance  
- **Dark Mode**: Team-color themed interface  

## 🛠️ Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **APIs**:  
  - OpenF1 (race data)  
  - OpenAI Whisper (audio transcription)  
  - OpenAI GPT (message summarization)  
- **Visualization**: Plotly, Pandas  

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/f1-strategy-analyzer.git
cd f1-strategy-analyzer
```

2. Set up environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```ini
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage

Run the app locally:

```bash
streamlit run app.py
```

## 🌐 Live Demo

Access the deployed version:  
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-zlatanised.streamlit.app/)

## 📊 Data Sources

- Race data: [OpenF1 API](https://github.com/berkeley-research-group/openf1)  
- Lap times: [Ergast API](https://ergast.com/mrd/)  
- Weather data: [Open-Meteo](https://open-meteo.com/)  

## ⚖️ Legal Disclaimer

This is an independent fan project using publicly available data. Not affiliated with or endorsed by Formula 1, the FIA, or any F1 teams. All trademarks remain property of their respective owners.

## 🤝 Contributing

1. Fork the project  
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your changes (`git commit -m 'Add some amazing feature'`)  
4. Push to the branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request  

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## ✉️ Contact

[Email - ujwalc1999@gmail.com ](mailto:ujwalc1999@gmail.com) | [LinkedIn](https://www.linkedin.com/in/ujwalc11/)

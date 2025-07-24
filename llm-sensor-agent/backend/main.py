from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json
import openai
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta

# Load OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str
    return_tables: bool = False  # Optional flag, default False

def load_sensor_data():
    folder = os.path.join(os.path.dirname(__file__), "sensor_data")
    all_data = []
    try:
        files = os.listdir(folder)
        print(f"Files found in sensor_data folder: {files}")
    except Exception as e:
        print(f"Error reading folder: {e}")
        return pd.DataFrame()

    rooms_found = []
    for filename in files:
        if filename.endswith(".ndjson"):
            if "Room" in filename:
                room_match = re.search(r'Room\s*(\d+)', filename)
                if room_match:
                    room = f"Room {room_match.group(1)}"
                else:
                    room = filename.replace(".ndjson", "").replace("_", " ").strip().title()
            else:
                room_raw = filename.replace(".ndjson", "")
                room = room_raw.replace("_", " ").replace("-", " ")
                room = re.sub(r"(\d+)", r" \1", room).strip().title()
            rooms_found.append(room)

            file_path = os.path.join(folder, filename)
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            data = {
                                "timestamp": record.get("timestamp"),
                                "co2": record.get("CO2 (ppm)") or record.get("co2") or record.get("CO2"),
                                "temperature": record.get("Temperature (°C)") or record.get("temperature") or record.get("temp") or record.get("Temp"),
                                "humidity": record.get("Relative Humidity (%)") or record.get("humidity") or record.get("rh") or record.get("RH"),
                                "room": room
                            }
                            all_data.append(data)
                        except Exception as e:
                            print(f"Error parsing line in {filename}: {e}")
                            continue
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue

    print(f"Rooms detected during load: {set(rooms_found)}")

    df = pd.DataFrame(all_data)
    if not df.empty:
        print(f"Rooms detected in DataFrame: {df['room'].unique()}")
    else:
        print("No data loaded into DataFrame.")

    if 'timestamp' in df.columns and 'room' in df.columns:
        df['room'] = df['room'].astype(str).str.strip().str.title()
        df = df.dropna(subset=['timestamp', 'room'])
    return df

def df_to_markdown_table(df, col_names):
    if df.empty:
        return "No data available"
    
    header = "| " + " | ".join(col_names) + " |"
    separator = "| " + " | ".join(["---"] * len(col_names)) + " |"
    rows = []
    for _, row in df.iterrows():
        formatted_row = []
        for val in row:
            if pd.isna(val):
                formatted_row.append("N/A")
            elif isinstance(val, (int, float)):
                formatted_row.append(f"{val:.2f}" if isinstance(val, float) else str(val))
            else:
                formatted_row.append(str(val))
        rows.append(f"| {' | '.join(formatted_row)} |")
    return "\n".join([header, separator] + rows)

def generate_comprehensive_analysis(df):
    """Generate comprehensive data analysis with multiple perspectives"""
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Time-based analysis
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['date'] = df['timestamp'].dt.date
    df['time_of_day'] = pd.cut(df['hour'], 
                              bins=[0, 6, 12, 18, 24], 
                              labels=['Night (0-6h)', 'Morning (6-12h)', 'Afternoon (12-18h)', 'Evening (18-24h)'],
                              include_lowest=True)
    
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    
    rooms = df['room'].unique().tolist()
    room_count = len(rooms)
    
    # Data quality assessment
    data_points_per_room = df.groupby('room').size()
    date_range = f"{df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} to {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}"
    total_hours = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
    
    # Basic statistics
    room_stats = df.groupby('room').agg({
        'temperature': ['mean', 'max', 'min', 'std'],
        'co2': ['mean', 'max', 'min', 'std'],
        'humidity': ['mean', 'max', 'min', 'std']
    }).round(2)
    room_stats.columns = ['_'.join(col) for col in room_stats.columns]
    room_stats.reset_index(inplace=True)
    
    # Time-based patterns
    hourly_patterns = df.groupby(['room', 'hour']).agg({
        'temperature': 'mean',
        'co2': 'mean',
        'humidity': 'mean'
    }).round(2).reset_index()
    
    daily_patterns = df.groupby(['room', 'day_of_week'], observed=True).agg({
        'temperature': 'mean',
        'co2': 'mean',
        'humidity': 'mean'
    }).round(2).reset_index()
    
    time_of_day_patterns = df.groupby(['room', 'time_of_day'], observed=True).agg({
        'temperature': 'mean',
        'co2': 'mean',
        'humidity': 'mean'
    }).round(2).reset_index()
    
    # Air quality assessment
    co2_quality = df.copy()
    co2_quality['air_quality'] = pd.cut(co2_quality['co2'], 
                                       bins=[0, 400, 800, 1200, float('inf')], 
                                       labels=['Excellent (<400)', 'Good (400-800)', 'Moderate (800-1200)', 'Poor (>1200)'])
    
    air_quality_distribution = co2_quality.groupby(['room', 'air_quality'], observed=True).size().unstack(fill_value=0)
    air_quality_percentage = air_quality_distribution.div(air_quality_distribution.sum(axis=1), axis=0) * 100
    air_quality_percentage = air_quality_percentage.round(1).reset_index()
    
    # Anomaly detection
    anomalies = []
    for room in rooms:
        room_data = df[df['room'] == room]
        
        # Temperature anomalies (outside typical comfort range)
        temp_anomalies = room_data[(room_data['temperature'] < 18) | (room_data['temperature'] > 26)]
        if len(temp_anomalies) > 0:
            anomalies.append(f"{room}: {len(temp_anomalies)} temperature readings outside comfort range (18-26°C)")
        
        # CO2 anomalies (very high levels)
        co2_anomalies = room_data[room_data['co2'] > 1200]
        if len(co2_anomalies) > 0:
            anomalies.append(f"{room}: {len(co2_anomalies)} readings with poor air quality (CO2 > 1200ppm)")
        
        # Humidity anomalies (outside optimal range)
        humidity_anomalies = room_data[(room_data['humidity'] < 30) | (room_data['humidity'] > 70)]
        if len(humidity_anomalies) > 0:
            anomalies.append(f"{room}: {len(humidity_anomalies)} humidity readings outside optimal range (30-70%)")
    
    # Room comparisons
    room_rankings = {
        'warmest': room_stats.loc[room_stats['temperature_mean'].idxmax(), 'room'],
        'coolest': room_stats.loc[room_stats['temperature_mean'].idxmin(), 'room'],
        'highest_co2': room_stats.loc[room_stats['co2_mean'].idxmax(), 'room'],
        'lowest_co2': room_stats.loc[room_stats['co2_mean'].idxmin(), 'room'],
        'most_humid': room_stats.loc[room_stats['humidity_mean'].idxmax(), 'room'],
        'least_humid': room_stats.loc[room_stats['humidity_mean'].idxmin(), 'room']
    }
    
    # Recent trends (last 24 hours if available)
    recent_cutoff = df['timestamp'].max() - timedelta(hours=24)
    recent_data = df[df['timestamp'] > recent_cutoff]
    recent_trends = {}
    if not recent_data.empty:
        recent_stats = recent_data.groupby('room').agg({
            'temperature': 'mean',
            'co2': 'mean',
            'humidity': 'mean'
        }).round(2)
        recent_trends = recent_stats.to_dict('index')
    
    return {
        'overview': {
            'rooms': rooms,
            'room_count': room_count,
            'date_range': date_range,
            'total_hours': round(total_hours, 1),
            'data_points_per_room': data_points_per_room.to_dict()
        },
        'room_stats': room_stats,
        'hourly_patterns': hourly_patterns,
        'daily_patterns': daily_patterns,
        'time_of_day_patterns': time_of_day_patterns,
        'air_quality_distribution': air_quality_percentage,
        'anomalies': anomalies,
        'room_rankings': room_rankings,
        'recent_trends': recent_trends
    }

@app.post("/ask")
async def ask_ai(query: Query):
    df = load_sensor_data()
    if df.empty:
        return {"answer": "No sensor data available."}

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['temperature', 'co2', 'humidity', 'timestamp'])

    if df.empty:
        return {"answer": "No valid sensor data after cleaning."}

    analysis = generate_comprehensive_analysis(df)

    if query.return_tables:
        # Return key tables as JSON and markdown
        room_stats_json = analysis['room_stats'].to_dict('records')
        hourly_patterns_json = analysis['hourly_patterns'].to_dict('records')
        daily_patterns_json = analysis['daily_patterns'].to_dict('records')
        time_of_day_patterns_json = analysis['time_of_day_patterns'].to_dict('records')
        air_quality_json = analysis['air_quality_distribution'].to_dict('records')
        room_stats_md = df_to_markdown_table(analysis['room_stats'], analysis['room_stats'].columns.tolist())

        return {
            "answer": "Tables returned as requested.",
            "tables": {
                "room_stats": room_stats_json,
                "hourly_patterns": hourly_patterns_json,
                "daily_patterns": daily_patterns_json,
                "time_of_day_patterns": time_of_day_patterns_json,
                "air_quality_distribution": air_quality_json,
                "room_stats_markdown": room_stats_md
            },
            "overview": analysis['overview'],
            "room_rankings": analysis['room_rankings'],
            "anomalies": analysis['anomalies'],
        }

    # Else return AI text answer
    room_stats_table = df_to_markdown_table(analysis['room_stats'], analysis['room_stats'].columns.tolist())

    prompt = f"""You are an environmental data analyst. Answer questions about indoor air quality data concisely and clearly.

**DATA OVERVIEW:**
Rooms: {analysis['overview']['rooms']} | Period: {analysis['overview']['date_range']} | Duration: {analysis['overview']['total_hours']}h

**KEY METRICS:**
{room_stats_table}

**ROOM RANKINGS:**
- Warmest: {analysis['room_rankings']['warmest']} | Coolest: {analysis['room_rankings']['coolest']}
- Highest CO2: {analysis['room_rankings']['highest_co2']} | Lowest CO2: {analysis['room_rankings']['lowest_co2']}
- Most Humid: {analysis['room_rankings']['most_humid']} | Least Humid: {analysis['room_rankings']['least_humid']}

**RECENT ISSUES:**
{chr(10).join(['• ' + anomaly for anomaly in analysis['anomalies'][:3]]) if analysis['anomalies'] else '• No major issues detected'}

**STANDARDS:** CO2: <400 excellent, 400-800 good, 800-1200 moderate, >1200 poor | Temp: 18-26°C comfort | Humidity: 30-70% optimal

**USER QUESTION:** {query.question}

**RESPONSE REQUIREMENTS:**
- Keep answer under 4 sentences
- Lead with the direct answer
- Include 1-2 specific data points
- Add one actionable recommendation if relevant
- Use simple language, avoid jargon

Answer briefly and helpfully:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"OpenAI API error: {e}"

    return {"answer": answer}

@app.get("/debug_stats")
async def debug_stats():
    df = load_sensor_data()
    if df.empty:
        return {"error": "No sensor data available."}

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['temperature', 'co2', 'humidity', 'timestamp'])

    if df.empty:
        return {"error": "No valid data after cleaning."}

    analysis = generate_comprehensive_analysis(df)
    
    return {
        "overview": analysis['overview'],
        "room_rankings": analysis['room_rankings'],
        "anomalies": analysis['anomalies'],
        "sample_stats": analysis['room_stats'].head().to_dict('records')
    }

@app.get("/full_analysis")
async def full_analysis():
    """Endpoint to get complete analysis without AI interpretation"""
    df = load_sensor_data()
    if df.empty:
        return {"error": "No sensor data available."}

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['temperature', 'co2', 'humidity', 'timestamp'])

    if df.empty:
        return {"error": "No valid data after cleaning."}

    analysis = generate_comprehensive_analysis(df)
    
    # Convert DataFrames to dicts for JSON response
    for key in ['room_stats', 'hourly_patterns', 'daily_patterns', 'time_of_day_patterns', 'air_quality_distribution']:
        if key in analysis and hasattr(analysis[key], 'to_dict'):
            analysis[key] = analysis[key].to_dict('records')
    
    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

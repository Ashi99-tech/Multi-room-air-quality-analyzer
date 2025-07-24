# 🌬️ Air Quality AI Agent

This project is an **AI-powered FastAPI web service** with a React frontend that allows users to ask natural language questions and analyze real-time air quality data from `.jsonl` sensor logs.

---

## ✨ Features

- 💬 Natural language queries (e.g., "What was the average CO2 in Room A yesterday?")
- 📊 Sensor data analysis with time filtering and aggregation
- 🧠 GPT-4 integration for intelligent data parsing and dynamic analysis
- ⚡ Dynamic Python code execution for flexible analytics
- 🌐 React frontend with a simple chat-style UI

---

## 📁 Project Structure

```
air-quality-ai-agent/
├── backend/
│   ├── main.py                 # FastAPI backend with OpenAI integration
│   ├── utils.py               # Dynamic data parsing and analysis
│   ├── sensor_data/           # Room-specific .jsonl files
│   └── .env                   # Your OpenAI API key
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── package.json           # React dependencies
├── README.md                  # Project documentation
└── requirements.txt           # Python backend dependencies
```

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/air-quality-ai-agent.git
cd air-quality-ai-agent
```

### 2. Backend Setup (FastAPI)

**a. Create and activate virtual environment:**

```bash
cd backend
python -m venv venv

# Activate:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**b. Install dependencies:**

```bash
pip install -r ../requirements.txt
```

**c. Add your OpenAI API key in .env:**

Create a file `backend/.env` with:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**d. Run FastAPI backend:**

```bash
uvicorn main:app --reload
```

The backend will be available at: **http://localhost:8000**

### 3. Frontend Setup (React)

```bash
cd ../frontend
npm install
npm start
```

The React app will open at: **http://localhost:3000**

---

## 💡 Usage

1. Open the app at **http://localhost:3000**
2. Ask questions like:
   - "What was the average CO2 in Room B today?"
   - "Compare temperature in Room A and Room B last week."
   - "Show humidity > 70% in Room C between 9am–12pm."
3. The backend reads `.jsonl` files from `backend/sensor_data/` and returns results

---

## 📄 Example .jsonl File Format

Each line in the `.jsonl` file (e.g., `Room1.jsonl`) should look like:

```json
{"timestamp": "2025-07-24T14:00:00", "temperature": 26.4, "humidity": 45.2, "co2": 520}
{"timestamp": "2025-07-24T15:00:00", "temperature": 27.1, "humidity": 44.0, "co2": 540}
```

- Each file should be named by room (e.g., `Room1.jsonl`, `Room2.jsonl`)

---

## 🛠️ Tech Stack

- **Backend:** Python 3, FastAPI, OpenAI, Pandas
- **Frontend:** React.js, Tailwind CSS
- **Data Format:** .jsonl files
- **AI Model:** OpenAI GPT-4

---

## ⚠️ Notes

- Do not commit your `.env` file (already in `.gitignore`)
- Place your `.jsonl` sensor files in: `backend/sensor_data/`
- Ensure consistent field names across sensor files: `timestamp`, `temperature`, `humidity`, `co2`

---

## 🙌 Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit:
   ```bash
   git commit -am 'Add your feature'
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request on GitHub 🎉

---

## 📜 License

MIT License © 2025 Your Name / Team

# 🌬️ Air Quality AI Agent

An AI-powered agent that allows users to analyze multi-room air quality sensor data using natural language queries.

This project uses:
- 🧠 OpenAI LLM to interpret and respond to queries
- 🐍 FastAPI (Python) for backend processing
- ⚛️ React.js for frontend UI
- 📂 Raw JSONL files for each room (no database)

---

## 📊 Features

- Accepts **natural language questions** (e.g., "Which room had the highest temperature last week?")
- Parses raw `.jsonl` files (each line is a JSON object)
- Handles **inconsistent field names** (e.g., `CO2`, `co2 (ppm)`, `carbonDioxide`)
- Uses **dynamic Python code execution** to generate insights
- Displays results as **tables**, **charts**, or **text summaries**
- Supports **live updates** from newly added data files

---

## 🚀 Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/air-quality-ai-agent.git
cd air-quality-ai-agent

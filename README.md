# MA Grader

Modern desktop application for grading Major Assignments (MA1, MA2, MA3) - Excel-based college math assignments.

## Architecture

```
MA-Grader/
├── frontend/          # Electron + React UI
│   ├── electron/      # Electron main process
│   ├── src/           # React components
│   └── package.json
├── backend/           # Python FastAPI server
│   ├── graders/       # Assignment grading logic
│   ├── orchestrator/  # Pipeline orchestration
│   ├── writers/       # Output generation
│   └── server.py      # API server
└── README.md
```

## Tech Stack

- **Frontend:** Electron + React + Tailwind CSS
- **Backend:** Python + FastAPI
- **Grading Engine:** openpyxl for Excel processing

## Setup

### Prerequisites

- Node.js 18+ 
- Python 3.10+
- npm or yarn

### Install Dependencies

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Development

Run both backend and frontend:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python server.py

# Terminal 2 - Frontend
cd frontend
npm run electron:dev
```

### Build for Distribution

```bash
cd frontend
npm run electron:build
```

This creates distributable packages in `frontend/dist-electron/`.

## Usage

1. **Settings (optional):** Click the gear icon to set your workspace folder
   - All output will be saved to your chosen folder
   - Great for organizing by course (e.g., `~/Documents/MAT-144/`)
2. Select assignment type (MA1, MA2, MA3)
3. Enter course label (e.g., MAT-144-501)
4. Drop or browse for student submission ZIP
5. Click "Run Pipeline"
6. Wait for grading to complete
7. Open output folder to retrieve graded files

## Features

- **Custom Workspace:** Set where all grading output goes (persists between sessions)
- **No Admin Required:** Portable app - just download and run
- **Drag & Drop:** Drop ZIP files directly into the app
- **Progress Tracking:** Visual step-by-step progress indicator
- **Multiple Assignments:** MA1 supported now; MA2/MA3 coming soon

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/state` | GET | Get pipeline state |
| `/grade` | POST | Start grading pipeline |
| `/reset` | POST | Reset pipeline state |
| `/folders/open` | POST | Open folder in system browser |

---

Built by Clayton Ragsdale with Claudio 🛠️

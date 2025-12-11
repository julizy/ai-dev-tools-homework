# Running the Online Coding Interview Platform

## Quick Start (Recommended)

### Option 1: Using npm/concurrently (Easiest)
```bash
cd online-coding-interviews
npm install    # First time only
npm run dev
```
This starts both client (http://localhost:8080) and server (http://localhost:5000) in one command.

### Option 2: Using shell script
```bash
cd online-coding-interviews
./start.sh                    # Run both (default)
./start.sh full              # Run both concurrently
./start.sh server            # Run only server
./start.sh client            # Run only client
```

### Option 3: Manual (separate terminals)
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 8080
```

## Available npm Scripts

```bash
npm run dev              # Start client and server concurrently
npm run server           # Start backend server only
npm run client           # Start frontend client only
npm run test             # Run all tests with verbose output
npm run test:quick       # Run tests with minimal output
npm run test:coverage    # Generate HTML coverage report
```

## Ports

- **Backend Server**: http://localhost:5000
- **Frontend Client**: http://localhost:8080

## Environment Variables

```bash
PORT=8000 npm run server    # Run server on custom port
PORT=3000 npm run client    # Run client on custom port
```

## Troubleshooting

### npm not installed
If you don't have npm installed, use the shell script approach:
```bash
./start.sh
```

### Port already in use
If port 5000 or 8080 is already in use:
```bash
PORT=8001 npm run server
PORT=8081 npm run client
```

### Python virtual environment issues
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing

```bash
cd backend
source venv/bin/activate
pytest -v                    # All tests verbose
pytest --tb=no -q           # Quick summary
pytest test_unit.py -v      # Unit tests only
pytest test_integration.py -v # Integration tests only
pytest --cov=app --cov-report=html  # Coverage report
```

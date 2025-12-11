# Online Coding Interview Platform - Quick Start Guide

## Getting Started

### Option 1: Using Shell Script (macOS/Linux)

```bash
# Make the script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

### Option 2: Using Batch Script (Windows)

```cmd
# Run the startup script
start.bat
```

### Option 3: Manual Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**
   ```bash
   python app.py
   ```

## Access the Platform

Once the server is running, open your browser and visit:

```
http://localhost:5000
```

## Verify Installation

When you see the following output, the server is ready:

```
 * Running on http://0.0.0.0:5000
 * WebSocket transport: polling
```

## Next Steps

1. Create an interview session
2. Share the session code with candidates
3. Start collaborating in real-time!

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, edit `backend/app.py` and change the port:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Module Not Found Errors
Ensure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### WebSocket Connection Issues
- Check firewall settings
- Ensure you're using the correct URL
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)

See README.md for more detailed information.

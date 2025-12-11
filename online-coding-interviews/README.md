# Online Coding Interview Platform

A real-time collaborative coding platform built with Flask (backend) and JavaScript (frontend). Multiple users can connect to an interview session, edit code together, and execute code safely in the browser.

## Features

✅ **Create and Share Sessions** - Generate unique interview session codes and share them with candidates
✅ **Real-time Code Synchronization** - All connected users see code changes instantly via WebSocket
✅ **Multi-language Support** - JavaScript, Python, Java, C++, C#, Ruby, PHP, Go, Rust, SQL, HTML, CSS
✅ **Syntax Highlighting** - Ace editor provides beautiful syntax highlighting for all languages
✅ **Safe Code Execution** - Execute code in the browser using Pyodide for Python and native JS for JavaScript
✅ **HTML/CSS Preview** - Render HTML and CSS code directly in the browser
✅ **Collaborative Features** - Real-time user count, join/leave notifications

## Quick Start

### 🐳 With Docker (Recommended - One Command!)
```bash
cd online-coding-interviews
docker-compose up -d
```
Then open: **http://localhost:8080**

See [DOCKER.md](DOCKER.md) for detailed Docker guide.

### Without Docker (Manual Setup)
```bash
cd online-coding-interviews
npm install
npm run dev
```
- Frontend: http://localhost:8080
- Backend: http://localhost:5000
./start.sh server      # Run only the backend server
./start.sh client      # Run only the frontend client
```

**Or start them in separate terminals:**
```bash
# Terminal 1 - Backend Server
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend Client
cd frontend
python3 -m http.server 8080
```

### Development Server

**Start the server:**
```bash
cd backend
source venv/bin/activate
python app.py
```
Server runs on `http://localhost:5000`

**Or with custom port:**
```bash
PORT=8000 python app.py
```

**On Windows:**
```cmd
cd backend
venv\Scripts\activate
python app.py
```

### Installation & Setup

**First-time setup:**
```bash
# Navigate to project root
cd online-coding-interviews

# Install npm dependencies (for concurrently)
npm install

# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

**Update dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

**npm scripts available:**
```bash
npm run dev         # Run client and server concurrently
npm run server      # Run only backend server
npm run client      # Run only frontend client
npm run test        # Run all tests
npm run test:quick  # Run tests with minimal output
npm run test:coverage  # Generate coverage report
```

---

## Testing the Application

### 1. Unit Tests

**Run all unit tests:**
```bash
cd backend
source venv/bin/activate
pytest test_unit.py -v
```

**Run specific unit test:**
```bash
pytest test_unit.py::TestInterviewSession::test_create_session -v
```

**Run with coverage report:**
```bash
pytest test_unit.py --cov=app --cov-report=html
```

**Unit tests cover:**
- Database model creation and updates
- Session persistence
- Data validation
- REST API endpoints
- Concurrent access patterns

### 2. Integration Tests

**Run all integration tests:**
```bash
cd backend
source venv/bin/activate
pytest test_integration.py -v
```

**Run specific integration test:**
```bash
pytest test_integration.py::TestServerIntegration::test_create_session_endpoint -v
```

**Run with verbose output:**
```bash
pytest test_integration.py -v -s
```

**Integration tests cover:**
- Server endpoints (HTTP)
- WebSocket connections
- Code synchronization between users
- User join/leave notifications
- Language change propagation
- Multi-user collaboration scenarios
- Error handling
- Large file handling

### 3. All Tests

**Run entire test suite:**
```bash
cd backend
source venv/bin/activate
pytest -v
```

**Generate coverage report:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```
Coverage report will be in `htmlcov/index.html`

---

## Manual Testing

### Test 1: Create and Join Session

1. Open `http://localhost:8000`
2. Click "Create Interview Session"
3. Copy the session code
4. In a new tab, paste the code and click "Join"
5. You should see both users in the session

**Expected:** Code changes sync in real-time

### Test 2: Code Execution

**JavaScript:**
```javascript
console.log("Hello World");
console.log(2 + 2);
```

**Python:**
```python
print("Hello Python")
x = [1, 2, 3]
print(sum(x))
```

**HTML:**
```html
<h1>Hello</h1>
<p style="color: blue;">Test</p>
```

### Test 3: Multi-User Collaboration

1. Open the same session in 3 browser tabs
2. Type code in different tabs
3. Verify all tabs show the same code
4. Verify user count updates

---

## API Testing with curl

### Create Session
```bash
curl -X POST http://localhost:5000/api/session
```

### Get Session Details
```bash
curl http://localhost:5000/api/session/ABC123XY
```

### Access Interview Page
```bash
curl http://localhost:5000/interview/ABC123XY
```

---

## Project Structure

```
online-coding-interviews/
├── backend/
│   ├── app.py                      # Flask + Socket.IO server
│   ├── requirements.txt            # Python dependencies
│   ├── test_unit.py                # Unit tests (~300 lines)
│   ├── test_integration.py         # Integration tests (~500 lines)
│   └── venv/                       # Virtual environment
├── frontend/
│   ├── static/
│   │   ├── app.js                  # Landing page
│   │   ├── editor.js               # Editor logic
│   │   └── styles.css              # Styling
│   └── templates/
│       ├── index.html              # Landing page
│       └── editor.html             # Editor page
└── Documentation/
    ├── README.md                   # This file
    ├── QUICKSTART.md
    ├── TESTING.md
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    └── ... (more docs)
```

---

## Installation

### Prerequisites
- Python 3.8+
- pip
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

---

## Usage

### Creating an Interview Session

1. Open `http://localhost:5000` in your browser
2. Click "Create Interview Session"
3. Share the generated session code or URL with candidates
4. Code changes will sync automatically to all connected users

### Joining an Interview Session

1. Open `http://localhost:5000`
2. Enter the session code in the "Join Existing Session" field
3. Click "Join Session"
4. Alternatively, directly access the shared URL

### Using the Editor

1. **Select Language**: Choose from the dropdown menu (default: JavaScript)
2. **Write Code**: Type or paste your code in the editor
3. **Execute Code**: Click "Execute Code" button to run the code
4. **View Output**: Results appear in the output panel below
5. **Real-time Updates**: All changes are immediately shared with connected users
6. **Copy Link**: Share the session link by clicking "Copy Link"

---

## Supported Languages

- **JavaScript** - Executed in browser, full support
- **Python** - Executed using Pyodide (WebAssembly runtime)
- **HTML** - Rendered in iframe preview
- **CSS** - Full styling support in HTML preview
- **Java, C++, C#, Ruby, PHP, Go, Rust, SQL** - Basic syntax highlighting (server-side execution available on request)

---

## How It Works

### Real-time Synchronization

1. **WebSocket Connection**: Users connect to the Flask-SocketIO server
2. **Session Management**: Each interview session has a unique ID and code state
3. **Code Broadcasting**: When a user edits code, changes are broadcast to all connected users
4. **Language Sync**: Language changes are shared across all users in the session

### Code Execution

- **JavaScript**: Runs in browser using native `eval()` with console capture
- **Python**: Executes using Pyodide (Python runtime compiled to WebAssembly)
- **HTML/CSS**: Rendered in a sandboxed iframe for safe preview
- **Other Languages**: Basic syntax highlighting only (can be extended with API calls to execution services)

---

## API Endpoints

### REST API

- `POST /api/session` - Create new interview session
- `GET /api/session/<session_code>` - Get session details
- `GET /interview/<session_code>` - Load interview page

### WebSocket Events

**Client → Server:**
- `join_session` - Join an interview session
- `code_change` - Notify code update
- `language_change` - Change programming language
- `execute_code` - Request code execution

**Server → Client:**
- `user_joined` - User joined the session
- `user_left` - User left the session
- `code_updated` - Code was updated by another user
- `language_updated` - Language was changed by another user
- `sync_code` - Sync current code and language to new user
- `error` - Error occurred

---

## Database

The application uses SQLite to persist interview sessions. Each session stores:
- Unique session ID
- Session code (human-readable)
- Current code
- Current language
- Connected user count
- Creation timestamp

---

## Testing Overview

### What's Tested

**Unit Tests (test_unit.py)**
- InterviewSession model CRUD operations
- Database persistence
- Data validation
- REST endpoint responses
- CORS headers
- Concurrent access patterns

**Integration Tests (test_integration.py)**
- HTTP endpoint creation
- WebSocket connection handling
- Real-time code synchronization between multiple clients
- Language change propagation
- User join/leave notifications
- Multi-user collaboration scenarios
- Error handling for invalid inputs
- Large code file transmission

### Test Execution Patterns

```bash
# Quick test (30 seconds)
pytest test_unit.py -v

# Full integration test (1-2 minutes)
pytest test_integration.py -v

# Everything with coverage
pytest --cov=app --cov-report=term-missing

# Watch mode (requires pytest-watch)
ptw -- -v
```

---

## Performance Considerations

- WebSocket ensures minimal latency for real-time updates
- Code changes are optimized to preserve cursor position
- Pyodide loads asynchronously without blocking the UI
- Ace editor is performant even with large code files

---

## Security Notes

⚠️ **Important**: This is for educational/interview purposes. For production use, consider:

1. **Code Execution**: Never execute untrusted code on a public server
   - Current implementation executes in browser only
   - For server-side execution, use isolated containers (Docker/Kubernetes)
   - Implement timeouts and memory limits

2. **Session Security**:
   - Add authentication/authorization
   - Use session tokens instead of simple codes
   - Implement HTTPS/WSS in production
   - Add session expiration

3. **Data Privacy**:
   - Encrypt session data in transit (SSL/TLS)
   - Don't store sensitive code on disk
   - Implement audit logging

---

## Troubleshooting

### WebSocket Connection Issues
- Ensure Flask-SocketIO is installed: `pip install flask-socketio`
- Check firewall settings
- Try clearing browser cache

### Tests Failing
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Clear pytest cache
pytest --cache-clear
```

### Code Execution Not Working
- Verify Pyodide is loading (check browser console)
- JavaScript errors should appear in output panel
- Python requires Pyodide CDN to be accessible

### Database Errors
- Delete `coding_interviews.db` and restart server to reset
- Ensure write permissions in backend directory

---

## Dependencies

See `backend/requirements.txt` for all dependencies:
- Flask 2.3.3
- Flask-SocketIO 5.3.4
- SQLAlchemy 2.0
- Pytest 7.4.2
- And more...

Install with:
```bash
pip install -r backend/requirements.txt
```

---

## Contributing

Feel free to extend this project with:
- Additional language support
- Better code execution sandboxing
- Performance optimizations
- UI/UX improvements
- Additional features
- More comprehensive tests

---

## License

MIT License - Feel free to use for educational and commercial purposes.

---

## Support

For issues or questions:
## Documentation

| Document | Purpose |
|----------|---------|
| [DOCKER.md](DOCKER.md) | Docker deployment guide with commands |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment & scaling |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture & design |
| [TESTING.md](TESTING.md) | Testing guide & test cases |

## Implementation Status

✅ All 5 core requirements implemented:
1. ✅ Session sharing - Generate codes & share links
2. ✅ Real-time editing - WebSocket synchronization
3. ✅ Multi-language - JavaScript & Python with syntax highlighting
4. ✅ Syntax highlighting - Ace editor with Monokai theme
5. ✅ Browser execution - Pyodide (Python) + Native JS

### Test Coverage
- ✅ 20 Unit Tests (passing)
- ✅ 16 Integration Tests (passing)
- ✅ 36/36 tests passing

### Deployment Options
- ✅ Docker (recommended)
- ✅ Local development
- ✅ Cloud platforms (AWS, GCP, Azure)
- ✅ Kubernetes ready

## Supported Languages

**Fully Supported** (with execution):
- JavaScript (native browser execution)
- Python (Pyodide/WASM)

## Troubleshooting

1. Check the relevant .md file (see Documentation section above)
2. Review TESTING.md for test procedures
3. See ARCHITECTURE.md for technical details
4. Check code comments

---

**Happy coding! 🚀**

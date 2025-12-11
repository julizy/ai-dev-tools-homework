# Testing Guide - Online Coding Interview Platform

## Quick Start

### 1. Start the Server

The server is pre-configured and should be running on port 8000.

Access the platform at: **http://localhost:8000**

If you need to restart:
```bash
cd backend
PORT=8000 venv/bin/python app.py
```

### 2. Access the Platform

Open your browser and navigate to: `http://localhost:8000`

You should see the landing page with options to:
- Create a new interview session
- Join an existing session

## Testing Features

### Test 1: Create an Interview Session

1. Click "Create Interview Session" button
2. You'll see a modal with:
   - Share Link
   - Session Code
3. Copy and note the session code (e.g., "ABC123XY")
4. You'll be redirected to the editor page

**Expected Results:**
- ✓ Session code displayed in the header
- ✓ Code editor is ready (Ace editor with syntax highlighting)
- ✓ Output panel is empty
- ✓ User count shows "1"

### Test 2: Real-time Code Synchronization

1. Create a session (from Test 1)
2. Open a new browser tab/window
3. Navigate to `http://localhost:8000`
4. Click "Join Existing Session"
5. Enter the session code from Test 1
6. In the first tab, type some code in the editor

**Expected Results:**
- ✓ Code appears in the second tab in real-time
- ✓ Both tabs show "Users: 2"
- ✓ Changes sync instantly

### Test 3: Multi-language Support

In any active session:

1. **JavaScript:**
   - Select "JavaScript" from dropdown
   - Type: `console.log('Hello World'); 5 + 3`
   - Click "Execute Code"
   - Expected output: `Hello World` and `8`

2. **Python:**
   - Select "Python" from dropdown
   - Type: `print('Hello Python'); x = [1,2,3]; print(sum(x))`
   - Click "Execute Code"
   - Expected output: `Hello Python` and `6`

3. **HTML:**
   - Select "HTML" from dropdown
   - Type: `<h1>Hello World</h1><p>This is HTML</p>`
   - Click "Execute Code"
   - Expected: HTML rendered in output panel

4. **Language Changes Sync:**
   - Have 2 users in the session
   - Change language in one tab
   - Expected: Other tab automatically switches language

### Test 4: Code Execution

#### JavaScript Execution
```javascript
// Test 1: Simple arithmetic
const result = 10 + 20;
console.log(result);  // Output: 30

// Test 2: Functions
function add(a, b) {
  return a + b;
}
console.log(add(5, 3));  // Output: 8

// Test 3: Array operations
const arr = [1, 2, 3, 4, 5];
console.log(arr.map(x => x * 2));  // Output: [2,4,6,8,10]
```

#### Python Execution
```python
# Test 1: Print statements
print("Hello from Python")
print(5 + 3)

# Test 2: Functions
def greet(name):
    return f"Hello, {name}"
print(greet("World"))

# Test 3: Lists and loops
for i in range(5):
    print(i)
```

#### HTML/CSS Rendering
```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: Arial; margin: 20px; }
  h1 { color: #007acc; }
  .box { background: #f0f0f0; padding: 10px; margin: 10px 0; }
</style>
</head>
<body>
  <h1>Live HTML Preview</h1>
  <div class="box">This is a styled box</div>
  <p>You can render and preview HTML/CSS here!</p>
</body>
</html>
```

### Test 5: User Collaboration

#### Two Users Editing:
1. Create a session in Tab 1
2. Join same session in Tab 2
3. In Tab 1, type: `// User 1 editing`
4. In Tab 2, add: `console.log('User 2');`
5. Switch between tabs

**Expected Results:**
- ✓ Both edits appear in both tabs
- ✓ Code is merged and synchronized
- ✓ Cursor position is preserved when updates arrive

#### User Join/Leave Notifications:
1. Have a session open in Tab 1
2. Open Tab 2 and join the same session
3. Watch Tab 1 - notification shows "User joined (Total: 2)"
4. Close Tab 2
5. Watch Tab 1 - notification shows "User left (Total: 1)"

### Test 6: Session Code Sharing

1. Create a session
2. Click "Copy Link" button
3. In a new browser window (incognito/private):
   - Paste the URL
   - Should join the same session
   - Code and language should sync
   - User count should update

4. Alternative - Use session code:
   - Copy the session code (e.g., "ABC123XY")
   - Go to home page
   - Enter code in "Join Session" field
   - Click Join
   - Should connect to same session

### Test 7: UI/UX Features

1. **Copy Link Button:**
   - Click it multiple times
   - Should show "Copied to clipboard!" notification
   - Link should be correct

2. **Language Dropdown:**
   - Select different languages
   - Code highlighting changes for each
   - Language persists in session

3. **Clear Code Button:**
   - Write some code
   - Click "Clear Code"
   - Code should be empty

4. **Clear Output Button:**
   - Execute code
   - See output
   - Click "Clear Output"
   - Output panel should be empty

5. **Responsive Design:**
   - Resize browser window
   - UI should adapt (sidebar collapsible on mobile)
   - Editor and output should still be accessible

### Test 8: Error Handling

#### JavaScript Errors:
```javascript
// This should show error message
const x = undefined.property;
```
Expected: Error displayed in output panel in red

#### Python Errors:
```python
# This should show error message
undefined_variable
```
Expected: Error displayed in output panel in red

#### Invalid Session:
1. Go to `http://localhost:8000/interview/INVALID`
2. Should show error page
3. Click "Back to Home" button
4. Should redirect to home page

### Test 9: Load Testing

#### Multiple Concurrent Users:
1. Open the same session in 5 different browser windows
2. All tabs should show "Users: 5"
3. Type in one tab
4. Code should appear in all other tabs (slight delay may occur)

**Expected Performance:**
- Code sync should occur within 100-200ms
- No significant lag with 5 concurrent users
- Server should handle without errors

### Test 10: Browser Compatibility

Test on:
- ✓ Chrome/Chromium
- ✓ Firefox
- ✓ Safari
- ✓ Edge

**Expected:** All features work consistently

## Troubleshooting

### Issue: Server won't start
**Solution:**
```bash
# Check if port 8000 is in use
netstat -an | grep 8000

# Kill process on port 8000 (macOS/Linux)
pkill -f "python app.py"

# Restart server
cd backend
PORT=8000 venv/bin/python app.py
```

### Issue: WebSocket connection fails
**Solution:**
- Check browser console for errors (F12)
- Verify server is running
- Clear browser cache
- Try different port (PORT=8001)

### Issue: Pyodide not loading for Python
**Solution:**
- Wait a few seconds for Pyodide to load
- Check network tab in browser DevTools
- Ensure internet connection is active
- Pyodide CDN must be accessible

### Issue: Code doesn't sync between tabs
**Solution:**
- Ensure both tabs have the same session code
- Check browser console for errors
- Refresh the page
- Both users should be in same room (check server logs)

### Issue: Syntax highlighting not working
**Solution:**
- Try refreshing page
- Check that Ace editor libraries loaded (Network tab)
- Select the language explicitly from dropdown

## Performance Metrics

### Expected Benchmarks:
- Page load time: < 2 seconds
- Code sync latency: < 200ms
- Pyodide load time: 3-5 seconds (first load)
- Max concurrent users in session: 50+
- Max code size: 100KB+ (depending on browser memory)

## Test Checklist

- [ ] Server starts on port 8000
- [ ] Landing page loads
- [ ] Can create new session
- [ ] Can join session with code
- [ ] Code syncs in real-time
- [ ] JavaScript code executes
- [ ] Python code executes
- [ ] HTML/CSS renders
- [ ] Language dropdown works
- [ ] Multi-user sees each other
- [ ] User count updates
- [ ] Copy link functionality works
- [ ] Clear buttons work
- [ ] Error messages display properly
- [ ] Mobile responsive
- [ ] No console errors

## Notes

- First Python execution may take 3-5 seconds (Pyodide initialization)
- Code execution is sandboxed in the browser
- For production, implement code timeouts and resource limits
- WebSocket requires modern browser (IE11+ not supported)

---

**Happy Testing! 🚀**

// Main application script for landing/creation page
let socket = null;
let editor = null;
let currentSessionCode = null;
let currentLanguage = 'javascript';
let pyodideReady = false;

// Initialize Pyodide
async function initPyodide() {
    try {
        let pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
        });
        window.pyodide = pyodide;
        pyodideReady = true;
        console.log('Pyodide loaded successfully');
    } catch (error) {
        console.error('Error loading Pyodide:', error);
    }
}

// Initialize Socket.IO connection
function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('error', (data) => {
        showNotification(`Error: ${data.message}`, 'error');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
}

// Initialize Ace Editor
function initEditor() {
    editor = ace.edit('editor');
    editor.setTheme('ace/theme/monokai');
    editor.session.setMode('ace/mode/javascript');
    editor.setShowPrintMargin(false);
    editor.setFontSize(14);
    editor.setHighlightActiveLine(true);
    editor.setShowInvisibles(false);

    // Set initial code
    editor.setValue('// Start coding here...\n', -1);

    // Listen for changes
    editor.on('change', () => {
        if (currentSessionCode) {
            const code = editor.getValue();
            socket.emit('code_change', {
                session_code: currentSessionCode,
                code: code
            });
        }
    });
}

// Language mode mapping
const languageModes = {
    'javascript': 'ace/mode/javascript',
    'python': 'ace/mode/python',
    'java': 'ace/mode/java',
    'cpp': 'ace/mode/c_cpp',
    'csharp': 'ace/mode/csharp',
    'ruby': 'ace/mode/ruby',
    'php': 'ace/mode/php',
    'go': 'ace/mode/golang',
    'rust': 'ace/mode/rust',
    'sql': 'ace/mode/sql',
    'html': 'ace/mode/html',
    'css': 'ace/mode/css'
};

// Change language
function changeLanguage(language) {
    currentLanguage = language;
    const mode = languageModes[language] || 'ace/mode/javascript';
    editor.session.setMode(mode);

    if (currentSessionCode) {
        socket.emit('language_change', {
            session_code: currentSessionCode,
            language: language
        });
    }
}

// Execute code
async function executeCode() {
    const code = editor.getValue();
    const outputPanel = document.getElementById('output');
    outputPanel.textContent = 'Executing...';

    try {
        if (currentLanguage === 'javascript') {
            executeJavaScript(code, outputPanel);
        } else if (currentLanguage === 'python') {
            await executePython(code, outputPanel);
        } else if (currentLanguage === 'html') {
            executeHTML(code, outputPanel);
        } else {
            outputPanel.textContent = `Execution not yet supported for ${currentLanguage}. (Server-side execution available upon request)`;
        }
    } catch (error) {
        outputPanel.textContent = `Error: ${error.message}`;
        outputPanel.classList.add('error');
    }
}

// Execute JavaScript
function executeJavaScript(code, outputPanel) {
    const originalLog = console.log;
    let output = '';

    // Override console.log
    console.log = function(...args) {
        output += args.map(arg => {
            if (typeof arg === 'object') {
                return JSON.stringify(arg, null, 2);
            }
            return String(arg);
        }).join(' ') + '\n';
    };

    try {
        const result = eval(code);
        if (result !== undefined) {
            output += String(result);
        }
        outputPanel.textContent = output || '(no output)';
        outputPanel.classList.remove('error');
        outputPanel.classList.add('success');
    } catch (error) {
        outputPanel.textContent = `Error: ${error.message}`;
        outputPanel.classList.add('error');
    } finally {
        console.log = originalLog;
        setTimeout(() => {
            outputPanel.classList.remove('success');
            outputPanel.classList.remove('error');
        }, 3000);
    }
}

// Execute Python
async function executePython(code, outputPanel) {
    if (!pyodideReady) {
        outputPanel.textContent = 'Python runtime is loading... Please try again in a moment.';
        return;
    }

    try {
        let pyodide = window.pyodide;

        // Capture stdout
        const originalStdout = pyodide.runPython(`
            import sys
            import io
            sys.stdout = io.StringIO()
        `);

        // Execute the code
        const result = pyodide.runPython(code);

        // Get the captured output
        const output = pyodide.runPython('sys.stdout.getvalue()');

        outputPanel.textContent = output || '(no output)';
        outputPanel.classList.remove('error');
        outputPanel.classList.add('success');
    } catch (error) {
        outputPanel.textContent = `Error: ${error.message}`;
        outputPanel.classList.add('error');
    } finally {
        setTimeout(() => {
            outputPanel.classList.remove('success');
            outputPanel.classList.remove('error');
        }, 3000);
    }
}

// Execute HTML (renders in output panel)
function executeHTML(code, outputPanel) {
    const iframe = document.createElement('iframe');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    iframe.style.background = 'white';

    outputPanel.innerHTML = '';
    outputPanel.appendChild(iframe);

    iframe.contentDocument.open();
    iframe.contentDocument.write(code);
    iframe.contentDocument.close();
}

// Create session
async function createSession() {
    try {
        const response = await fetch('/api/session', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            currentSessionCode = data.session_code;
            showEditorPage();
            connectToSession(data.session_code);
            displayShareModal(data.session_code, data.url);
        }
    } catch (error) {
        showNotification(`Error creating session: ${error}`, 'error');
    }
}

// Join session
async function joinSession(sessionCode) {
    try {
        const response = await fetch(`/api/session/${sessionCode}`);
        const data = await response.json();

        if (data.success) {
            currentSessionCode = sessionCode;
            showEditorPage();
            connectToSession(sessionCode);
            document.getElementById('sessionCodeDisplay').textContent = sessionCode;
        } else {
            showNotification('Session not found', 'error');
        }
    } catch (error) {
        showNotification(`Error joining session: ${error}`, 'error');
    }
}

// Connect to WebSocket session
function connectToSession(sessionCode) {
    socket.emit('join_session', { session_code: sessionCode });
}

// Show editor page
function showEditorPage() {
    document.getElementById('landingPage').classList.add('hidden');
    document.getElementById('editorPage').classList.remove('hidden');
}

// Display share modal
function displayShareModal(sessionCode, url) {
    const modal = document.getElementById('shareModal');
    document.getElementById('shareCode').textContent = sessionCode;
    document.getElementById('shareLink').value = window.location.origin + url;
    modal.classList.remove('hidden');
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        showNotification('Failed to copy', 'error');
    });
}

// Initialize everything
window.addEventListener('DOMContentLoaded', () => {
    initPyodide();
    initSocket();
    initEditor();

    // Event listeners
    document.getElementById('createSessionBtn').addEventListener('click', createSession);
    document.getElementById('createSessionBtnLanding').addEventListener('click', createSession);
    document.getElementById('joinSessionBtn').addEventListener('click', () => {
        const code = document.getElementById('sessionCodeInput').value.trim().toUpperCase();
        if (code) {
            joinSession(code);
        } else {
            showNotification('Please enter a session code', 'error');
        }
    });

    document.getElementById('languageSelect').addEventListener('change', (e) => {
        changeLanguage(e.target.value);
    });

    document.getElementById('executeBtn').addEventListener('click', executeCode);

    document.getElementById('clearBtn').addEventListener('click', () => {
        editor.setValue('');
    });

    document.getElementById('clearOutputBtn').addEventListener('click', () => {
        document.getElementById('output').textContent = '';
    });

    document.getElementById('leaveBtn').addEventListener('click', () => {
        window.location.href = '/';
    });

    document.getElementById('copyLinkBtn').addEventListener('click', () => {
        const url = window.location.origin + '/interview/' + currentSessionCode;
        copyToClipboard(url);
    });

    // Modal close
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('shareModal').classList.add('hidden');
    });

    document.getElementById('copyShareLinkBtn').addEventListener('click', () => {
        const link = document.getElementById('shareLink').value;
        copyToClipboard(link);
    });

    // Socket events
    if (socket) {
        socket.on('user_joined', (data) => {
            document.getElementById('userCount').textContent = `👥 Users: ${data.user_count}`;
            showNotification(`User joined (Total: ${data.user_count})`);
        });

        socket.on('code_updated', (data) => {
            const currentCode = editor.getValue();
            const newCode = data.code;
            if (currentCode !== newCode) {
                const cursorPos = editor.getCursorPosition();
                editor.setValue(newCode, -1);
                editor.moveCursorToPosition(cursorPos);
            }
        });

        socket.on('language_updated', (data) => {
            currentLanguage = data.language;
            document.getElementById('languageSelect').value = data.language;
            changeLanguage(data.language);
        });

        socket.on('sync_code', (data) => {
            editor.setValue(data.code, -1);
            currentLanguage = data.language;
            document.getElementById('languageSelect').value = data.language;
            changeLanguage(data.language);
        });

        socket.on('user_left', (data) => {
            document.getElementById('userCount').textContent = `👥 Users: ${data.user_count}`;
            showNotification(`User left (Total: ${data.user_count})`);
        });
    }
});

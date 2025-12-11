// Editor page script - for joining existing interview sessions
let socket = null;
let editor = null;
let currentSessionCode = null;
let currentLanguage = 'javascript';
let pyodideReady = false;

// Get session code from URL
function getSessionCodeFromURL() {
    const parts = window.location.pathname.split('/');
    return parts[parts.length - 1];
}

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
        currentSessionCode = getSessionCodeFromURL();
        joinSession();
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
    editor.setValue('// Waiting to join session...\n', -1);

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
    'python': 'ace/mode/python'
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
        } else {
            outputPanel.textContent = `Execution not yet supported for ${currentLanguage}.`;
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
        pyodide.runPython(`
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

// Join session
function joinSession() {
    try {
        document.getElementById('sessionCodeDisplay').textContent = currentSessionCode;
        document.getElementById('loadingPage').classList.add('hidden');
        document.getElementById('editorPage').classList.remove('hidden');

        socket.emit('join_session', { session_code: currentSessionCode });
    } catch (error) {
        showError(`Error joining session: ${error.message}`);
    }
}

// Show error page
function showError(message) {
    document.getElementById('loadingPage').classList.add('hidden');
    document.getElementById('errorPage').classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
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
        const url = window.location.href;
        copyToClipboard(url);
    });

    document.getElementById('backToHomeBtn').addEventListener('click', () => {
        window.location.href = '/';
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
            showNotification('Session synced successfully');
        });

        socket.on('user_left', (data) => {
            document.getElementById('userCount').textContent = `👥 Users: ${data.user_count}`;
            showNotification(`User left (Total: ${data.user_count})`);
        });

        socket.on('error', (data) => {
            showError(data.message || 'Session not found or connection error');
        });
    }
});

// Main application script for landing/creation page
let socket = null;
let editor = null;
let currentSessionCode = null;
let currentLanguage = 'javascript';
let pyodideReady = false;
let pyodideWorkerReady = false;
let isUpdatingOwnCode = false; // Flag to prevent self-update loops

// Detect Safari
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

// Initialize Pyodide (now using Worker)
async function initPyodide() {
    try {
        await initPyodideWorker();
        pyodideWorkerReady = true;
        pyodideReady = true;
        console.log('Pyodide Worker loaded successfully');
        showNotification('Python runtime ready', 'success');
    } catch (error) {
        console.error('Error loading Pyodide Worker:', error);
        showNotification('Error loading Python runtime', 'error');
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

    // Enhanced syntax highlighting settings
    editor.session.setUseWorker(true); // Enable worker for better performance
    editor.setHighlightSelectedWord(true); // Highlight all occurrences of selected word
    editor.session.setTabSize(4);
    editor.session.setUseSoftTabs(true);
    editor.setOption('useWrapMode', false);
    editor.setOption('enableSnippets', true);
    editor.setOption('enableLiveAutocompletion', true);
    editor.setOption('enableBasicAutocompletion', true);

    // Set initial code
    editor.setValue('// Start coding here...\n', -1);

    // Listen for changes with debounce to prevent excessive broadcasts
    let changeTimeout;
    editor.on('change', () => {
        if (currentSessionCode && !isUpdatingOwnCode) {
            clearTimeout(changeTimeout);
            changeTimeout = setTimeout(() => {
                const code = editor.getValue();
                isUpdatingOwnCode = true;
                socket.emit('code_change', {
                    session_code: currentSessionCode,
                    code: code
                });
                // Reset flag after sending
                setTimeout(() => {
                    isUpdatingOwnCode = false;
                }, 100);
            }, 500); // Debounce: wait 500ms after user stops typing
        }
    });
}

// Language mode mapping
const languageModes = {
    'javascript': 'ace/mode/javascript',
    'python': 'ace/mode/python'
};

// Change language
function changeLanguage(language, fromSocket = false) {
    currentLanguage = language;
    const mode = languageModes[language] || 'ace/mode/javascript';
    editor.session.setMode(mode);

    // Only emit if this change was initiated by the user, not from socket
    if (currentSessionCode && !fromSocket) {
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
            outputPanel.textContent = `Execution not supported for ${currentLanguage}.`;
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
        // Create a function from the code instead of using eval
        const asyncFunction = new Function(code);
        const result = asyncFunction();

        // Handle async results
        if (result instanceof Promise) {
            result.then(res => {
                if (res !== undefined) {
                    output += String(res);
                }
                outputPanel.textContent = output || '(no output)';
                outputPanel.classList.remove('error');
                outputPanel.classList.add('success');
            }).catch(err => {
                outputPanel.textContent = `Error: ${err.message}`;
                outputPanel.classList.add('error');
            });
        } else {
            if (result !== undefined) {
                output += String(result);
            }
            outputPanel.textContent = output || '(no output)';
            outputPanel.classList.remove('error');
            outputPanel.classList.add('success');
        }
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

// Execute Python using Web Worker
async function executePython(code, outputPanel) {
    if (!pyodideWorkerReady) {
        outputPanel.textContent = '⏳ Python runtime is still loading... This can take 10-30 seconds on first use. Please wait and try again.';
        outputPanel.classList.add('error');
        return;
    }

    if (!code.trim()) {
        outputPanel.textContent = '(no code to execute)';
        return;
    }

    try {
        outputPanel.textContent = 'Executing...';
        const output = await executePythonInWorker(code);

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
            // Only update if not currently typing (wait for debounce)
            if (!isUpdatingOwnCode) {
                const currentCode = editor.getValue();
                const newCode = data.code;
                if (currentCode !== newCode) {
                    const cursorPos = editor.getCursorPosition();
                    isUpdatingOwnCode = true;
                    editor.setValue(newCode, -1);
                    editor.moveCursorToPosition(cursorPos);
                    setTimeout(() => {
                        isUpdatingOwnCode = false;
                    }, 100);
                }
            }
        });

        socket.on('language_updated', (data) => {
            currentLanguage = data.language;
            document.getElementById('languageSelect').value = data.language;
            changeLanguage(data.language, true);
        });

        socket.on('sync_code', (data) => {
            editor.setValue(data.code, -1);
            currentLanguage = data.language;
            document.getElementById('languageSelect').value = data.language;
            changeLanguage(data.language, true);
        });

        socket.on('user_left', (data) => {
            document.getElementById('userCount').textContent = `👥 Users: ${data.user_count}`;
            showNotification(`User left (Total: ${data.user_count})`);
        });
    }
});

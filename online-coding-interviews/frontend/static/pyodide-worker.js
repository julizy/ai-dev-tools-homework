// Web Worker for Python execution
let pyodideWorker = null;

async function initPyodideWorker() {
    return new Promise((resolve) => {
        const workerCode = `
importScripts('https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js');

let pyodide = null;

async function initPyodide() {
    try {
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
        });
        self.postMessage({ type: 'ready', data: 'Python runtime loaded' });
    } catch (error) {
        self.postMessage({ type: 'error', data: error.message });
    }
}

self.onmessage = async function(event) {
    if (event.data.type === 'init') {
        await initPyodide();
    } else if (event.data.type === 'execute') {
        try {
            const code = event.data.code;

            // Simple approach: capture stdout and run code
            const wrappedCode = \`
import sys
import io
from io import StringIO

# Redirect stdout
old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    exec('''\\n\${code}\\n''')
    output = sys.stdout.getvalue()
except Exception as e:
    import traceback
    output = traceback.format_exc()
finally:
    sys.stdout = old_stdout

output
\`;

            const output = pyodide.runPython(wrappedCode);

            self.postMessage({ type: 'success', data: output });
        } catch (error) {
            self.postMessage({ type: 'error', data: error.toString() });
        }
    }
};

initPyodide();
`;

        const blob = new Blob([workerCode], { type: 'application/javascript' });
        const workerURL = URL.createObjectURL(blob);
        pyodideWorker = new Worker(workerURL);

        pyodideWorker.onmessage = (event) => {
            if (event.data.type === 'ready') {
                resolve(true);
            }
        };

        pyodideWorker.postMessage({ type: 'init' });
    });
}

function executePythonInWorker(code) {
    return new Promise((resolve, reject) => {
        const handler = (event) => {
            pyodideWorker.removeEventListener('message', handler);
            if (event.data.type === 'success') {
                resolve(event.data.data);
            } else if (event.data.type === 'error') {
                reject(new Error(event.data.data));
            }
        };

        pyodideWorker.addEventListener('message', handler);
        pyodideWorker.postMessage({ type: 'execute', code: code });
    });
}

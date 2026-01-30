// electron/main.js
// Electron main process - manages window and Python backend

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// Determine if we're in development or production
const isDev = !app.isPackaged;

// Get the backend path
function getBackendPath() {
  if (isDev) {
    return path.join(__dirname, '..', '..', 'backend');
  }
  return path.join(process.resourcesPath, 'backend');
}

// Check if bundled executable exists
function getBundledExecutable() {
  const backendPath = getBackendPath();
  const exeName = process.platform === 'win32' ? 'ma-grader-server.exe' : 'ma-grader-server';
  const exePath = path.join(backendPath, 'dist', exeName);
  
  if (require('fs').existsSync(exePath)) {
    return exePath;
  }
  return null;
}

// Start Python backend server
function startPythonBackend() {
  const backendPath = getBackendPath();
  const bundledExe = getBundledExecutable();
  
  // Set UTF-8 encoding to handle emoji/unicode in output (fixes Windows encoding errors)
  const processEnv = {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1'
  };
  
  if (bundledExe && !isDev) {
    // Production: use bundled executable
    console.log('Starting bundled backend:', bundledExe);
    
    pythonProcess = spawn(bundledExe, [], {
      cwd: backendPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: processEnv
    });
  } else {
    // Development: use Python directly
    const serverScript = path.join(backendPath, 'server.py');
    console.log('Starting Python backend from:', serverScript);
    
    // Use python3 on macOS/Linux, python on Windows
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    pythonProcess = spawn(pythonCmd, [serverScript], {
      cwd: backendPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: processEnv
    });
  }
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Backend] ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Backend Error] ${data}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Backend exited with code ${code}`);
  });
  
  pythonProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });
}

// Stop Python backend
function stopPythonBackend() {
  if (pythonProcess) {
    console.log('Stopping Python backend...');
    pythonProcess.kill();
    pythonProcess = null;
  }
}

// Get the icon path based on platform
function getIconPath() {
  let assetsPath;
  if (isDev) {
    assetsPath = path.join(__dirname, '..', 'assets');
  } else {
    // In production, assets are inside the app.asar or app folder
    assetsPath = path.join(app.getAppPath(), 'assets');
  }
  
  if (process.platform === 'win32') {
    return path.join(assetsPath, 'icon.ico');
  } else {
    // Use PNG for macOS and Linux (more reliable in dev mode)
    return path.join(assetsPath, 'logo.png');
  }
}

// Create the main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 800,
    minWidth: 900,
    minHeight: 700,
    backgroundColor: '#0a0e14',
    icon: getIconPath(),
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 15, y: 15 },
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    }
  });

  // Enable drag and drop
  mainWindow.webContents.on('will-navigate', (event) => {
    event.preventDefault();
  });
  
  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(() => {
  // Set dock icon on macOS (needs PNG, not icns) - use padded version
  if (process.platform === 'darwin' && app.dock) {
    const iconPath = path.join(__dirname, '..', 'assets', 'logo-padded.png');
    if (require('fs').existsSync(iconPath)) {
      try {
        app.dock.setIcon(iconPath);
      } catch (e) {
        console.log('Could not set dock icon:', e.message);
      }
    }
  }
  
  startPythonBackend();
  
  // Wait a moment for Python to start, then create window
  setTimeout(createWindow, 1000);
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  stopPythonBackend();
});

// IPC Handlers for renderer process
ipcMain.handle('dialog:openFile', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: options?.filters || [{ name: 'ZIP Files', extensions: ['zip'] }]
  });
  return result.filePaths[0] || null;
});

ipcMain.handle('dialog:openDirectory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0] || null;
});

ipcMain.handle('shell:openPath', async (event, folderPath) => {
  if (folderPath) {
    shell.openPath(folderPath);
  }
});

ipcMain.handle('clipboard:write', async (event, text) => {
  const { clipboard } = require('electron');
  clipboard.writeText(text);
});

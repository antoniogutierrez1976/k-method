import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';
import http from 'http';

let mainWindow: BrowserWindow | null = null;
let sidecarProcess: ChildProcess | null = null;

function checkBackendHealth(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:8000/api/status', (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1500, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function ensureBackendRunning() {
  const isHealthy = await checkBackendHealth();
  if (isHealthy) {
    console.log('[Sidecar] Python ASGI backend is already running on port 8000.');
    return;
  }

  console.log('[Sidecar] Launching Python ASGI backend sidecar...');
  const repoRoot = app.isPackaged
    ? (process.env.K_METHOD_WORKSPACE || process.cwd())
    : path.resolve(__dirname, '../../');
  const pythonScript = path.join(repoRoot, 'scripts', 'harness', 'gui', 'launch.py');

  try {
    sidecarProcess = spawn('python', [pythonScript, '--headless'], {
      cwd: repoRoot,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: 'pipe',
      shell: true
    });

    sidecarProcess.stdout?.on('data', (data) => {
      console.log(`[Python Backend]: ${data.toString().trim()}`);
    });

    sidecarProcess.stderr?.on('data', (data) => {
      console.error(`[Python Backend Error]: ${data.toString().trim()}`);
    });

    sidecarProcess.on('exit', (code) => {
      console.log(`[Sidecar] Python process exited with code ${code}`);
      sidecarProcess = null;
    });
  } catch (err) {
    console.error('[Sidecar] Failed to start Python backend:', err);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    title: 'k-method app',
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#0d1117',
    frame: true,
    titleBarStyle: 'default',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Window control handlers
ipcMain.on('window-minimize', () => {
  mainWindow?.minimize();
});

ipcMain.on('window-maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.on('window-close', () => {
  mainWindow?.close();
});

app.whenReady().then(async () => {
  await ensureBackendRunning();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (sidecarProcess) {
    console.log('[Sidecar] Terminating Python sidecar process...');
    sidecarProcess.kill();
    sidecarProcess = null;
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (sidecarProcess) {
    sidecarProcess.kill();
    sidecarProcess = null;
  }
});

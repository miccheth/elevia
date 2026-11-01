import { app, shell, BrowserWindow, ipcMain, screen } from 'electron'
import { join } from 'path'
import { spawn } from 'child_process'
import { electronApp, is } from '@electron-toolkit/utils'
import icon from '../../resources/elevia-icon.png?asset'
import dockIcon from '../../resources/elevia-dock.png?asset'
import type { VocabularyRequest, VocabularyResponse } from '../preload/vocabulary'

function runVocabulary(request: VocabularyRequest): Promise<VocabularyResponse> {
  if (app.isPackaged) {
    return Promise.resolve({ error: 'Il core non è ancora disponibile nella versione installata.' })
  }

  const root = join(app.getAppPath(), '..')
  const python = join(
    root,
    '.venv',
    process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python'
  )
  return new Promise((resolve) => {
    const child = spawn(python, ['-m', 'app.desktop_bridge'], { cwd: root })
    let output = ''
    child.stdout.setEncoding('utf8')
    child.stdout.on('data', (chunk: string) => {
      output += chunk
    })
    child.on('error', () =>
      resolve({ error: 'Impossibile avviare il core. Controlla che .venv sia configurato.' })
    )
    child.on('close', (code) => {
      try {
        resolve(
          code === 0 ? JSON.parse(output) : { error: 'Errore durante l’esecuzione del core.' }
        )
      } catch {
        resolve({ error: 'Risposta non valida dal core.' })
      }
    })
    child.stdin.on('error', () => {})
    child.stdin.end(JSON.stringify(request))
  })
}

function createWindow(): void {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: Math.round(width * 0.85),
    height: Math.round(height * 0.85),
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    backgroundColor: '#0d1630',
    ...(process.platform === 'darwin'
      ? { titleBarStyle: 'hidden' as const, trafficLightPosition: { x: 16, y: 17 } }
      : {}),
    show: false,
    autoHideMenuBar: true,
    ...(process.platform !== 'darwin' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      devTools: false,
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  ipcMain.handle('vocabulary', (_, request: VocabularyRequest) => runVocabulary(request))
  if (process.platform === 'darwin' && is.dev) {
    app.dock?.setIcon(dockIcon)
    app.on('will-quit', () => app.dock?.hide())
  }
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  app.on('browser-window-created', (_, window) => {
    window.webContents.on('before-input-event', (event, input) => {
      if (input.type !== 'keyDown') return

      const commandOrControl = input.control || input.meta
      const devToolsShortcut =
        input.code === 'F12' ||
        (((input.control && input.shift) || (input.meta && input.alt)) &&
          ['KeyI', 'KeyJ', 'KeyC'].includes(input.code))
      const reloadShortcut = !is.dev && commandOrControl && input.code === 'KeyR'
      const zoomShortcut =
        commandOrControl && (input.code === 'Minus' || (input.code === 'Equal' && input.shift))

      if (devToolsShortcut || reloadShortcut || zoomShortcut) event.preventDefault()
    })
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

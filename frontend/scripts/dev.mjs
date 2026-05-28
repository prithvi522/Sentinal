import { execFileSync, spawn } from 'node:child_process';

const port = 5173;

function getOwningProcessId(targetPort) {
  try {
    const output = execFileSync('powershell', [
      '-NoProfile',
      '-Command',
      `Get-NetTCPConnection -LocalPort ${targetPort} -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess`,
    ], { encoding: 'utf8' }).trim();

    if (!output) {
      return null;
    }

    const parsed = Number.parseInt(output, 10);
    return Number.isNaN(parsed) ? null : parsed;
  } catch {
    return null;
  }
}

function isViteProcess(pid) {
  try {
    const commandLine = execFileSync('powershell', [
      '-NoProfile',
      '-Command',
      `Get-CimInstance Win32_Process -Filter "ProcessId = ${pid}" | Select-Object -ExpandProperty CommandLine`,
    ], { encoding: 'utf8' }).trim();

    return /vite\.js|node_modules\\\.bin\\.*vite/i.test(commandLine);
  } catch {
    return false;
  }
}

function stopProcess(pid) {
  execFileSync('taskkill', ['/PID', String(pid), '/F'], { stdio: 'ignore' });
}

const owningProcessId = getOwningProcessId(port);
if (owningProcessId && isViteProcess(owningProcessId)) {
  console.log(`Stopping stale Vite process on port ${port} (PID ${owningProcessId})...`);
  stopProcess(owningProcessId);
}

const child = spawn('vite', ['--host', '--port', String(port), '--strictPort'], {
  stdio: 'inherit',
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.exit(1);
  }

  process.exit(code ?? 0);
});
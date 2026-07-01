import os, sys, time, shutil
from pathlib import Path
from subprocess import Popen, run, check_output


class Runner:
    BASE = Path(__file__).resolve().parent
    VENV = BASE / ".venv"
    PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    NPM = "npm.cmd" if os.name == "nt" else "npm"
    PY_ERR = "Python 3.13 not found. Install Python 3.13: https://www.python.org/downloads/"
    NPM_ERR = "NPM not found. Install Node.js LTS: https://nodejs.org/"

    @classmethod
    def start(cls):
        if "--install" in sys.argv:
            if not shutil.which("py"):
                print(cls.PY_ERR); return
            if not shutil.which(cls.NPM):
                print(cls.NPM_ERR); return
            if os.name == "nt" and not shutil.which("cloudflared"):
                if not shutil.which("winget"):
                    print("winget not found. Install App Installer from Microsoft Store."); return
                if run(["winget", "install", "-e", "--id", "Cloudflare.cloudflared",
                        "--accept-package-agreements", "--accept-source-agreements"]).returncode:
                    print("cloudflared install failed"); return

            ver = check_output([cls.PY, "-c", "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')"], text=True).strip() if cls.PY.exists() else ""

            if ver != "3.13":
                shutil.rmtree(cls.VENV, ignore_errors=True)
                if run(["py", "-3.13", "-m", "venv", cls.VENV]).returncode:
                    print(cls.PY_ERR); return

            for cmd, cwd in [
                ([cls.PY, "-m", "pip", "install", "--upgrade", "pip"], cls.BASE),
                ([cls.PY, "-m", "pip", "install", "-r", "requirements.txt"], cls.BASE),
                ([cls.NPM, "install"], cls.BASE / "frontend"),
            ]:
                if run(cmd, cwd=cwd).returncode:
                    return

        if not shutil.which(cls.NPM):
            print(cls.NPM_ERR); return
        if "--tun" in sys.argv and not shutil.which("cloudflared"):
            print("cloudflared not found. Run with --install first."); return

        cmds = [
            ([cls.PY if cls.PY.exists() else sys.executable, "run.py"], cls.BASE / "backend"),
            ([cls.NPM, "run", "dev"], cls.BASE / "frontend"),
        ] + ([(["cloudflared", "tunnel", "--url", "http://localhost:5173"], cls.BASE)] if "--tun" in sys.argv else [])

        procs = [Popen(cmd, cwd=cwd) for cmd, cwd in cmds if cwd.exists()]

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for p in procs: p.terminate()
            for p in procs: p.wait()
        finally:
            time.sleep(3)
            print("\033[2J\033[3J\033[H", end="", flush=True)


if __name__ == "__main__":
    Runner.start()
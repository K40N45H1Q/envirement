if __name__ == "__main__":
    from os import name
    from time import sleep
    from pathlib import Path
    from sys import argv, executable
    from shutil import which, rmtree
    from signal import signal, SIGINT, SIG_IGN
    from subprocess import Popen, run, check_output

    class Runner:
        BASE = Path(__file__).resolve().parent
        VENV = BASE / ".venv"
        PY = VENV / ("Scripts/python.exe" if name == "nt" else "bin/python")
        NPM = "npm.cmd" if name == "nt" else "npm"

        ERR = [
            "Python 3.13 not found. Install Python 3.13: https://www.python.org/downloads/",
            "NPM not found. Install Node.js LTS: https://nodejs.org/",
            "Winget not found. Install App Installer from Microsoft Store.",
            "Cloudflared not found. Run with --install first.",
            "Cloudflared install failed",
        ]

        @classmethod
        def start(cls):
            if "--install" in argv:
                if not which("py"):
                    print(cls.ERR[0]); return
                if not which(cls.NPM):
                    print(cls.ERR[1]); return
                if name == "nt" and not which("cloudflared"):
                    if not which("winget"):
                        print(cls.ERR[2]); return
                    if run(["winget", "install", "-e", "--id", "Cloudflare.cloudflared",
                            "--accept-package-agreements", "--accept-source-agreements"]).returncode:
                        print(cls.ERR[4]); return

                if (check_output(
                    [cls.PY, "-c", "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                    text=True
                ).strip() if cls.PY.exists() else "") != "3.13":
                    rmtree(cls.VENV, ignore_errors=True)
                    if run(["py", "-3.13", "-m", "venv", cls.VENV]).returncode:
                        print(cls.ERR[0]); return

                for cmd, cwd in [
                    ([cls.PY, "-m", "pip", "install", "--upgrade", "pip"], cls.BASE),
                    ([cls.PY, "-m", "pip", "install", "-r", "requirements.txt"], cls.BASE),
                    ([cls.NPM, "install"], cls.BASE / "frontend"),
                ]:
                    if run(cmd, cwd=cwd).returncode:
                        return

            if not which(cls.NPM):
                print(cls.ERR[1]); return
            if "--tun" in argv and not which("cloudflared"):
                print(cls.ERR[3]); return

            procs = [
                Popen(cmd, cwd=cwd)
                for cmd, cwd in [
                    ([cls.PY if cls.PY.exists() else executable, "run.py"], cls.BASE / "backend"),
                    ([cls.NPM, "run", "dev"], cls.BASE / "frontend"),
                ] + (
                    [(["cloudflared", "tunnel", "--url", "http://localhost:5173"], cls.BASE)]
                    if "--tun" in argv else []
                )
                if cwd.exists()
            ]

            try:
                while True:
                    sleep(1)
            except KeyboardInterrupt:
                signal(SIGINT, SIG_IGN)
                for p in procs: p.terminate()
                for p in procs: p.wait()
            finally:
                signal(SIGINT, SIG_IGN)
                sleep(3)
                print("\033[2J\033[3J\033[H", end="", flush=True)

    Runner.start()
import time
from sys import argv
from pathlib import Path
from subprocess import Popen

class Runner:
    BASE_DIR = Path(__file__).parent

    @staticmethod
    def start():
        commands = [
            (["python", "run.py"], Runner.BASE_DIR / "backend"),
            (["npm.cmd", "run", "dev"], Runner.BASE_DIR / "frontend"),
        ]

        if "--tun" in argv:
            commands.append(
                (["cloudflared", "tunnel", "--url", "http://localhost:5173"], Runner.BASE_DIR)
            )

        processes = [
            Popen(cmd, cwd=cwd)
            for cmd, cwd in commands
            if cwd.exists()
        ]

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for p in processes:
                p.terminate()
            for p in processes:
                p.wait()
            time.sleep(3)
            print("\033[2J\033[3J\033[H", end="", flush=True)

Runner.start()
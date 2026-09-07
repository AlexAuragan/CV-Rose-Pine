import asyncio
import fcntl
import os
import pty
import struct
import sys
import termios
import time
from pathlib import Path
from signal import SIGWINCH

import asyncssh

BASE_DIR = Path(__file__).resolve().parent
MAIN_PATH = BASE_DIR / "main.py"

SSH_HOST = os.environ.get("SSH_HOST", "0.0.0.0")
SSH_PORT = int(os.environ.get("SSH_PORT", "2222"))
HOST_KEY_PATH = Path(
    os.environ.get(
        "SSH_HOST_KEY",
        str(BASE_DIR / ".ssh" / "ssh_host_ed25519_key"),
    )
)


class ResumeSSHServer(asyncssh.SSHServer):
    """Accept every SSH username without authentication."""

    def connection_made(
        self,
        conn: asyncssh.SSHServerConnection,
    ) -> None:
        self.connected_at = time.perf_counter()
        print(f"connection_made: {time.perf_counter():.3f}", flush=True)

    def begin_auth(self, username: str) -> bool:
        elapsed = time.perf_counter() - self.connected_at
        print(
            f"begin_auth after {elapsed:.3f}s "
            f"for username={username!r}",
            flush=True,
        )
        return False


def ensure_host_key() -> None:
    """Create a persistent Ed25519 host key on first launch."""

    if HOST_KEY_PATH.exists():
        return

    HOST_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

    key = asyncssh.generate_private_key("ssh-ed25519")
    key.write_private_key(HOST_KEY_PATH)
    HOST_KEY_PATH.chmod(0o600)

    print(f"Generated SSH host key: {HOST_KEY_PATH}")


async def handle_client(
    process: asyncssh.SSHServerProcess[bytes],
) -> None:
    started_at = time.perf_counter()
    print(
        "handle_client called",
        f"at {time.perf_counter():.3f}",
        flush=True,
    )
    print(
        "SSH session:",
        f"term={process.term_type!r}",
        f"size={process.term_size!r}",
        flush=True,
    )

    if process.term_type is None:
        process.stderr.write(b"A terminal is required.\r\n")
        process.exit(1)
        return

    master_fd, slave_fd = pty.openpty()

    cols, rows, pixel_width, pixel_height = process.term_size

    fcntl.ioctl(
        slave_fd,
        termios.TIOCSWINSZ,
        struct.pack(
            "HHHH",
            rows,
            cols,
            pixel_width,
            pixel_height,
        ),
    )

    env = os.environ.copy()
    env["TERM"] = process.term_type
    env.setdefault("COLORTERM", "truecolor")

    child: asyncio.subprocess.Process | None = None
    input_task = None
    try:
        child = await asyncio.create_subprocess_exec(
            sys.executable,
            str(MAIN_PATH),
            cwd=BASE_DIR,
            env=env,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            start_new_session=True,
        )
        print(
            f"before spawn: {time.perf_counter() - started_at:.3f}s",
            flush=True,
        )

        os.close(slave_fd)
        slave_fd = -1

        print(
            f"Started main.py as PID {child.pid}",
            flush=True,
        )
        async def forward_input() -> None:
            while True:
                try:
                    data = await process.stdin.read(65536)

                except asyncssh.TerminalSizeChanged as resize:
                    fcntl.ioctl(
                        master_fd,
                        termios.TIOCSWINSZ,
                        struct.pack(
                            "HHHH",
                            resize.height,
                            resize.width,
                            resize.pixwidth,
                            resize.pixheight,
                        ),
                    )

                    if child.returncode is None:
                        try:
                            os.killpg(child.pid, SIGWINCH)
                        except ProcessLookupError:
                            pass

                    continue

                if not data:
                    break

                await asyncio.to_thread(
                    os.write,
                    master_fd,
                    data,
                )
        input_task = asyncio.create_task(forward_input())
        chunk_index = 0

        while True:
            try:
                data = await asyncio.to_thread(
                    os.read,
                    master_fd,
                    65536,
                )
            except OSError as exc:
                print(
                    f"PTY read stopped: {exc!r}",
                    flush=True,
                )
                break

            if not data:
                break

            elapsed = time.perf_counter() - started_at

            if chunk_index < 15:
                print(
                    f"chunk {chunk_index}: "
                    f"{elapsed:.3f}s "
                    f"{len(data)} bytes "
                    f"{data[:100]!r}",
                    flush=True,
                )

            chunk_index += 1

            process.stdout.write(data)
            await process.stdout.drain()

        return_code = await child.wait()

        print(
            f"main.py exited with code {return_code}",
            flush=True,
        )

        process.exit(return_code)

    finally:
        if input_task is not None:
            input_task.cancel()

            try:
                await input_task
            except asyncio.CancelledError:
                pass

        if slave_fd >= 0:
            os.close(slave_fd)

        os.close(master_fd)

        if child is not None and child.returncode is None:
            child.terminate()
            await child.wait()



async def main() -> None:
    ensure_host_key()

    server = await asyncssh.create_server(
        ResumeSSHServer,
        SSH_HOST,
        SSH_PORT,
        server_host_keys=[HOST_KEY_PATH],
        process_factory=handle_client,
        encoding=None,
        line_editor=False,
        allow_pty=True,
        x11_forwarding=False,
        agent_forwarding=False,

        gss_host=None,
        gss_kex=False,
        gss_auth=False,
    )

    print(f"Resume SSH server listening on {SSH_HOST}:{SSH_PORT}")
    print(f"Local test: ssh -p {SSH_PORT} localhost")

    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (OSError, asyncssh.Error) as exc:
        raise SystemExit(f"SSH server failed: {exc}") from exc

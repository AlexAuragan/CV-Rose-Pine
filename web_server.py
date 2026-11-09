import os
import shlex
from importlib.resources import files
from pathlib import Path

from textual_serve.server import Server

AUTOFOCUS_SCRIPT = r"""
<script>
(() => {
  const focusTerminal = () => {
    // Wait until textual-serve has actually received output from the app.
    if (!document.body.classList.contains("-first-byte")) {
      return false;
    }

    // xterm.js receives keyboard input through this hidden textarea.
    const input = document.querySelector(
      "#terminal .xterm-helper-textarea"
    );

    if (!(input instanceof HTMLTextAreaElement)) {
      return false;
    }

    input.focus({ preventScroll: true });
    return document.activeElement === input;
  };

  if (focusTerminal()) {
    return;
  }

  // textual-serve / xterm.js initializes asynchronously, so wait until
  // both the terminal DOM and the first app output are available.
  const observer = new MutationObserver(() => {
    if (focusTerminal()) {
      observer.disconnect();
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["class"],
    childList: true,
    subtree: true,
  });
})();
</script>
"""


def build_templates(destination: Path) -> Path:
    """Copy textual-serve's template and add terminal autofocus."""
    source = (
        files("textual_serve")
        .joinpath("templates")
        .joinpath("app_index.html")
        .read_text(encoding="utf-8")
    )

    closing_body = "</body>"
    if closing_body not in source:
        raise RuntimeError("textual-serve's app_index.html no longer contains </body>")

    destination.mkdir(parents=True, exist_ok=True)

    template = source.replace(
        closing_body,
        f"{AUTOFOCUS_SCRIPT}\n{closing_body}",
        1,
    )

    (destination / "app_index.html").write_text(
        template,
        encoding="utf-8",
    )

    return destination


def _resolve_binary() -> Path:
    base_dir = Path(__file__).resolve().parent
    candidates = (
        base_dir / "resume_rust" / "bin" / "resume",
        base_dir / "resume_rust" / "target" / "release" / "resume",
    )
    override = os.environ.get("RESUME_BINARY")
    if override:
        return Path(override)
    return next((path for path in candidates if path.exists()), candidates[-1])


def main() -> None:
    binary = _resolve_binary()

    if not binary.exists():
        raise SystemExit(
            f"resume binary not found: {binary}\n"
            "Build it with: resume_rust/build.sh"
        )

    command = shlex.quote(str(binary))

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8001"))
    public_url = os.environ.get("PUBLIC_URL") or None

    runtime_dir = Path("/run/cv-rose-pine-web")
    templates_path = build_templates(runtime_dir / "templates")

    server = Server(
        command=command,
        host=host,
        port=port,
        title="CV — Rose Pine",
        public_url=public_url,
        templates_path=templates_path,
    )

    server.serve()


if __name__ == "__main__":
    main()

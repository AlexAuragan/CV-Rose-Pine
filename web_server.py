import os
import shlex
import sys
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory

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
        raise RuntimeError(
            "textual-serve's app_index.html no longer contains </body>"
        )

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


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    app_path = base_dir / "main.py"

    command = " ".join(
        (
            shlex.quote(sys.executable),
            shlex.quote(str(app_path)),
        )
    )

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8001"))
    public_url = os.environ.get("PUBLIC_URL") or None

    with TemporaryDirectory(prefix="cv-rose-pine-web-") as temp_dir:
        templates_path = build_templates(Path(temp_dir))

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

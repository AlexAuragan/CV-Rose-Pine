# resume_rust

A Rust port of the Python/Textual Rosé Pine résumé TUI (`../main.py` +
`../resume/`).

It is a single self-contained binary that renders the same content with the
same keybindings, theme, and responsive breakpoints. Because the existing
servers launch the UI as a child process inside a PTY, this binary can be
dropped in **without touching `ssh_server.py` or `web_server.py`** (see
*Deployment* below).

## Why

Cold start of the Python app is dominated by interpreter + Textual import
(typically a few hundred milliseconds). The Rust binary starts, parses its
content, and renders its first frame in **~4 ms**, with no runtime
dependencies.

## Layout

```
resume_rust/
├── Cargo.toml
├── content/            # generated JSON content (single source of truth)
│   ├── links.json
│   ├── en.json
│   └── fr.json
├── tools/
│   └── gen_content.py  # serialises ../resume/content/*.py -> content/*.json
└── src/
    ├── main.rs         # terminal setup, event loop, panic hook
    ├── app.rs          # state machine, keybindings, layout + render
    ├── render.rs       # widget rendering (mirrors resume/widgets.py)
    ├── models.rs       # data model (mirrors resume/models.py)
    ├── content.rs      # embedded JSON, parsed once
    ├── theme.rs        # Rosé Pine palette (mirrors resume/style.css)
    └── text.rs         # unicode wrapping + Textual-markup subset
```

## Build & run

```sh
cargo build --release      # produces target/release/resume
./target/release/resume    # run in a terminal
cargo test                 # headless render + navigation + search tests
```

### Headless render dump

To preview a single frame without a real terminal (useful in CI or for
screenshots):

```sh
RESUME_DUMP=120x40 ./target/release/resume
RESUME_DUMP=80x30  ./target/release/resume   # narrow: sidebar on top
RESUME_DUMP=55x20  ./target/release/resume   # tiny: sidebar hidden
```

## Content

The content lives in `../resume/content/*.py` and is the single source of
truth. After editing it, regenerate the JSON:

```sh
python3 resume_rust/tools/gen_content.py
```

`links.json` holds the shared hyperlinks; `en.json` / `fr.json` hold each
language's résumé, referencing links by id.

## Keybindings

Identical to the Python app: `↑↓ jk` move, `←→ hl` switch pane, `↵` browse,
`esc` back, `/ f` search (`n` / `N` cycle), `R` toggle FR/EN, `0`-`4` jump,
`q` quit.

## Deployment

The Python servers only need the command they spawn changed:

- `ssh_server.py`: replace `sys.executable, str(MAIN_PATH)` with the path to
  `target/release/resume`.
- `web_server.py`: point the `textual-serve` `command` at the same binary.

## Known differences from the Textual version

- **OSC 8 hyperlinks** are not emitted (ratatui has no first-class support),
  so links are styled/underlined but not clickable.
- At very narrow widths a card's right-aligned period can be squeezed
  against a long title instead of wrapping.

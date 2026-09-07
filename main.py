from functools import partial
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Static

from resume.content.fr import resume_fr
from resume.widgets import (
    MiscWidget,
    NavigationBar,
    PostWidget,
    ProfileWidget,
    ProjectWidget,
    SectionPanel,
    StudyWidget,
)

BASE_DIR = Path(__file__).resolve().parent
CSS = (BASE_DIR / "resume" / "style.css").read_text()

# Row-major order of the 2x2 grid: experience | projects / studies | misc.
SECTION_IDS = ["panel-experience", "panel-projects", "panel-studies", "panel-misc"]

HINTS = {
    "nav": [
        "[bold #c4a7e7]↑↓←→[/] [#6e6a86]sections[/]",
        "[bold #c4a7e7]↵[/] [#6e6a86]browse[/]",
        "[bold #c4a7e7]1-4[/] [#6e6a86]jump[/]",
        "[bold #c4a7e7]q[/] [#6e6a86]quit[/]",
    ],
    "inside": [
        "[bold #c4a7e7]↑↓[/] [#6e6a86]scroll[/]",
        "[bold #c4a7e7]←→[/] [#6e6a86]select entry[/]",
        "[bold #c4a7e7]esc[/] [#6e6a86]sections[/]",
        "[bold #c4a7e7]q[/] [#6e6a86]quit[/]",
    ],
}


class Resume(App[None]):
    HORIZONTAL_BREAKPOINTS = [
        (0, "-tiny"),
        (65, "-narrow"),
        (100, "-wide"),
    ]

    # vim-flavoured navigation:
    #   nav mode    -> arrows move the focus between the 4 subdivisions
    #   inside mode -> arrows scroll / browse the focused subdivision
    BINDINGS = [
        Binding("up,k", "move('up')", show=False, priority=True),
        Binding("down,j", "move('down')", show=False, priority=True),
        Binding("left,h", "move('left')", show=False, priority=True),
        Binding("right,l", "move('right')", show=False, priority=True),
        Binding("enter", "enter_section", show=False, priority=True),
        Binding("escape", "leave_section", show=False, priority=True),
        Binding("1", "jump(0)", show=False, priority=True),
        Binding("2", "jump(1)", show=False, priority=True),
        Binding("3", "jump(2)", show=False, priority=True),
        Binding("4", "jump(3)", show=False, priority=True),
        Binding("q", "quit", show=False),
    ]

    mode = reactive("nav")

    CSS = CSS

    def compose(self) -> ComposeResult:
        with Horizontal(id="body"):
            yield ProfileWidget(resume_fr.profile, id="sidebar")

            with Grid(id="content"):
                yield SectionPanel(
                    "1 · Experience",
                    [partial(PostWidget, p) for p in resume_fr.work_experience],
                    id="panel-experience",
                )
                yield SectionPanel(
                    "2 · Projects",
                    [partial(ProjectWidget, p) for p in resume_fr.personal_projects],
                    id="panel-projects",
                )
                yield SectionPanel(
                    "3 · Studies",
                    [partial(StudyWidget, s) for s in resume_fr.studies],
                    id="panel-studies",
                )
                yield SectionPanel(
                    "4 · Misc",
                    [partial(MiscWidget, m) for m in resume_fr.misc],
                    id="panel-misc",
                )

        yield NavigationBar(HINTS["nav"], id="footer")

    def on_mount(self) -> None:
        _ = self.query_one("#" + SECTION_IDS[0]).focus()
        self._sync_footer()

    # -- mode handling ------------------------------------------------------

    def watch_mode(self, mode: str) -> None:
        try:
            panels = self._panels()
        except NoMatches:
            return
        for panel in panels:
            _ = panel.remove_class("-active", "-dim")
        if mode == "inside":
            panel = self._focused_panel()
            if panel is not None:
                _ = panel.add_class("-active")
                for other in panels:
                    if other is not panel:
                        _ = other.add_class("-dim")
        try:
            footer = self.query_one("#footer", NavigationBar)
        except NoMatches:
            return
        footer.update_controls(HINTS[mode])
        self._sync_footer()

    def _sync_footer(self) -> None:
        """Show where the cursor is (which section) in the footer bar."""
        panel = self._focused_panel()
        if panel is None and self.mode == "nav":
            try:
                panel = self._panels()[0]
            except NoMatches:
                return
        title = panel.panel_title if panel is not None else "resume"
        try:
            footer = self.query_one("#footer-location", Static)
        except NoMatches:
            return
        if self.mode == "nav":
            text = f"[bold #eb6f92]◆[/] [bold]{title}[/] [#6e6a86]· ↵ to browse[/]"
        else:
            text = f"[bold #eb6f92]◆[/] [bold #9ccfd8]{title}[/] [#6e6a86]· esc to go back[/]"
        footer.update(text)

    # -- navigation ---------------------------------------------------------

    def _panels(self) -> list[SectionPanel]:
        return [self.query_one("#" + section_id, SectionPanel) for section_id in SECTION_IDS]

    def _focused_panel(self) -> SectionPanel | None:
        focused = self.focused
        return focused if isinstance(focused, SectionPanel) else None

    def action_move(self, direction: str) -> None:
        if self.mode == "nav":
            self._move_between_sections(direction)
        else:
            self._move_inside_section(direction)

    def _move_between_sections(self, direction: str) -> None:
        panels = self._panels()
        focused = self._focused_panel()

        index = 0
        for i, panel in enumerate(panels):
            if panel is focused:
                index = i
                break

        step = {"up": -2, "down": 2, "left": -1, "right": 1}[direction]
        _ = panels[(index + step) % len(panels)].focus()
        self._sync_footer()

    def _focus_child(self, panel: SectionPanel, step: int) -> None:
        focusables = [w for w in panel.query("*") if w.focusable]
        if step > 0:
            focusables = [*reversed(focusables)]
        current = self.focused
        # find first focusable strictly after (resp. before) the focused node
        # in DOM order; wrap around at the end
        try:
            start = focusables.index(current)  # type: ignore[arg-type]
            order = focusables[start + 1 :]
        except ValueError:
            order = focusables
        if not order:
            return
        order[-1].focus()

    def _move_inside_section(self, direction: str) -> None:
        panel = self._focused_panel()
        if panel is None:
            return

        match direction:
            case "up":
                panel.scroll_up()
            case "down":
                panel.scroll_down()
            case "left":
                self._focus_child(panel, -1)
            case "right":
                self._focus_child(panel, 1)
            case _:
                pass

    def action_enter_section(self) -> None:
        if self.mode != "nav":
            return
        panel = self._focused_panel()
        if panel is None:
            return
        panel.scroll_home(animate=False)
        self.mode = "inside"

    def action_leave_section(self) -> None:
        for panel in self._panels():
            panel.remove_class("-active")
        self.mode = "nav"

    def action_jump(self, index: int) -> None:
        if self.mode == "inside":
            self.action_leave_section()
        _ = self._panels()[index % len(self._panels())].focus()
        self._sync_footer()


if __name__ == "__main__":
    _ = Resume().run()

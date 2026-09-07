import os

os.environ["COLORTERM"] = "truecolor"

from functools import partial
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
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

SECTION_IDS = ["panel-experience", "panel-projects", "panel-studies", "panel-misc"]

HINTS = {
    "nav": [
        "[bold #c4a7e7]←→ hl[/] [#908caa]pane[/]",
        "[bold #c4a7e7]↑↓ jk[/] [#908caa]section[/]",
        "[bold #c4a7e7]↵[/] [#908caa]browse[/]",
        "[bold #c4a7e7]1-4[/] [#908caa]jump[/]",
        "[bold #c4a7e7]q[/] [#908caa]quit[/]",
    ],
    "inside": [
        "[bold #c4a7e7]↑↓ jk[/] [#908caa]select[/]",
        "[bold #c4a7e7]← h[/] [#908caa]profile[/]",
        "[bold #c4a7e7]tab[/] [#908caa]links[/]",
        "[bold #c4a7e7]esc[/] [#908caa]sections[/]",
        "[bold #c4a7e7]q[/] [#908caa]quit[/]",
    ],
}


class Resume(App[None]):
    HORIZONTAL_BREAKPOINTS = [
        (0, "-tiny"),
        (65, "-narrow"),
        (100, "-wide"),
    ]

    BINDINGS = [
        Binding("up,k", "move_vertical(-1)", show=False, priority=True),
        Binding("down,j", "move_vertical(1)", show=False, priority=True),
        Binding("left,h", "move_pane(-1)", show=False, priority=True),
        Binding("right,l", "move_pane(1)", show=False, priority=True),
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

    def __init__(self) -> None:
        super().__init__()
        self.section_index = 0
        self.entry_indexes = [0 for _ in SECTION_IDS]
        self.nav_area = "sections"

    def compose(self) -> ComposeResult:
        with Horizontal(id="body"):
            yield ProfileWidget(resume_fr.profile, id="sidebar")

            with VerticalScroll(id="content"):
                yield SectionPanel(
                    "1 / experience",
                    [partial(PostWidget, post) for post in resume_fr.work_experience],
                    id="panel-experience",
                )
                yield SectionPanel(
                    "2 / projects",
                    [partial(ProjectWidget, project) for project in resume_fr.personal_projects],
                    id="panel-projects",
                )
                yield SectionPanel(
                    "3 / studies",
                    [partial(StudyWidget, study) for study in resume_fr.studies],
                    id="panel-studies",
                )
                yield SectionPanel(
                    "4 / misc",
                    [partial(MiscWidget, item) for item in resume_fr.misc],
                    id="panel-misc",
                )

        yield NavigationBar(HINTS["nav"], id="footer")

    def on_mount(self) -> None:
        self._current_panel().focus()
        self._sync_panel_classes()
        self._sync_footer()

    def watch_mode(self, mode: str) -> None:
        try:
            footer = self.query_one("#footer", NavigationBar)
        except NoMatches:
            return

        footer.update_controls(HINTS[mode])
        self._sync_panel_classes()
        self._sync_footer()

    def _profile(self) -> ProfileWidget:
        return self.query_one("#sidebar", ProfileWidget)

    def _panels(self) -> list[SectionPanel]:
        return [
            self.query_one("#" + section_id, SectionPanel)
            for section_id in SECTION_IDS
        ]

    def _current_panel(self) -> SectionPanel:
        panels = self._panels()
        return panels[self.section_index % len(panels)]

    def _content(self) -> VerticalScroll:
        return self.query_one("#content", VerticalScroll)

    def _reveal_section(self, panel: SectionPanel, *, pin: bool) -> None:
        self._content().scroll_to_widget(
            panel,
            animate=True,
            top=pin,
        )

    def _entries(self, panel: SectionPanel) -> list[Widget]:
        return [child for child in panel.children if child.focusable]

    def _sync_panel_classes(self) -> None:
        try:
            panels = self._panels()
        except NoMatches:
            return

        for index, panel in enumerate(panels):
            panel.remove_class("-active", "-dim")
            if self.mode == "inside":
                if index == self.section_index:
                    panel.add_class("-active")
                else:
                    panel.add_class("-dim")

    def _sync_footer(self) -> None:
        try:
            footer = self.query_one("#footer-location", Static)
        except NoMatches:
            return

        if self.mode == "nav" and self.nav_area == "profile":
            footer.update(
                "[bold #eb6f92]>[/] [bold #e0def4]profile[/] "
                "[#908caa]:: → back to sections[/]"
            )
            return

        panel = self._current_panel()
        if self.mode == "nav":
            footer.update(
                f"[bold #eb6f92]>[/] [bold #e0def4]{panel.panel_title}[/] "
                "[#908caa]:: ← profile :: enter to browse[/]"
            )
            return

        entries = self._entries(panel)
        selected = self.entry_indexes[self.section_index] + 1 if entries else 0
        total = len(entries)
        footer.update(
            f"[bold #9ccfd8]>[/] [bold #c4a7e7]{panel.panel_title}[/] "
            f"[#908caa]:: item {selected}/{total} :: esc to sections[/]"
        )

    def action_move_vertical(self, step: int) -> None:
        if self.mode == "inside":
            self._move_between_entries(step)
            return

        if self.nav_area == "sections":
            self._move_between_sections(step)

    def action_move_pane(self, step: int) -> None:
        if self.mode == "inside":
            if step < 0:
                self.nav_area = "profile"
                self.mode = "nav"
                self._profile().focus()
                self._sync_footer()
            return

        if step < 0 and self.nav_area != "profile":
            self.nav_area = "profile"
            self._profile().focus()
            self._sync_footer()
            return

        if step > 0 and self.nav_area != "sections":
            self.nav_area = "sections"
            self._current_panel().focus()
            self._sync_footer()

    def _move_between_sections(self, step: int) -> None:
        panels = self._panels()
        self.section_index = (self.section_index + step) % len(panels)
        panel = self._current_panel()
        panel.focus()
        self._reveal_section(panel, pin=False)
        self._sync_footer()

    def _move_between_entries(self, step: int) -> None:
        panel = self._current_panel()
        entries = self._entries(panel)
        if not entries:
            return

        current_index = self.entry_indexes[self.section_index] % len(entries)
        next_index = (current_index + step) % len(entries)
        self.entry_indexes[self.section_index] = next_index
        entries[next_index].focus()
        self._sync_footer()

    def action_enter_section(self) -> None:
        if self.mode != "nav" or self.nav_area != "sections":
            return

        panel = self._current_panel()
        entries = self._entries(panel)
        self.mode = "inside"

        if not entries:
            panel.focus()
            self._reveal_section(panel, pin=True)
            return

        # Entering a section starts at its first entry and pins the whole
        # section to the top of the right-hand viewport.
        self.entry_indexes[self.section_index] = 0
        entries[0].focus()
        self._reveal_section(panel, pin=True)
        self._sync_footer()

    def action_leave_section(self) -> None:
        if self.mode != "inside":
            return

        self.nav_area = "sections"
        self.mode = "nav"
        self._current_panel().focus()
        self._sync_footer()

    def action_jump(self, index: int) -> None:
        panels = self._panels()
        self.section_index = index % len(panels)
        self.nav_area = "sections"
        self.mode = "nav"
        panel = self._current_panel()
        panel.focus()
        self._reveal_section(panel, pin=False)
        self._sync_panel_classes()
        self._sync_footer()


if __name__ == "__main__":
    Resume().run()

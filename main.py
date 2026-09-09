import os

from textual.widget import Widget

from resume.models import Language

os.environ["COLORTERM"] = "truecolor"

from functools import partial
from pathlib import Path
from unicodedata import combining, normalize

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive

# from textual.widget import Widget
from textual.widgets import Input, Static

from resume.content.en import resume_en
from resume.content.fr import resume_fr
from resume.widgets import (
    MiscWidget,
    NavigationBar,
    PostWidget,
    ProfileWidget,
    ProjectWidget,
    SectionPanel,
    StudyWidget,
    TagRow,
)

BASE_DIR = Path(__file__).resolve().parent
CSS = (BASE_DIR / "resume" / "style.css").read_text()

SECTION_IDS = ["panel-experience", "panel-projects", "panel-studies", "panel-misc"]

HINTS = {
    "nav": [
        "[bold #c4a7e7]←→ hl[/] [#908caa]pane[/]",
        "[bold #c4a7e7]↑↓ jk[/] [#908caa]section[/]",
        "[bold #c4a7e7]↵[/] [#908caa]browse[/]",
        "[bold #c4a7e7]/ f[/] [#908caa]search[/]",
        "[bold #c4a7e7]R[/] [#908caa]FR/EN[/]",
        "[bold #c4a7e7]0-4[/] [#908caa]jump[/]",
        "[bold #c4a7e7]q[/] [#908caa]quit[/]",
    ],
    "inside": [
        "[bold #c4a7e7]↑↓ jk[/] [#908caa]select[/]",
        "[bold #c4a7e7]← h[/] [#908caa]profile[/]",
        "[bold #c4a7e7]/ f[/] [#908caa]search[/]",
        "[bold #c4a7e7]R[/] [#908caa]FR/EN[/]",
        "[bold #c4a7e7]tab[/] [#908caa]links[/]",
        "[bold #c4a7e7]esc[/] [#908caa]sections[/]",
        "[bold #c4a7e7]q[/] [#908caa]quit[/]",
    ],
}

def normalize_search(text: str) -> str:
    decomposed = normalize("NFKD", text.casefold())
    return "".join(
        character
        for character in decomposed
        if not combining(character)
    )

class ResumeApp(App[None]):
    HORIZONTAL_BREAKPOINTS = [
        (0, "-tiny"),
        (65, "-narrow"),
        (100, "-wide"),
    ]

    BINDINGS = [
        Binding("up", "move_vertical(-1)", show=False, priority=True),
        Binding("k", "move_vertical(-1)", show=False),

        Binding("down", "move_vertical(1)", show=False, priority=True),
        Binding("j", "move_vertical(1)", show=False),

        Binding("left", "move_pane(-1)", show=False, priority=True),
        Binding("h", "move_pane(-1)", show=False),

        Binding("right", "move_pane(1)", show=False, priority=True),
        Binding("l", "move_pane(1)", show=False),

        Binding("r,R", "toggle_language", show=False),
        Binding("enter", "enter_section", show=False),
        Binding("escape", "leave_section", show=False),

        Binding("slash,f", "open_search", show=False),
        Binding("n", "next_search(1)", show=False),
        Binding("N", "next_search(-1)", show=False),

        Binding("0", "profile", show=False),
        Binding("1", "jump(0)", show=False),
        Binding("2", "jump(1)", show=False),
        Binding("3", "jump(2)", show=False),
        Binding("4", "jump(3)", show=False),

        Binding("q", "quit", show=False),
    ]

    mode = reactive("nav")
    language: reactive[Language] = reactive("fr")

    CSS = CSS

    def __init__(self) -> None:
        super().__init__()
        self.section_index = 0
        self.entry_indexes = [0 for _ in SECTION_IDS]
        self.nav_area = "profile"

        # Search
        self.search_mode = False
        self.search_query = ""
        self.search_matches: list[Static] = []
        self.search_match_index = 0

        self._profile_widget: ProfileWidget
        self._panel_widgets: list[SectionPanel]
        self._content_widget: VerticalScroll


    @property
    def profile(self) -> ProfileWidget:
        return self._profile_widget

    @property
    def panels(self) -> list[SectionPanel]:
        return self._panel_widgets

    @property
    def content(self) -> VerticalScroll:
        return self._content_widget

    def compose(self) -> ComposeResult:
        resume = resume_fr if self.language == "fr" else resume_en

        with Horizontal(id="body"):
            yield ProfileWidget(resume.profile, id="sidebar")

            with VerticalScroll(id="content"):
                yield SectionPanel(
                    "1 / experience",
                    [
                        partial(PostWidget, post, self.language)
                        for post in resume.work_experience
                    ],
                    id="panel-experience",
                )
                yield SectionPanel(
                    "2 / projects",
                    [
                        partial(ProjectWidget, project, self.language)
                        for project in resume.personal_projects
                    ],
                    id="panel-projects",
                )
                yield SectionPanel(
                    "3 / studies",
                    [
                        partial(StudyWidget, study, self.language)
                        for study in resume.studies
                    ],
                    id="panel-studies",
                )
                yield SectionPanel(
                    "4 / misc",
                    [
                        partial(MiscWidget, item, self.language)
                        for item in resume.misc
                    ],
                    id="panel-misc",
                )

        yield NavigationBar(HINTS[self.mode], id="footer")
        yield Input(
            placeholder="grep...",
            id="search-input",
        )

    def on_mount(self) -> None:
        self._cache_widgets()

        self.profile.focus()
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



    def _current_panel(self) -> SectionPanel:
        return self.panels[self.section_index % len(self.panels)]


    def _reveal_section(self, panel: SectionPanel, *, pin: bool) -> None:
        self.content.scroll_to_widget(
            panel,
            animate=False,
            top=pin,
        )

    def _entries(self, panel: SectionPanel) -> list[Widget]:
        return [child for child in panel.children if child.focusable]

    def _sync_panel_classes(self) -> None:
        try:
            panels = self.panels
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
        if self.search_mode:
            return

        if self.nav_area == "profile":
            if step < 0:
                self.profile.scroll_up(animate=False)
            else:
                self.profile.scroll_down(animate=False)
            return

        if self.mode == "inside":
            self._move_between_entries(step)
            return

        self._move_between_sections(step)

    def action_profile(self) -> None:
        self.nav_area = "profile"
        self.mode = "nav"
        self.profile.focus()
        self._sync_panel_classes()
        self._sync_footer()

    def action_move_pane(self, step: int) -> None:
        if step < 0:
            self.action_profile()
            return

        if step > 0 and self.nav_area == "profile":
            self.nav_area = "sections"
            self.mode = "nav"
            self._current_panel().focus(scroll_visible=False)
            self._sync_footer()

    def _move_between_sections(self, step: int) -> None:
        self.section_index = (self.section_index + step) % len(self.panels)
        self.nav_area = "sections"

        panel = self._current_panel()
        panel.focus(scroll_visible=False)

        self._reveal_section(panel, pin=True)
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
            panel.focus(scroll_visible=False)
            self._reveal_section(panel, pin=True)
            return

        self.entry_indexes[self.section_index] = 0
        entries[0].focus(scroll_visible=False)

        self._reveal_section(panel, pin=True)
        self._sync_footer()

    def action_leave_section(self) -> None:
        if self.search_mode:
            self._close_search_input()
            self._restore_current_focus()
            self._sync_footer()
            return

        if self.mode != "inside":
            return

        self.nav_area = "sections"
        self.mode = "nav"
        self._current_panel().focus()
        self._sync_footer()

    def action_jump(self, index: int) -> None:
        self.section_index = index % len(self.panels)
        self.nav_area = "sections"
        self.mode = "nav"

        panel = self._current_panel()
        panel.focus(scroll_visible=False)

        self._sync_panel_classes()
        self._sync_footer()

    def _cache_widgets(self) -> None:
        self._profile_widget = self.query_one("#sidebar", ProfileWidget)
        self._panel_widgets = [
            self.query_one(f"#{section_id}", SectionPanel)
            for section_id in SECTION_IDS
        ]
        self._content_widget = self.query_one("#content", VerticalScroll)

    async def action_toggle_language(self) -> None:
        self.search_query = ""
        self.search_matches.clear()
        self.search_match_index = 0

        self.language = "en" if self.language == "fr" else "fr"

        await self.recompose()
        self._cache_widgets()
        self._restore_focus_after_language_change()

    def _restore_focus_after_language_change(self) -> None:
        self._sync_panel_classes()

        if self.nav_area == "profile":
            self.profile.focus()
            self._sync_footer()
            return

        panel = self._current_panel()

        if self.mode == "inside":
            entries = self._entries(panel)

            if entries:
                index = min(
                    self.entry_indexes[self.section_index],
                    len(entries) - 1,
                )
                self.entry_indexes[self.section_index] = index
                entries[index].focus()
            else:
                panel.focus()

            self._reveal_section(panel, pin=True)
        else:
            panel.focus()
            self._reveal_section(panel, pin=False)

        self._sync_footer()

    def _searchable_text(self, widget: Static) -> str:
        if isinstance(widget, TagRow):
            return widget.search_text()

        return str(widget.content)


    def _find_search_matches(self, query: str) -> list[Static]:
        needle = normalize_search(query)
        matches: list[Static] = []

        body = self.query_one("#body")

        for widget in body.query(Static):
            text = normalize_search(self._searchable_text(widget))

            if needle in text:
                matches.append(widget)

        return matches

    def _search_owner(self, target: Widget) -> Widget | None:
        node = target

        while node is not None:
            if isinstance(node, ProfileWidget):
                return node

            if isinstance(
                node,
                (
                    PostWidget,
                    ProjectWidget,
                    StudyWidget,
                    MiscWidget,
                ),
            ):
                return node

            node = node.parent

        return None

    def _sync_search_footer(self) -> None:
        footer = self.query_one("#footer-location", Static)

        footer.update(
            f"[bold #f6c177]/ {self.search_query}[/] "
            f"[#908caa]:: "
            f"{self.search_match_index + 1}/{len(self.search_matches)} "
            f":: n/N next/prev[/]"
        )

    def _focus_search_match(self) -> None:
        if not self.search_matches:
            return

        target = self.search_matches[self.search_match_index]
        owner = self._search_owner(target)

        if owner is None:
            return

        if isinstance(owner, ProfileWidget):
            self.nav_area = "profile"
            self.mode = "nav"

            owner.focus()
            owner.scroll_to_widget(
                target,
                animate=False,
            )

            self._sync_panel_classes()
            self._sync_search_footer()
            return

        for section_index, panel in enumerate(self.panels):
            entries = self._entries(panel)

            for entry_index, entry in enumerate(entries):
                if entry is not owner:
                    continue

                self.section_index = section_index
                self.entry_indexes[section_index] = entry_index
                self.nav_area = "sections"
                self.mode = "inside"

                owner.focus()

                self.content.scroll_to_widget(
                    target,
                    animate=False,
                    top=True,
                )

                self._sync_panel_classes()
                self._sync_search_footer()
                return

    def action_open_search(self) -> None:
        if self.search_mode:
            return

        self.search_mode = True

        search_input = self.query_one("#search-input", Input)
        search_input.value = ""

        self.screen.add_class("-search")
        self.call_after_refresh(search_input.focus)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "search-input":
            return

        query = event.value.strip()

        self._close_search_input()

        if not query:
            self._restore_current_focus()
            self._sync_footer()
            return

        self.search_query = query
        self.search_matches = self._find_search_matches(query)
        self.search_match_index = 0

        if not self.search_matches:
            self._restore_current_focus()
            self._sync_footer()

            footer = self.query_one("#footer-location", Static)
            footer.update(
                f"[bold #eb6f92]/ {query}[/] "
                "[#908caa]:: no matches[/]"
            )
            return

        self._focus_search_match()

    def _close_search_input(self) -> None:
        self.search_mode = False
        self.screen.remove_class("-search")

    def _restore_current_focus(self) -> None:
        if self.nav_area == "profile":
            self.profile.focus()
            return

        panel = self._current_panel()

        if self.mode == "nav":
            panel.focus()
            return

        entries = self._entries(panel)

        if not entries:
            panel.focus()
            return

        index = min(
            self.entry_indexes[self.section_index],
            len(entries) - 1,
        )

        entries[index].focus()

    def action_next_search(self, step: int) -> None:
        if self.search_mode:
            return

        if not self.search_matches:
            return

        self.search_match_index = (
            self.search_match_index + step
        ) % len(self.search_matches)

        self._focus_search_match()

if __name__ == "__main__":
    ResumeApp().run()

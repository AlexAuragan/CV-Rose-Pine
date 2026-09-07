from collections.abc import Callable, Iterable
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalGroup
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Link, Static

from resume.models import (
    HyperLink,
    Language,
    MiscItem,
    PersonalProject,
    Post,
    Profile,
    Serializable,
    Study,
    Tool,
)


class DescriptionWidget(Vertical):
    def __init__(
        self,
        value: Serializable,
        language: Language,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.language: Language = language
        self.add_class("description")

    def compose(self) -> ComposeResult:
        value = self.value

        if isinstance(value, str):
            yield Static(
                f"· {value}",
                classes="description-line",
            )
            return

        if isinstance(value, HyperLink):
            yield Link(
                f"-> {value.title(self.language)}",
                url=value.url,
                classes="description-link",
            )
            return

        if isinstance(value, list):
            for item in value:
                yield DescriptionWidget(
                    item,
                    self.language,
                )
            return

        title, child = value

        yield Static(
            f":: {title}",
            classes="description-group-title",
        )

        yield DescriptionWidget(
            child,
            self.language,
            classes="description-children",
        )


class TagRow(Horizontal):
    def __init__(
        self,
        label: str,
        values: list[str] | list[Tool],
        language: Language,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.values = values
        self.language: Language = language
        self.add_class("tag-row")

    def compose(self) -> ComposeResult:
        yield Static(
            f"{self.label}:",
            classes="tag-label",
        )

        for value in self.values:
            if isinstance(value, HyperLink):
                yield Link(
                    value.title(self.language),
                    url=value.url,
                    classes="tag tag-link",
                )
            else:
                yield Static(
                    value,
                    classes="tag",
                )


class LinksRow(Horizontal):
    def __init__(
        self,
        links: list[HyperLink],
        language: Language,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.links = links
        self.language: Language = language
        self.add_class("links-row")

    def compose(self) -> ComposeResult:
        yield Static(
            "links:",
            classes="links-label",
        )

        for link in self.links:
            yield Link(
                f"-> {link.title(self.language)}",
                url=link.url,
                classes="external-link",
            )


class PostWidget(Vertical):
    can_focus = True

    def __init__(
        self,
        post: Post,
        language: Language = "fr",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.post = post
        self.language: Language = language
        self.add_class("entry", "post")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="card-header"):
            yield Static(
                self.post.title,
                classes="card-title post-title",
            )

            yield Static(
                self.post.period,
                classes="card-period",
            )

        with Horizontal(classes="card-meta"):
            yield Link(
                self.post.company,
                url=self.post.company_link.url,
                classes="company-link",
            )

            yield Static(
                self.post.region,
                classes="card-region",
            )

        yield DescriptionWidget(
            self.post.desc,
            self.language,
        )

        if self.post.skills:
            yield TagRow(
                "skills",
                self.post.skills,
                self.language,
                classes="skills",
            )

        if self.post.tools:
            yield TagRow(
                "tools",
                self.post.tools,
                self.language,
                classes="tools",
            )

        if self.post.links:
            yield LinksRow(
                self.post.links,
                self.language,
            )


class ProjectWidget(Vertical):
    can_focus = True

    def __init__(
        self,
        project: PersonalProject,
        language: Language = "fr",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.project = project
        self.language: Language = language
        self.add_class("entry", "project")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="card-header"):
            yield Static(
                self.project.title,
                classes="card-title project-title",
            )

            yield Static(
                self.project.period,
                classes="card-period",
            )

        yield Static(
            self.project.modality,
            classes="card-meta project-modality",
        )

        yield DescriptionWidget(
            self.project.desc,
            self.language,
        )

        if self.project.skills:
            yield TagRow(
                "skills",
                self.project.skills,
                self.language,
                classes="skills",
            )

        if self.project.tools:
            yield TagRow(
                "tools",
                self.project.tools,
                self.language,
                classes="tools",
            )

        if self.project.links:
            yield LinksRow(
                self.project.links,
                self.language,
            )


class StudyWidget(Vertical):
    can_focus = True

    def __init__(
        self,
        study: Study,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study = study
        self.add_class("entry", "study")

    def compose(self) -> ComposeResult:
        yield Static(
            self.study.title,
            classes="card-title study-title",
        )

        yield Static(
            self.study.spe,
            classes="study-speciality",
        )

        yield Static(
            self.study.region,
            classes="card-region",
        )

        if self.study.tags:
            yield TagRow(
                "topics",
                self.study.tags,
                "fr",
                classes="study-tags",
            )


class MiscWidget(Vertical):
    can_focus = True

    def __init__(
        self,
        item: MiscItem,
        language: Language = "fr",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.item = item
        self.language: Language = language
        self.add_class("entry", "misc")

    def compose(self) -> ComposeResult:
        yield Static(
            self.item.title,
            classes="card-title misc-title",
        )

        yield DescriptionWidget(
            self.item.desc,
            self.language,
        )

        if self.item.tags:
            yield TagRow(
                "tags",
                self.item.tags,
                self.language,
            )

        if self.item.links:
            yield LinksRow(
                self.item.links,
                self.language,
            )


class ProfileWidget(Vertical):
    can_focus = True

    def __init__(
        self,
        profile: Profile,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.profile = profile
        self.border_title = " profile "

    def compose(self) -> ComposeResult:
        if self.profile.ascii_art:
            yield Static(
                self.profile.ascii_art.strip("\n"),
                classes="profile-art",
            )

        yield Static(
            self.profile.name,
            classes="profile-name",
        )

        yield Static(
            self.profile.title,
            classes="profile-title",
        )

        yield Static(
            self.profile.region,
            classes="profile-region",
        )

        if self.profile.highlights:
            with Vertical(classes="profile-highlights"):
                for highlight in self.profile.highlights:
                    yield Static(
                        f"> {highlight}",
                        classes="profile-highlight",
                    )

        if self.profile.current:
            yield Static(
                ":: currently",
                classes="profile-current-label",
            )

            yield Static(
                self.profile.current,
                classes="profile-current",
            )


class SectionPanel(VerticalGroup):
    """An expanded resume section; the right-hand column owns scrolling."""

    can_focus = True

    def __init__(
        self,
        title: str,
        builders: Iterable[Callable[[], Widget]],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.panel_title = title
        self.builders: list[Callable[[], Widget]] = list(builders)
        self.border_title = f" {title} "
        self.add_class("section-panel")

    def compose(self) -> ComposeResult:
        if not self.builders:
            yield Static("-- empty --", classes="section-empty")
            return

        for builder in self.builders:
            yield builder()


class NavigationBar(Horizontal):
    def __init__(
        self,
        controls: list[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.controls = controls
        self.location_text = ""

    def compose(self) -> ComposeResult:
        yield Static(self.location_text, id="footer-location")
        with Horizontal(id="footer-hints"):
            for binding in self.controls:
                yield Static(binding, classes="contact-item")

    def update_controls(self, controls: list[str]) -> None:
        self.controls = controls
        hints = self.query_one("#footer-hints")
        hints.remove_children()
        hints.mount_all(
            Static(binding, classes="contact-item")
            for binding in controls
        )

    def set_location(self, text: str) -> None:
        self.location_text = text
        try:
            self.query_one("#footer-location", Static).update(text)
        except NoMatches:
            pass

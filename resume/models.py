
from dataclasses import dataclass, field
from typing import Literal
from rich.align import Align
from rich.console import Group, RenderableType
from rich.rule import Rule
from rich.text import Text

type Language = Literal["en", "fr"]


type Serializable = (
    str
    | HyperLink
    | list[Serializable]
    | tuple[str, Serializable]
)

type Tool = str | HyperLink





@dataclass(frozen=True)
class HyperLink:
    title_en: str
    title_fr: str
    url: str

    def title(self, language: Language) -> str:
        match language:
            case "fr":
                return self.title_fr
            case "en":
                return self.title_en


@dataclass(frozen=True)
class Post:
    title: str
    company: str
    company_link: HyperLink
    start_month: str
    end_month: str
    desc: Serializable
    skills: list[str]
    tools: list[Tool]
    region: str
    links: list[HyperLink] = field(default_factory=list)

    @property
    def period(self) -> str:
        return f"{self.start_month} — {self.end_month}"


@dataclass(frozen=True)
class Study:
    title: str
    spe: str
    region: str
    tags: list[str]


@dataclass(frozen=True)
class PersonalProject:
    title: str
    desc: Serializable
    modality: str  # e.g. solo, duo, team
    year: int | str
    skills: list[str]
    tools: list[Tool]
    links: list[HyperLink] = field(default_factory=list)

    @property
    def period(self) -> str:
        return str(self.year)


@dataclass(frozen=True)
class Profile:
    name: str
    title: str
    region: str
    ascii_art: str = ""
    highlights: list[str] = field(default_factory=list)
    current: str | None = None


@dataclass(frozen=True)
class MiscItem:
    title: str
    desc: Serializable
    tags: list[str] = field(default_factory=list)
    links: list[HyperLink] = field(default_factory=list)


@dataclass(frozen=True)
class ContactInfo:
    label: str
    value: str
    url: str | None = None


@dataclass(frozen=True)
class Resume:
    profile: Profile
    work_experience: list[Post]
    personal_projects: list[PersonalProject]
    misc: list[MiscItem]
    studies: list[Study] = field(default_factory=list)
    contacts: list[ContactInfo] = field(default_factory=list)
    links: list[HyperLink] = field(default_factory=list)

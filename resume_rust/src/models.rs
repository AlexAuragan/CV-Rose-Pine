//! Data model, mirroring `resume/models.py`.

use std::collections::HashMap;

use serde::Deserialize;

/// Language selector, mirroring the Python `Literal["en", "fr"]`.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Language {
    En,
    Fr,
}

impl Language {
    pub fn toggle(self) -> Self {
        match self {
            Language::En => Language::Fr,
            Language::Fr => Language::En,
        }
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct HyperLink {
    pub title_en: String,
    pub title_fr: String,
    pub url: String,
}

impl HyperLink {
    pub fn title(&self, language: Language) -> &str {
        match language {
            Language::En => &self.title_en,
            Language::Fr => &self.title_fr,
        }
    }
}

pub type Links = HashMap<String, HyperLink>;

#[derive(Clone, Debug, Deserialize)]
pub struct LinkRef {
    pub link: String,
}

/// The recursive `Serializable` union from `models.py`.
#[derive(Clone, Debug, Deserialize)]
#[serde(untagged)]
pub enum Node {
    Text(String),
    Link(LinkRef),
    Group(GroupNode),
    Seq(Vec<Node>),
}

#[derive(Clone, Debug, Deserialize)]
pub struct GroupNode {
    pub group: String,
    pub items: Vec<Node>,
}

/// `str | HyperLink`.
#[derive(Clone, Debug, Deserialize)]
#[serde(untagged)]
pub enum Tool {
    Text(String),
    Link(LinkRef),
}

/// `int | str` (used for `PersonalProject.year`).
#[derive(Clone, Debug, Deserialize)]
#[serde(untagged)]
pub enum Year {
    Num(i64),
    Str(String),
}

impl Year {
    pub fn text(&self) -> String {
        match self {
            Year::Num(n) => n.to_string(),
            Year::Str(s) => s.clone(),
        }
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct Post {
    pub title: String,
    pub company: String,
    pub company_link: String,
    pub start_month: String,
    pub end_month: String,
    pub desc: Node,
    #[serde(default)]
    pub skills: Vec<String>,
    #[serde(default)]
    pub tools: Vec<Tool>,
    pub region: String,
    #[serde(default)]
    pub links: Vec<String>,
}

impl Post {
    pub fn period(&self) -> String {
        format!("{} — {}", self.start_month, self.end_month)
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct PersonalProject {
    pub title: String,
    pub desc: Node,
    pub modality: String,
    pub year: Year,
    #[serde(default)]
    pub skills: Vec<String>,
    #[serde(default)]
    pub tools: Vec<Tool>,
    #[serde(default)]
    pub links: Vec<String>,
}

impl PersonalProject {
    pub fn period(&self) -> String {
        self.year.text()
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct Study {
    pub title: String,
    pub spe: String,
    pub region: String,
    #[serde(default)]
    pub tags: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ContactInfo {
    pub label: String,
    pub value: String,
    #[serde(default)]
    pub url: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Profile {
    pub name: String,
    pub title: String,
    pub region: String,
    #[serde(default)]
    pub ascii_art: String,
    #[serde(default)]
    pub highlights: Vec<String>,
    #[serde(default)]
    pub contact: Vec<ContactInfo>,
    #[serde(default)]
    pub current: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct MiscItem {
    pub title: String,
    pub desc: Node,
    #[serde(default)]
    pub tags: Vec<String>,
    #[serde(default)]
    pub links: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Resume {
    pub profile: Profile,
    pub work_experience: Vec<Post>,
    pub personal_projects: Vec<PersonalProject>,
    #[serde(default)]
    pub studies: Vec<Study>,
    #[serde(default)]
    pub misc: Vec<MiscItem>,
}

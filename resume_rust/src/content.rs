//! Embedded resume content, generated from the Python sources by
//! `tools/gen_content.py` and parsed at first use.

use std::sync::OnceLock;

use crate::models::{Language, Links, Resume};

const LINKS_JSON: &str = include_str!("../content/links.json");
const EN_JSON: &str = include_str!("../content/en.json");
const FR_JSON: &str = include_str!("../content/fr.json");

pub fn links() -> &'static Links {
    static LINKS: OnceLock<Links> = OnceLock::new();
    LINKS.get_or_init(|| serde_json::from_str(LINKS_JSON).expect("valid links.json"))
}

pub fn resume(language: Language) -> &'static Resume {
    static EN: OnceLock<Resume> = OnceLock::new();
    static FR: OnceLock<Resume> = OnceLock::new();

    match language {
        Language::En => EN.get_or_init(|| serde_json::from_str(EN_JSON).expect("valid en.json")),
        Language::Fr => FR.get_or_init(|| serde_json::from_str(FR_JSON).expect("valid fr.json")),
    }
}

//! Rosé Pine palette, mirroring `resume/style.css`.

use ratatui::style::{Color, Modifier, Style};

pub const BASE: Color = Color::Rgb(0x19, 0x17, 0x24);
pub const SURFACE: Color = Color::Rgb(0x1f, 0x1d, 0x2e);
pub const OVERLAY: Color = Color::Rgb(0x26, 0x23, 0x3a);
pub const MUTED: Color = Color::Rgb(0x6e, 0x6a, 0x86);
pub const SUBTLE: Color = Color::Rgb(0x90, 0x8c, 0xaa);
pub const TEXT: Color = Color::Rgb(0xe0, 0xde, 0xf4);
pub const LOVE: Color = Color::Rgb(0xeb, 0x6f, 0x92);
pub const GOLD: Color = Color::Rgb(0xf6, 0xc1, 0x77);
pub const ROSE: Color = Color::Rgb(0xea, 0x9a, 0x97);
#[allow(dead_code)]
pub const PINE: Color = Color::Rgb(0x3e, 0x8f, 0xb0);
pub const FOAM: Color = Color::Rgb(0x9c, 0xcf, 0xd8);
pub const IRIS: Color = Color::Rgb(0xc4, 0xa7, 0xe7);
pub const HIGHLIGHT_MED: Color = Color::Rgb(0x44, 0x41, 0x5a);

pub fn fg(color: Color) -> Style {
    Style::default().fg(color)
}

pub fn bg(color: Color) -> Style {
    Style::default().bg(color)
}

pub fn bold(style: Style) -> Style {
    style.add_modifier(Modifier::BOLD)
}

pub fn italic(style: Style) -> Style {
    style.add_modifier(Modifier::ITALIC)
}

pub fn underlined(style: Style) -> Style {
    style.add_modifier(Modifier::UNDERLINED)
}

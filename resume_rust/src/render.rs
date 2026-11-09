//! Widget rendering: turns the data model into styled `Line`s. This is the
//! Rust equivalent of `resume/widgets.py` plus the layout glue from
//! `style.css`.

use ratatui::style::{Color, Style};
use ratatui::text::{Line, Span};

use crate::models::{
    Language, Links, MiscItem, Node, PersonalProject, Post, Profile, Resume, Tool,
};
use crate::text::{centered, display_width, line_width, markup, wrap_chunks, wrap_indented, Chunk};
use crate::theme::*;

// ---------------------------------------------------------------------------
// Borders / framing
// ---------------------------------------------------------------------------

fn bg_style(color: Color) -> Style {
    Style::default().bg(color)
}

pub fn border_top(
    width: usize,
    title: &str,
    title_style: Style,
    border: Color,
    panel_bg: Color,
) -> Line<'static> {
    let border_style = fg(border).bg(panel_bg);
    let mut spans = vec![Span::styled("╭", border_style)];
    let mut used = 1usize;

    if !title.is_empty() {
        spans.push(Span::styled("─ ", border_style));
        used += 2;
        used += display_width(title);
        spans.push(Span::styled(title.to_string(), title_style));
        spans.push(Span::styled(" ", border_style));
        used += 1;
    }

    let fill = width.saturating_sub(used + 1);
    spans.push(Span::styled("─".repeat(fill), border_style));
    spans.push(Span::styled("╮", border_style));
    Line::from(spans)
}

pub fn border_bottom(width: usize, border: Color, panel_bg: Color) -> Line<'static> {
    let border_style = fg(border).bg(panel_bg);
    let inner = width.saturating_sub(2);
    Line::from(vec![
        Span::styled("╰", border_style),
        Span::styled("─".repeat(inner), border_style),
        Span::styled("╯", border_style),
    ])
}

pub fn border_row(
    line: Line<'static>,
    width: usize,
    border: Color,
    panel_bg: Color,
    row_bg: Color,
) -> Line<'static> {
    let width_used = line_width(&line);
    let inner = width.saturating_sub(2);
    let border_style = fg(border).bg(panel_bg);

    let mut spans = vec![Span::styled("│", border_style)];
    spans.extend(line.spans);
    if width_used < inner {
        spans.push(Span::styled(
            " ".repeat(inner - width_used),
            bg_style(row_bg),
        ));
    }
    spans.push(Span::styled("│", border_style));

    let mut out = Line::from(spans);
    out.style = bg_style(row_bg);
    out
}

pub fn blank_row(bg: Color) -> Line<'static> {
    let mut line = Line::default();
    line.style = bg_style(bg);
    line
}

fn header_line(
    left: Vec<Span<'static>>,
    right: Vec<Span<'static>>,
    width: usize,
    bg: Color,
) -> Line<'static> {
    let left_w: usize = left.iter().map(|s| display_width(&s.content)).sum();
    let right_w: usize = right.iter().map(|s| display_width(&s.content)).sum();
    let pad = width.saturating_sub(left_w + right_w).max(1);

    let mut spans = left;
    spans.push(Span::styled(" ".repeat(pad), bg_style(bg)));
    spans.extend(right);
    Line::from(spans)
}

// ---------------------------------------------------------------------------
// Descriptions (`Serializable` flattened like `DescriptionWidget`)
// ---------------------------------------------------------------------------

fn desc_collect(
    node: &Node,
    links: &Links,
    language: Language,
    depth: usize,
    out: &mut Vec<(usize, Vec<Chunk>)>,
) {
    match node {
        Node::Text(text) => {
            let mut chunks: Vec<Chunk> = vec![("· ".to_string(), fg(TEXT))];
            chunks.extend(markup(text, fg(TEXT)));
            out.push((depth, chunks));
        }
        Node::Link(reference) => {
            if let Some(link) = links.get(&reference.link) {
                out.push((
                    depth,
                    vec![
                        ("-> ".to_string(), fg(FOAM)),
                        (link.title(language).to_string(), underlined(fg(FOAM))),
                    ],
                ));
            }
        }
        Node::Group(group) => {
            out.push((
                depth,
                vec![
                    (":: ".to_string(), bold(fg(GOLD))),
                    (group.group.clone(), bold(fg(GOLD))),
                ],
            ));
            for item in &group.items {
                desc_collect(item, links, language, depth + 1, out);
            }
        }
        Node::Seq(items) => {
            for item in items {
                desc_collect(item, links, language, depth, out);
            }
        }
    }
}

pub fn description_lines(
    node: &Node,
    links: &Links,
    language: Language,
    width: usize,
) -> Vec<Line<'static>> {
    let mut collected: Vec<(usize, Vec<Chunk>)> = Vec::new();
    desc_collect(node, links, language, 0, &mut collected);

    let mut lines = Vec::new();
    for (depth, chunks) in collected {
        lines.extend(wrap_indented(&chunks, width, depth * 2, Style::default()));
    }
    lines
}

// ---------------------------------------------------------------------------
// Tag rows / link rows
// ---------------------------------------------------------------------------

fn plain_pills(values: &[String]) -> Vec<Chunk> {
    values
        .iter()
        .map(|value| (format!(" {value} "), fg(ROSE).bg(OVERLAY)))
        .collect()
}

fn tool_pills(tools: &[Tool], links: &Links, language: Language) -> Vec<Chunk> {
    tools
        .iter()
        .filter_map(|tool| match tool {
            Tool::Text(value) => Some((format!(" {value} "), fg(ROSE).bg(OVERLAY))),
            Tool::Link(reference) => links.get(&reference.link).map(|link| {
                (
                    format!(" {} ", link.title(language)),
                    underlined(fg(FOAM)).bg(OVERLAY),
                )
            }),
        })
        .collect()
}

fn tag_row(label: &str, pills: Vec<Chunk>, width: usize) -> Vec<Line<'static>> {
    let mut chunks: Vec<Chunk> = vec![(format!("{label}: "), italic(fg(SUBTLE)))];
    for pill in pills {
        chunks.push(pill);
        chunks.push((" ".to_string(), Style::default()));
    }
    wrap_chunks(&chunks, width)
}

fn links_row(
    ids: &[String],
    links: &Links,
    language: Language,
    width: usize,
) -> Vec<Line<'static>> {
    let mut chunks: Vec<Chunk> = vec![
        ("links:".to_string(), fg(SUBTLE)),
        (" ".to_string(), Style::default()),
    ];
    for id in ids {
        if let Some(link) = links.get(id) {
            chunks.push((format!("-> {}", link.title(language)), underlined(fg(FOAM))));
            chunks.push(("  ".to_string(), Style::default()));
        }
    }
    wrap_chunks(&chunks, width)
}

// ---------------------------------------------------------------------------
// Entry widgets
// ---------------------------------------------------------------------------

fn post_entry(post: &Post, links: &Links, language: Language, width: usize) -> Vec<Line<'static>> {
    let mut lines = vec![header_line(
        vec![Span::styled(post.title.clone(), bold(fg(LOVE)))],
        vec![Span::styled(post.period(), fg(MUTED))],
        width,
        SURFACE,
    )];

    let meta: Vec<Chunk> = vec![
        (post.company.clone(), underlined(fg(FOAM))),
        ("  ".to_string(), Style::default()),
        (post.region.clone(), fg(MUTED)),
    ];
    lines.extend(wrap_chunks(&meta, width));
    lines.extend(description_lines(&post.desc, links, language, width));

    if !post.skills.is_empty() {
        lines.extend(tag_row("skills", plain_pills(&post.skills), width));
    }
    if !post.tools.is_empty() {
        lines.extend(tag_row(
            "tools",
            tool_pills(&post.tools, links, language),
            width,
        ));
    }
    if !post.links.is_empty() {
        lines.extend(links_row(&post.links, links, language, width));
    }
    lines
}

fn project_entry(
    project: &PersonalProject,
    links: &Links,
    language: Language,
    width: usize,
) -> Vec<Line<'static>> {
    let mut lines = vec![header_line(
        vec![Span::styled(project.title.clone(), bold(fg(FOAM)))],
        vec![Span::styled(project.period(), fg(MUTED))],
        width,
        SURFACE,
    )];

    lines.extend(wrap_chunks(
        &[(project.modality.clone(), fg(SUBTLE))],
        width,
    ));
    lines.extend(description_lines(&project.desc, links, language, width));

    if !project.skills.is_empty() {
        lines.extend(tag_row("skills", plain_pills(&project.skills), width));
    }
    if !project.tools.is_empty() {
        lines.extend(tag_row(
            "tools",
            tool_pills(&project.tools, links, language),
            width,
        ));
    }
    if !project.links.is_empty() {
        lines.extend(links_row(&project.links, links, language, width));
    }
    lines
}

fn study_entry(
    study: &crate::models::Study,
    language: Language,
    width: usize,
) -> Vec<Line<'static>> {
    let _ = language;
    let mut lines = vec![Line::from(Span::styled(
        study.title.clone(),
        bold(fg(ROSE)),
    ))];
    lines.extend(wrap_chunks(&[(study.spe.clone(), fg(SUBTLE))], width));
    lines.extend(wrap_chunks(&[(study.region.clone(), fg(MUTED))], width));

    if !study.tags.is_empty() {
        lines.extend(tag_row("topics", plain_pills(&study.tags), width));
    }
    lines
}

fn misc_entry(
    item: &MiscItem,
    links: &Links,
    language: Language,
    width: usize,
) -> Vec<Line<'static>> {
    let mut lines = vec![Line::from(Span::styled(item.title.clone(), bold(fg(IRIS))))];
    lines.extend(description_lines(&item.desc, links, language, width));

    if !item.tags.is_empty() {
        lines.extend(tag_row("tags", plain_pills(&item.tags), width));
    }
    if !item.links.is_empty() {
        lines.extend(links_row(&item.links, links, language, width));
    }
    lines
}

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------

pub const SECTION_COUNT: usize = 4;

pub fn section_title(section: usize) -> &'static str {
    match section {
        0 => "1 / experience",
        1 => "2 / projects",
        2 => "3 / studies",
        _ => "4 / misc",
    }
}

pub fn entry_count(section: usize, resume: &Resume) -> usize {
    match section {
        0 => resume.work_experience.len(),
        1 => resume.personal_projects.len(),
        2 => resume.studies.len(),
        _ => resume.misc.len(),
    }
}

/// Returns the panel title and one `Vec<Line>` per focusable entry.
pub fn section_entries(
    section: usize,
    resume: &Resume,
    links: &Links,
    language: Language,
    width: usize,
) -> Vec<Vec<Line<'static>>> {
    match section {
        0 => resume
            .work_experience
            .iter()
            .map(|post| post_entry(post, links, language, width))
            .collect(),
        1 => resume
            .personal_projects
            .iter()
            .map(|project| project_entry(project, links, language, width))
            .collect(),
        2 => resume
            .studies
            .iter()
            .map(|study| study_entry(study, language, width))
            .collect(),
        _ => resume
            .misc
            .iter()
            .map(|item| misc_entry(item, links, language, width))
            .collect(),
    }
}

pub fn empty_placeholder(width: usize, style: Style) -> Line<'static> {
    centered("-- empty --", width, style)
}

// ---------------------------------------------------------------------------
// Profile sidebar
// ---------------------------------------------------------------------------

pub fn profile_lines(profile: &Profile, width: usize) -> Vec<Line<'static>> {
    let mut lines: Vec<Line<'static>> = Vec::new();

    if !profile.ascii_art.is_empty() {
        for art_line in profile.ascii_art.split('\n') {
            lines.push(Line::from(Span::styled(art_line.to_string(), fg(IRIS))));
        }
        lines.push(Line::default());
    }

    lines.extend(wrap_chunks(
        &[(profile.name.clone(), bold(fg(TEXT)))],
        width,
    ));
    lines.push(crate::text::rule(width, fg(HIGHLIGHT_MED)));
    lines.extend(wrap_chunks(
        &[(profile.title.clone(), bold(fg(ROSE)))],
        width,
    ));
    lines.extend(wrap_chunks(&[(profile.region.clone(), fg(MUTED))], width));

    if !profile.highlights.is_empty() {
        lines.push(Line::default());
        for highlight in &profile.highlights {
            lines.extend(wrap_chunks(&[(format!("> {highlight}"), fg(GOLD))], width));
        }
    }

    if let Some(current) = &profile.current {
        lines.push(Line::default());
        lines.push(Line::from(Span::styled(
            ":: currently".to_string(),
            bold(fg(MUTED)),
        )));
        lines.extend(wrap_chunks(&[(current.clone(), fg(FOAM))], width));
    }

    lines.push(crate::text::rule(width, fg(HIGHLIGHT_MED)));

    if !profile.contact.is_empty() {
        lines.push(Line::from(Span::styled(
            ":: contact".to_string(),
            bold(fg(MUTED)),
        )));
        for contact in &profile.contact {
            let pad = 10usize.saturating_sub(display_width(&contact.label));
            let value_style = if contact.url.is_some() {
                underlined(fg(FOAM))
            } else {
                fg(FOAM)
            };
            lines.push(Line::from(vec![
                Span::styled(contact.label.clone(), fg(SUBTLE)),
                Span::styled(" ".repeat(pad), Style::default()),
                Span::styled(contact.value.clone(), value_style),
            ]));
        }
    }

    lines
}

// ---------------------------------------------------------------------------
// Searchable text
// ---------------------------------------------------------------------------

fn plain(text: &str) -> String {
    markup(text, Style::default())
        .into_iter()
        .map(|(chunk, _)| chunk)
        .collect()
}

fn node_text(node: &Node, links: &Links, language: Language, out: &mut String) {
    match node {
        Node::Text(text) => {
            out.push_str(&plain(text));
            out.push(' ');
        }
        Node::Link(reference) => {
            if let Some(link) = links.get(&reference.link) {
                out.push_str(link.title(language));
                out.push(' ');
                out.push_str(&link.url);
                out.push(' ');
            }
        }
        Node::Group(group) => {
            out.push_str(&group.group);
            out.push(' ');
            for item in &group.items {
                node_text(item, links, language, out);
            }
        }
        Node::Seq(items) => {
            for item in items {
                node_text(item, links, language, out);
            }
        }
    }
}

fn push_link_text(id: &str, links: &Links, language: Language, out: &mut String) {
    if let Some(link) = links.get(id) {
        out.push_str(link.title(language));
        out.push(' ');
        out.push_str(&link.url);
        out.push(' ');
    }
}

pub fn entry_search_text(
    section: usize,
    entry: usize,
    resume: &Resume,
    links: &Links,
    language: Language,
) -> String {
    let mut out = String::new();

    match section {
        0 => {
            if let Some(post) = resume.work_experience.get(entry) {
                out.push_str(&post.title);
                out.push(' ');
                out.push_str(&post.company);
                out.push(' ');
                push_link_text(&post.company_link, links, language, &mut out);
                out.push_str(&post.period());
                out.push(' ');
                out.push_str(&post.region);
                out.push(' ');
                node_text(&post.desc, links, language, &mut out);
                for skill in &post.skills {
                    out.push_str(skill);
                    out.push(' ');
                }
                for tool in &post.tools {
                    match tool {
                        Tool::Text(value) => {
                            out.push_str(value);
                            out.push(' ');
                        }
                        Tool::Link(reference) => {
                            push_link_text(&reference.link, links, language, &mut out)
                        }
                    }
                }
                for id in &post.links {
                    push_link_text(id, links, language, &mut out);
                }
            }
        }
        1 => {
            if let Some(project) = resume.personal_projects.get(entry) {
                out.push_str(&project.title);
                out.push(' ');
                out.push_str(&project.period());
                out.push(' ');
                out.push_str(&project.modality);
                out.push(' ');
                node_text(&project.desc, links, language, &mut out);
                for skill in &project.skills {
                    out.push_str(skill);
                    out.push(' ');
                }
                for tool in &project.tools {
                    match tool {
                        Tool::Text(value) => {
                            out.push_str(value);
                            out.push(' ');
                        }
                        Tool::Link(reference) => {
                            push_link_text(&reference.link, links, language, &mut out)
                        }
                    }
                }
                for id in &project.links {
                    push_link_text(id, links, language, &mut out);
                }
            }
        }
        2 => {
            if let Some(study) = resume.studies.get(entry) {
                out.push_str(&study.title);
                out.push(' ');
                out.push_str(&study.spe);
                out.push(' ');
                out.push_str(&study.region);
                out.push(' ');
                for tag in &study.tags {
                    out.push_str(tag);
                    out.push(' ');
                }
            }
        }
        _ => {
            if let Some(item) = resume.misc.get(entry) {
                out.push_str(&item.title);
                out.push(' ');
                node_text(&item.desc, links, language, &mut out);
                for tag in &item.tags {
                    out.push_str(tag);
                    out.push(' ');
                }
                for id in &item.links {
                    push_link_text(id, links, language, &mut out);
                }
            }
        }
    }

    out
}

pub fn profile_search_text(profile: &Profile) -> String {
    let mut out = String::new();
    out.push_str(&profile.name);
    out.push(' ');
    out.push_str(&profile.title);
    out.push(' ');
    out.push_str(&profile.region);
    out.push(' ');
    for highlight in &profile.highlights {
        out.push_str(highlight);
        out.push(' ');
    }
    if let Some(current) = &profile.current {
        out.push_str(current);
        out.push(' ');
    }
    for contact in &profile.contact {
        out.push_str(&contact.label);
        out.push(' ');
        out.push_str(&contact.value);
        out.push(' ');
        if let Some(url) = &contact.url {
            out.push_str(url);
            out.push(' ');
        }
    }
    out
}

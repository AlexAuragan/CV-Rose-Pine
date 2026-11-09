//! Styled-text helpers: span construction, unicode-aware wrapping, and a
//! tiny subset of Textual markup (`[bold]`, `[italic #rrggbb]`, `[/]`).

use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use unicode_width::UnicodeWidthChar;

/// A styled run of text.
pub type Chunk = (String, Style);

pub fn display_width(text: &str) -> usize {
    text.chars()
        .map(|c| UnicodeWidthChar::width(c).unwrap_or(0))
        .sum()
}

pub fn spans(chunks: &[Chunk]) -> Vec<Span<'static>> {
    chunks
        .iter()
        .map(|(text, style)| Span::styled(text.clone(), *style))
        .collect()
}

fn parse_hex(token: &str) -> Option<Color> {
    let hex = token.strip_prefix('#')?;
    if hex.len() != 6 {
        return None;
    }
    let value = u32::from_str_radix(hex, 16).ok()?;
    Some(Color::Rgb(
        ((value >> 16) & 0xff) as u8,
        ((value >> 8) & 0xff) as u8,
        (value & 0xff) as u8,
    ))
}

/// Parse a minimal subset of Textual inline markup into styled chunks.
pub fn markup(text: &str, base: Style) -> Vec<Chunk> {
    let mut out: Vec<Chunk> = Vec::new();
    let mut cur = String::new();
    let mut style = base;
    let mut stack: Vec<Style> = vec![base];
    let mut chars = text.chars();

    macro_rules! flush {
        () => {
            if !cur.is_empty() {
                out.push((std::mem::take(&mut cur), style));
            }
        };
    }

    while let Some(c) = chars.next() {
        if c == '[' {
            let mut tag = String::new();
            let mut closed = false;
            for d in chars.by_ref() {
                if d == ']' {
                    closed = true;
                    break;
                }
                tag.push(d);
            }
            if !closed {
                cur.push('[');
                cur.push_str(&tag);
                continue;
            }
            flush!();
            if tag == "/" {
                if stack.len() > 1 {
                    stack.pop();
                }
                style = *stack.last().unwrap_or(&base);
            } else {
                let mut next = *stack.last().unwrap_or(&base);
                for token in tag.split_whitespace() {
                    match token {
                        "bold" => next = next.add_modifier(Modifier::BOLD),
                        "italic" => next = next.add_modifier(Modifier::ITALIC),
                        "underline" => next = next.add_modifier(Modifier::UNDERLINED),
                        other if other.starts_with('#') => {
                            if let Some(color) = parse_hex(other) {
                                next = next.fg(color);
                            }
                        }
                        _ => {}
                    }
                }
                stack.push(next);
                style = next;
            }
            continue;
        }
        cur.push(c);
    }

    flush!();
    out
}

fn push_char(buf: &mut Vec<Span<'static>>, ch: char, style: Style) {
    if let Some(last) = buf.last_mut() {
        if last.style == style {
            last.content.to_mut().push(ch);
            return;
        }
    }
    buf.push(Span::styled(ch.to_string(), style));
}

#[allow(clippy::too_many_arguments)]
fn flush_word(
    lines: &mut Vec<Vec<Span<'static>>>,
    cur: &mut Vec<Span<'static>>,
    cur_w: &mut usize,
    word: &mut Vec<(char, Style)>,
    word_w: &mut usize,
    pending_space: &mut bool,
    width: usize,
) {
    if word.is_empty() {
        return;
    }

    let lead = if *pending_space && !cur.is_empty() { 1 } else { 0 };
    if *cur_w > 0 && *cur_w + lead + *word_w > width {
        lines.push(std::mem::take(cur));
        *cur_w = 0;
    }

    if *pending_space && !cur.is_empty() {
        push_char(cur, ' ', Style::default());
        *cur_w += 1;
    }
    *pending_space = false;

    for (ch, style) in word.drain(..) {
        let cw = UnicodeWidthChar::width(ch).unwrap_or(0);
        if *cur_w + cw > width && *cur_w > 0 {
            lines.push(std::mem::take(cur));
            *cur_w = 0;
        }
        push_char(cur, ch, style);
        *cur_w += cw;
    }
    *word_w = 0;
}

/// Word-wrap styled chunks to `width` columns, honouring explicit newlines.
pub fn wrap_chunks(chunks: &[Chunk], width: usize) -> Vec<Line<'static>> {
    let width = width.max(1);
    let mut lines: Vec<Vec<Span<'static>>> = Vec::new();
    let mut cur: Vec<Span<'static>> = Vec::new();
    let mut cur_w = 0usize;
    let mut word: Vec<(char, Style)> = Vec::new();
    let mut word_w = 0usize;
    let mut pending_space = false;

    for (text, style) in chunks {
        for ch in text.chars() {
            if ch == '\n' {
                flush_word(
                    &mut lines,
                    &mut cur,
                    &mut cur_w,
                    &mut word,
                    &mut word_w,
                    &mut pending_space,
                    width,
                );
                lines.push(std::mem::take(&mut cur));
                cur_w = 0;
                continue;
            }
            if ch == ' ' {
                flush_word(
                    &mut lines,
                    &mut cur,
                    &mut cur_w,
                    &mut word,
                    &mut word_w,
                    &mut pending_space,
                    width,
                );
                pending_space = true;
                continue;
            }
            word.push((ch, *style));
            word_w += UnicodeWidthChar::width(ch).unwrap_or(0);
        }
    }

    flush_word(
        &mut lines,
        &mut cur,
        &mut cur_w,
        &mut word,
        &mut word_w,
        &mut pending_space,
        width,
    );

    if !cur.is_empty() || lines.is_empty() {
        lines.push(cur);
    }

    lines.into_iter().map(Line::from).collect()
}

/// Wrap to `width` with a hanging indent of `indent` columns.
pub fn wrap_indented(
    chunks: &[Chunk],
    width: usize,
    indent: usize,
    indent_style: Style,
) -> Vec<Line<'static>> {
    if indent == 0 {
        return wrap_chunks(chunks, width);
    }
    let inner = width.saturating_sub(indent).max(1);
    wrap_chunks(chunks, inner)
        .into_iter()
        .map(|line| {
            let mut spans = vec![Span::styled(" ".repeat(indent), indent_style)];
            spans.extend(line.spans);
            Line::from(spans)
        })
        .collect()
}

pub fn rule(width: usize, style: Style) -> Line<'static> {
    Line::from(Span::styled("─".repeat(width), style))
}

pub fn centered(text: &str, width: usize, style: Style) -> Line<'static> {
    let text_w = display_width(text).min(width);
    let left = (width.saturating_sub(text_w)) / 2;
    let mut spans = Vec::new();
    if left > 0 {
        spans.push(Span::styled(" ".repeat(left), Style::default()));
    }
    spans.push(Span::styled(text.to_string(), style));
    Line::from(spans)
}

pub fn line_width(line: &Line<'static>) -> usize {
    line.spans
        .iter()
        .map(|span| display_width(&span.content))
        .sum()
}

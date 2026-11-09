//! Application state, event handling, and rendering — the Rust equivalent of
//! `ResumeApp` in `main.py`.

use ratatui::crossterm::event::{KeyCode, KeyEvent};
use ratatui::layout::{Constraint, Layout, Rect};
use ratatui::style::Style;
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, BorderType, Borders, Paragraph};
use ratatui::Frame;

use crate::content;
use crate::models::{Language, Links, Resume};
use crate::render::{
    blank_row, border_bottom, border_row, border_top, empty_placeholder, entry_count,
    entry_search_text, profile_lines, profile_search_text, section_entries, section_title,
    SECTION_COUNT,
};
use crate::text::{spans, Chunk};
use crate::theme::*;

#[derive(Clone, Copy, PartialEq, Eq)]
enum Mode {
    Nav,
    Inside,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum NavArea {
    Profile,
    Sections,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Reveal {
    None,
    SectionPinned(usize),
    Entry(usize, usize),
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum MatchTarget {
    Profile,
    Entry { section: usize, entry: usize },
}

pub struct App {
    mode: Mode,
    nav_area: NavArea,
    language: Language,
    section_index: usize,
    entry_indexes: [usize; SECTION_COUNT],
    pub quit: bool,

    // Search
    search_mode: bool,
    search_input: String,
    search_query: String,
    search_matches: Vec<MatchTarget>,
    search_match_index: usize,
    search_index: Vec<(MatchTarget, String)>,
    showing_search: bool,

    reveal: Reveal,
    profile_scroll: u16,
    content_scroll: u16,

    // Geometry, refreshed every render.
    content_lines: Vec<Line<'static>>,
    section_top: Vec<usize>,
    entry_top: Vec<Vec<usize>>,
}

impl App {
    pub fn new() -> Self {
        let mut app = App {
            mode: Mode::Nav,
            nav_area: NavArea::Profile,
            language: Language::Fr,
            section_index: 0,
            entry_indexes: [0; SECTION_COUNT],
            quit: false,
            search_mode: false,
            search_input: String::new(),
            search_query: String::new(),
            search_matches: Vec::new(),
            search_match_index: 0,
            search_index: Vec::new(),
            showing_search: false,
            reveal: Reveal::None,
            profile_scroll: 0,
            content_scroll: 0,
            content_lines: Vec::new(),
            section_top: Vec::new(),
            entry_top: Vec::new(),
        };
        app.rebuild_search_index();
        app
    }

    // -- helpers ------------------------------------------------------------

    fn current_resume(&self) -> &'static Resume {
        content::resume(self.language)
    }

    fn entries_len(&self, section: usize) -> usize {
        entry_count(section, self.current_resume())
    }

    fn rebuild_search_index(&mut self) {
        let resume = self.current_resume();
        let links = content::links();
        let mut index = Vec::new();

        index.push((
            MatchTarget::Profile,
            fold(&profile_search_text(&resume.profile)),
        ));

        for section in 0..SECTION_COUNT {
            for entry in 0..entry_count(section, resume) {
                let text = entry_search_text(section, entry, resume, links, self.language);
                index.push((MatchTarget::Entry { section, entry }, fold(&text)));
            }
        }

        self.search_index = index;
    }

    // -- actions ------------------------------------------------------------

    fn action_profile(&mut self) {
        self.nav_area = NavArea::Profile;
        self.mode = Mode::Nav;
        self.showing_search = false;
    }

    fn move_vertical(&mut self, step: i32) {
        if self.search_mode {
            return;
        }
        self.showing_search = false;

        if self.nav_area == NavArea::Profile {
            if step < 0 {
                self.profile_scroll = self.profile_scroll.saturating_sub(1);
            } else {
                self.profile_scroll = self.profile_scroll.saturating_add(1);
            }
            return;
        }

        if self.mode == Mode::Inside {
            self.move_between_entries(step);
            return;
        }

        self.move_between_sections(step);
    }

    fn move_pane(&mut self, step: i32) {
        if step < 0 {
            self.action_profile();
            return;
        }
        if step > 0 && self.nav_area == NavArea::Profile {
            self.nav_area = NavArea::Sections;
            self.mode = Mode::Nav;
            self.showing_search = false;
            self.reveal = Reveal::SectionPinned(self.section_index);
        }
    }

    fn move_between_sections(&mut self, step: i32) {
        let count = SECTION_COUNT as i32;
        self.section_index = (self.section_index as i32 + step).rem_euclid(count) as usize;
        self.nav_area = NavArea::Sections;
        self.reveal = Reveal::SectionPinned(self.section_index);
    }

    fn move_between_entries(&mut self, step: i32) {
        let section = self.section_index;
        let len = self.entries_len(section);
        if len == 0 {
            return;
        }
        let current = self.entry_indexes[section] % len;
        let next = (current as i32 + step).rem_euclid(len as i32) as usize;
        self.entry_indexes[section] = next;
        self.reveal = Reveal::Entry(section, next);
    }

    fn enter_section(&mut self) {
        if self.mode != Mode::Nav || self.nav_area != NavArea::Sections {
            return;
        }
        let section = self.section_index;
        self.mode = Mode::Inside;

        if self.entries_len(section) == 0 {
            self.reveal = Reveal::SectionPinned(section);
            return;
        }

        self.entry_indexes[section] = 0;
        self.reveal = Reveal::Entry(section, 0);
    }

    fn leave_section(&mut self) {
        if self.search_mode {
            self.search_mode = false;
            self.search_input.clear();
            return;
        }
        if self.mode != Mode::Inside {
            return;
        }
        self.nav_area = NavArea::Sections;
        self.mode = Mode::Nav;
        self.reveal = Reveal::SectionPinned(self.section_index);
    }

    fn jump(&mut self, index: usize) {
        self.section_index = index % SECTION_COUNT;
        self.nav_area = NavArea::Sections;
        self.mode = Mode::Nav;
        self.showing_search = false;
        self.reveal = Reveal::SectionPinned(self.section_index);
    }

    fn toggle_language(&mut self) {
        self.language = self.language.toggle();
        self.search_query.clear();
        self.search_matches.clear();
        self.search_match_index = 0;
        self.showing_search = false;
        self.rebuild_search_index();

        self.reveal = match self.nav_area {
            NavArea::Profile => Reveal::None,
            NavArea::Sections => {
                if self.mode == Mode::Inside {
                    let section = self.section_index;
                    let len = self.entries_len(section);
                    if len == 0 {
                        Reveal::SectionPinned(section)
                    } else {
                        let index = self.entry_indexes[section].min(len - 1);
                        self.entry_indexes[section] = index;
                        Reveal::Entry(section, index)
                    }
                } else {
                    Reveal::SectionPinned(self.section_index)
                }
            }
        };
    }

    fn open_search(&mut self) {
        self.search_mode = true;
        self.search_input.clear();
    }

    fn submit_search(&mut self) {
        let query = self.search_input.trim().to_string();
        self.search_mode = false;

        if query.is_empty() {
            self.showing_search = false;
            return;
        }

        let needle = fold(&query);
        self.search_query = query;
        self.search_matches = self
            .search_index
            .iter()
            .filter(|(_, text)| text.contains(&needle))
            .map(|(target, _)| *target)
            .collect();
        self.search_match_index = 0;
        self.showing_search = true;

        if !self.search_matches.is_empty() {
            self.focus_match();
        }
    }

    fn next_search(&mut self, step: i32) {
        if self.search_mode || self.search_matches.is_empty() {
            return;
        }
        let len = self.search_matches.len() as i32;
        self.search_match_index = (self.search_match_index as i32 + step).rem_euclid(len) as usize;
        self.showing_search = true;
        self.focus_match();
    }

    fn focus_match(&mut self) {
        if self.search_matches.is_empty() {
            return;
        }
        match self.search_matches[self.search_match_index] {
            MatchTarget::Profile => {
                self.nav_area = NavArea::Profile;
                self.mode = Mode::Nav;
                self.reveal = Reveal::None;
            }
            MatchTarget::Entry { section, entry } => {
                self.section_index = section;
                self.entry_indexes[section] = entry;
                self.nav_area = NavArea::Sections;
                self.mode = Mode::Inside;
                self.reveal = Reveal::Entry(section, entry);
            }
        }
    }

    // -- input --------------------------------------------------------------

    pub fn on_key(&mut self, key: KeyEvent) {
        if self.search_mode {
            self.on_search_key(key);
            return;
        }

        match key.code {
            KeyCode::Char('q') => self.quit = true,
            KeyCode::Char('r' | 'R') => self.toggle_language(),
            KeyCode::Up | KeyCode::Char('k') => self.move_vertical(-1),
            KeyCode::Down | KeyCode::Char('j') => self.move_vertical(1),
            KeyCode::Left | KeyCode::Char('h') => self.move_pane(-1),
            KeyCode::Right | KeyCode::Char('l') => self.move_pane(1),
            KeyCode::Enter => self.enter_section(),
            KeyCode::Esc => self.leave_section(),
            KeyCode::Char('/') | KeyCode::Char('f') => self.open_search(),
            KeyCode::Char('n') => self.next_search(1),
            KeyCode::Char('N') => self.next_search(-1),
            KeyCode::Char('0') => self.action_profile(),
            KeyCode::Char('1') => self.jump(0),
            KeyCode::Char('2') => self.jump(1),
            KeyCode::Char('3') => self.jump(2),
            KeyCode::Char('4') => self.jump(3),
            _ => {}
        }
    }

    fn on_search_key(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc => {
                self.search_mode = false;
                self.search_input.clear();
            }
            KeyCode::Enter => self.submit_search(),
            KeyCode::Backspace => {
                self.search_input.pop();
            }
            KeyCode::Char(c) => self.search_input.push(c),
            _ => {}
        }
    }

    // -- rendering ----------------------------------------------------------

    fn build_doc(&mut self, width: usize) {
        let resume = self.current_resume();
        let links: &Links = content::links();
        let panel_bg = SURFACE;
        let entry_width = width.saturating_sub(4).max(8);

        let mut doc: Vec<Line<'static>> = Vec::new();
        let mut section_top: Vec<usize> = Vec::with_capacity(SECTION_COUNT);
        let mut entry_top: Vec<Vec<usize>> = Vec::with_capacity(SECTION_COUNT);

        for section in 0..SECTION_COUNT {
            section_top.push(doc.len());

            let current = section == self.section_index;
            let focused = current && self.mode == Mode::Inside;
            let border = if focused {
                FOAM
            } else if current {
                IRIS
            } else {
                HIGHLIGHT_MED
            };
            let title_style = if current { bold(fg(GOLD)) } else { fg(MUTED) };

            doc.push(border_top(
                width,
                section_title(section),
                title_style,
                border,
                panel_bg,
            ));

            let entries = section_entries(section, resume, links, self.language, entry_width);

            if entries.is_empty() {
                let line = empty_placeholder(width.saturating_sub(2), fg(MUTED));
                doc.push(border_row(line, width, border, panel_bg, panel_bg));
            }

            let mut tops: Vec<usize> = Vec::with_capacity(entries.len());
            for (index, entry_lines) in entries.iter().enumerate() {
                tops.push(doc.len());
                let selected = focused && index == self.entry_indexes[section];
                let row_bg = if selected { HIGHLIGHT_MED } else { panel_bg };

                for line in entry_lines {
                    let line = indent(line.clone(), 2);
                    doc.push(border_row(line, width, border, panel_bg, row_bg));
                }
                doc.push(border_row(
                    blank_row(panel_bg),
                    width,
                    border,
                    panel_bg,
                    panel_bg,
                ));
            }

            entry_top.push(tops);
            doc.push(border_bottom(width, border, panel_bg));
            doc.push(Line::default());
        }

        self.content_lines = doc;
        self.section_top = section_top;
        self.entry_top = entry_top;
    }

    fn resolve_scroll(&mut self, viewport: usize) {
        let max_scroll = self.content_lines.len().saturating_sub(viewport);

        match self.reveal {
            Reveal::SectionPinned(section) => {
                let top = *self.section_top.get(section).unwrap_or(&0);
                self.content_scroll = top.min(u16::MAX as usize) as u16;
            }
            Reveal::Entry(section, entry) => {
                let target = *self
                    .entry_top
                    .get(section)
                    .and_then(|entries| entries.get(entry))
                    .unwrap_or(&0);
                let current = self.content_scroll as usize;
                if !(current..current + viewport.max(1)).contains(&target) {
                    self.content_scroll = target.min(u16::MAX as usize) as u16;
                }
            }
            Reveal::None => {}
        }
        self.reveal = Reveal::None;

        let max_scroll = max_scroll.min(u16::MAX as usize) as u16;
        self.content_scroll = self.content_scroll.min(max_scroll);
    }

    fn location_spans(&self) -> Vec<Span<'static>> {
        if self.showing_search {
            if self.search_matches.is_empty() {
                return vec![
                    Span::styled("/ ", bold(fg(LOVE))),
                    Span::styled(self.search_query.clone(), bold(fg(GOLD))),
                    Span::styled(" :: no matches".to_string(), fg(SUBTLE)),
                ];
            }
            return vec![
                Span::styled("/ ", bold(fg(LOVE))),
                Span::styled(self.search_query.clone(), bold(fg(GOLD))),
                Span::styled(
                    format!(
                        " :: {}/{} :: n/N next/prev",
                        self.search_match_index + 1,
                        self.search_matches.len()
                    ),
                    fg(SUBTLE),
                ),
            ];
        }

        if self.mode == Mode::Nav && self.nav_area == NavArea::Profile {
            return vec![
                Span::styled("> ", bold(fg(LOVE))),
                Span::styled("profile".to_string(), bold(fg(TEXT))),
                Span::styled(" :: → back to sections".to_string(), fg(SUBTLE)),
            ];
        }

        let title = section_title(self.section_index);

        if self.mode == Mode::Nav {
            return vec![
                Span::styled("> ", bold(fg(LOVE))),
                Span::styled(title.to_string(), bold(fg(TEXT))),
                Span::styled(" :: ← profile :: enter to browse".to_string(), fg(SUBTLE)),
            ];
        }

        let total = self.entries_len(self.section_index);
        let selected = if total == 0 {
            0
        } else {
            self.entry_indexes[self.section_index] + 1
        };
        vec![
            Span::styled("> ", bold(fg(FOAM))),
            Span::styled(title.to_string(), bold(fg(IRIS))),
            Span::styled(
                format!(" :: item {selected}/{total} :: esc to sections"),
                fg(SUBTLE),
            ),
        ]
    }

    fn render_sidebar(&mut self, frame: &mut Frame, rect: Rect) {
        if rect.width < 4 || rect.height < 3 {
            return;
        }
        let resume = self.current_resume();
        let inner_width = rect.width.saturating_sub(2) as usize;
        let lines = profile_lines(&resume.profile, inner_width);

        let viewport = rect.height.saturating_sub(2) as usize;
        let max_scroll = lines.len().saturating_sub(viewport);
        self.profile_scroll = self
            .profile_scroll
            .min(max_scroll.min(u16::MAX as usize) as u16);

        let can_up = self.profile_scroll > 0;
        let can_down = (self.profile_scroll as usize) < max_scroll;

        let focused = self.nav_area == NavArea::Profile;
        let border_color = if focused { IRIS } else { HIGHLIGHT_MED };
        let title_color = if focused { GOLD } else { MUTED };
        let marker = match (can_up, can_down) {
            (true, true) => "^v",
            (true, false) => "^",
            (false, true) => "v",
            (false, false) => "",
        };
        let title = if marker.is_empty() {
            " profile ".to_string()
        } else {
            format!(" profile {marker} ")
        };

        let block = Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded)
            .border_style(fg(border_color))
            .title(Span::styled(title, fg(title_color)))
            .style(bg(SURFACE));

        let paragraph = Paragraph::new(lines)
            .block(block)
            .scroll((self.profile_scroll, 0))
            .style(bg(SURFACE));
        frame.render_widget(paragraph, rect);
    }

    fn render_content(&mut self, frame: &mut Frame, rect: Rect) {
        if rect.width < 4 || rect.height < 1 {
            return;
        }
        self.build_doc(rect.width as usize);
        self.resolve_scroll(rect.height as usize);

        let paragraph = Paragraph::new(self.content_lines.clone())
            .scroll((self.content_scroll, 0))
            .style(bg(BASE));
        frame.render_widget(paragraph, rect);
    }

    fn render_footer(&self, frame: &mut Frame, rect: Rect) {
        let width = rect.width as usize;
        let border = if self.search_mode {
            GOLD
        } else {
            HIGHLIGHT_MED
        };
        let mut lines: Vec<Line<'static>> = Vec::new();
        lines.push(Line::from(Span::styled("─".repeat(width), fg(border))));

        if self.search_mode {
            let mut spans: Vec<Span<'static>> = Vec::new();
            if self.search_input.is_empty() {
                spans.push(Span::styled("grep...".to_string(), fg(MUTED)));
            } else {
                spans.push(Span::styled(self.search_input.clone(), fg(TEXT)));
            }
            spans.push(Span::styled("▏".to_string(), fg(GOLD)));
            lines.push(Line::from(spans));
            lines.push(Line::default());
        } else {
            let hints = hint_spans(self.mode);
            lines.push(self.footer_line(hints, width));
            lines.push(Line::default());
        }

        let paragraph = Paragraph::new(lines).style(bg(SURFACE));
        frame.render_widget(paragraph, rect);
    }

    fn footer_line(&self, hints: Vec<Span<'static>>, width: usize) -> Line<'static> {
        let location = self.location_spans();
        let location_w: usize = location
            .iter()
            .map(|span| crate::text::display_width(&span.content))
            .sum();
        let hints_w: usize = hints
            .iter()
            .map(|span| crate::text::display_width(&span.content))
            .sum();

        let pad = width.saturating_sub(location_w + hints_w).max(1);
        let mut spans = location;
        spans.push(Span::styled(" ".repeat(pad), bg(SURFACE)));
        spans.extend(hints);
        let mut line = Line::from(spans);
        line.style = bg(SURFACE);
        line
    }

    pub fn render(&mut self, frame: &mut Frame) {
        let area = frame.area();
        frame.render_widget(Block::default().style(bg(BASE)), area);

        if area.width == 0 || area.height == 0 {
            return;
        }

        let rows = Layout::vertical([Constraint::Min(0), Constraint::Length(3)]).split(area);
        let body = rows[0];
        let footer = rows[1];

        // `#body` has padding: 1.
        let body_inner = Rect {
            x: body.x.saturating_add(1),
            y: body.y.saturating_add(1),
            width: body.width.saturating_sub(2),
            height: body.height.saturating_sub(2),
        };

        if body_inner.width > 0 && body_inner.height > 0 {
            if area.width >= 100 {
                let sidebar_width = 40.min(body_inner.width);
                let columns =
                    Layout::horizontal([Constraint::Length(sidebar_width), Constraint::Min(0)])
                        .split(body_inner);
                let sidebar_rect = columns[0];
                let mut content_rect = columns[1];
                if content_rect.width > 1 {
                    content_rect.x = content_rect.x.saturating_add(1);
                    content_rect.width = content_rect.width.saturating_sub(1);
                }
                self.render_sidebar(frame, sidebar_rect);
                self.render_content(frame, content_rect);
            } else if area.width >= 65 {
                let sidebar_height = 14.min(body_inner.height);
                let sections =
                    Layout::vertical([Constraint::Length(sidebar_height), Constraint::Min(0)])
                        .split(body_inner);
                self.render_sidebar(frame, sections[0]);
                self.render_content(frame, sections[1]);
            } else {
                self.render_content(frame, body_inner);
            }
        }

        self.render_footer(frame, footer);
    }

    /// Render a single frame to a string using a test backend (for debugging
    /// and screenshots without a live terminal).
    pub fn debug_render(width: u16, height: u16) -> String {
        use ratatui::backend::TestBackend;
        use ratatui::Terminal;

        let backend = TestBackend::new(width, height);
        let mut terminal = Terminal::new(backend).expect("test terminal");
        let mut app = App::new();
        terminal
            .draw(|frame| app.render(frame))
            .expect("render frame");

        let buffer = terminal.backend().buffer();
        let mut out = String::new();
        for y in 0..buffer.area.height {
            for x in 0..buffer.area.width {
                out.push_str(buffer[(x, y)].symbol());
            }
            out.push('\n');
        }
        out
    }
}

fn indent(line: Line<'static>, count: usize) -> Line<'static> {
    let mut spans = vec![Span::styled(" ".repeat(count), Style::default())];
    spans.extend(line.spans);
    let mut out = Line::from(spans);
    out.style = line.style;
    out
}

fn hint_spans(mode: Mode) -> Vec<Span<'static>> {
    let pairs: &[(&str, &str)] = match mode {
        Mode::Nav => &[
            ("←→ hl", "pane"),
            ("↑↓ jk", "section"),
            ("↵", "browse"),
            ("/ f", "search"),
            ("R", "FR/EN"),
            ("0-4", "jump"),
            ("q", "quit"),
        ],
        Mode::Inside => &[
            ("↑↓ jk", "select"),
            ("← h", "profile"),
            ("/ f", "search"),
            ("R", "FR/EN"),
            ("tab", "links"),
            ("esc", "sections"),
            ("q", "quit"),
        ],
    };

    let mut chunks: Vec<Chunk> = Vec::new();
    let last = pairs.len().saturating_sub(1);
    for (index, (key, description)) in pairs.iter().enumerate() {
        chunks.push(((*key).to_string(), bold(fg(IRIS))));
        chunks.push((" ".to_string(), Style::default()));
        chunks.push(((*description).to_string(), fg(SUBTLE)));
        if index != last {
            chunks.push(("  ".to_string(), Style::default()));
        }
    }
    spans(&chunks)
}

#[cfg(test)]
mod tests {
    use super::*;
    use ratatui::backend::TestBackend;
    use ratatui::crossterm::event::KeyModifiers;
    use ratatui::Terminal;

    fn text_of(terminal: &Terminal<TestBackend>) -> String {
        let buffer = terminal.backend().buffer();
        let mut out = String::new();
        for y in 0..buffer.area.height {
            for x in 0..buffer.area.width {
                out.push_str(buffer[(x, y)].symbol());
            }
            out.push('\n');
        }
        out
    }

    fn press(app: &mut App, code: KeyCode) {
        app.on_key(KeyEvent::new(code, KeyModifiers::NONE));
    }

    #[test]
    fn renders_and_navigates() {
        let sizes = [(120u16, 40u16), (80, 30), (50, 20), (20, 6)];

        for (width, height) in sizes {
            let backend = TestBackend::new(width, height);
            let mut terminal = Terminal::new(backend).unwrap();
            let mut app = App::new();

            terminal.draw(|frame| app.render(frame)).unwrap();
            let first = text_of(&terminal);
            assert!(
                first.contains("experience"),
                "section panel missing at {width}x{height}"
            );

            for code in [
                KeyCode::Right,
                KeyCode::Char('j'),
                KeyCode::Enter,
                KeyCode::Char('j'),
                KeyCode::Char('n'),
                KeyCode::Char('R'),
                KeyCode::Char('/'),
                KeyCode::Char('a'),
                KeyCode::Enter,
                KeyCode::Esc,
                KeyCode::Char('0'),
                KeyCode::Char('2'),
                KeyCode::Char('q'),
            ] {
                press(&mut app, code);
                terminal.draw(|frame| app.render(frame)).unwrap();
            }
        }
    }

    #[test]
    fn language_toggle_switches_content() {
        let backend = TestBackend::new(120, 40);
        let mut terminal = Terminal::new(backend).unwrap();
        let mut app = App::new();

        terminal.draw(|frame| app.render(frame)).unwrap();
        let french = text_of(&terminal);
        assert!(french.contains("Ingénieur"), "expected FR profile title");

        press(&mut app, KeyCode::Char('R'));
        terminal.draw(|frame| app.render(frame)).unwrap();
        let english = text_of(&terminal);
        assert!(
            english.contains("Machine Learning"),
            "expected EN profile title"
        );
        assert!(!english.contains("Ingénieur"));
    }

    #[test]
    fn search_finds_and_reports_matches() {
        let mut app = App::new();
        app.open_search();
        for ch in "kitware".chars() {
            press(&mut app, KeyCode::Char(ch));
        }
        press(&mut app, KeyCode::Enter);

        assert!(!app.search_matches.is_empty());
        assert!(app.mode == Mode::Inside);
    }
}

/// Case- and accent-folding for search (stand-in for Python's NFKD fold).
fn fold(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for ch in text.chars() {
        let lowered = ch.to_lowercase().next().unwrap_or(ch);
        match lowered {
            '\u{0300}'..='\u{036f}' => {}
            'à' | 'â' | 'ä' | 'á' | 'ã' | 'å' => out.push('a'),
            'é' | 'è' | 'ê' | 'ë' => out.push('e'),
            'î' | 'ï' | 'í' | 'ì' => out.push('i'),
            'ô' | 'ö' | 'ó' | 'ò' | 'õ' => out.push('o'),
            'û' | 'ü' | 'ú' | 'ù' => out.push('u'),
            'ç' => out.push('c'),
            'ñ' => out.push('n'),
            'ÿ' => out.push('y'),
            _ => out.push(lowered),
        }
    }
    out
}

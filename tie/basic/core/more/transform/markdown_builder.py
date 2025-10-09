"""Markdown formatting utilities."""

# standard library
from abc import ABC, abstractmethod


def _format_txt(text, msg='..(truncated)', max_len=500, prepend='', append=''):
    full_text = f'{prepend}{text}{append}'
    # Remove prepend/append from text if already present to avoid duplication
    if prepend and text.startswith(prepend):
        text = text[len(prepend) :]
    if append and text.endswith(append):
        text = text[: -len(append)]

    full_text = f'{prepend}{text}{append}'
    if len(full_text) > max_len:
        allowed_length = max_len - len(msg)
        # Ensure we don't truncate prepend/append
        text_length = allowed_length - len(prepend) - len(append)
        truncated_text = text[: max(text_length, 0)] + msg
        return f'{prepend}{truncated_text}{append}'
    return full_text


class ContentABC(ABC):
    """Abstract Base Class for Markdown components."""

    @abstractmethod
    def to_markdown(self) -> str:
        """Convert to markdown format."""


class Header(ContentABC):
    """Represents a markdown header."""

    def __init__(self, text: str, *, level: int = 3, spacing: int = 2):
        """Initialize class properties."""
        self.text = text
        self.level = level
        self.spacing = '\n' * spacing

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        return f'{"#" * self.level} {self.text}{self.spacing}'


class TextList(ContentABC):
    """Represents a list of text items in markdown format."""

    def __init__(
        self,
        title,
        sub_title,
        *,
        spacing=2,
        max_items=3,
        max_item_length=500,
        append='',
        prepend='',
    ):
        """Initialize class properties."""
        for name, value in [
            ('spacing', spacing),
            ('max_item_length', max_item_length),
            ('max_items', max_items),
        ]:
            if value < 0:
                ex_msg = f'{name} must be positive'
                raise ValueError(ex_msg)

        self.title = title
        self.sub_title = sub_title
        self.items = []
        self.spacing = '\n' * spacing
        self.max_items = max_items
        self.prepend = prepend
        self.append = append
        self.max_item_length = max_item_length

    def add_item(self, *item: str):
        """Add an item to the list."""
        self.items.extend(item)

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        title_block = Header(self.title, level=3).to_markdown()

        if not self.items:
            return f'{title_block}No Data Provided.{self.spacing}'

        items_ = self.items[: self.max_items]
        markdown = [title_block]
        for index, item in enumerate(items_, start=1):
            item = _format_txt(
                item, max_len=self.max_item_length, prepend=self.prepend, append=self.append
            )
            markdown.append(f'**{self.sub_title} {index}**\n{item}\n\n')
        if len(self.items) > self.max_items:
            more_items_block = f'\n...and {len(self.items) - self.max_items} more items.'
            markdown.append(more_items_block)
        return '\n\n'.join(markdown) + self.spacing


class Text(ContentABC):
    """Represents a single line of markdown with a bolded key and value."""

    def __init__(self, content: str | dict, *, spacing=1, max_length=500, prepend='', append=''):
        """Initialize class properties."""
        for name, value in [
            ('spacing', spacing),
            ('max_length', max_length),
        ]:
            if value < 0:
                ex_msg = f'{name} must be positive'
                raise ValueError(ex_msg)
        self.content = content
        self.spacing = '\n' * spacing
        self.max_length = max_length
        self.prepend = prepend
        self.append = append

    def _truncate(self, text: str) -> str:
        truncation_message = '...(truncated)'
        full_text = f'{self.prepend}{text}{self.append}'
        if len(full_text) > self.max_length:
            allowed_length = self.max_length - len(truncation_message)
            # Ensure we don't truncate prepend/append
            text_length = allowed_length - len(self.prepend) - len(self.append)
            truncated_text = text[: max(text_length, 0)] + truncation_message
            return f'{self.prepend}{truncated_text}{self.append}'
        return full_text

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        if isinstance(self.content, dict):
            lines = []
            for k, v in self.content.items():
                v = _format_txt(
                    str(v), max_len=self.max_length, prepend=self.prepend, append=self.append
                )
                # v = self._truncate(str(v))
                lines.append(f'**{k}**: {v if v else "N/A"}')
            return self.spacing.join(lines) + self.spacing
        content = _format_txt(
            self.content, max_len=self.max_length, prepend=self.prepend, append=self.append
        )
        return f'{content}{self.spacing}'


class Table(ContentABC):
    """Represents a markdown table."""

    def __init__(self, title, *, spacing=2, max_row_length=50, level=3, max_rows=100):
        """Initialize class properties."""
        for name, value in [
            ('spacing', spacing),
            ('max_row_length', max_row_length),
            ('level', level),
            ('max_rows', max_rows),
        ]:
            if value < 0:
                ex_msg = f'{name} must be positive'
                raise ValueError(ex_msg)
        self.title = title
        self.headers = []
        self.rows = []
        self.spacing = '\n' * spacing
        self.level = level
        self.max_row_length = max_row_length
        self.max_rows = max_rows

    def set_headers(self, headers):
        """Set the table headers."""
        self.headers = headers

    def add_row(self, *row: dict):
        """Add a row to the table (only header keys are kept)."""
        if not self.headers:
            ex_msg = 'Headers must be set before adding rows.'
            raise ValueError(ex_msg)
        self.rows.extend(row)

    def to_markdown(self) -> str:
        """Convert the table to a markdown formatted string (with title)."""
        title_block = Header(self.title, level=self.level).to_markdown()

        # No data → show message instead of an empty table
        if not self.rows:
            return f'{title_block}No Data Provided.{self.spacing}'

        order = self.headers or list(self.rows[0].keys())

        header_line = f'|{"|".join(order)}|'
        sep_line = f'|{"|".join("-" for _ in order)}|'
        data = self.rows[: self.max_rows]

        parts = [header_line, sep_line]
        for row_ in data:
            row = []
            for col in order:
                row.append(_format_txt(row_.get(col, ''), max_len=self.max_row_length))
            parts.append(f'|{"|".join(row)}|')

        table = '\n'.join(parts)
        return f'{title_block}{table}{self.spacing}'


class MarkdownBuilder:
    """A simple class to format sections in Markdown."""

    def __init__(self):
        """Initialize class properties."""
        self.content = []

    def add_content(self, *content: ContentABC):
        """Add a table to the list."""
        self.content.extend(content)

    def clear(self):
        """Clear all content."""
        self.content = []

    def to_markdown(self):
        """Format the tables for output."""
        markdown = ''
        for c in self.content:
            markdown += c.to_markdown()
        markdown = markdown.rstrip('\n')
        return markdown

    def header(self, **kwargs) -> Header:
        """Add a Header to the content list.

        Args:
            **kwargs: Keyword-only arguments forwarded to `Header(...)`.
                Supported keys:
                    text (str): Header text. (required)
                    level (int): Header level (1-6). Defaults to 3.
                    spacing (int): Newlines after the header. Defaults to 2.

        Returns:
            Header: The created header component.
        """
        obj = Header(**kwargs)
        self.add_content(obj)
        return obj

    def text(self, **kwargs) -> Text:
        """Add a Text block to the content list.

        Args:
            **kwargs: Keyword-only arguments forwarded to ``Text(...)``.
                Supported keys:
                    content (str | dict): Text or key/value dict to render. (required)
                    spacing (int, optional): Newlines after the block. Defaults to 1.
                    max_length (int, optional): Truncation length. Defaults to 500.
                    prepend (str, optional): Prefix for content. Defaults to ''.
                    append (str, optional): Suffix for content. Defaults to ''.

        Returns:
            Text: The created text component.
        """
        obj = Text(**kwargs)
        self.add_content(obj)
        return obj

    def text_list(self, **kwargs) -> TextList:
        """Add a TextList to the content list.

        Args:
            **kwargs: Keyword-only arguments forwarded to ``TextList(...)``.
                Supported keys:
                    title (str): Section title. (required)
                    sub_title (str): Label used per item (e.g., "Note"). (required)
                    spacing (int, optional): Newlines after the section. Defaults to 2.
                    max_items (int, optional): Max items to render. Defaults to 3.
                    max_item_length (int, optional): Per-item truncation length. Defaults to 500.
                    prepend (str, optional): Prefix for each item. Defaults to ''.
                    append (str, optional): Suffix for each item. Defaults to ''.

        Returns:
            TextList: The created list component.
        """
        obj = TextList(**kwargs)
        self.add_content(obj)
        return obj

    def table(self, **kwargs) -> Table:
        """Add a Table to the content list.

        Args:
            **kwargs: Keyword-only arguments forwarded to ``Table(...)``.
                Supported keys:
                    title (str): Table title. (required)
                    spacing (int, optional): Newlines after the table. Defaults to 2.
                    max_row_length (int, optional): Per-cell truncation length. Defaults to 50.
                    level (int, optional): Header level for the title. Defaults to 3.
                    max_rows (int, optional): Max rows to render. Defaults to 100.

        Returns:
            Table: The created table component.
        """
        obj = Table(**kwargs)
        self.add_content(obj)
        return obj

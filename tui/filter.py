import uuid
from textual.widgets import Button, Input


class FilterChip(Button):
    """Custom button widget representing an active filter."""

    BINDINGS = [
        ("left", "focus_previous_chip", "Focus Previous Filter"),
        ("right", "focus_next_chip", "Focus Next Filter"),
    ]

    def __init__(self, keyword: str):
        filter_id = f"id-{uuid.uuid4().hex}"
        super().__init__(f"✖ {keyword}", variant="error", id=filter_id)
        self.keyword = keyword

    def action_focus_previous_chip(self) -> None:
        parent = self.parent
        if parent is None:
            return
        chips = [child for child in parent.children if isinstance(child, FilterChip)]
        if self in chips:
            idx = chips.index(self)
            chips[idx - 1].focus()

    def action_focus_next_chip(self) -> None:
        parent = self.parent
        if parent is None:
            return
        chips = [child for child in parent.children if isinstance(child, FilterChip)]
        if self in chips:
            idx = chips.index(self)
            chips[(idx + 1) % len(chips)].focus()


class FilterInput(Input):
    """Custom Input widget that releases focus when Escape is pressed."""

    BINDINGS = [
        ("escape", "unfocus", "Unfocus Input"),
    ]

    def action_unfocus(self) -> None:
        self.app.set_focus(None)

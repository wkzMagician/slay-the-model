"""
Display-related actions
"""
from actions.base import Action
from utils.registry import register


class DisplayTextAction(Action):
    """Display text to user
    
    Required:
        text (str): Text to display
        OR
        text_key (str): Localization key
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {
        "text": (str, ""),
        "text_key": (str, None),
    }

    def execute(self):
        from localization import t
        text_key = self.kwargs.get('text_key')
        text = self.kwargs.get('text', '')
        if text_key:
            text = t(text_key, default=text, **self.kwargs)
        elif isinstance(text, str) and text.startswith("@"):
            text = t(text[1:], default=text[1:], **self.kwargs)
        print(text)


class SelectAction(Action):
    """Action that presents choices to user"""
    def __init__(self, title, options=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_key = kwargs.get("title_key")
        if options is None:
            options = kwargs.get("options", [])
        self.options = options  # List of dicts with 'name' and 'actions', or tuples (description, action_list)

    def _normalize_options(self):
        """Normalize options to list of (name, actions) tuples"""
        normalized = []
        for option in self.options:
            if isinstance(option, dict):
                normalized.append((option.get('name', ''), option.get('actions', [])))
            elif isinstance(option, (list, tuple)) and len(option) == 2:
                normalized.append(option)
            else:
                # Invalid format, skip or handle
                normalized.append(('', []))
        return normalized

    def execute(self):
        # If only one choice (and we're not in a menu), execute it directly
        base_choices = self._normalize_options()
        if self._should_auto_select(base_choices):
            _, action_list = base_choices[0]
            return action_list
        if self._should_auto_advance_empty(base_choices):
            return []

        from actions.menu import add_menu_choice_if_human
        effective_choices = add_menu_choice_if_human(
            base_choices,
            self._create_return_action(),
        )
        from localization import t
        title = self.title
        if self.title_key:
            title = t(self.title_key, default=title)
        elif isinstance(title, str) and title.startswith("@"):
            title = t(title[1:], default=title[1:])
        # Display choices
        if self._should_show_menu():
            print(f"\n=== {title} ===")
            for i, (description, _) in enumerate(effective_choices):
                label = description
                if isinstance(label, str) and label.startswith("@"):
                    label = t(label[1:], default=label[1:])
                print(f"{i+1}. {label}")

        if self._should_auto_select_first(effective_choices):
            _, action_list = effective_choices[0]
            return action_list

        while True:
            try:
                prompt = t("ui.select_prompt", default=f"Choose (1-{len(effective_choices)}): ", count=len(effective_choices))
                choice = int(input(prompt)) - 1
                if 0 <= choice < len(effective_choices):
                    _, action_list = effective_choices[choice]
                    return action_list  # Return list of actions to execute
                else:
                    print(t("ui.invalid_choice", default="Invalid choice!"))
            except (ValueError, EOFError):
                print(t("ui.invalid_number", default="Please enter a valid number"))

    def _should_auto_select(self, base_choices):
        game_state = self._get_game_state()
        if len(base_choices) != 1:
            return False
        if game_state.config.get("mode") != "human":
            return True
        return bool(game_state.config.get("auto_select_single_option", False))

    def _should_auto_advance_empty(self, base_choices):
        return len(base_choices) == 0

    def _should_show_menu(self):
        game_state = self._get_game_state()
        return bool(game_state.config.get("show_menu", True))

    def _should_auto_select_first(self, effective_choices):
        game_state = self._get_game_state()
        if not effective_choices:
            return False
        return bool(game_state.config.get("ai_debug", False))

    def _create_return_action(self):
        """Create an action that returns to this same selection pool"""
        return SelectAction(
            self.title,
            options=self.options,
        )

    def _get_game_state(self):
        """Helper to get game state - avoids circular imports"""
        from engine.game_state import game_state
        return game_state
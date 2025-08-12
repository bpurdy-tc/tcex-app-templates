"""UIConfigBuilderABC concrete implementation for building UI configurations."""

# standard library
from abc import abstractmethod

# first-party
from core.task.task_path_pipe_abc import TaskPathPipeABC


class UIConfigBuilderABC:
    """Abstract base class for building UI configuration."""

    def __init__(self, api_properties):
        """Initialize the UI configuration builder with settings."""
        self.settings = api_properties.settings
        self.tasks = api_properties.tasks
        self.sdk = api_properties.sdk

    @property
    def all_statuses(self):
        """All statuses for the job table."""
        statuses = []
        for task in self.tasks.all():
            if isinstance(task, TaskPathPipeABC):
                statuses.append(task.task_settings.status_active.title())
                statuses.append(task.task_settings.status_complete.title())

        statuses += ['Failed', 'Pending']
        return statuses

    @abstractmethod
    def populate(self) -> dict:
        """Abstract method to populate the configuration."""

    def generate_field(self, field: str, label: str, type_: str | None = None):
        """Generate a field."""
        field = {'field': field, 'label': label}
        if type_:
            field['type'] = type_
        return field

    def generate_side_nav_item(self, label: str, path: str):
        """Generate a side nav item."""
        return {'label': label, 'path': path}

    def generate_form_field(
        self,
        name: str,
        label: str,
        type_: str | None = None,
        choices: list[str] | None = None,
        default: str | list[str] = '',
        required: bool = False,
        additional_validators: list[dict] | None = None,
        info: str | None = None,
        min_width: int | None = None,
    ):
        """Generate a form field."""
        choices = choices or []
        additional_validators = additional_validators or []

        field = {
            'name': name,
            'label': label,
            'type': type_,
            'choices': choices,
            'default': default,
            'validators': [],
            'info': info,
            'minWidth': min_width,
        }
        if required and 'required' not in [
            validator['name'] for validator in additional_validators
        ]:
            field['validators'].append({'name': 'required'})

        field = {key: value for key, value in field.items() if value is not None}
        return field

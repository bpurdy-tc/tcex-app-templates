"""UIConfigBuilderABC — abstract base for building UI configurations."""

from abc import abstractmethod

from core.task.task_path_pipe_abc import TaskPathPipeABC


class UIConfigBuilderABC:
    """Abstract base class for building UI configuration.

    Concrete subclasses override ``populate()`` and the various ``*_columns``,
    ``*_details``, ``*_filters``, and ``*_form_fields`` methods to define the
    data-driven UI for their app type.
    """

    def __init__(self, api_properties):
        """Initialize the UI configuration builder with settings."""
        self.settings = api_properties.settings
        self.tasks = api_properties.tasks
        self.sdk = getattr(api_properties, 'sdk', None)

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Top-level assembler (abstract)
    # ------------------------------------------------------------------

    @abstractmethod
    def populate(self) -> dict:
        """Build and return the complete UI configuration dict."""

    # ------------------------------------------------------------------
    # Field generators
    # ------------------------------------------------------------------

    def generate_field(
        self, field: str, label: str, type_: str | None = None, tooltip: str | None = None
    ):
        """Generate a table column / detail field descriptor."""
        field_info = {'field': field, 'label': label}
        if type_:
            field_info['type'] = type_
        if tooltip:
            field_info['tooltip'] = tooltip
        return field_info

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
        """Generate a form field descriptor."""
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

    # ------------------------------------------------------------------
    # Configure page (egress TQL config management)
    # ------------------------------------------------------------------

    def configure_table_columns(self) -> list[dict]:
        """Columns shown in the Configure table.

        Override to customise which config fields appear as table columns.
        Default returns an empty list (no configure page).
        """
        return []

    def configure_form_fields(self) -> list[dict]:
        """Form fields for the Configure add/edit drawer.

        Override to provide the dynamic form layout for configuring TQL queries
        (owners, types, sort field/direction, TQL text, etc.).
        """
        return []

    def configure_info_tooltip(self) -> str | None:
        """Optional tooltip text displayed next to the Configure page title.

        Override to provide app-specific guidance (e.g. explaining TQL query
        ordering and dedup behaviour).
        """
        return None

    # ------------------------------------------------------------------
    # Egress errors page
    # ------------------------------------------------------------------

    def egress_error_table_columns(self) -> list[dict]:
        """Columns shown in the Egress Errors table.

        Override to customise which error fields appear as table columns.
        Default returns an empty list (no egress errors page).
        """
        return []

    def egress_error_table_details(self) -> list[dict]:
        """Fields shown in the Egress Error detail / side-drawer view.

        Override to customise the detail view for egress errors.
        """
        return []

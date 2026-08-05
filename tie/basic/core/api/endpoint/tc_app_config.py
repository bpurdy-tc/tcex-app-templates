"""Class for /api/tc/app-config endpoint"""

from typing import Any

from pydantic import ConfigDict
from spectree import Response

from core.api.endpoint.endpoint_base_abc import EndpointBaseABC
from core.api.falcon_request import FalconRequest
from core.api.falcon_response import FalconResponse
from core.api.spec import spec, tag_settings
from core.api.validation.models.query_param_filter_model import QueryParamFilterModel
from core.model.tie.item_model import ItemModel

try:
    from api.ui_config_builder import UIConfigBuilder
except ImportError:
    UIConfigBuilder = None


class FieldLabelModel(ItemModel):
    """Field Label Model"""

    model_config = ConfigDict(extra='allow')

    field: str
    label: str


class FormModel(ItemModel):
    """Form Model"""

    model_config = ConfigDict(extra='allow')

    choices: list[str] | None = None
    default: str | list[str] | None = None
    info: str | None = None
    label: str
    minWidth: int | None = None  # noqa: N815
    name: str
    type: str | None = None
    validators: list


class FieldsModel(ItemModel):
    """Fields Model"""

    model_config = ConfigDict(extra='allow')

    fields: list[FormModel]


class ValidatorModel(ItemModel):
    """Validator Model"""

    model_config = ConfigDict(extra='allow')

    config: Any
    name: str


class AdhocRequestModel(ItemModel):
    """Adhoc Request Model"""

    model_config = ConfigDict(extra='allow')

    form: FieldsModel


class DownloadTiModel(ItemModel):
    """Download TI Model"""

    model_config = ConfigDict(extra='allow')

    form: FieldsModel


class JobTableModel(ItemModel):
    """Job Table Model"""

    model_config = ConfigDict(extra='allow')

    columns: list[FieldLabelModel]
    details: list[FieldLabelModel]
    filters: FieldsModel


class UiModel(ItemModel):
    """UI Model"""

    model_config = ConfigDict(extra='allow')

    adhocRequest: AdhocRequestModel | None = None  # noqa: N815
    downloadTI: DownloadTiModel | None = None  # noqa: N815
    jobTable: JobTableModel | None = None  # noqa: N815
    owner: str
    title: str
    version: str


class AppConfig(ItemModel):
    """App Config Model"""

    model_config = ConfigDict(extra='allow')

    schema_version: str
    ui: UiModel


class TcAppConfig(EndpointBaseABC):
    """Class for /api/tc/app-config endpoint"""

    @spec.validate(
        query=QueryParamFilterModel,
        resp=Response(HTTP_200=AppConfig),
        skip_validation=True,
        tags=[tag_settings],
    )
    def on_get(
        self,
        _req: FalconRequest,
        resp: FalconResponse,
        query_params: QueryParamFilterModel,
    ):
        """Get the UI configuration for the App."""
        ui_config = {}
        brand = 'threatconnect'

        if UIConfigBuilder:
            ui_config_builder = UIConfigBuilder(self)
            ui_config = ui_config_builder.populate()
            brand = ui_config_builder.brand()

        resp_media = {
            'schema_version': '1.0.0',
            'ui': {
                'title': str(self.tcex.app.ij.model.display_name),
                'version': str(self.tcex.app.ij.model.program_version),
                'owner': self.settings.tc_owner,
                'brand': brand,
                **ui_config,
            },
        }
        resp.media = resp.response_model(resp_media, AppConfig, query_params)

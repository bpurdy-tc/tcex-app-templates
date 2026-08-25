"""Test config resource for /api/tql-config/test endpoint."""

# standard library
import contextlib

# third-party
import falcon
from model.tql_config_model import TqlConfigPostModel
from pydantic import ValidationError

# first-party
from core.api.endpoint.endpoint_base_abc import EndpointBaseABC


class TestConfigResource(EndpointBaseABC):
    """Class for /api/tql-config/test endpoint."""

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """Handle POST requests — validate a TQL config against the TC API and return results."""
        try:
            tql_config = TqlConfigPostModel.parse_obj(req.media or {})
        except ValidationError as ex:
            raise falcon.HTTPBadRequest(description=str(ex)) from ex
        owners = (f'"{o}"' for o in tql_config.owners)

        types = {f'"{t.split(":")[0]}"' for t in tql_config.types}
        tql = (
            f'({tql_config.tql}) and ownerName in ({",".join(owners)}) and typeName in '
            f'({",".join(types)})'
        )

        sorting = f'{tql_config.sort_field} {tql_config.sort_direction}'
        if tql_config.sort_field.lower() != 'id':
            sorting += ' ID DESC'

        params = {
            'count': 'true',
            'fields': [],
            'resultLimit': 1,
            'sorting': sorting,
        }

        indicators = self.tcex.api.tc.v3.indicators(params=params)
        indicators.tql.set_raw_tql(tql)
        with contextlib.suppress(Exception):
            next(iter(indicators))

        response = indicators.request.json()
        resp.media = response

"""Class for /api/tc/app-config endpoint"""

# standard library
from functools import cached_property

# third-party
import falcon
from spectree import Response

# first-party
from core.api.endpoint.tcvf.endpoint_base import EndpointBase
from core.api.falcon_request import FalconRequest
from core.api.falcon_response import FalconResponse
from core.api.spec import spec, tag_job
from core.api.validation.models import QueryParamModel
from core.dao.job_dao import JobRequestDAO


# pylint: disable=unused-argument
class JobRetryResource(EndpointBase):
    """Class for /api/tc/app-config endpoint"""

    @cached_property
    def dao(self) -> JobRequestDAO:
        """Return the dao."""
        return JobRequestDAO(self.db, self.settings)

    @spec.validate(
        resp=Response('HTTP_200'),
        query=QueryParamModel,
        skip_validation=True,
        tags=[tag_job],
    )
    def on_get(
        self,
        _req: FalconRequest,
        resp: FalconResponse,  # noqa: ARG002
        query_params: QueryParamModel,  # noqa: ARG002
        job_id: str,
    ):
        """Download a job files."""
        search_dir = self.settings.base_path / 'failed_working_dir'

        try:
            request = self.dao.get(job_id)
        except FileNotFoundError as f:
            raise falcon.HTTPNotFound from f

        if request.status.lower() != 'failed':
            # TODO uncomment raise falcon.HTTPBadRequest('Job is not failed')
            pass
        for path in search_dir.glob(f'*#{job_id}'):
            if path.is_dir():
                self.log.debug(
                    f'event=found-failed-job-dir, path={path}, action=move-to-upload-dir'
                )
                path.rename(self.settings.base_path / 'upload_working_dir' / path.name)
                break
        else:
            self.log.info('event=failed-job-dir-not-found, job_id={job_id}')
            raise falcon.HTTPNotFound

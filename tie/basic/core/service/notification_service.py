"""Notification Service - Sends TC notifications for pipeline health events."""

import logging
from functools import cached_property

from tcex import TcEx
from tcex.api.tc.v3.tql.tql_operator import TqlOperator

logger = logging.getLogger('tcex')


class NotificationService:
    """Sends TC notifications for pipeline health events."""

    def __init__(self, tcex: TcEx, owner_name: str):
        """Initialize with TcEx instance for API access."""
        self.tcex = tcex
        self.owner_id = self._resolve_owner_id(owner_name)
        self.log = logger
        self._display_name = str(tcex.app.ij.model.display_name)
        self._app_version = str(tcex.app.ij.model.program_version)

    @cached_property
    def msg_prefix(self) -> str:
        """Prefix for all notification messages, truncated to stay within API limits."""
        max_prefix_len = 100
        name = self._display_name
        suffix = f' v{self._app_version}: '

        if len(name) + len(suffix) > max_prefix_len:
            name = name[: max_prefix_len - len(suffix) - 3] + '...'

        return f'{name}{suffix}'

    def _resolve_owner_id(self, owner_name: str) -> int:
        """Resolve owner name to numeric owner ID via TC API."""
        owners = self.tcex.api.tc.v3.security.owners()
        owners.filter.owner_name(TqlOperator.EQ, owner_name)
        for owner in owners:
            if owner.model.id is not None:
                return owner.model.id
        raise RuntimeError(f'Cannot find owner {owner_name!r} in ThreatConnect instance.')

    def send(
        self,
        message: str,
        priority: str = 'Low',
        notification_type: str = 'TIE Pipeline Alert',
    ) -> dict:
        """Send an org-wide notification via POST /v2/notifications.

        Calls the TC API directly to capture the full request and response
        for auditing. Always returns a dict — never raises.
        """
        prefixed_message = f'{self.msg_prefix}{message}'
        request_body = {
            'notificationType': notification_type,
            'priority': priority,
            'isOrganization': False,
            'ownerId': self.owner_id,
            'message': prefixed_message,
        }
        api_request = {'method': 'POST', 'path': '/v2/notifications', 'body': request_body}

        try:
            r = self.tcex.session.tc.post('/v2/notifications', json=request_body)

            try:
                response_body = r.json()
            except Exception:
                response_body = r.text

            api_response = {'statusCode': r.status_code, 'body': response_body}

            if r.ok:
                return {
                    'send_status': 'success',
                    'status_code': r.status_code,
                    'status_text': r.reason,
                    'api_request': api_request,
                    'api_response': api_response,
                }
            return {
                'send_status': 'failed',
                'status_code': r.status_code,
                'status_text': r.text,
                'api_request': api_request,
                'api_response': api_response,
            }
        except Exception as ex:
            self.log.exception('notification-event=send-failed')
            return {
                'send_status': 'failed',
                'status_code': None,
                'status_text': str(ex),
                'api_request': api_request,
                'api_response': None,
            }

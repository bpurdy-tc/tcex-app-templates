"""Notification Service - Sends TC notifications for pipeline health events."""

import logging

from tcex import TcEx

logger = logging.getLogger('tcex')


class NotificationService:
    """Sends TC notifications for pipeline health events."""

    def __init__(self, tcex: TcEx):
        """Initialize with TcEx instance for API access."""
        self.tcex = tcex
        self.log = logger

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
        request_body = {
            'notificationType': notification_type,
            'priority': priority,
            'isOrganization': True,
            'message': message,
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

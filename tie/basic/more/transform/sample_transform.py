"""Transform for various Indicator types"""

from pathlib import Path

from more.transform.custom_transform_abc import CustomTransformABC


class SampleTransform(CustomTransformABC):
    """SAMPLE Transform"""

    def __init__(self, settings, tcex):
        """Initialize class properties."""
        super().__init__(settings, tcex, Path('sample_transform'))

    def _lower_case_example(self, value, **kwargs):  # noqa: ARG002
        """Lower Case Example"""
        return value.lower()

    def register_custom_functions(self):
        """Register custom functions."""
        self.custom_fns.update(
            {
                'lower_case_example': self._lower_case_example,
            }
        )

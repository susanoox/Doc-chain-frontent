from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import WebLinkTestMixin


class WebLinkViewTestCase(WebLinkTestMixin, BaseTestCase):
    def test_method_get_absolute_url(self):
        self._create_test_web_link()

        self._clear_events()

        self.assertTrue(
            self._test_web_link.get_absolute_url()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

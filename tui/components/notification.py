from textual.widget import Widget
from textual.widgets import Static

from tui.icons import NerdIcon

class Notification(Static):

    message = ''
    type = None

    @property
    def notification_style(self):
        type_to_style = {
            'success': {
                'icon': NerdIcon.CHECK,
                'color': 'green',
            },
            'info': {
                'icon': NerdIcon.INFO,
                'color': 'darkcyan',
            },
            'open': {
                'icon': NerdIcon.EXTERNAL_LINK,
                'color': 'darkcyan',
            },
            'warning': {
                'icon': NerdIcon.WARNING,
                'color': 'darkgoldenrod',
            }
        }
        return type_to_style.get(self.type)

    def on_mount(self) -> None:
        self.update(f"{NerdIcon.CHECK} test")

    def notify(self, message, type='success') -> None:
        self._timers.clear()
        self.type = type
        self.message = message
        self.update(f"{self.notification_style['icon']} {self.message}")
        self.styles.background = self.notification_style['color']
        notification = self.query_one('#notification')
        notification.add_class('-active')
        self.set_timer(3, self.stop_notify)

    def stop_notify(self) -> None:
        notification = self.query_one('#notification')
        notification.remove_class('-active')

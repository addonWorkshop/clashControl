import config
import globalPluginHandler
import queueHandler
import ui
from logHandler import log as logger
from scriptHandler import script

from .clash.client import ClashClient
from .clash.service import ClashService
from .deferred_operation_manager import DeferredOperationManager
from .interface import add_settings, remove_settings

config.conf.spec["clashControl"] = {
    "clash_base_url": 'string(default="http://127.0.0.1:9090")',
    "clash_secret": 'string(default="")',
    "clash_modes": 'string(default="")',
}


def safe_message(*args, **kwargs):
    queueHandler.queueFunction(queueHandler.eventQueue, ui.message, *args, **kwargs)


def _call_and_notify(callback, *args, **kwargs):
    try:
        callback(*args, **kwargs)
        safe_message("Applied")
    except Exception:
        ui.message("Operation failed, see logs for details")
        raise


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Clash Control"
    for number in range(1, 11):

        @script(
            description=f"Select clash mode {number}",
            gesture=f"kb:nvda+alt+{number % 10}",
        )
        def script_select_clash_mode(self, gesture, number=number):
            self.select_mode(number - 1)

        _script_name = f"select_mode{number}"
        locals()[f"script_{_script_name}"] = script_select_clash_mode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config.conf["clashControl"]
        add_settings(self.on_save_config)
        self.initialize_service()
        self.operation_manager = DeferredOperationManager()
        self.current_mode_index = None
        self.current_proxy_indexes = [None]

    def terminate(self):
        remove_settings()

    def on_save_config(self):
        self.initialize_service()

    def initialize_service(self):
        modes = None
        if self.config["clash_modes"]:
            modes = self.config["clash_modes"].split(",")
        self.service = ClashService(
            client=ClashClient(
                clash_base_url=self.config["clash_base_url"],
                clash_secret=self.config["clash_secret"],
            ),
            modes=modes,
        )

    def _prepare_service(self, ignore_cache=False):
        try:
            self.service.fetch_data(ignore_cache=ignore_cache)
        except Exception:
            ui.message(
                "Failed to fetch information from the clash server, see logs for details"
            )
            logger.exception("Clash server data fetch failed:")
            return False
        return True

    @script(description="Cycle modes")
    def script_cycle_modes(self, gesture):
        if not self._prepare_service():
            return
        if not self.service.modes:
            ui.message("No modes found")
            return
        current_mode_index = self.current_mode_index
        if current_mode_index is None:
            current_mode_index = self.service.current_mode_index
        self.current_mode_index = (current_mode_index + 1) % len(self.service.modes)
        self.apply_mode_selection()

    def select_mode(self, mode_index: int):
        if not self._prepare_service():
            return
        if len(self.service.modes) <= mode_index:
            ui.message("Mode not found")
            return
        self.current_mode_index = mode_index
        self.apply_mode_selection(0)

    def apply_mode_selection(self, delay=1):
        ui.message(self.service.modes[self.current_mode_index])
        self.operation_manager.schedule(
            "change_mode",
            delay,
            _call_and_notify,
            self.service.set_mode_by_index,
            self.current_mode_index,
        )

    @script(description="Cycle first proxy group")
    def script_cycle_group(self, gesture):
        if not self._prepare_service():
            return
        group_index = 0
        if len(self.service.proxy_groups) <= group_index:
            ui.message("No proxy groups found")
            return
        group = self.service.proxy_groups[group_index]
        current_proxy_index = self.current_proxy_indexes[group_index]
        if current_proxy_index is None:
            current_proxy_index = group.current_proxy_index
        self.current_proxy_indexes[group_index] = (current_proxy_index + 1) % len(
            group.proxy_names
        )
        ui.message(group.proxy_names[self.current_proxy_indexes[group_index]])
        self.operation_manager.schedule(
            f"change_proxy_group_{group_index}",
            1,
            _call_and_notify,
            self.service.select_group_proxy_by_index,
            group_index,
            self.current_proxy_indexes[group_index],
        )

    @script(description="Synchronize and announce state")
    def script_sync(self, gesture):
        if not self._prepare_service(True):
            return
        part = [f'Mode: "{self.service.mode}".']
        for group in self.service.proxy_groups:
            part.append(f'Group "{group.name}": "{group.current_proxy_name}".')
        ui.message(" ".join(part))

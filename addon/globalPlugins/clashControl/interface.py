import addonHandler
import config
import gui.guiHelper
import wx

from .interface_helpers import ConfigBoundSettingsPanel, bind_with_config

addonHandler.initTranslation()


class ClashControlSettingsPanel(ConfigBoundSettingsPanel):
    title = addonHandler.getCodeAddon().manifest["summary"]

    def makeSettings(self, settings_sizer):
        self.config = config.conf["clashControl"]
        sizer = gui.guiHelper.BoxSizerHelper(self, sizer=settings_sizer)
        clash_base_url_field = sizer.addLabeledControl(_("Clash server base url"), wx.TextCtrl)
        self.clash_base_url_field = bind_with_config(clash_base_url_field, "clash_base_url")
        clash_secret_field = sizer.addLabeledControl(_("Clash secret"), wx.TextCtrl)
        self.clash_secret_field = bind_with_config(clash_secret_field, "clash_secret")
        clash_modes_field = sizer.addLabeledControl(_("Clash modes (comma separated)"), wx.TextCtrl)
        self.clash_modes_field = bind_with_config(clash_modes_field, "clash_modes")


def add_settings(on_save_callback):
    ClashControlSettingsPanel.on_save_callback = on_save_callback
    gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(ClashControlSettingsPanel)


def remove_settings():
    gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(ClashControlSettingsPanel)

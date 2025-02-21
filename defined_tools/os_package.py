from GIt.tools.package_tool import PACKAGES
from GIt.tools.base_tool import BaseTool
from GIt.tools.tool_manager import PackageVal, ToolVal
from pywinauto.application import Application
from pywinauto import Desktop
import win32gui
import inspect
from typing import Dict, List


class GuiOp(PACKAGES):
    NAME : str = "Guitools"
    DESCRIPTION : str = "This package Useful for Gui operation and automation"
    DEFAULT_ARGUS : Dict = {}

    def t_inspect_current_app(self,description="It gives information of active window"):
        window_handle = win32gui.GetForegroundWindow()

        if window_handle == 0:
            active_gui = "No active window found."
        else:
            app = Application(backend="uia").connect(handle=window_handle)
            main_window = app.window(handle=window_handle)

            active_app = main_window.print_control_identifiers()

            active_gui = f"""Inspecting currently active window: '{main_window.window_text()}'
    Class name: {main_window.class_name()}
    Window Rectangle: {main_window.rectangle()}
    Available Cintrols in Active App: {active_app}
            """
        return active_gui

    def t_inspect_desktop_window(self,description:str="It inspects running windows",
                                 window_title : str = "title of window"):
        desktop = Desktop(backend="uia")
        window = desktop.window(title=window_title)

        title = f"\nInspecting window: '{window_title}'"
        class_ = f"\nClass name: {window.class_name()}"
        shape = f"\nWindow Rectangle: {window.rectangle()}"
        controls = "\nAvailable Controls in the Window:" + window.print_control_identifiers()

        active_gui = title + class_ + shape + controls

        return active_gui

    def t_list_desktop_windows(self,description="It gives currently activated windows"):
        windows = Desktop(backend="uia").windows()
        list_ = "Open Windows on Desktop:"
        for i, window in enumerate(windows):
            list_ += f"\n{i + 1}. {window.window_text()}"
        return list_
    


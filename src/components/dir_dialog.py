import wx
import os

class DirDialog(wx.DirDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_dialog(parent)

    def create_dialog(self, parent):
        with wx.DirDialog(parent, "Choose output directory", os.getcwd(),
                        wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
            return dirDialog
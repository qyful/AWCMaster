import wx

class menuBar:
    def __init__(self, parent):
        self.parent = parent
        self.create_menu_bar()

    def create_menu_bar(self):
        self.frame_menubar = wx.MenuBar()

        self.file = wx.Menu()
        self.frame_menubar.newProj = self.file.Append(-1, "New Project\tCtrl+N", "Create a new project")
        self.frame_menubar.openProj = self.file.Append(-1, "Open Project\tCtrl+O", "Open an existing project")
        self.file.AppendSeparator()
        self.frame_menubar.saveProj = self.file.Append(-1, "Save Project...\tCtrl+S", "Save your current project")
        self.frame_menubar.saveProjAs = self.file.Append(-1, "Save Project As...\tCtrl+Shift+S", "Save your project using another filename")
        self.frame_menubar.Append(self.file, "File")

        self.options = wx.Menu()
        self.options.Append(-1, "Generate fxmanifest.lua", "Generate an fxmanifest.lua file for FiveM", kind=wx.ITEM_CHECK)
        self.frame_menubar.Append(self.options, "Options")

        self.parent.SetMenuBar(self.frame_menubar)
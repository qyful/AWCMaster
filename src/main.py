from helpers import get_path
import wx
from components import menuBar, PropertiesPanel, SoundListPanel 
import XMLGen

loadedProject = {}
currentProject = {}

class App(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.BORDER_SIMPLE | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 600))
        self.SetTitle("AWCMaster v1.1.0")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.frame_statusbar = self.CreateStatusBar(1, wx.STB_SIZEGRIP)
        self.frame_statusbar.SetStatusWidths([-1])

        self.splitterParent = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitterParent.SetMinimumPaneSize(20)

        self.leftSplitterPanel = wx.Panel(self.splitterParent, wx.ID_ANY)
        self.rightSplitterPanel = wx.Panel(self.splitterParent, wx.ID_ANY)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.leftSplitterPanel.SetSizer(left_sizer)
        self.rightSplitterPanel.SetSizer(right_sizer)

        self.properties_panel = PropertiesPanel(self.rightSplitterPanel)
        right_sizer.Add(self.properties_panel, 1, wx.EXPAND)
        
        self.sound_list_panel = SoundListPanel(self.leftSplitterPanel)
        left_sizer.Add(self.sound_list_panel, 1, wx.EXPAND)

        self.splitterParent.SplitVertically(self.leftSplitterPanel, self.rightSplitterPanel)

        self.Layout()

    def onClose(self, event):
        if event.CanVeto():
            if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?", wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
                event.Veto()
                return
            
        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = App(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        self.menu_bar = menuBar(self.frame)

        _menuBar = self.menu_bar.frame_menubar

        _menuBar.Bind(wx.EVT_MENU, self.newProj, _menuBar.newProj)
        _menuBar.Bind(wx.EVT_MENU, self.openProj, _menuBar.openProj)
        _menuBar.Bind(wx.EVT_MENU, self.saveProj, _menuBar.saveProj)
        _menuBar.Bind(wx.EVT_MENU, self.saveProjAs, _menuBar.saveProjAs)

        return True
    
    def newProj(self, e):
        if loadedProject != currentProject:
            if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?", wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                return

            print("I was changed")
        else:
            print("I wasn't")

    def openProj(self, e):
        with wx.FileDialog(self.frame, "Open AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            if loadedProject != currentProject:
                if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?", wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                    return
            
            pathname = fileDialog.GetPath()
            try:
                print(pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def saveProj(self, e):
        print("3")

    def saveProjAs(self, e):
        with wx.FileDialog(self.frame, "Save AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                print(pathname)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)
    
def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()
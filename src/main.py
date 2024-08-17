import wx
from helpers import get_file_info, save_project, open_project
from components import menuBar, PropertiesPanel, SoundListPanel
# import XMLGen
# import pyi_splash # For Pyinstaller purposes

currentProjectPath = ""
currentProject = {"sound_files": {}}
loadedProject = {"sound_files": {}}

currentItem = ""

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

        self.sound_list_panel.addSoundBtn.Bind(wx.EVT_BUTTON, self.onAddSound)
        self.sound_list_panel.delSoundBtn.Bind(wx.EVT_BUTTON, self.onRemoveSound)
        self.sound_list_panel.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.sound_list_panel.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemDeselected)

        self.properties_panel.SetDefaultProperties()
        self.Layout()

    def onItemDeselected(self, e):
        self.properties_panel.SetDefaultProperties()

    def onItemSelected(self, e):
        soundsList = self.sound_list_panel.soundsList

        index = soundsList.GetFirstSelected()

        if index >= 0:
            item = soundsList.GetItem(index, 0)
            file_name = item.GetText()

            self.properties_panel.soundName.SetValue(file_name)
            
            for item in currentProject["sound_files"][file_name]["flags"]:
                self.properties_panel.flags.Check(item)

            self.properties_panel.Enable()

    def onRemoveSound(self, e):
        selected = self.sound_list_panel.soundsList.GetFirstSelected()

        if selected != -1:
            file_name = [file_name for file_name in currentProject["sound_files"].keys()][selected]
            currentProject["sound_files"].pop(file_name)

            self.sound_list_panel.soundsList.DeleteItem(selected)

            if self.sound_list_panel.soundsList.GetItemCount() < 1:
                self.properties_panel.SetDefaultProperties()
                self.sound_list_panel.delSoundBtn.Disable()
        else:
            wx.MessageBox("You need to select an item", "An error occurred", wx.ICON_ERROR | wx.OK)

    def onAddSound(self, e):
        with wx.FileDialog(self, "Open Audio File", wildcard="*.wav;*.mp3;*.ogg",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path_name = fileDialog.GetPath()
            try:
                self.properties_panel.Enable()

                info = get_file_info(path_name)

                if info:
                    currentProject["sound_files"][info["file_name"]] = info
                    currentProject["sound_files"][info["file_name"]]["flags"] = [2, 15]

                    data = [info["file_name"], info["file_extension"], info["duration"], info["file_size"]]
                    self.sound_list_panel.soundsList.Append(data)

                    _indexed_file_names = [file_name for file_name in currentProject["sound_files"].keys()]
                    
                    for item in _indexed_file_names:
                        if item == info["file_name"]:
                            self.sound_list_panel.soundsList.Select(_indexed_file_names.index(item))
                            break

                    self.properties_panel.flags.Check(2) # Volume
                    self.properties_panel.flags.Check(15) # Category
                    self.properties_panel.soundName.SetValue(info["file_name"])
                    self.sound_list_panel.delSoundBtn.Enable()

            except IOError:
                wx.LogError("Cannot open file '%s'." % path_name)

    def onClose(self, e):
        if e.CanVeto():
            if loadedProject != currentProject:
                if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?", wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
                    e.Veto()
                    return

        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = App(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        self.menu_bar = menuBar(self.frame)

        _menu_bar = self.menu_bar.frame_menubar

        _menu_bar.Bind(wx.EVT_MENU, self.newProj, _menu_bar.newProj)
        _menu_bar.Bind(wx.EVT_MENU, self.openProj, _menu_bar.openProj)
        _menu_bar.Bind(wx.EVT_MENU, self.saveProj, _menu_bar.saveProj)
        _menu_bar.Bind(wx.EVT_MENU, self.saveProjAs, _menu_bar.saveProjAs)

        return True

    def newProj(self, e):
        if loadedProject != currentProject:
            if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?",
                             wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                return
            
            currentProject["sound_files"] = {}

            self.frame.sound_list_panel.soundsList.DeleteAllItems()
            self.frame.properties_panel.SetDefaultProperties()

    def openProj(self, e):
        with wx.FileDialog(self.frame, "Open AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            if loadedProject != currentProject:
                if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?",
                                 wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                    return

            path_name = fileDialog.GetPath()
            
            global currentProjectPath
            currentProjectPath = path_name

            try:
                result = open_project(path_name)

                if result:
                    currentProject["sound_files"] = result["sound_files"]
                    for value in currentProject["sound_files"].values():
                        self.frame.sound_list_panel.soundsList.Append(
                            [
                                value["file_name"],
                                value["file_extension"],
                                value["duration"],
                                value["file_size"]
                            ]
                        )

            except IOError:
                wx.LogError("Cannot open file '%s'." % path_name)

    def saveProj(self, e):
        if currentProjectPath != "":
            save_project(currentProjectPath, currentProject)
        else:
            self.saveProjAs(wx.EVT_BUTTON)

    def saveProjAs(self, e):
        with wx.FileDialog(self.frame, "Save AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path_name = fileDialog.GetPath()
            try:
                save_project(path_name, currentProject)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % path_name)
    
def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()
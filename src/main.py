import wx
import sys
import wave
import time
from helpers import get_file_info, save_project, open_project, convert_to_wav
from components import menuBar, PropertiesPanel, SoundListPanel, DirDialog
import generation

# For Pyinstaller purposes
# import pyi_splash
# pyi_splash.close()

current_project_path = ""
current_project = {"sound_files": {}, "audiobank_name": "custom_sounds", "soundset_name": "custom_sounds", "fxmanifest": False}
loaded_project = {"sound_files": {}, "audiobank_name": "custom_sounds", "soundset_name": "custom_sounds", "fxmanifest": False}

class App(wx.Frame):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.BORDER_SIMPLE | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        
        self.SetSize((800, 600))
        self.SetTitle("AWCMaster v2.1.1")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        icon = wx.IconLocation(sys.executable, 0)
        self.SetIcon(wx.Icon(icon))

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
        self.properties_panel.generateBtn.Bind(wx.EVT_BUTTON, self.onGenerate)
        self.properties_panel.audiobankName.Bind(wx.EVT_TEXT, self.onAudiobankUpdate)
        self.properties_panel.soundsetName.Bind(wx.EVT_TEXT, self.onSoundsetUpdate)
        self.properties_panel.soundName.Bind(wx.EVT_TEXT, self.onSoundNameUpdate)
        self.properties_panel.sampleRate.Bind(wx.EVT_CHOICE, self.onSampleRateUpdate)
        self.properties_panel.flags.Bind(wx.EVT_CHECKLISTBOX, self.onFlagUpdate)

        self.properties_panel.SetDefaultProperties()
        self.Layout()

    def _get_current_sound(self) -> str:
        selected = self.sound_list_panel.soundsList.GetFirstSelected()

        if selected != -1:
            file_name = [file_name for file_name in current_project["sound_files"].keys()][selected]

            return file_name
        else:
            return False

    def onAudiobankUpdate(self, e):
        current_project["audiobank_name"] = self.properties_panel.audiobankName.GetValue()

    def onSoundsetUpdate(self, e):
        current_project["soundset_name"] = self.properties_panel.soundsetName.GetValue()

    def onSampleRateUpdate(self, e):
        selected = self._get_current_sound()

        if selected:
            index = self.properties_panel.sampleRate.GetSelection()

            current_item = current_project["sound_files"][selected]

            current_item["sample_rate"] = self.properties_panel.sampleRate.GetItems()[index]
    
    def onSoundNameUpdate(self, e):
        selected = self._get_current_sound()

        if selected:
            current_project["sound_files"][selected]["file_name"] = self.properties_panel.soundName.GetValue()

            # index = self.sound_list_panel.soundsList.GetFirstSelected()
            # self.sound_list_panel.soundsList.SetItem(index, 0, self.properties_panel.soundName.GetValue())

            # The above bricks the selection code. Need to think of a better way to use the `current_project` dictionary

    def onFlagUpdate(self, e):
        selected = self._get_current_sound()

        if selected:
            current_project["sound_files"][selected]["flags"] = self.properties_panel.flags.GetCheckedStrings()

    def onGenerate(self, e):
        dirDialog = DirDialog(self)

        if dirDialog.ShowModal() == wx.ID_OK:
            path_name = dirDialog.GetPath()

        current_project["sound_files"] = convert_to_wav(current_project,
                                                        output_path=path_name + "\\output",
                                                        fxmanifest = current_project["fxmanifest"]
                                                       )["sound_files"]

        time.sleep(1)

        if self.properties_panel.soundType.GetStringSelection() == "SimpleSound":
            data = {}

            for key, item in current_project["sound_files"].items():
                with wave.open(item["wav_path"], 'rb') as audio_file:
                    sample_rate = audio_file.getframerate()
                    num_frames = audio_file.getnframes()
                    duration_seconds = num_frames / float(sample_rate)
                    num_samples = int(sample_rate * duration_seconds)

                data[key] = {
                    'track': item["file_name"],
                    'flags': item["flags"],
                    'samples': str(num_samples),
                    'sample_rate': str(item["sample_rate"]),
                    'tracks': {'ss': f'{item["file_name"]}.wav'}
                }
            ss = generation.SimpleSound(data,
                                        self.properties_panel.audiobankName.GetValue(),
                                        self.properties_panel.soundsetName.GetValue(),
                                        path_name + "\\output"
                                       )
            
            ss.construct()
            wx.MessageBox("Output was generated in " + path_name, "Success",
                            wx.ICON_INFORMATION | wx.OK, self)

    def onItemDeselected(self, e):
        self.properties_panel.SetDefaultProperties()

    def onItemSelected(self, e):
        soundsList = self.sound_list_panel.soundsList

        index = soundsList.GetFirstSelected()

        if index >= 0:
            item = soundsList.GetItem(index, 0)
            file_name = item.GetText()
            current_file = current_project["sound_files"][file_name]

            self.properties_panel.soundName.ChangeValue(current_file["file_name"])
            self.properties_panel.sampleRate.SetStringSelection(current_file["sample_rate"])
            self.properties_panel.flags.SetCheckedStrings(current_file["flags"])

            self.properties_panel.EnableProperties()

    def onRemoveSound(self, e):
        selected = self._get_current_sound()

        if selected:
            current_project["sound_files"].pop(selected)

            index = self.sound_list_panel.soundsList.GetFirstSelected()
            self.sound_list_panel.soundsList.DeleteItem(index)

            if self.sound_list_panel.soundsList.GetItemCount() < 1:
                self.properties_panel.SetDefaultProperties()
                self.sound_list_panel.delSoundBtn.Disable()
            else:
                self.sound_list_panel.soundsList.Select(0)
        else:
            wx.MessageBox("You need to select an item", "An error occurred", wx.ICON_ERROR | wx.OK)

    def onAddSound(self, e):
        with wx.FileDialog(self, "Open Audio File", wildcard="*.wav;*.mp3;*.ogg",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            paths = fileDialog.GetPaths()

            for path in paths:
                try:
                    self.properties_panel.EnableProperties()

                    info = get_file_info(path)

                    if info:
                        current_project["sound_files"][info["file_name"]] = info

                        current_file = current_project["sound_files"][info["file_name"]]
                        current_file["flags"] = ["Volume", "Category"]
                        current_file["sample_rate"] = "44100"

                        data = [info["file_name"], info["file_extension"], info["duration"], info["file_size"]]

                        if self.sound_list_panel.soundsList.FindItem(-1, info["file_name"]) == wx.NOT_FOUND:
                            self.sound_list_panel.soundsList.Append(data)

                        self.properties_panel.soundName.ChangeValue(info["file_name"])
                        self.sound_list_panel.delSoundBtn.Enable()
                        
                except IOError:
                    wx.LogError("Cannot open file '%s'." % path)

    def onClose(self, e):
        if e.CanVeto():
            if loaded_project != current_project:
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
        _menu_bar.Bind(wx.EVT_MENU, self.fxManifest, _menu_bar.genFx)

        return True

    def fxManifest(self, e):
        if self.menu_bar.frame_menubar.genFx.IsChecked():
            current_project["fxmanifest"] = True
        else:
            current_project["fxmanifest"] = False

    def newProj(self, e):
        if loaded_project != current_project:
            if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?",
                             wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                return
            
            current_project["sound_files"] = {}

            self.frame.sound_list_panel.soundsList.DeleteAllItems()
            self.frame.properties_panel.SetDefaultProperties()

    def openProj(self, e):
        with wx.FileDialog(self.frame, "Open AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            if loaded_project != current_project:
                if wx.MessageBox("Any unsaved changes will be lost", "Are you sure?",
                                 wx.ICON_QUESTION | wx.YES_NO, self.frame) == wx.NO:
                    return

            path_name = fileDialog.GetPath()
            
            global current_project_path
            current_project_path = path_name

            try:
                result = open_project(path_name)

                if result:
                    self.frame.sound_list_panel.soundsList.DeleteAllItems()
                    current_project["sound_files"] = result["sound_files"]
                    for value in current_project["sound_files"].values():
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
        if current_project_path != "":
            save_project(current_project_path, current_project)
        else:
            self.saveProjAs(wx.EVT_BUTTON)

    def saveProjAs(self, e):
        with wx.FileDialog(self.frame, "Save AWCMaster Project", wildcard="AWC Project (*.awcproj)|*.awcproj",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path_name = fileDialog.GetPath()
            try:
                save_project(path_name, current_project)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % path_name)
    
def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()
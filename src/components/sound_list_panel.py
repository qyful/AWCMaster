import wx

class SoundListPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_list()
    
    def create_list(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        soundLabelContainer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Sounds"), wx.HORIZONTAL)
        sizer.Add(soundLabelContainer, 1, wx.ALL | wx.EXPAND, 8)

        self.soundsList = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_NONE | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.soundsList.AppendColumn("Name", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.soundsList.AppendColumn("Type", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.soundsList.AppendColumn("Length", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.soundsList.AppendColumn("Size", format=wx.LIST_FORMAT_LEFT, width=-1)
        soundLabelContainer.Add(self.soundsList, 1, wx.ALL | wx.EXPAND, 4)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT, 8)

        self.addSoundBtn = wx.Button(self, wx.ID_ANY, "Add")
        button_sizer.Add(self.addSoundBtn, 0, 0, 0)

        self.delSoundBtn = wx.Button(self, wx.ID_ANY, "Remove selected")
        button_sizer.Add(self.delSoundBtn, 0, wx.EXPAND | wx.LEFT, 4)

        self.SetSizer(sizer)
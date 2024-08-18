import wx

class PropertiesPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_properties()
    
    def create_properties(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        selectedSLabelContainer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Edit selected sound"), wx.VERTICAL)
        sizer.Add(selectedSLabelContainer, 1, wx.ALL | wx.EXPAND, 8)

        AWCContainer = wx.BoxSizer(wx.HORIZONTAL)
        selectedSLabelContainer.Add(AWCContainer, 0, wx.EXPAND, 0)

        leftAWCContainer = wx.BoxSizer(wx.VERTICAL)
        AWCContainer.Add(leftAWCContainer, 1, wx.EXPAND, 0)

        # Sound Type
        soundTypeLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Type"), wx.HORIZONTAL)
        leftAWCContainer.Add(soundTypeLabel, 0, wx.ALL | wx.EXPAND, 4)
        self.soundType = wx.Choice(self, wx.ID_ANY, choices=["SimpleSound", "Siren"])
        self.soundType.SetSelection(0)
        self.soundType.Disable()
        soundTypeLabel.Add(self.soundType, 1, wx.EXPAND, 0)

        # Sample Rate
        sampleRateLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Sample rate"), wx.HORIZONTAL)
        leftAWCContainer.Add(sampleRateLabel, 0, wx.ALL | wx.EXPAND, 4)
        self.sampleRate = wx.Choice(self, wx.ID_ANY, choices=["8000", "11025", "16000", "22050", "32000", "44100", "48000"])
        self.sampleRate.SetSelection(5)
        sampleRateLabel.Add(self.sampleRate, 1, wx.EXPAND, 0)

        # Sound Name
        soundNameLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Name"), wx.HORIZONTAL)
        leftAWCContainer.Add(soundNameLabel, 0, wx.ALL | wx.EXPAND, 4)
        self.soundName = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE | wx.TE_NO_VSCROLL)
        soundNameLabel.Add(self.soundName, 1, wx.EXPAND, 0)

        # Flags
        rightAWCContainer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Flags"), wx.HORIZONTAL)
        AWCContainer.Add(rightAWCContainer, 1, wx.ALL, 4)
        self.flags = wx.CheckListBox(self, wx.ID_ANY, choices=["Flags2","Unk01","Volume","VolumeVariance","Pitch","PitchVariance","Pan","PanVariance","PreDelay","PreDelayVariance","StartOffset","StartOffsetVariance","AttackTime","ReleaseTime","DopplerFactor","Category","LPFCutOff","LPFCutOffVariance","HPFCutOff","HPFCutOffVariance","UnkHash3","DistanceAttentuation","Unk19","Unk20"], style=wx.LB_SINGLE)
        rightAWCContainer.Add(self.flags, 0, 0, 0)

        # Audiobank and Soundset Name
        AWCPropContainer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(AWCPropContainer, 1, wx.ALL | wx.EXPAND, 8)

        AWCLabelContainer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Edit current container"), wx.VERTICAL)
        AWCPropContainer.Add(AWCLabelContainer, 1, wx.EXPAND, 0)

        # Audiobank Name
        sizer_12 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Audiobank Name"), wx.HORIZONTAL)
        AWCLabelContainer.Add(sizer_12, 0, wx.ALL | wx.EXPAND, 4)
        self.audiobankName = wx.TextCtrl(self, wx.ID_ANY, "custom_sounds")
        sizer_12.Add(self.audiobankName, 1, wx.ALL, 4)

        # Soundset Name
        sizer_16 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Soundset Name"), wx.HORIZONTAL)
        AWCLabelContainer.Add(sizer_16, 0, wx.ALL | wx.EXPAND, 4)
        self.soundsetName = wx.TextCtrl(self, wx.ID_ANY, "custom_sounds")
        sizer_16.Add(self.soundsetName, 1, wx.ALL, 4)

        # Generate Button
        generateBtnContainer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(generateBtnContainer, 0, wx.ALL | wx.EXPAND, 8)

        self.generateBtn = wx.Button(self, wx.ID_ANY, "Generate")
        generateBtnContainer.Add(self.generateBtn, 0, 0, 4)

        self.SetSizer(sizer)

    def EnableProperties(self):
        for item in [self.soundType, self.sampleRate, self.flags, self.soundName]:
            item.Enable()

    def SetDefaultProperties(self):
        for item in [self.soundType, self.sampleRate, self.flags, self.soundName]:
            item.Disable()

        self.soundName.SetValue("")
        self.sampleRate.SetSelection(5)
        
        checkedItems = self.flags.CheckedItems

        for checked in checkedItems:
            self.flags.Check(checked, False)

    def GetSizer(self):
        return super().GetSizer()
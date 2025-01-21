
import traceback
import typing

## Used for theming/coloring configuration for the UI
import ttkbootstrap as tk

from tkinter import ttk, font
from tkinterdnd2 import TkinterDnD
from tk_scroll_frame import ScrollFrame

#from steam_auto_cracker_gui import *
from script_constants import *

from steam_auto_cracker_gui import App


ThemeOption_var: tk.StringVar
UpdateOption_var: tk.StringVar
CrackOption_var: tk.StringVar
Steamless_var: tk.StringVar
SteamApi_var: tk.StringVar
SteamApi64_var: tk.StringVar
GameEXE_var: tk.StringVar
BakSuffix_var: tk.StringVar
RetryDelay_var: tk.StringVar
RetryMax_var: tk.StringVar
BypassGameVerification_var: tk.StringVar





class Root(TkinterDnD.Tk):
    def __init__(self, app: App, *args, **kwargs):
        TkinterDnD.Tk.__init__(self, *args, **kwargs)
        
        self.app = app
        
        # Adding a title to the window
        self.wm_title(f"SteamAutoCracker GUI v{VERSION}")

        self.container = tk.Frame(self, height=400, width=600)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def post_init(self):
        self.settingsPage = SettingsPage(self.container, self)
        self.mainPage = MainPage(self.container, self)

        self.mainPage.post_init()
        #self.settingsPage.post_init()
        
        self.mainPage.grid(row=0, column=0, sticky="nsew")
        self.settingsPage.grid(row=0, column=0, sticky="nsew")

        
        self.mainPage.settingsBtn.setup_ClickHandler(self.showSettings)
        self.settingsPage.homeBtn.setup_ClickHandler(self.showMain)
        

        self.update()
        self.showMain()

        #UpdateSelectedCrackDisplay() # Updates the text of selectCrackButton

    def showSettings(self):
        self.settingsPage.tkraise()

    def showMain(self):
        self.mainPage.tkraise()




class MainPage(tk.Frame):
    def __init__(self, parent, window: Root):
        tk.Frame.__init__(self, parent)
        self.title = f"SteamAutoCracker GUI v{VERSION}"

        self.window = window
        
        self.lblTItle: ttk.Label
        self.lblAuthor: ttk.Label
        
        self.updatesButton: ttk.Button
        
        self.settingsBtn: Settings_TButton
        
        self.scrollFrame: ScrollFrame
        
        self.selectFolderBtn: ttk.Button
        self.selectedFolderFrame: tk.Frame
        self.selectedFolderLabel: tk.Label
        
        self.frameGame: ttk.Frame
        self.frameGame2: ttk.Frame
        self.frame4: ttk.Frame
        self.gameNameEntry: tk.Entry
        self.searchGameButton: ttk.Button
        self.updateAppListButton: ttk.Button
        
        self.gameFoundStatus: ttk.Label
        
        self.frameCrack: ttk.Frame
        self.frameCrack2: ttk.Frame
        self.selectedCrackFrame: ttk.Frame
        self.selectCrackButton: ttk.Button
        self.crackGameButton: ttk.Button
        
        self.logs_text: tk.Text

    def post_init(self):
        self.lblTitle = ttk.Label(self, text=TITLE_MAIN, font=self.window.app.AllFonts["FONT2"], padding=0).pack(pady=(10, 0), anchor="center")
        self.lblAuthor = ttk.Label(self, text=f"by {OPCREDIT}", padding=0).pack(pady=(0, 0), anchor="center")

        self.updatesButton = ttk.Button(self, text=BTN_UPDATECHECK, command=self.window.app.CheckUpdates, padding=0)
        self.updatesButton.place(relx=1, rely=0, anchor='ne')

        self.settingsBtn = Settings_TButton(self, height=24, width=24)
        self.settingsBtn.place(x=2, y=2, anchor="nw")

        #ttk.Separator(self, orient='horizontal').pack(fill="x", padx=220)
        
        self.scrollFrame = ScrollFrame(self)

        # Select folder fields
        tk.Label(self.scrollFrame.viewPort, text=LBL_SELECTFOLDER,).pack(pady=(0, 5), anchor="center")
        self.selectFolderBtn = ttk.Button(self.scrollFrame.viewPort, text=BTN_SELECTFOLDER, command=self.window.app.handle_folder_selection)
        self.selectFolderBtn.pack(pady=(0, 10))

        self.selectedFolderFrame = tk.Frame(self.scrollFrame.viewPort) # This frame will contain the label. This is so we can resize the root window properly when the text is empty.
        self.selectedFolderFrame.pack()
        tk.Frame(self.selectedFolderFrame, width=1, height=1).pack() # 1x1 frame, else selectedFolderFrame will not update its size after it is emptied (by selectedFolderLabel.pack_forget)
        self.selectedFolderLabel = tk.Label(self.selectedFolderFrame, text="", wraplength=700)
        self.selectedFolderLabel.pack()
        self.selectedFolderLabel.pack_forget()

        # Enter game name or appID fields
        self.frameGame = ttk.Frame(self.scrollFrame.viewPort) # Main frame for the game
        self.frameGame.pack(pady=(5, 0), anchor="center")

        tk.Frame(self.frameGame, width=1, height=1).pack() # 1x1 frame, else frameGame will not update its size after it is emptied (by frameGame2.pack_forget)
        self.frameGame2 = ttk.Frame(self.frameGame) # The elements will be inside this one. This is so we can call pack_forget and still preserve the location of frameGame.
        self.frameGame2.pack()
        ttk.Separator(self.frameGame2, orient='horizontal').pack(fill="x", padx=50, pady=(15, 0))
        ttk.Label(self.frameGame2, text=LBL_GAMECRACKENTRY).pack(pady=(15, 0), anchor="center")

        self.frame4 = ttk.Frame(self.frameGame2)
        self.frame4.pack(pady=(5, 0), anchor="center")
        self.gameNameEntry = tk.Entry(self.frame4, width=35, font=self.window.app.AllFonts["FONT_APP_ENTRY"])
        self.gameNameEntry.grid(row=0, column=0, ipady=5)
        self.searchGameButton = ttk.Button(self.frame4, text=BTN_SEARCH, padding=5, command=self.window.app.search_game)
        self.searchGameButton.grid(row=0, column=1, padx=(10, 0))
        self.updateAppListButton = ttk.Button(self.frame4, text=BTN_UDPATEAPPLIST, padding=0, command=self.window.app.UpdateAppList)

        self.gameFoundStatus = ttk.Label(self.frameGame2, text="")
        self.gameFoundStatus.pack(pady=(5, 0), anchor="center")

        self.frameGame2.pack_forget() # Hide the elements, but preserves their location thanks to frameGame still being packed but empty

        # Crack fields
        self.frameCrack = ttk.Frame(self.scrollFrame.viewPort)
        self.frameCrack.pack(pady=(15, 0), anchor="center")
        tk.Frame(self.frameCrack, width=1, height=1).pack() # 1x1 frame
        self.frameCrack2 = ttk.Frame(self.frameCrack)
        self.frameCrack2.pack()
        ttk.Separator(self.frameCrack2, orient='horizontal').pack(fill="x", padx=0, pady=(0, 15))
        self.selectedCrackFrame = ttk.Frame(self.frameCrack2)
        self.selectedCrackFrame.pack()
        tk.Label(self.selectedCrackFrame, text=LBL_SELECTEDCRACK).grid(row=0, column=0)
        self.selectCrackButton = ttk.Button(self.selectedCrackFrame, text=BTN_NONE, padding=5, command=self.window.app.DisplayCrackList)
        self.selectCrackButton.grid(row=0, column=1, padx=(10, 0))
        self.crackGameButton = ttk.Button(self.selectedCrackFrame, text=BTN_CRACKGAME, padding=5, command=self.window.app.CrackGame)
        self.crackGameButton.grid(row=0, column=2, padx=(10, 0))

        self.frameCrack2.pack_forget() # Hide the elements, but preserves their location thanks to frameCrack still being packed but empty

        # Spacer
        #tk.Label(root, text="").pack()

        # Logs scroll text widget
        self.logs_text = tk.Text(self, height=10, width=100, font='TkFixedFont')
        self.logs_text.pack(pady=10, padx=10, fill='both', side='bottom', expand=True)

        text = f"{TITLE_MAIN} by {OPCREDIT}"
        buf = ""
        for i in range(len(text)):
            buf += "-"

        self.logs_text.insert("1.0", f"{buf}\n{text}\n{buf}")
        self.logs_text.config(state=tk.DISABLED) # Prevents users from editing the text inside logs_text
        
        self.scrollFrame.pack(side="top", fill="both", expand=True)


class SettingsPage(tk.Frame):
    def __init__(self, parent, window: Root):
        tk.Frame.__init__(self, parent)
        self.title = TITLE_SETTINGS
        
        self.window = window

        self.lblTitle = ttk.Label(self, text= LBL_TITLESETTINGS, font=self.window.app.AllFonts["FONT2"]).pack(pady=(10,10), anchor="center")
        self.btnReset = ttk.Button(self, text=BTN_RESETSETTINGS, padding=0, command=self.window.app.ResetSettingsButton).pack(pady=(0,0), anchor="center")

        self.homeBtn = Home_TButton(self, height=24, width=24)
        self.homeBtn.place(x=2, y=2, anchor="nw")

        self.scrollFrame = ScrollFrame(self)

        # Theme options (ThemeOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_THEME, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        settings_frame_theme = ttk.Frame(self.scrollFrame.viewPort)
        settings_frame_theme.pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='x')

        # Radios
        global ThemeOption_var
        ThemeOption_var = tk.StringVar()
        ThemeOption_var.set(self.window.app.config["Preferences"]["ThemeOption"])

        # Display subset of themes that correspond to the
        # typical 'light', 'dark', and 'black' theme options
        themeRow = 0
        self.theme_radio_buttons = []
        for themeIdx, themeKey in enumerate(tuple(self.window.app.GetThemes().keys())):
            radiobtn = ttk.Radiobutton(
                settings_frame_theme, text=f"{themeKey}\n({self.window.app.ThemeAliases[themeIdx]})", variable=ThemeOption_var,
                value=themeKey, command=lambda: self.window.app.UpdateConfAndUI("Preferences", "ThemeOption", ThemeOption_var.get())
            )
            self.theme_radio_buttons.append(radiobtn)
            radiobtn.grid(padx=(4,4), pady=(2,2), row=0, column=themeRow, sticky="")
            ##print(f"{themeRow} {themeCol}")
            themeRow += 1
        settings_frame_theme.grid_columnconfigure(tuple(range(3)), weight=1, minsize=100)
        settings_frame_theme.grid_rowconfigure(tuple(range(3)), weight=1)

        # Update options (UpdateOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_UPDATES, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        updateSubNote = Autosized_TLabel(self.scrollFrame.viewPort, self.window.app.AllFonts["FONT4"], foreground="#575757", text=LBL_UPDATESDESC)
        updateSubNote.pack(padx=(0, 6), pady=(0,0), anchor="w", fill="both", side="top", expand=True)
        settings_frame_updates = ttk.Frame(self.scrollFrame.viewPort)
        settings_frame_updates.pack(padx=(15, 0), pady=(0, 0), anchor="w")

        ## Radio
        global UpdateOption_var
        UpdateOption_var = tk.StringVar()
        UpdateOption_var.set(self.window.app.config["Preferences"]["UpdateOption"])
        ttk.Radiobutton(settings_frame_updates, text=RADIOBTN_UPDATECHECKNO, variable=UpdateOption_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "UpdateOption", UpdateOption_var.get())).grid(sticky="w")
        ttk.Radiobutton(settings_frame_updates, text=RADIOBTN_UPDATECHECKAUTO, variable=UpdateOption_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "UpdateOption", UpdateOption_var.get())).grid(sticky="w")

        # Crack approach (CrackOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_CRACKMETHOD, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        settings_frame1 = ttk.Frame(self.scrollFrame.viewPort)
        settings_frame1.pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='x', expand=True)

        ## Radio
        global CrackOption_var
        CrackOption_var = tk.StringVar()
        CrackOption_var.set(self.window.app.config["Preferences"]["CrackOption"])
        ttk.Radiobutton(settings_frame1, text=RADIOBTN_CRACKAUTO, variable=CrackOption_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).pack(anchor="w", pady=0)
        ttk.Radiobutton(settings_frame1, text="Alternate Method 1", variable=CrackOption_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).pack(anchor="w", pady=0)
        Autosized_TLabel(settings_frame1, text=RADIOBTN_CRACKCONFIGDLLGAMEDIR, font=self.window.app.AllFonts["FONT4"], foreground="#575757").pack(anchor="w", fill='x', expand=True, pady=0)
        ttk.Radiobutton(settings_frame1, text="Alternate Method 2", variable=CrackOption_var, value="2", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).pack(anchor="w", pady=0)
        Autosized_TLabel(settings_frame1, text=RADIOBTN_CRACKCONFIGDLLGAMEDIR, font=self.window.app.AllFonts["FONT4"], foreground="#575757").pack(anchor="w", fill='x', expand=True, pady=0)

        # Steamless (Steamless)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_STEAMLESS, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        Autosized_TLabel(self.scrollFrame.viewPort, text=LBL_STEAMLESSDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757").pack(padx=(6, 0), pady=(0,0), anchor="w", fill='x', expand=True)

        settings_frame2 = ttk.Frame(self.scrollFrame.viewPort)
        settings_frame2.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        ## Radio
        global Steamless_var
        Steamless_var = tk.StringVar()
        Steamless_var.set(self.window.app.config["Preferences"]["Steamless"])
        ttk.Radiobutton(settings_frame2, text=RADIOBTN_STEAMLESSNO, variable=Steamless_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "Steamless", Steamless_var.get())).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(settings_frame2, text=RADIOBTN_STEAMLESSYES, variable=Steamless_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "Steamless", Steamless_var.get())).grid(row=1, column=0, sticky="w")

        # FileNames
        ttk.Label(self.scrollFrame.viewPort, text=LBL_FILENAMES, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(self.scrollFrame.viewPort, text=LBL_FILENAMESDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")

        fileNamesFrame = ttk.Frame(self.scrollFrame.viewPort)
        fileNamesFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w", expand=True)

        tk.Label(fileNamesFrame, text=LBL_APIDLLBAK).grid(row=0, column=0, sticky='w')
        global SteamApi_var
        SteamApi_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=SteamApi_var)
        steamApiEntry.grid(row=1, column=0, ipadx=10, ipady=3, padx=(20, 0))
        SteamApi_var.set(self.window.app.config["FileNames"]["SteamAPI"])
        ttk.Button(fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("SteamAPI", SteamApi_var)).grid(row=1, column=1, padx=(0, 20), ipadx=10)

        tk.Label(fileNamesFrame, text=LBL_API64DLLBAK).grid(row=2, column=0, sticky='w')
        global SteamApi64_var
        SteamApi64_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=SteamApi64_var)
        steamApiEntry.grid(row=3, column=0, ipadx=10, ipady=3, padx=(20, 0))
        SteamApi64_var.set(self.window.app.config["FileNames"]["SteamAPI64"])
        ttk.Button(fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("SteamAPI64", SteamApi64_var)).grid(row=3, column=1, padx=(0, 20), ipadx=10)

        tk.Label(fileNamesFrame, text=LBL_EXESUFFIXBAK).grid(row=4, column=0, sticky='w')
        global GameEXE_var
        GameEXE_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=GameEXE_var)
        steamApiEntry.grid(row=5, column=0, ipadx=10, ipady=3, padx=(20, 0))
        GameEXE_var.set(self.window.app.config["FileNames"]["GameEXE"])
        ttk.Button(fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("GameEXE", GameEXE_var)).grid(row=5, column=1, padx=(0, 20), ipadx=10)

        tk.Label(fileNamesFrame, text=LBL_OTHERSUFFIXBAK).grid(row=6, column=0, sticky='w')
        global BakSuffix_var
        BakSuffix_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=BakSuffix_var)
        steamApiEntry.grid(row=7, column=0, ipadx=10, ipady=3, padx=(20, 0))
        BakSuffix_var.set(self.window.app.config["FileNames"]["BakSuffix"])
        ttk.Button(fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("BakSuffix", BakSuffix_var)).grid(row=7, column=1, padx=(0, 20), ipadx=10)

        fileNamesFrame.grid_columnconfigure(0, weight=50, minsize=120)

        # Advanced
        ttk.Label(self.scrollFrame.viewPort, text=LBL_ADVANCED, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(self.scrollFrame.viewPort, text=LBL_ADVANCEDDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757", wraplength=300).pack(padx=(6, 0), pady=(0,0), anchor="w")

        advTextFrame = ttk.Frame(self.scrollFrame.viewPort)
        advTextFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        tk.Label(advTextFrame, text=LBL_RETRYDELAY).grid(row=0, column=0)
        global RetryDelay_var
        RetryDelay_var = tk.StringVar()
        steamApiEntry = tk.Entry(advTextFrame, width=10, textvariable=RetryDelay_var)
        steamApiEntry.grid(row=0, column=1, ipadx=10, ipady=3)
        RetryDelay_var.set(self.window.app.config["Advanced"]["RetryDelay"])
        ttk.Button(advTextFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateAdvanced("RetryDelay", RetryDelay_var)).grid(row=0, column=2, ipadx=10)

        tk.Label(advTextFrame, text=LBL_RETRYMAX).grid(row=1, column=0)
        global RetryMax_var
        RetryMax_var = tk.StringVar()
        steamApiEntry = tk.Entry(advTextFrame, width=10, textvariable=RetryMax_var)
        steamApiEntry.grid(row=1, column=1, ipadx=10, ipady=3)
        RetryMax_var.set(self.window.app.config["Advanced"]["RetryMax"])
        ttk.Button(advTextFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateAdvanced("RetryMax", RetryMax_var)).grid(row=1, column=2, ipadx=10)

        global BypassGameVerification_var
        BypassGameVerification_var = tk.StringVar()
        BypassGameVerification_var.set(self.window.app.config["Advanced"]["BypassGameVerification"])
        advBypassGameVerification = ttk.Checkbutton(self.scrollFrame.viewPort, text=CHKBOX_BYPASSGAMEVERIF, variable=BypassGameVerification_var, command=lambda: self.window.app.UpdateAdvanced("BypassGameVerification", BypassGameVerification_var))
        advBypassGameVerification.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        self.scrollFrame.pack(side="top", fill="both", expand=True)


class TopLevelWindow(tk.Toplevel):
    def __init__(self, app: App, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.app = app


class UpdatePopup(TopLevelWindow):
    def __init__(self, latestVersion: str, *args, **kwargs):
        TopLevelWindow.__init__(self, *args, **kwargs)
        
        self.latestVersion = latestVersion
        
        self.title(TITLE_UPDATE)
        self.resizable(False, False)
        
        self.biggerFont = self.app.AllFonts["DEFAULT_FONT"].copy().config(size=10)
        
        self.updateDisplayButtonsFrame: ttk.Frame
        self.updateDisplayButtonUpdate: ttk.Button
        self.updateDisplayButtonCopy: ttk.Button
        self.updateDisplayButtonClose: ttk.Button
        self.updateDisplayStatusLabel: ttk.Label

        
    def post_init(self):
        
        ttk.Label(self, text=LBL_TITLEUPDATE, font=self.app.AllFonts["FONT2"]).pack(padx=200, pady=(10,10), anchor="center")
        ttk.Label(self, text=LBL_UPDATEAVAILCONFIRM, font=self.biggerFont, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(self, text=LBL_VERSIONCUR, font=self.biggerFont, padding=0).pack(padx=(6, 0), pady=(15,0), anchor="w")
        ttk.Label(self, text=LBL_VERSIONNEW.format(version=self.latestVersion), font=self.biggerFont, padding=0).pack(padx=(6, 0), pady=(0,10), anchor="w")
        
        self.updateDisplayButtonsFrame = ttk.Frame(self)
        self.updateDisplayButtonsFrame.pack(pady=(5,20))
        
        self.updateDisplayButtonUpdate = ttk.Button(self.updateDisplayButtonsFrame, text=BTN_UPDATE, command=self.app.UpdateSAC, padding=3)
        self.updateDisplayButtonUpdate.grid(row=0, column=0)

        self.updateDisplayButtonCopy = ttk.Button(self.updateDisplayButtonsFrame, text=BTN_COPYRELURL, command=self.app.CopyReleaseURL, padding=3)
        self.updateDisplayButtonCopy.grid(row=0, column=1, padx=(50,0))

        self.updateDisplayButtonClose = ttk.Button(self.updateDisplayButtonsFrame, text=BTN_DONTUPDATE, command=self.destroy, padding=3)
        self.updateDisplayButtonClose.grid(row=0, column=2, padx=(50,0))

        self.updateDisplayStatusLabel = ttk.Label(self, text="", font=self.biggerFont, padding=0)


class Canvas_TButton(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.buttonSize = 24

        self.btnImg: tk.PhotoImage = None
        self.btnImg: tk.PhotoImage = None
        self.btnImg_Hover: tk.PhotoImage = None
        self.btnImg_Hover: tk.PhotoImage = None

        self.bind("<Enter>", self.btn_mouseEvent)
        self.bind("<Leave>", self.btn_mouseEvent)

    def setup_ClickHandler(self, func: typing.Callable[[], None]):
        self.bind("<Button>", lambda _: func())

    def btn_mouseEvent(self, e):
        match str(e.type):
            case "7": # Mouse Enter
                self.itemconfig(1, image=self.btnImg_Hover)
            case "8": # Mouse Leave
                self.itemconfig(1, image=self.btnImg)

    def setImage(self, imgType: typing.Literal['base', 'hover'], imgPath: str) -> tk.PhotoImage | None:
        match imgType:
            case 'base':
                self.btnImg = tk.PhotoImage(file=imgPath)
                self.btnImg = self.btnImg.subsample(round(self.btnImg.width() / self.buttonSize / 1.0))
                self.create_image(self.buttonSize / 2.0, self.buttonSize / 2.0, anchor="center", image=self.btnImg)
                return self.btnImg
            case 'hover':
                self.btnImg_Hover = tk.PhotoImage(file=imgPath)
                self.btnImg_Hover = self.btnImg_Hover.subsample(round(self.btnImg_Hover.width() / self.buttonSize / 1.0))
                return self.btnImg_Hover
            case _:
                return None

    def setup(self, size: int, imagePath: str = None, func_on_click: typing.Callable[[],None] = None, imagePath_hover: str = None):
        self.buttonSize = size
        if (imagePath is not None):
            self.btnImg = self.setImage('base', imagePath)
        if (imagePath_hover is None):
            imagePath_hover = imagePath
        if (imagePath_hover is not None):
            self.btnImg_Hover = self.setImage('hover', imagePath_hover)
        if (func_on_click is not None):
            self.setup_ClickHandler(func_on_click)


class Autosized_TLabel(tk.Label):
    def __init__(self, parent: tk.tk.Misc | None, font: tk.font.Font, *args, **kwargs):
        tk.Label.__init__(self, parent, *args, font=font, **kwargs)
        self.parent = parent
        self.font = font
        self.bind("<Configure>", self.onConfigureEvent)

    def onConfigureEvent(self, _):
        try:
            offsetW = 6 + 4 + 6 + 4 # includes system padding/border/etc. (kinda magic number-y/arbitrary)
            targetWidth = min(900, self.parent.winfo_width()) - offsetW
            if (targetWidth > 900):
                return
            
            curWidth = 0
            lineWidth = 0
            text: str = self.cget("text")
            for i in range(len(text)):
                char = text[i]
                charWidth = self.font.measure(char)
                lineWidth = charWidth + lineWidth
                if (char == '\n'):
                    curWidth = max(lineWidth, curWidth)
                    lineWidth = 0
                elif (lineWidth <= targetWidth):
                    curWidth = max(lineWidth, curWidth)
                else:
                    lineWidth = charWidth
            self.config(wraplength=targetWidth, width=targetWidth + 50, justify="left")
        except:
            traceback.print_exc()


class Settings_TButton(Canvas_TButton):
    def __init__(self, *args, **kwargs):
        Canvas_TButton.__init__(self, *args, **kwargs)
        self.setup(
            self.buttonSize,
            "./imgs/windows_settings_icon.png",
            None,
            "./imgs/windows_settings_icon-hover.png"
        )


class Home_TButton(Canvas_TButton):
    def __init__(self, *args, **kwargs):
        Canvas_TButton.__init__(self, *args, **kwargs)
        self.setup(
            self.buttonSize,
            "./imgs/back_64.png",
            None,
            "./imgs/back_64_hover.png",
        )


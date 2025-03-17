
import tkinter.font
import tkinter.ttk
import traceback
import typing

## Used for theming/coloring configuration for the UI
import ttkbootstrap as tkb

tk = tkb.ttk

import tkinter as tkinter
from tkinter import ttk, font, Tk
from tkinterdnd2 import TkinterDnD
from tk_scroll_frame import ScrollFrame

from script_constants import *
from steam_auto_cracker_gui import App



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
        self.settingsPage.post_init()
        
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
        
        self.lblTitle: ttk.Label
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
        
        self.logs_text: tkinter.Text

    def post_init(self):
        self.lblTitle = ttk.Label(self, text=TITLE_MAIN, font=self.window.app.AllFonts["FONT2"], padding=0).pack(pady=(10, 0), anchor="center")
        self.lblAuthor = ttk.Label(self, text=f"by {OPCREDIT}", padding=0).pack(pady=(0, 0), anchor="center")

        self.updatesButton = ttk.Button(self, text=BTN_UPDATECHECK, command=self.window.app.CheckUpdates, padding=0)
        self.updatesButton.place(relx=1, rely=0, anchor='ne')

        self.settingsBtn = Settings_TButton(self, 31, height=31, width=31)
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
        self.logs_text = tkinter.Text(self, height=10, width=100, font='TkFixedFont')
        self.logs_text.pack(pady=10, padx=10, fill='both', side='bottom', expand=True)

        text = f"{TITLE_MAIN} by {OPCREDIT}"
        buf = ""
        for i in range(len(text)):
            buf += "-"

        self.logs_text.insert("1.0", f"{buf}\n{text}\n{buf}")
        self.logs_text.config(state=tkinter.DISABLED) # Prevents users from editing the text inside logs_text
        
        self.scrollFrame.pack(side="top", fill="both", expand=True)


class SettingsPage(tk.Frame):
    def __init__(self, parent, window: Root):
        tk.Frame.__init__(self, parent)
        self.title = TITLE_SETTINGS
        
        self.window = window

        self.lblTitle: ttk.Label
        self.btnReset: ttk.Button

        self.homeBtn: Home_TButton

        self.scrollFrame: ScrollFrame

        self.settings_frame_theme: ttk.Frame

        self.ThemeOption_var: tkinter.StringVar
        self.theme_radio_buttons: list[ttk.Radiobutton]
    
        self.updateSubNote: Autosized_TLabel
        self.settings_frame_updates: ttk.Frame

        self.UpdateOption_var: tkinter.StringVar

        self.settings_frame_crack: ttk.Frame

        self.CrackOption_var: tkinter.StringVar
        
        self.settings_frame_steamless: ttk.Frame

        self.Steamless_var: tkinter.StringVar
        
        self.fileNamesFrame: ttk.Frame

        self.SteamApi_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry
        
        self.SteamApi64_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry
        
        self.GameEXE_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry

        self.BakSuffix_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry
        
        self.advTextFrame: ttk.Frame

        self.RetryDelay_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry
        
        self.RetryMax_var: tkinter.StringVar
        self.steamApiEntry: tk.Entry
                
        self.BypassGameVerif_var: tkinter.StringVar
        self.advBypassGameVerif: ttk.Checkbutton
        
    def post_init(self):
        
        self.lblTitle = ttk.Label(self, text= LBL_TITLESETTINGS, font=self.window.app.AllFonts["FONT2"]).pack(pady=(10,10), anchor='center')
        self.btnReset = ttk.Button(self, text=BTN_RESETSETTINGS, padding=0, command=self.window.app.ResetSettingsButton).pack(pady=(0,0), anchor="center")

        self.homeBtn = Home_TButton(self, 24, height=24, width=24)
        self.homeBtn.place(x=4, y=4, anchor="nw")

        self.scrollFrame = ScrollFrame(self)

        # Theme options (ThemeOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_THEME, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        self.settings_frame_theme = ttk.Frame(self.scrollFrame.viewPort)
        self.settings_frame_theme.pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='x')

        # Radios
        self.ThemeOption_var = tkinter.StringVar()
        self.ThemeOption_var.set(self.window.app.config["Preferences"]["ThemeOption"])

        # Display subset of themes that correspond to the
        # typical 'light', 'dark', and 'black' theme options
        themeRow = 0
        self.theme_radio_buttons = []
        for themeIdx, themeKey in enumerate(tuple(self.window.app.GetThemes().keys())):
            radiobtn = ttk.Radiobutton(
                self.settings_frame_theme, text=f"{themeKey}\n({self.window.app.ThemeAliases[themeIdx]})", variable=self.ThemeOption_var,
                value=themeKey, command=lambda: self.window.app.UpdateConfAndUI("Preferences", "ThemeOption", self.ThemeOption_var.get())
            )
            self.theme_radio_buttons.append(radiobtn)
            radiobtn.grid(padx=(4,4), pady=(2,2), row=0, column=themeRow, sticky="")
            ##print(f"{themeRow} {themeCol}")
            themeRow += 1
        self.settings_frame_theme.grid_columnconfigure(tuple(range(3)), weight=1, minsize=100)
        self.settings_frame_theme.grid_rowconfigure(tuple(range(3)), weight=1)

        # Update options (UpdateOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_UPDATES, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        self.updateSubNote = Autosized_TLabel(self.scrollFrame.viewPort, self.window.app.AllFonts["FONT4"], foreground="#575757", text=LBL_UPDATESDESC)
        self.updateSubNote.pack(padx=(0, 6), pady=(0,0), anchor="w", fill="both", side="top", expand=True)
        self.settings_frame_updates = ttk.Frame(self.scrollFrame.viewPort)
        self.settings_frame_updates.pack(padx=(15, 0), pady=(0, 0), anchor="w")

        ## Radio
        self.UpdateOption_var = tkinter.StringVar()
        self.UpdateOption_var.set(self.window.app.config["Preferences"]["UpdateOption"])
        ttk.Radiobutton(self.settings_frame_updates, text=RADIOBTN_UPDATECHECKNO, variable=self.UpdateOption_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "UpdateOption", self.UpdateOption_var.get())).grid(sticky="w")
        ttk.Radiobutton(self.settings_frame_updates, text=RADIOBTN_UPDATECHECKAUTO, variable=self.UpdateOption_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "UpdateOption", self.UpdateOption_var.get())).grid(sticky="w")

        # Crack approach (CrackOption)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_CRACKMETHOD, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        self.settings_frame_crack = ttk.Frame(self.scrollFrame.viewPort)
        self.settings_frame_crack.pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='x', expand=True)

        ## Radio
        self.CrackOption_var = tkinter.StringVar()
        self.CrackOption_var.set(self.window.app.config["Preferences"]["CrackOption"])
        ttk.Radiobutton(self.settings_frame_crack, text=RADIOBTN_CRACKAUTO, variable=self.CrackOption_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", self.CrackOption_var.get())).pack(anchor="w", pady=0)
        ttk.Radiobutton(self.settings_frame_crack, text="Alternate Method 1", variable=self.CrackOption_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", self.rackOption_var.get())).pack(anchor="w", pady=0)
        Autosized_TLabel(self.settings_frame_crack, text=RADIOBTN_CRACKCONFIGDLLGAMEDIR, font=self.window.app.AllFonts["FONT4"], foreground="#575757").pack(anchor="w", fill='x', expand=True, pady=0)
        ttk.Radiobutton(self.settings_frame_crack, text="Alternate Method 2", variable=self.CrackOption_var, value="2", command=lambda: self.window.app.UpdateConfigKey("Preferences", "CrackOption", self.CrackOption_var.get())).pack(anchor="w", pady=0)
        Autosized_TLabel(self.settings_frame_crack, text=RADIOBTN_CRACKCONFIGDLLGAMEDIR, font=self.window.app.AllFonts["FONT4"], foreground="#575757").pack(anchor="w", fill='x', expand=True, pady=0)

        # Steamless (Steamless)
        ttk.Label(self.scrollFrame.viewPort, text=LBL_STEAMLESS, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        Autosized_TLabel(self.scrollFrame.viewPort, text=LBL_STEAMLESSDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757").pack(padx=(6, 0), pady=(0,0), anchor="w", fill='x', expand=True)

        self.settings_frame_steamless = ttk.Frame(self.scrollFrame.viewPort)
        self.settings_frame_steamless.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        ## Radio
        self.Steamless_var = tkinter.StringVar()
        self.Steamless_var.set(self.window.app.config["Preferences"]["Steamless"])
        ttk.Radiobutton(self.settings_frame_steamless, text=RADIOBTN_STEAMLESSNO, variable=self.Steamless_var, value="0", command=lambda: self.window.app.UpdateConfigKey("Preferences", "Steamless", self.Steamless_var.get())).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.settings_frame_steamless, text=RADIOBTN_STEAMLESSYES, variable=self.Steamless_var, value="1", command=lambda: self.window.app.UpdateConfigKey("Preferences", "Steamless", self.Steamless_var.get())).grid(row=1, column=0, sticky="w")

        # FileNames
        ttk.Label(self.scrollFrame.viewPort, text=LBL_FILENAMES, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(self.scrollFrame.viewPort, text=LBL_FILENAMESDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")

        self.fileNamesFrame = ttk.Frame(self.scrollFrame.viewPort)
        self.fileNamesFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w", expand=True)

        tk.Label(self.fileNamesFrame, text=LBL_APIDLLBAK).grid(row=0, column=0, sticky='w')
        self.SteamApi_var = tkinter.StringVar()
        self.steamApiEntry = tk.Entry(self.fileNamesFrame, width=35, textvariable=self.SteamApi_var)
        self.steamApiEntry.grid(row=1, column=0, ipadx=10, ipady=3, padx=(20, 0))
        self.SteamApi_var.set(self.window.app.config["FileNames"]["SteamAPI"])
        Canvas_TButton(self.fileNamesFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("SteamAPI", self.SteamApi_var), "./imgs/save-hover.png").grid(row=1, column=1, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.fileNamesFrame, text="", image=tkinter.PhotoImage("./imgs/save.png"), padding=3, command=lambda: self.window.app.UpdateFileName("SteamAPI", self.SteamApi_var)).grid(row=1, column=1, padx=(0, 20), ipadx=10)

        tk.Label(self.fileNamesFrame, text=LBL_API64DLLBAK).grid(row=2, column=0, sticky='w')
        self.SteamApi64_var = tkinter.StringVar()
        self.steamApiEntry = tk.Entry(self.fileNamesFrame, width=35, textvariable=self.SteamApi64_var)
        self.steamApiEntry.grid(row=3, column=0, ipadx=10, ipady=3, padx=(20, 0))
        self.SteamApi64_var.set(self.window.app.config["FileNames"]["SteamAPI64"])
        Canvas_TButton(self.fileNamesFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("SteamAPI64", self.SteamApi64_var), "./imgs/save-hover.png").grid(row=3, column=1, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("SteamAPI64", self.SteamApi64_var)).grid(row=3, column=1, padx=(0, 20), ipadx=10)

        tk.Label(self.fileNamesFrame, text=LBL_EXESUFFIXBAK).grid(row=4, column=0, sticky='w')
        self.GameEXE_var = tkinter.StringVar()
        self.steamApiEntry = tk.Entry(self.fileNamesFrame, width=35, textvariable=self.GameEXE_var)
        self.steamApiEntry.grid(row=5, column=0, ipadx=10, ipady=3, padx=(20, 0))
        self.GameEXE_var.set(self.window.app.config["FileNames"]["GameEXE"])
        Canvas_TButton(self.fileNamesFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("GameEXE", self.GameEXE_var), "./imgs/save-hover.png").grid(row=5, column=1, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("GameEXE", self.GameEXE_var)).grid(row=5, column=1, padx=(0, 20), ipadx=10)

        tk.Label(self.fileNamesFrame, text=LBL_OTHERSUFFIXBAK).grid(row=6, column=0, sticky='w')
        self.BakSuffix_var = tkinter.StringVar()
        self.steamApiEntry = tk.Entry(self.fileNamesFrame, width=35, textvariable=self.BakSuffix_var)
        self.steamApiEntry.grid(row=7, column=0, ipadx=10, ipady=3, padx=(20, 0))
        self.BakSuffix_var.set(self.window.app.config["FileNames"]["BakSuffix"])
        Canvas_TButton(self.fileNamesFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("BakSuffix", self.BakSuffix_var), "./imgs/save-hover.png").grid(row=7, column=1, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.fileNamesFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateFileName("BakSuffix", self.BakSuffix_var)).grid(row=7, column=1, padx=(0, 20), ipadx=10)

        self.fileNamesFrame.grid_columnconfigure(0, weight=50, minsize=120)

        # Advanced
        ttk.Label(self.scrollFrame.viewPort, text=LBL_ADVANCED, font=self.window.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(self.scrollFrame.viewPort, text=LBL_ADVANCEDDESC, font=self.window.app.AllFonts["FONT4"], padding=0, foreground="#575757", wraplength=300).pack(padx=(6, 0), pady=(0,0), anchor="w")

        self.advTextFrame = ttk.Frame(self.scrollFrame.viewPort)
        self.advTextFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        tk.Label(self.advTextFrame, text=LBL_RETRYDELAY).grid(row=0, column=0)
        self.RetryDelay_var = tkinter.StringVar()
        steamApiEntry = tk.Entry(self.advTextFrame, width=10, textvariable=self.RetryDelay_var)
        steamApiEntry.grid(row=0, column=1, ipadx=10, ipady=3)
        self.RetryDelay_var.set(self.window.app.config["Advanced"]["RetryDelay"])
        Canvas_TButton(self.advTextFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("RetryDelay", self.RetryDelay_var), "./imgs/save-hover.png").grid(row=0, column=2, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.advTextFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateAdvanced("RetryDelay", self.RetryDelay_var)).grid(row=0, column=2, ipadx=10)

        tk.Label(self.advTextFrame, text=LBL_RETRYMAX).grid(row=1, column=0)
        self.RetryMax_var = tkinter.StringVar()
        self.steamApiEntry = tk.Entry(self.advTextFrame, width=10, textvariable=self.RetryMax_var)
        self.steamApiEntry.grid(row=1, column=1, ipadx=10, ipady=3)
        self.RetryMax_var.set(self.window.app.config["Advanced"]["RetryMax"])
        Canvas_TButton(self.advTextFrame, 20, width=20, height=20).setup(24, "./imgs/save.png", lambda: self.window.app.UpdateFileName("RetryMax", self.RetryMax_var), "./imgs/save-hover.png").grid(row=1, column=2, padx=(0, 0), ipadx=0)
        ##ttk.Button(self.advTextFrame, text=BTN_SAVE, padding=3, command=lambda: self.window.app.UpdateAdvanced("RetryMax", self.RetryMax_var)).grid(row=1, column=2, ipadx=10)

        self.BypassGameVerif_var = tkinter.StringVar()
        self.BypassGameVerif_var.set(self.window.app.config["Advanced"]["BypassGameVerification"])
        self.advBypassGameVerif = ttk.Checkbutton(self.scrollFrame.viewPort, text=CHKBOX_BYPASSGAMEVERIF, variable=self.BypassGameVerif_var, command=lambda: self.window.app.UpdateAdvanced("BypassGameVerification", self.BypassGameVerif_var))
        self.advBypassGameVerif.pack({'padx': (15, 0), 'pady': (0, 10), 'anchor': "w"})
        
        self.scrollFrame.pack(side="top", fill="both", expand=True)


class TopLevelWindow(tkinter.Toplevel):
    def __init__(self, app: App, *args, **kwargs):
        tkinter.Toplevel.__init__(self, *args, **kwargs)
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


class CrackListPopup(TopLevelWindow):
    def __init__(self, app: App, *args, **kwargs):
        TopLevelWindow.__init__(self, app, *args, **kwargs)
        
        self.title(TITLE_CRACKS)
        self.resizable(False, False)
        
        self.biggerFont = self.app.AllFonts["DEFAULT_FONT"].copy().config(size=10)
        
        self.lblTitle: ttk.Label
        self.btnReset: ttk.Button
        
        self.scrollFrame: ScrollFrame
        self.lblSelectedCrack: ttk.Label
        self.settingsframe_crack: ttk.Frame
        self.SelectedCrack_var: tkinter.StringVar
        self.optCrack: ttk.Radiobutton
        self.spacerBottom: tk.Label
        
    
    def post_init(self):
        
        self.scrollFrame = ScrollFrame(self)
        self.lblTitle = ttk.Label(self, text=LBL_CRACKLIST, font=self.app.AllFonts["FONT2"]).pack(pady=(10,10), anchor="center")
        self.btnReset = ttk.Button(self, text=BTN_RESETCRACK, padding=0, command=self.app.ResetCrackListButton).pack(pady=(0,0), anchor="center")
        self.lblSelectedCrack = ttk.Label(self.scrollFrame.viewPort, text=LBL_SELECTEDCRACK, font=self.app.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        self.settingsframe_crack = ttk.Frame(self.scrollFrame.viewPort).pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='both', side='top', expand=True)
        self.SelectedCrack_var = tkinter.StringVar()
        self.SelectedCrack_var.set(self.app.config["Crack"]["SelectedCrack"])
        
        rowNum = 0
        for k, v in self.app.crackList.items():
            ttk.Radiobutton(self.settingsframe_crack, text=v[0], variable=self.SelectedCrack_var, value=k, command=lambda: self.app.UpdateSelectedCrack()).pack(anchor="w")
            rowNum += 1
            if len(v) > 1: # Contains a description
                Autosized_TLabel(self.settingsframe_crack, self.app.AllFonts["FONT4"], text=v[1], foreground="#575757", wraplength=700, justify="left").pack(ipadx=20, anchor="w", fill="both", side="top", expand=True)
                rowNum += 1
        
        self.spacerBottom = tk.Label(self.scrollFrame.viewPort, text="").pack()
        
        self.scrollFrame.pack(side="top", fill="both", expand=True)


class Canvas_TButton(tkinter.Canvas):
    def __init__(self, parent, buttonSize: int = 24, *args, **kwargs):
        tkinter.Canvas.__init__(self, parent, *args, **kwargs)
        self.buttonSize = buttonSize
        self.btnImg: tkinter.PhotoImage = None
        self.btnImg: tkinter.PhotoImage = None
        self.btnImg_Hover: tkinter.PhotoImage = None
        self.btnImg_Hover: tkinter.PhotoImage = None

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

    def setImage(self, imgType: typing.Literal['base', 'hover'], imgPath: str) -> tkinter.PhotoImage | None:
        match imgType:
            case 'base':
                self.btnImg = tkinter.PhotoImage(file=imgPath)
                print(self.btnImg.width())
                self.btnImg = self.btnImg.subsample(round(self.btnImg.width() / self.buttonSize / 1.0))
                self.create_image(self.buttonSize / 2.0, self.buttonSize / 2.0, anchor="center", image=self.btnImg)
                return self.btnImg
            case 'hover':
                self.btnImg_Hover = tkinter.PhotoImage(file=imgPath)
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
        return self


class Autosized_TLabel(tk.Label):
    def __init__(self, parent: tkinter.Misc | None, font: font.Font, *args, **kwargs):
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
    def __init__(self, buttonSize: int, *args, **kwargs):
        Canvas_TButton.__init__(self, buttonSize, *args, **kwargs)
        self.setup(
            self.buttonSize,
            "./imgs/Cog_x96.png",
            None,
            "./imgs/Cog-hover_x96.png"
        )


class Home_TButton(Canvas_TButton):
    def __init__(self, buttonSize: int, *args, **kwargs):
        Canvas_TButton.__init__(self, buttonSize, *args, **kwargs)
        self.setup(
            self.buttonSize,
            "./imgs/Back_x96.png",
            None,
            "./imgs/Back-hover_x96.png",
        )


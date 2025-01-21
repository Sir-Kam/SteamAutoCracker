import traceback
import requests
import configparser
import json
import os
import subprocess
from sac_lib.get_file_version import GetFileVersion
import shutil
from time import sleep
from sys import exit
import typing




try: # Handles Python errors to write them to a log file so they can be reported and fixed more easily.
    
    ## Replaced by 'ttkbootstrap' for [easier] themes
    from tkinter import ttk, filedialog, font, Tk
    from tkinterdnd2 import DND_FILES, TkinterDnD
    from script_constants import *
    #from tk_gui import *
    ## Used for theming/coloring configuration for the UI
    #import ttkbootstrap
    import ttkbootstrap as tk
    from tk_scroll_frame import ScrollFrame
   


    folder_path = ""
    appID = 0
    gameSearchDone = False

    STATE_FindingInAppList = False
    STATE_UpdatingAppList = False

    class App(object):
        def __init__(self):
            from tk_gui import Root
            self.main: Root
            
            self.config: configparser.ConfigParser
            
            # Style ttk
            self.style: tk.Style
            
            
            AllFonts: dict[str, font.Font] = {
                "DEFAULT_FONT": None,
                "FONT2": None,
                "FONT3": None,
                "FONT4": None,
                "FONT_APP_ENTRY": None,
            }
            
            self.AllFonts = AllFonts
            
            self.AllThemes: dict[str, dict[str, typing.Any]] = tk.themes.standard.STANDARD_THEMES
            self.ThemeFilter = ('cosmo', 'darkly', 'cyborg')
            self.ThemeAliases = ('light', 'dark', 'black')
            self.ThemesSubset = dict([t for t in self.AllThemes.items() if t[0] in self.ThemeFilter])
            
            self.ReloadConfig()
            
            """
            baseRefScreenRes = (2560, 1440)
            baseRefWinSize = (500.0, 700.0)
            baseRefWinMinSize = (400, 400)
            baseScale = [
                baseRefScreenRes[0] / baseRefWinSize[0],
                baseRefScreenRes[1] / baseRefWinSize[1]
            ]
            winSize = (root.winfo_screenwidth(), root.winfo_screenheight())
            scaledWinSize = (round(winSize[0] / baseScale[0]), round(winSize[1] / baseScale[1]))
            root.wm_maxsize(round(winSize[0] / 4.0), round(winSize[1] / 1.25))
            root.minsize(baseRefWinMinSize[0], baseRefWinMinSize[1])
            """

        def init_ui(self):
            from tk_gui import Root
            self.main = Root(self)
            self.main.attributes('-alpha', 0.0)
            self.main.iconbitmap("./imgs/icon_hashtag.ico")
            
            # Style ttk
            self.style = tk.Style(theme=self.config["Preferences"]["ThemeOption"])
            self.ApplyStyle()
            
            self.AllFonts["DEFAULT_FONT"] = font.nametofont('TkTextFont')
            self.AllFonts["FONT2"] = self.AllFonts["DEFAULT_FONT"].copy()
            self.AllFonts["FONT2"].config(size=15)
            self.AllFonts["FONT3"] = self.AllFonts["DEFAULT_FONT"].copy()
            self.AllFonts["FONT3"].config(size=12)
            self.AllFonts["FONT4"] = self.AllFonts["DEFAULT_FONT"].copy()
            self.AllFonts["FONT4"].config(size=8)
            self.AllFonts["FONT_APP_ENTRY"] = self.AllFonts["DEFAULT_FONT"].copy()
            self.AllFonts["FONT_APP_ENTRY"].config(size=10)
            
            self.main.post_init()
            self.main.update()
            self.UpdateSelectedCrackDisplay()
            
            self.main.attributes('-alpha', 1.0)
            
            self.main.mainloop()

        def OnTkinterError(self, exc, val, tb):
            # Handle Tkinter Python errors
            print("\n[!!!] A Tkinter Python error occurred! Writing the error to the error_tkinter.log file.\n---")
            with open("error_tkinter.log", "w", encoding="utf-8") as errorFile:
                errorFile.write(f"SteamAutoCracker GUI v{VERSION}\n---\nA Tkinter Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\nNOTE: '_tkinter.TclError: invalid command name' errors are normal if you closed the window while SAC was busy. In that case, you should not report the issue and just ignore it.\n---\n\n")
                traceback.print_exc(file=errorFile)
            traceback.print_exc()
            print("---\nError written to error_tkinter.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")

            try:
                self.update_logs("[!!!] A Tkinter Python error occurred! The error has written to error_tkinter.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")
            except Exception:
                pass

        class SACRequest:
            def __init__(self, url:str, name:str = "Unnamed"):
                self.url = url
                self.tries = 0
                self.name = name
                self.DoRequest(App.update_logs)

            def DoRequest(self, update_logs: callable):
                self.tries += 1
                req = requests.get(self.url, timeout=10)
                if not req.ok:
                    if self.tries < int(self.config["Advanced"]["RetryMax"]):
                        # Do another try
                        self.update_logs("- " + self.name + " request failed, retrying in " + self.config["Advanced"]["RetryDelay"] + "s... (" + str(self.tries) + "/" + self.config["Advanced"]["RetryMax"] + " tries)")
                        self.main.update()
                        sleep(int(self.config["Advanced"]["RetryDelay"]))
                        self.DoRequest(update_logs)
                    else:
                        update_logs("[!] Connection failed after " + self.config["Advanced"]["RetryMax"] + " tries. Are you connected to the Internet? Is Steam online?\nIf you being rate limited (too many DLCs), you should try increasing retrydelay and retrymax in the config")
                        raise Exception(f"SACRequest: Connection failed after {self.config['Advanced']['RetryMax']} tries")
                else:
                    self.req = req

        def handle_folder_selection(self, event=None):
            global folder_path
            global last_selected_folder
            last_selected_folder = self.config["Preferences"].get("last_selected_folder", "")
            # Reset and hide UI elements related to folder selection and game cracking
            def reset_folder_selection_ui():
                self.main.mainPage.selectedFolderLabel.config(text="")
                self.main.mainPage.selectedFolderLabel.pack_forget()
                self.main.mainPage.frameGame2.pack_forget()
                self.main.mainPage.frameCrack2.pack_forget() # Hide the crack frame

            # Determine the folder path based on the event type
            if event:  # Handling drag and drop
                folder_path_temp = event.data.strip("{}").replace("\\", "/") # Returns the directory with no "/" at the end
            else:  # Handling button click
                initial_dir = "/"
                if last_selected_folder != "" and os.path.isdir(last_selected_folder):
                    initial_dir = last_selected_folder
                folder_path_temp = filedialog.askdirectory(initialdir=initial_dir) # Returns the directory with no "/" at the end

            if os.path.isdir(folder_path_temp):
                folder_path = folder_path_temp
                # Update the last dropped folder for future use
                last_selected_folder = os.path.dirname(folder_path) # If no "/" at the end, returns the parent directory
                self.config["Preferences"]["last_selected_folder"] = last_selected_folder
                self.UpdateConfig()
                folder_name = os.path.basename(folder_path) # Gets the name of the folder ("C:/Something/Games/Hello" will return "Hello")

                # Update UI elements with the selected folder information
                self.update_logs(LBL_SELECTEDFOLDER_LOG.format(path=folder_path))
                self.main.mainPage.selectedFolderLabel.config(text=LBL_SELECTEDFOLDER.format(path=folder_path))
                self.main.mainPage.selectedFolderLabel.pack()
                self.main.mainPage.frameGame2.pack()

                # Update the game name entry with the folder name
                self.main.mainPage.gameNameEntry.delete(0, tk.END) # Removes the content of the Entry element starting from index 0 to the end
                self.main.mainPage.gameNameEntry.insert(0, folder_name) # Inserts the name of the folder in the Entry element at the start of it (index 0)

                # Show crack frame if game search is done
                if gameSearchDone:
                    self.main.mainPage.frameCrack2.pack()
            else:
                # Handle invalid folder selection
                self.update_logs("\nNo valid folder selected")
                folder_path = ""
                reset_folder_selection_ui()

        def update_logs(self, log_message):
            global main
            # Get current content
            current_logs = self.main.mainPage.logs_text.get("1.0", tk.END)

            self.main.mainPage.logs_text.config(state=tk.NORMAL)  # Enables modification (needed to add content)
            # Delete the current content
            self.main.mainPage.logs_text.delete("1.0", tk.END)

            # Insert the new message at the end with a linebreak
            self.main.mainPage.logs_text.insert(tk.END, current_logs + log_message)

            # Scroll the widget to the bottom
            self.main.mainPage.logs_text.yview_moveto(1.0)

            # Focus on the end
            self.main.mainPage.logs_text.see(tk.END)
            self.main.mainPage.logs_text.config(state=tk.DISABLED)  # Disables modification (prevents the user from writing inside the field)

        def search_game(self):
            self.main.mainPage.searchGameButton.config(state=tk.DISABLED) # Prevents the user from starting multiple searches at the same time
            self.main.mainPage.frameCrack2.pack_forget() # Hide the crack frame
            global gameSearchDone
            gameSearchDone = False

            self.main.mainPage.gameFoundStatus.config(text=f"")
            # Disable the ability to change the selected folder
            self.main.mainPage.selectFolderBtn.config(state=tk.DISABLED)
            self.main.mainPage.updateAppListButton.grid_forget()
            self.main.mainPage.update()

            global appID
            appID = 0
            if self.main.mainPage.gameNameEntry.get() == "":
                self.update_logs("\n[!] Please enter a valid Name or AppID")
                self.main.mainPage.searchGameButton.config(state=tk.NORMAL)  # Re-enable the ability to search the game
                self.main.mainPage.selectFolderButton.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder
                return

            try:
                appID = int(self.main.mainPage.gameNameEntry.get())
            except:
                appID = self.FindInAppList(self.main.mainPage.gameNameEntry.get())

            if appID != 0 and self.RetrieveGame(): # On success
                # We are now on step 3
                gameSearchDone = True
                self.main.mainPage.frameCrack2.pack() # Show the crack frame
                self.main.mainPage.searchGameButton.config(state=tk.NORMAL) # Re-enable the ability to search the game
                self.main.mainPage.selectFolderBtn.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder
            else:
                self.main.mainPage.searchGameButton.config(state=tk.NORMAL) # Re-enable the ability to search the game
                self.main.mainPage.selectFolderBtn.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder

        def FindInAppList(self, appName):
            self.update_logs("\nImporting and searching the App List, this could take a few seconds if your computer isn't powerful enough.")
            self.main.mainPage.gameFoundStatus.config(text=LBL_SEARCHINGAPPLIST)
            self.main.mainPage.update() # Update the window now
            try:
                with open("applist.txt", "r", encoding="utf-8") as file:
                    data = json.load(file)
            except:
                self.update_logs(LBL_DLAPPLIST)
                self.UpdateAppList()
                return self.FindInAppList(appName) # Re launch this funtion

            for elem in data["applist"]["apps"]:
                if elem["name"].lower() != appName.lower():
                    continue

                return elem["appid"]

            self.update_logs("[!] The App was not found, make sure you entered EXACTLY the Steam Game's name (watch it on Steam)")
            self.update_logs("If you typed it properly, you can try to update the App List. Alternatively, you can try entering the AppID.")
            self.main.mainPage.gameFoundStatus.config(text=LBL_APPNOTFOUND)

            self.main.mainPage.updateAppListButton.grid(row=0, column=2, padx=(10, 0))
            return 0

        def UpdateAppList(self):
            self.main.mainPage.updateAppListButton.grid_forget()
            self.update_logs("\nUpdating the App List, this could take a few seconds to up to a minute, depending on your internet connection.")
            self.main.mainPage.gameFoundStatus.config(text=LBL_UPDATINGAPPLIST)
            self.main.mainPage.update()
            try:
                req = self.SACRequest("https://api.steampowered.com/ISteamApps/GetAppList/v2/", "UpdateAppList").req
            except Exception:
                self.main.mainPage.gameFoundStatus.config(text=LBL_REQERROR)
                return

            with open("applist.txt", "w", encoding="utf-8") as file:
                file.write(req.text)
            self.update_logs(LBL_UPDATEDAPPLIST)
            self.main.mainPage.gameFoundStatus.config(text=LBL_UPDATEDAPPLIST)

        def RetrieveAppName(self, appID: int) -> str:
            try:
                req = self.SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveAppName").req
            except Exception:
                return "error"

            data = req.json()
            data = data[str(appID)]
            if (not "data" in data) or (not "name" in data["data"]):
                return "error"
            return data["data"]["name"]

        def RetrieveGame(self) -> bool:
            global appID
            global gameName
            global dlcIDs
            global dlcNames

            dlcIDs = []
            dlcNames = []

            self.update_logs(f"\n{LBL_GETTINGSTEAMGAMEINFO}")
            self.main.mainPage.gameFoundStatus.config(text=LBL_GETTINGSTEAMGAMEINFO)
            self.main.mainPage.update()
            # https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#appdetails
            try:
                req = self.SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveGame").req
            except Exception:
                self.main.mainPage.gameFoundStatus.config(text=LBL_REQERROR)
                return False
            data = req.json()
            data = data[str(appID)]
            if not data["success"]:
                self.update_logs(f"\n[!] {LBL_APPIDNOTFOUND.format(id=appID)}")
                self.main.mainPage.gameFoundStatus.config(text=LBL_APPIDNOTFOUND.format(id=appID))
                appID = 0
                return False
            if self.config["Advanced"]["BypassGameVerification"] != "1" and data["data"]["type"] != "game":
                self.update_logs(f"\n[!] {LBL_APPIDNOTGAME.format(id=appID)}")
                self.main.mainPage.gameFoundStatus.config(text=LBL_APPIDNOTGAME.format(id=appID))
                appID = 0
                return False

            gameName = data["data"]["name"]
            appID = data["data"]["steam_appid"]
            self.update_logs(f"- Game found! Name: {gameName} - AppID: {appID}")

            self.update_logs(f"\n{LBL_GETTINGSTEAMGAMEDLC}")
            self.main.mainPage.gameFoundStatus.config(text=LBL_GETTINGSTEAMGAMEDLC)
            self.main.mainPage.update()

            # Optional config check
            option = "0"
            try:
                option = self.config["Developer"]["RetrieveDLCOption"]
            except:
                pass

            if option == "1":
                # Old retrieve option
                self.update_logs(LBL_OLDRETRIEVEOPT)

                if "dlc" in data["data"]:
                    dlcIDs = data["data"]["dlc"]
                    dlcIDsLen = len(dlcIDs)

                    if dlcIDsLen >= HIGH_DLC_WARNING:
                        self.update_logs(f"/!\\ {LBL_GAMEHIGHDLC}")

                    # Get DLCs names
                    for i in range(dlcIDsLen):
                        appName =self.RetrieveAppName(dlcIDs[i])
                        if appName == "error":
                            self.update_logs(f"[!] {LBL_NOAPPNAMEFORDLC.format(id=dlcIDs[i])}")
                            self.main.mainPage.gameFoundStatus.config(text=f"[!] {LBL_NOAPPNAMEFORDLC.format(id=dlcIDs[i])}")
                            appID = 0
                            return False
                        dlcNames.append(appName)
                        self.update_logs("- Found DLC " + str(i+1) + "/" + str(dlcIDsLen) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
                        self.main.mainPage.gameFoundStatus.config(text=f"{LBL_GETTINGSTEAMGAMEDLC} ({i+1}/{dlcIDsLen})")
                        self.main.mainPage.update()
                else:
                    self.update_logs(LBL_NOGAMEDLC)
            else:
                # Default retrieve option

                try:
                    req2 = self.SACRequest("https://store.steampowered.com/dlc/" + str(appID) +"/random/ajaxgetfilteredrecommendations/?query&count=10000", "RetrieveDLC").req
                except Exception:
                    self.main.mainPage.gameFoundStatus.config(text=LBL_REQERROR)
                    return False
                data2 = req2.json()
                if not data2["success"]:
                    self.update_logs(f"[!] {LBL_DLCREQFAILED}")
                    self.main.mainPage.gameFoundStatus.config(text=LBL_DLCREQFAILED)
                    appID = 0
                    return False

                if data2["total_count"] == 0:
                    self.update_logs(LBL_NOGAMEDLC)
                else:
                    if data2["total_count"] >= HIGH_DLC_WARNING:
                        self.update_logs(f"/!\\ {LBL_GAMEHIGHDLC}")

                    resultsIndex = 0

                    # format: data-ds-appid="1812883"
                    i = -1
                    while i + 1 < data2["total_count"]:
                        i += 1

                        resultsStr = ""
                        resultsIndex = data2["results_html"].find("data-ds-appid=\"", resultsIndex)
                        resultsIndex += len("data-ds-appid=\"")

                        while data2["results_html"][resultsIndex] != "\"":
                            resultsStr += data2["results_html"][resultsIndex]
                            resultsIndex += 1

                        dlcID = int(resultsStr)
                        if dlcID in dlcIDs: # data-ds-appid is present 2 times for each AppID currently. This will allow us to not include it if it is already.
                            i -= 1
                            continue
                        dlcIDs.append(int(resultsStr))

                        # Retrieve DLC name
                        appName = self.RetrieveAppName(dlcIDs[i])
                        if appName == "error":
                            self.update_logs(f"[!] {LBL_NOAPPNAMEFORDLC.format(id=dlcIDs[i])}")
                            self.main.mainPage.gameFoundStatus.config(text=LBL_NOAPPNAMEFORDLC.format(id=dlcIDs[i]))
                            appID = 0
                            return False
                        dlcNames.append(appName)
                        self.update_logs(f"- {LBL_FOUNDDLC} " + str(i+1) + "/" + str(data2["total_count"]) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
                        self.main.mainPage.gameFoundStatus.config(text=f"{LBL_GETTINGSTEAMGAMEDLC}({i+1}/{data2['total_count']})")
                        self.main.mainPage.update()

            self.update_logs(LBL_FETCHEDDETAILSFORGAME.format(name=gameName, id=appID))
            self.main.mainPage.gameFoundStatus.config(text=LBL_FETCHEDDETAILSFORGAME_S.format(name=gameName))
            return True # Retrieved game and DLCs successfully

        def CrackGame(self):
            global appID

            # Prevents the user from searching a game or selecting a folder or re-clicking the crack game button
            self.main.mainPage.selectFolderBtn.config(state=tk.DISABLED)
            self.main.mainPage.searchGameButton.config(state=tk.DISABLED)
            self.main.mainPage.selectCrackButton.config(state=tk.DISABLED)
            self.main.mainPage.crackGameButton.config(state=tk.DISABLED)

            self.update_logs("\nSearching Steam API DLLs and cracking them...")
            cracked = False

            if self.config["Crack"]["SelectedCrack"][:3] == "dlc" and len(dlcIDs) == 0: # If a dlc only crack has been selected, but the game has no DLC
                self.update_logs("-----\nNo DLC is available, and you selected a DLC only crack. Aborting the cracking process.")
                self.EndCrack()
                return

            configDir = os.path.join(os.getcwd(), "sac_emu\\" + self.config["Crack"]["SelectedCrack"]) # "sac_emu/game_ali213" for example
            try:
                self.config.read(configDir + "\\config_override.ini")
            except Exception:
                pass

            configDir = os.path.join(configDir, "files") # "sac_emu/game_ali213/files" for example

            # Check if some custom Steamless options have been set up
            steamlessOptions = ""
            try:
                steamlessOptions = self.config["Developer"]["SteamlessOptions"] + " "
            except:
                pass

            self.main.mainPage.update()

            dllLocations = []
            for root_dir, dirs, files in os.walk(folder_path):
                apiFile = ""

                # Use Steamless if configured
                if self.config["Preferences"]["Steamless"] == "1" and self.crackListSteamless[self.config["Crack"]["SelectedCrack"]]:
                    # Run Steamless on every .exe file. If it's not under DRM or not the wrong file, no problem!
                    for fileName in files:
                        if not fileName.endswith(".exe"):
                            continue
                        self.update_logs(f"- Attempting to run Steamless on {fileName}")
                        self.main.mainPage.update()
                        #update_logs("\n[[[ Steamless logs ]]]")
                        fileLocation = root_dir + "/" + fileName
                        shutil.move(fileLocation, fileName) # Move the file to our location
                        subprocess.call("Steamless_CLI\\Steamless.CLI.exe " + steamlessOptions + "\"" + fileName + "\"", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE) # Run Steamless on the game
                        #update_logs("[[[ -------------- ]]]\n")

                        # Check if the game was NOT unpacked
                        if not os.path.isfile(fileName + ".unpacked.exe"):
                            # Move back the original game's exe since it didn't change
                            self.update_logs("- Couldn't run Steamless on " + fileName + ", it is probably not under DRM.")
                            shutil.move(fileName, fileLocation)
                            self.main.mainPage.update()
                            continue

                        self.update_logs(f"- Removed Steam Stub DRM from {fileName}")
                        if self.config["FileNames"]["GameEXE"] != "":
                            # Rename and move back the original game's exe
                            shutil.move(fileName, fileLocation + self.config["FileNames"]["GameEXE"])
                        else:
                            # Delete the original game's exe
                            os.remove(fileName)
                        # Rename and move the unpacked exe to the game's directory
                        shutil.move(fileName + ".unpacked.exe", fileLocation)
                        self.main.mainPage.update()

                if "steam_api.dll" in files:
                    if self.config["FileNames"]["SteamAPI"] in files:
                        self.update_logs("[!] Seems like a file named " + self.config["FileNames"]["SteamAPI"] + " is present. This could indicate that steam_api.dll has already been cracked! Overwriting steam_api.dll. No backup of the previous steam_api.dll could be created, and the file has been deleted. " + self.config["FileNames"]["SteamAPI"] + " has been restored.")
                        os.remove(root_dir + "/steam_api.dll")
                        shutil.move(root_dir + "/" + self.config["FileNames"]["SteamAPI"], root_dir + "/steam_api.dll")

                    apiFile = root_dir + "/steam_api.dll"
                    try:
                        apiFileVersion = GetFileVersion(apiFile)
                    except Exception:
                        self.update_logs("[!] steam_api.dll: could not retrieve the file version! Seems like the steam_api.dll file has already been cracked! Aborting...")
                        self.EndCrack()
                        return

                    self.update_logs(f"- Found steam_api.dll in {root_dir}, planning crack application")

                if "steam_api64.dll" in files:
                    if self.config["FileNames"]["SteamAPI64"] in files:
                        self.update_logs("[!] Seems like a file named " + self.config["FileNames"]["SteamAPI64"] + " is present. This could indicate that steam_api64.dll has already been cracked! Overwriting steam_api64.dll. No backup of the previous steam_api64.dll could be created, and the file has been deleted. " + self.config["FileNames"]["SteamAPI64"] + " has been restored.")
                        os.remove(root_dir + "/steam_api64.dll")
                        shutil.move(root_dir + "/" + self.config["FileNames"]["SteamAPI64"], root_dir + "/steam_api64.dll")

                    apiFile = root_dir + "/steam_api64.dll"
                    try:
                        apiFileVersion = GetFileVersion(apiFile)
                    except Exception:
                        self.update_logs("[!] steam_api64.dll: could not retrieve the file version! Seems like the steam_api64.dll file has already been cracked! Aborting...")
                        self.EndCrack()
                        return

                    self.update_logs(f"- Found steam_api64.dll in {root_dir}, planning crack application")

                if apiFile != "":
                    if root_dir not in dllLocations:
                        dllLocations.append(root_dir)

                    cracked = True
                    self.main.mainPage.update()

            for dllCurrentLocation in dllLocations:
                for root_dir, dirs, files in os.walk(configDir):
                    relativeRootDir = root_dir[len(configDir) + 1:]
                    dllAbsoluteRelativeLocation = os.path.join(dllCurrentLocation, relativeRootDir)

                    # To make it look right, add a "\" at the end of relativeRootDir if it is not empty
                    if len(relativeRootDir) > 0:
                        relativeRootDir += "\\"

                    # Create all missing directories
                    for dir in dirs:
                        if not os.path.isdir(os.path.join(dllAbsoluteRelativeLocation, dir)):
                            os.mkdir(os.path.join(dllAbsoluteRelativeLocation, dir))
                            self.update_logs("Created new directory " + relativeRootDir + dir)
                            self.main.mainPage.update()

                    # Create all files
                    for fileName in files:
                        self.main.mainPage.update()
                        if os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, fileName)): # The file already exists in the game, rename it to .bak
                            newName = fileName + self.config["FileNames"]["BakSuffix"]
                            if fileName == "steam_api.dll" or fileName == "steam_api64.dll":
                                if self.config["Preferences"]["CrackOption"] != "0": # Only create config
                                    self.update_logs("Ignoring " + relativeRootDir + fileName + " because of the set crack approach")
                                    continue

                                if fileName == "steam_api.dll":
                                    newName = self.config["FileNames"]["SteamAPI"]
                                else:
                                    newName = self.config["FileNames"]["SteamAPI64"]

                            if newName == "": # Don't keep a backup of the steam_api(64).dll file
                                os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                                self.update_logs("Removed old " + relativeRootDir + fileName + " file because no backup file name is set")
                            elif os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, newName)): # A backup of this file already exists, the game might already be cracked, abort!
                                self.update_logs("[!] Seems like the backup of " + relativeRootDir + fileName + " file already exists! This could indicate that the game has already been cracked. Overwriting it. No backup of " + relativeRootDir + fileName + " could be created, and the file has been deleted.")
                                os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                            else:
                                shutil.move(os.path.join(dllAbsoluteRelativeLocation, fileName), os.path.join(dllAbsoluteRelativeLocation, newName))
                                self.update_logs("Backupped old file " + relativeRootDir + fileName + " -> " + newName)
                        elif fileName == "steam_api.dll" or fileName == "steam_api64.dll": # No existing file, and this file is the steam_api(64).dll one
                            continue # Ignore this file

                        shutil.copyfile(os.path.join(root_dir, fileName), os.path.join(dllAbsoluteRelativeLocation, fileName))

                        # Check if ends with a specific extension, so we can replace the presets inside
                        if any(fileName.endswith(extension) for extension in EXTS_TO_REPLACE):
                            # Read the file's content
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "r", encoding="utf-8") as file:
                                fileContent = file.read()

                            # Replace the presets if any
                            fileContent = fileContent.replace("SAC_AppID", str(appID))
                            fileContent = fileContent.replace("SAC_APIVersion", apiFileVersion)
                            buffer = ""
                            for i in range(len(dlcIDs)):
                                buffer += str(dlcIDs[i]) + " = " + dlcNames[i] + "\n"
                            fileContent = fileContent.replace("SAC_DLC", buffer)
                            buffer = ""
                            for i in range(len(dlcIDs)):
                                buffer += str(dlcIDs[i]) + "=" + dlcNames[i] + "\n"
                            fileContent = fileContent.replace("SAC_NoSpaceDLC", buffer)

                            # Write the changes
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "w", encoding="utf-8") as file:
                                file.write(fileContent)

                        self.update_logs("Created new file " + relativeRootDir + fileName)


            self.update_logs("\n-----\nFinished cracking the game!")
            if not cracked:
                self.update_logs("[!] No Steam API DLL was found in the game!")
            else:
                self.update_logs("The game has been cracked successfully! (If you attempt to crack if again, SAC will try its best to make it work, but will let some leftovers of old cracks.)")

            self.EndCrack()

        def EndCrack(self):
            # Cracking process done!
            self.ReloadConfig() # Reload the config to remove the overwritten config from config_override.ini

            # Now let's remove locks
            self.main.mainPage.selectFolderBtn.config(state=tk.NORMAL)
            self.main.mainPage.searchGameButton.config(state=tk.NORMAL)
            self.main.mainPage.selectCrackButton.config(state=tk.NORMAL)
            self.main.mainPage.crackGameButton.config(state=tk.NORMAL)


        # Theming
        def GetThemes(self) -> dict[str, dict[str, typing.Any]]:
            return self.ThemesSubset
        
        # Changes appearance according to the theme in the config
        def ApplyStyle(self) -> None:
            
            if (self.config["Preferences"]["ThemeOption"] in tuple(self.GetThemes().keys())):
                ##print(config["Preferences"]["ThemeOption"])
                self.style.theme_use(self.config["Preferences"]["ThemeOption"])
                
                self.style.configure("TFrame", padding=0)
                self.style.configure("TLabel", padding=6)
                self.style.configure("TRadiobutton", padding=6)
                self.style.configure("TButton", padding=10)
                self.style.configure("TEntry", padding=6)
                self.style.configure("TEntry", padding=0)


        def UpdateFileName(self, key, strVar):
            value = strVar.get().strip()
            strVar.set(value)
            self.UpdateConfigKey("FileNames", key, value)

        def UpdateAdvanced(self, key, strVar):
            value = strVar.get().strip()
            try:
                int(value)
            except:
                strVar.set(self.config["Advanced"][key])
            else: # If no error
                strVar.set(value)
                self.UpdateConfigKey("Advanced", key, value)

        def ResetSettingsButton(self):
            self.ResetConfig(1)
            
            from tk_gui import \
                GameEXE_var, RetryMax_var, SteamApi_var, BakSuffix_var, \
                Steamless_var, RetryDelay_var, SteamApi64_var, CrackOption_var, \
                ThemeOption_var, UpdateOption_var, BypassGameVerification_var

            # Update the radio buttons values
            ThemeOption_var.set(self.config["Preferences"]["ThemeOption"])
            UpdateOption_var.set(self.config["Preferences"]["UpdateOption"])
            CrackOption_var.set(self.config["Preferences"]["CrackOption"])
            Steamless_var.set(self.config["Preferences"]["Steamless"])
            SteamApi_var.set(self.config["FileNames"]["SteamAPI"])
            SteamApi64_var.set(self.config["FileNames"]["SteamAPI64"])
            GameEXE_var.set(self.config["FileNames"]["GameEXE"])
            BakSuffix_var.set(self.config["FileNames"]["BakSuffix"])
            RetryDelay_var.set(self.config["Advanced"]["RetryDelay"])
            RetryMax_var.set(self.config["Advanced"]["RetryMax"])
            BypassGameVerification_var.set(self.config["Advanced"]["BypassGameVerification"])

        # ----- Crack List -----

        crackList = { # A list of all selectable cracks
            "game_ali213": ["ALI213 (Game)", "The ALI213 crack is simple and can crack a full game. It will unlock all DLCs and will also prevent the game from connecting to the internet. The game folder can then freely be shared with others as the crack is contained inside the game folder. If it doesn't work, consider using Goldberg instead."],
            "game_goldberg": ["Goldberg (Game)", "The Goldberg (experimental) crack is similar to ALI213's one. It is open-source, which is better, but might not work with older games, due to SAC's current partial support. This crack will however work better for recent games, where ALI213 could fail. Internet connection is blocked, but LAN is enabled."],
            "dlc_creamapi": ["CreamAPI (DLC)", "The CreamAPI crack will unlock all DLCs but will not crack the main game. It is meant to be used with bought copies of a game, with your real Steam account. Only use this is you have purchased the game on Steam and want to unlock its DLCs. Will not work for most online games, but might exceptionally work with some like Beat Saber."]
        }

        crackListSteamless = { # Whether to use Steamless with a specific crack. True = use Steamless
            "game_ali213": True,
            "game_goldberg": True,
            "dlc_creamapi": False
        }

        def DisplayCrackList(self):
            from tk_gui import Autosized_TLabel
            top = tk.Toplevel(self.main)
            top.title(f"SteamAutoCracker GUI v{VERSION} - Crack List")
            top.resizable(True, True) # Prevents resizing the window's width and height
            biggerFont = self.AllFonts["DEFAULT_FONT"].copy()
            biggerFont.config(size=10)
            ttk.Label(top, text= LBL_CRACKLIST, font=self.AllFonts["FONT2"]).pack(pady=(10,10), anchor="center")

            ttk.Button(top, text=BTN_RESETCRACK, padding=0, command=self.ResetCrackListButton).pack(pady=(0,0), anchor="center")

            scrollFrame = ScrollFrame(top)

            # Selected crack (SelectedCrack)
            ttk.Label(scrollFrame.viewPort, text=LBL_SELECTEDCRACK, font=self.AllFonts["FONT3"], padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
            settings_frame1 = ttk.Frame(scrollFrame.viewPort)
            settings_frame1.pack(padx=(15, 0), pady=(0, 0), anchor="w", fill='both', side='top', expand=True)

            ## Radio
            global SelectedCrack_var
            SelectedCrack_var = tk.StringVar()
            SelectedCrack_var.set(self.config["Crack"]["SelectedCrack"])
            rowNum = 0
            for k, v in self.crackList.items():
                ttk.Radiobutton(settings_frame1, text=v[0], variable=SelectedCrack_var, value=k, command=lambda: self.UpdateSelectedCrack()).pack(anchor="w")
                rowNum += 1
                if len(v) > 1: # Contains a description
                    Autosized_TLabel(settings_frame1, self.AllFonts["FONT4"], text=v[1], foreground="#575757", wraplength=700, justify="left").pack(ipadx=20, anchor="w", fill="both", side="top", expand=True)
                    rowNum += 1

            # Spacer
            tk.Label(scrollFrame.viewPort, text="").pack()
            
            scrollFrame.pack(side="top", fill="both", expand=True)

            top.grab_set() # Catches all interactions, prevents the user from interacting with the root window

        def UpdateSelectedCrack(self):
            value = SelectedCrack_var.get()
            self.UpdateConfigKey("Crack", "SelectedCrack", value)
            self.UpdateSelectedCrackDisplay()

        def UpdateSelectedCrackDisplay(self):
            self.main.mainPage.selectCrackButton.config(text=self.crackList[self.config["Crack"]["SelectedCrack"]][0]) # Display the name of the selected crack on the select crack button in the root window

        def ResetCrackListButton(self):
            self.ResetConfig(2)

            # Update the radio buttons values
            SelectedCrack_var.set(self.config["Crack"]["SelectedCrack"])

            # Update the root button's text
            self.UpdateSelectedCrackDisplay()

        # ---------------------------------------

        def UpdateConfig(self):
            with open(CONFIG, "w", encoding="utf-8") as configFile:
                self.config.write(configFile)

        def UpdateConfAndUI(self, section: str, key: str, value: str):
            self.UpdateConfigKey(section, key, value)
            # Reapply with new selection
            self.ApplyStyle()

        def UpdateConfigKey(self, section: str, key: str, value: str):
            self.config[section][key] = value
            self.UpdateConfig()

        def ResetConfig(self, resetLevel = 0, customConfig=None):
            """resetLevel values:
            0 = Everything
            1 = Main settings only (Preferences, FileNames, Advanced)
            2 = Crack selection settings only (Crack)
            """
            if customConfig:
                currentConfig = customConfig
            else:
                currentConfig = self.config

            if resetLevel == 0 or resetLevel == 1:
                currentConfig["Preferences"] = {}
                currentConfig["Preferences"]["ThemeOption"] = list(self.GetThemes().keys())[0]
                currentConfig["Preferences"]["UpdateOption"] = "0"
                currentConfig["Preferences"]["CrackOption"] = "0"
                currentConfig["Preferences"]["Steamless"] = "1"
                currentConfig["Preferences"]["last_selected_folder"] = ""

                currentConfig["FileNames"] = {}
                currentConfig["FileNames"]["GameEXE"] = ".bak"
                currentConfig["FileNames"]["BakSuffix"] = ".bak"
                currentConfig["FileNames"]["SteamAPI"] = "steam_api.dll.bak"
                currentConfig["FileNames"]["SteamAPI64"] = "steam_api64.dll.bak"

                currentConfig["Advanced"] = {}
                currentConfig["Advanced"]["RetryDelay"] = str(RETRY_DELAY)
                currentConfig["Advanced"]["RetryMax"] = str(RETRY_MAX)
                currentConfig["Advanced"]["BypassGameVerification"] = "0"
            if resetLevel == 0 or resetLevel == 2:
                currentConfig["Crack"] = {}
                currentConfig["Crack"]["SelectedCrack"] = "game_ali213"

            if not customConfig:
                self.UpdateConfig()

        def FillConfig(self, currentConfig, configDefault):
            changed = False
            for k, v in configDefault.items():
                if k not in currentConfig:
                    currentConfig[k] = v
                    print("Updated", k, "->", v)
                    changed = True
                if type(v) == configparser.SectionProxy:
                    if self.FillConfig(currentConfig[k], v):
                        changed = True

            return changed

        def ReloadConfig(self):
            self.config = configparser.ConfigParser()

            if self.config.read(CONFIG) == []:
                # Config doesn't exist, create it
                self.ResetConfig()
            else:
                # Create a config with default values
                configDefault = configparser.ConfigParser()
                self.ResetConfig(0, configDefault)

                # Check if the config is complete. If not, complete it.
                changed = self.FillConfig(self.config, configDefault)
                if changed:
                    print("[SAC] config.ini has been updated, missing entries have been created")
                    self.UpdateConfig()

        # ---------------------------------------

        def CheckUpdates(self):
            self.main.mainPage.updatesButton.config(text=LBL_SEARCHINGUPDATE, state=tk.DISABLED)
            self.main.mainPage.update()

            req = self.SACRequest(GITHUB_LATESTVERSIONJSON, "RetrieveLatestVersionJson").req
            data = req.json()
            global latestversion
            latestversion = data["version"]
            if latestversion == VERSION: # The latest stable version is the one we're running
                self.main.mainPage.updatesButton.config(text=LBL_UPTODATE, state=tk.NORMAL)
                return

            global release_link
            release_link = data["release"]
            release_link = release_link.replace("[VERSION]", latestversion)

            self.main.mainPage.updatesButton.config(text=LBL_OUTDATED, state=tk.NORMAL)
            self.DisplayUpdate()

        def DisplayUpdate(self):
            from tk_gui import UpdatePopup
            top = UpdatePopup(latestversion, app=app)
            top.post_init()
            
            global updateDisplayTop
            updateDisplayTop = top

        def UpdateSAC(self):
            updateDisplayTop.updateDisplayButtonUpdate.config(state=tk.DISABLED)
            updateDisplayTop.updateDisplayButtonCopy.config(state=tk.DISABLED)
            updateDisplayTop.updateDisplayButtonClose.config(state=tk.DISABLED)

            updateDisplayTop.updateDisplayStatusLabel.pack(pady=(0,20), anchor="center")
            updateDisplayTop.updateDisplayStatusLabel.config(text=LBL_DLUPDATERPLSWAIT)
            self.main.update()

            # Check for the existence of a leftover autoupdater
            if os.path.isfile(AUTOUPDATER_EXE):
                try:
                    os.remove(AUTOUPDATER_EXE)
                except Exception: # In case the file is locked for example
                    updateDisplayTop.updateDisplayButtonUpdate.config(state=tk.NORMAL)
                    updateDisplayTop.updateDisplayButtonCopy.config(state=tk.NORMAL)
                    updateDisplayTop.updateDisplayButtonClose.config(state=tk.NORMAL)
                    updateDisplayTop.updateDisplayStatusLabel.config(text=LBL_UDATEERROR)
                    self.main.update()
                    return
                print("Removed leftover autoupdater")

            # Override RetryDelay and RetryMax
            self.config["Advanced"]["RetryDelay"] = "3"
            self.config["Advanced"]["RetryMax"] = "5"

            req = self.SACRequest(GITHUB_AUTOUPDATER, "DownloadAutoupdater").req

            updateDisplayTop.updateDisplayStatusLabel.config(text=LBL_UPDATERSAVING)
            self.main.update()

            with open(AUTOUPDATER_EXE, mode="wb") as file:
                file.write(req.content)

            updateDisplayTop.updateDisplayStatusLabel.config(text=LBL_UPDATERINSTALLED)
            self.main.update()

            sleep(3)
            subprocess.Popen(AUTOUPDATER_EXE) # Open SAC GUI Autoupdater
            exit()

        def CopyReleaseURL(self):
            self.main.clipboard_clear()
            self.main.clipboard_append(release_link)

    if (__name__ == '__main__'):        
        app = App()
        app.init_ui()

except Exception:
    # Handle Python errors
    print("\n[!!!] A Python error occurred! Writing the error to the error.log file.\n---")
    with open("error.log", "w", encoding="utf-8") as errorFile:
        errorFile.write(f"SteamAutoCracker GUI v{VERSION}\n---\nA Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\n---\n\n")
        traceback.print_exc(file=errorFile)
    traceback.print_exc()
    print("---\nError written to error.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")

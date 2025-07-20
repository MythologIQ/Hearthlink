Set WshShell = CreateObject("WScript.Shell")
Set oFSO = CreateObject("Scripting.FileSystemObject")

' Get the current directory
strCurrentDir = oFSO.GetParentFolderName(WScript.ScriptFullName)

' Create desktop shortcut
strDesktopPath = WshShell.SpecialFolders("Desktop")
Set oShellLink = WshShell.CreateShortcut(strDesktopPath & "\Hearthlink.lnk")
oShellLink.TargetPath = strCurrentDir & "\HearthlinkDirect.bat"
oShellLink.WorkingDirectory = strCurrentDir
oShellLink.Description = "Hearthlink AI Orchestration System - Direct Launch"
oShellLink.IconLocation = strCurrentDir & "\src\assets\Hearthlink.png"
oShellLink.Save

' Create start menu shortcut
strStartMenuPath = WshShell.SpecialFolders("StartMenu") & "\Programs"
Set oShellLink2 = WshShell.CreateShortcut(strStartMenuPath & "\Hearthlink.lnk")
oShellLink2.TargetPath = strCurrentDir & "\HearthlinkDirect.bat"
oShellLink2.WorkingDirectory = strCurrentDir
oShellLink2.Description = "Hearthlink AI Orchestration System - Direct Launch"
oShellLink2.IconLocation = strCurrentDir & "\src\assets\Hearthlink.png"
oShellLink2.Save

WScript.Echo "✅ Hearthlink shortcuts created successfully!"
WScript.Echo ""
WScript.Echo "📌 To pin to taskbar:"
WScript.Echo "1. Right-click the desktop shortcut"
WScript.Echo "2. Select 'Pin to taskbar'"
WScript.Echo ""
WScript.Echo "🚀 Ready to launch Hearthlink from your taskbar!"

Set WshShell = Nothing
Set oFSO = Nothing
Set oShellLink = Nothing
Set oShellLink2 = Nothing
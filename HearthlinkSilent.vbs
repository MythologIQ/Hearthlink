Set WshShell = CreateObject("WScript.Shell")
' Run the service batch file completely hidden
WshShell.Run Chr(34) & "HearthlinkService.bat" & Chr(34), 0, False
Set WshShell = Nothing
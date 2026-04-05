Option Explicit

Dim shell, fso, pwshPath, scriptPath, command, i, arg

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

If WScript.Arguments.Count < 1 Then
    WScript.Quit 64
End If

pwshPath = "C:\Program Files\PowerShell\7\pwsh.exe"
If Not fso.FileExists(pwshPath) Then
    pwshPath = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")
End If

scriptPath = WScript.Arguments(0)
command = """" & pwshPath & """ -NoProfile -ExecutionPolicy Bypass -NonInteractive -File """ & scriptPath & """"

For i = 1 To WScript.Arguments.Count - 1
    arg = Replace(WScript.Arguments(i), """", """""")
    command = command & " """ & arg & """"
Next

shell.Run command, 0, False

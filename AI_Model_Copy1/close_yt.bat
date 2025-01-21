@echo off
:: Run the PowerShell script to close YouTube tabs in Microsoft Edge
powershell.exe -ExecutionPolicy Bypass -Command "
$edgeProcesses = Get-Process msedge -ErrorAction SilentlyContinue;
if ($edgeProcesses) {
    foreach ($process in $edgeProcesses) {
        $windowTitle = (Get-Process -Id $process.Id | Select-Object MainWindowTitle).MainWindowTitle;
        if ($windowTitle -like '*YouTube*') {
            Write-Host 'Closing YouTube tab for process ID $($process.Id)';
            Stop-Process -Id $process.Id -Force;
        }
    }
} else {
    Write-Host 'No Microsoft Edge processes are running.';
}"

param(
[Parameter(Mandatory=$true)] $EnvName, [Parameter(Mandatory=$true)] $SavesPath
)
 "Name of virtual Environment (not Path!): " + $EnvName

$QROGUE_PATH = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$QROGUE_PATH = Split-Path -Path $QROGUE_PATH -Parent

# activate environment
Enter-CondaEnvironment ${EnvName}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate specified Conda environment. Please make sure you only specified the NAME, not the Path!"
    return 1
}

# check validity of SavesPath
if ((-Not ${SavesPath}) -or (${SavesPath} -eq ".")) {
    $SavesPath = $QROGUE_PATH
}
while (-Not (Test-Path ${SavesPath})) {
    $SavesPath = Read-Host -Prompt ("[Qrogue] Path does not exist! Please choose another one or press q to abort:")
    if (${SavesPath} -eq "q") {
        return 0
    }
}

$SavesPath = Join-Path -Path ${SavesPath} -ChildPath "QrogueData"
Write-Host "[Qrogue] Folder for Game data will be created as:" ${SavesPath}
$continue = Read-Host -Prompt ("[Qrogue] Press y to start installation")
if ($continue -eq "y") {
    Write-Host "[Qrogue] Installing the required packages in the specified environment..."
    $REQUIREMENTS = Join-Path -Path ${QROGUE_PATH} -ChildPath "installer\requirements_windows.txt"
    pip install -r ${REQUIREMENTS}
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install the required dependencies. Please check the output of pip!
        Exit code = " $LASTEXITCODE     # not sure if this is now the result of if or still of pip
        return 2
    }
    Write-Host "[Qrogue] Done installing dependencies!"

    Write-Host "[Qrogue] Setting up Game data..."
    $CONFIG_PATH = Join-Path -Path ${QROGUE_PATH} -ChildPath "installer\qrogue.config"
    $EnvName | Out-File -FilePath ${CONFIG_PATH} -Encoding utf8
    $SavesPath | Out-File -FilePath ${CONFIG_PATH} -Encoding utf8 -Append

    # create the needed data directories if they don't already exist (e.g. because of a previous installation)
    $LOGS_PATH = Join-Path -Path ${SavesPath} -ChildPath "logs"
    $KEYLOGS_PATH = Join-Path -Path ${SavesPath} -ChildPath "keylogs"
    $SCREEN_PATH = Join-Path -Path ${SavesPath} -ChildPath "screenprints"
    if (-not (Test-Path ${SavesPath})) {
        New-Item -ItemType Directory -Path ${SavesPath}
    }
    if (-not (Test-Path ${LOGS_PATH})) {
        New-Item -ItemType Directory -Path ${LOGS_PATH}
    }
    if (-not (Test-Path ${KEYLOGS_PATH})) {
        New-Item -ItemType Directory -Path ${KEYLOGS_PATH}
    }
    if (-not (Test-Path ${SCREEN_PATH})) {
        New-Item -ItemType Directory -Path ${SCREEN_PATH}
    }
    Write-Host "[Qrogue] Finished. You can play now by executing play_qrogue.ps1"

    Exit-CondaEnvironment
}
else {
    Write-Host "Aborted installation by User input."
    return 2
}

Write-Host "last line"

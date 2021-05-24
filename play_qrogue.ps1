$QROGUE_PATH = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$CONFIG_PATH = Join-Path -Path ${QROGUE_PATH} -ChildPath "installer\qrogue.config"
$GAME_PATH = Join-Path -Path ${QROGUE_PATH} -ChildPath "main.py"

$config = Get-Content ${CONFIG_PATH}

# load powershell profile
#$profile_parent = Split-Path -Path $profile -Parent
#$qrogue_profile = Join-Path -ChildPath QrogueProfile.ps1 -Path ${profile_parent}
#. ${qrogue_profile}

# resize window
#$max_size = (Get-Host).UI.RawUI.MaxPhysicalWindowSize
#$new_size = (Get-Host).UI.RawUI.WindowSize
#$new_size.Width = 150
#$new_size.Height = 50
#IF ($new_size.Width -gt $max_size.Width)
#{
#    $new_size.Width = $max_size.Width
#}
#IF ($new_size.Height -gt $max_size.Height)
#{
#    $new_size.Height = $max_size.Height
#}
#
#(Get-Host).UI.RawUI.BufferSize = $new_size
#(Get-Host).UI.RawUI.WindowSize = $new_size
#Write-Host "New Window Size: " $new_size

# start game
$ENV_NAME = ${config} | Select-Object -First 1
Enter-CondaEnvironment ${ENV_NAME}
& python ${GAME_PATH}
Exit-CondaEnvironment

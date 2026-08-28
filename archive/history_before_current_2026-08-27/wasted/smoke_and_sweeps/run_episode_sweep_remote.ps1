$ErrorActionPreference = "Stop"

$Python = "H:\anaconda\envs\yolo\python.exe"
$Root = "H:\degree-dissertation\md_dqn_rsf"
$Status = Join-Path $Root "episode_sweep_status.log"

function Write-Status {
    param([string]$Message)
    Add-Content -Path $Status -Value "[$(Get-Date -Format o)] $Message"
}

function Run-Policy {
    param(
        [string]$Policy,
        [int]$Episodes,
        [string]$OutputName
    )

    $Output = Join-Path $Root $OutputName
    New-Item -ItemType Directory -Force -Path $Output | Out-Null
    $Stdout = Join-Path $Output "run.log"
    $Stderr = Join-Path $Output "run.err.log"
    Write-Status "starting $Policy episodes=$Episodes"

    $RunArguments = @(
        (Join-Path $Root "run_single_policy.py"),
        "--resume",
        "--policy", $Policy,
        "--episodes", $Episodes,
        "--horizon", 64,
        "--seeds", 5,
        "--test-traces", 20,
        "--output", $Output
    )
    & $Python @RunArguments 1> $Stdout 2> $Stderr
    if ($LASTEXITCODE -ne 0) {
        throw "$Policy training failed with exit code $LASTEXITCODE"
    }

    $VerifyArguments = @(
        (Join-Path $Root "verify_model_archive.py"),
        "--models", (Join-Path $Output "models"),
        "--report", (Join-Path $Output "model_verification.json")
    )
    & $Python @VerifyArguments 1>> $Stdout 2>> $Stderr
    if ($LASTEXITCODE -ne 0) {
        throw "$Policy verification failed with exit code $LASTEXITCODE"
    }

    Write-Status "completed $Policy episodes=$Episodes"
}

Set-Content -Path $Status -Value "[$(Get-Date -Format o)] sweep started"
try {
    Run-Policy -Policy "standard_dqn" -Episodes 400 -OutputName "outputs_standard_dqn_ep400"
    Run-Policy -Policy "dqn_r" -Episodes 470 -OutputName "outputs_dqn_r_ep470"
    Run-Policy -Policy "dqn_rs" -Episodes 540 -OutputName "outputs_dqn_rs_ep540"
    Write-Status "sweep completed successfully"
    exit 0
}
catch {
    Write-Status "FAILED: $($_.Exception.Message)"
    exit 1
}

param(
    [string]$BaseDir  = 'C:\Users\raest\Documents\Karma_SADE',
    [string]$BindAddr = 'http://+:7771/',
    [string]$TokenFile = 'C:\Users\raest\Documents\Karma_SADE\.local-file-token'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Web

# Load token from file (never hardcode)
if (-not (Test-Path $TokenFile)) {
    Write-Error "Token file not found: $TokenFile. Run Scripts/generate-file-token.ps1 first."
    exit 1
}
$AUTH_TOKEN = (Get-Content $TokenFile -Raw).Trim()
Write-Output "[karma-file-server] Starting on $BindAddr serving $BaseDir"
Write-Output "[karma-file-server] Token loaded ($($AUTH_TOKEN.Length) chars)"

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($BindAddr)

try {
    $listener.Start()
} catch {
    Write-Error "[karma-file-server] Failed to start listener: $_`nTry running as admin or check if port 7771 is in use."
    exit 1
}

Write-Output "[karma-file-server] Listening on port 7771..."

while ($listener.IsListening) {
    try {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $res = $ctx.Response

        function Send-Json($statusCode, $body) {
            $res.StatusCode = $statusCode
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
            $res.ContentType = 'application/json; charset=utf-8'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
        }

        # Auth check
        $authHeader = $req.Headers['Authorization']
        if ($authHeader -ne "Bearer $AUTH_TOKEN") {
            Send-Json 401 '{"error":"unauthorized"}'
            continue
        }

        # Route: GET /v1/local-dir — list files in a directory
        if ($req.HttpMethod -eq 'GET' -and $req.Url.AbsolutePath -eq '/v1/local-dir') {
            $dirPath = [System.Web.HttpUtility]::ParseQueryString($req.Url.Query)['path']
            if (-not $dirPath) { $dirPath = '' }  # empty = root of Karma_SADE
            $fullDir = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($BaseDir, $dirPath))
            if (-not $fullDir.StartsWith($BaseDir + '\') -and $fullDir -ne $BaseDir) {
                Send-Json 403 '{"error":"traversal_denied"}'
                continue
            }
            if (-not (Test-Path $fullDir -PathType Container)) {
                Send-Json 404 '{"error":"dir_not_found"}'
                continue
            }
            $items = Get-ChildItem $fullDir | ForEach-Object {
                $rel = $_.FullName.Substring($BaseDir.Length + 1).Replace('\','/')
                [PSCustomObject]@{ name = $_.Name; path = $rel; type = $(if ($_.PSIsContainer) { 'dir' } else { 'file' }); bytes = $(if ($_.PSIsContainer) { 0 } else { $_.Length }) }
            }
            $payload = [PSCustomObject]@{ ok = $true; dir = $(if ($dirPath) { $dirPath } else { '.' }); entries = @($items) } | ConvertTo-Json -Compress -Depth 4
            Send-Json 200 $payload
            Write-Output "[karma-file-server] $(Get-Date -Format 'HH:mm:ss') DIR $fullDir ($($items.Count) entries)"
            continue
        }

        # Only GET /v1/local-file
        if ($req.HttpMethod -ne 'GET' -or $req.Url.AbsolutePath -ne '/v1/local-file') {
            Send-Json 404 '{"error":"not_found"}'
            continue
        }

        # Parse path param
        $queryPath = [System.Web.HttpUtility]::ParseQueryString($req.Url.Query)['path']
        if (-not $queryPath) {
            Send-Json 400 '{"error":"missing_path","message":"path query parameter is required"}'
            continue
        }

        # Traversal protection
        $fullPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($BaseDir, $queryPath))
        if (-not $fullPath.StartsWith($BaseDir + '\') -and $fullPath -ne $BaseDir) {
            Send-Json 403 '{"error":"traversal_denied","message":"Path must be within Karma_SADE folder"}'
            continue
        }

        # File must exist and be a file (not directory)
        if (-not (Test-Path $fullPath -PathType Leaf)) {
            $escaped = $queryPath -replace '"','\"'
            Send-Json 404 "{`"error`":`"file_not_found`",`"path`":`"$escaped`"}"
            continue
        }

        # Read file with cap
        $content = Get-Content $fullPath -Raw -Encoding UTF8 -ErrorAction Stop
        if ($null -eq $content) { $content = '' }
        if ($content.Length -gt 40000) { $content = $content.Substring(0, 40000) }

        $payload = [PSCustomObject]@{
            ok      = $true
            path    = $queryPath
            content = $content
            bytes   = $content.Length
        } | ConvertTo-Json -Compress -Depth 2
        Send-Json 200 $payload
        Write-Output "[karma-file-server] $(Get-Date -Format 'HH:mm:ss') $queryPath ($($content.Length) chars)"
    } catch {
        Write-Warning "[karma-file-server] Unhandled error: $_"
        try { $res.OutputStream.Close() } catch {}
    }
}

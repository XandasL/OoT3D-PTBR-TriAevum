# OoT3D PT-BR - ativador portatil (codigo-fonte aberto).
# Faz apenas operacoes locais: valida a integridade do O3RO, cria um backup
# do perfil de inicializacao e configura --romfs-overlay no arquivo JSON.
# Nao altera TriAevum.exe, a RomFS original, saves ou packs de texturas.
# Nao baixa arquivos, nao acessa a rede e nao instala servicos.
# Execute com o jogo e o Forge fechados.

$ErrorActionPreference = 'Stop'
try {
    Write-Host "Verificando arquivos locais da traducao..."
    $runtime = (Resolve-Path -LiteralPath $PSScriptRoot -ErrorAction Stop).ProviderPath
    $profile = Join-Path $runtime 'data\TriAevum.launch.json'
    $overlay = Join-Path $runtime 'data\mods\OoT3D-PTBR\OoT3D-PTBR.o3ro'
    $expected = '4B2DC3E7734518200F8BF5483F74F16353DA939B3914AB3986F1E20968EED9E3'
    if (!(Test-Path -LiteralPath $profile -PathType Leaf)) { throw "Perfil do Forge nao encontrado: $profile" }
    if (!(Test-Path -LiteralPath $overlay -PathType Leaf)) { throw "Arquivo de traducao nao encontrado: $overlay" }
    if ((Get-FileHash -LiteralPath $overlay -Algorithm SHA256).Hash -ne $expected) { throw 'O3RO nao corresponde ao arquivo classico beta.1.2 validado.' }
    $obj = Get-Content -LiteralPath $profile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $obj.arguments -or $obj.arguments -isnot [array]) { throw 'Perfil inesperado: arguments deve ser um vetor.' }
    $argsList = [System.Collections.Generic.List[string]]::new()
    foreach ($a in $obj.arguments) { if ($a -isnot [string]) { throw 'Argumento nao textual no perfil.' }; $argsList.Add($a) }
    $indices = @(for ($i = 0; $i -lt $argsList.Count; $i++) { if ($argsList[$i] -ceq '--romfs-overlay') { $i } })
    if ($indices.Count -gt 1) { throw 'Perfil com --romfs-overlay duplicado.' }
    if ($indices.Count -eq 1) {
        $i = [int]$indices[0]
        if ($i + 1 -ge $argsList.Count -or $argsList[$i + 1].StartsWith('--')) { throw 'Argumento --romfs-overlay incompleto.' }
        $argsList[$i + 1] = $overlay
    } else {
        $argsList.Add('--romfs-overlay'); $argsList.Add($overlay)
    }
    # Keep Forge-selected graphics options untouched. This package adds no HD artwork.
    $obj.arguments = @($argsList.ToArray())
    $json = $obj | ConvertTo-Json -Depth 100
    $check = $json | ConvertFrom-Json
    if (@($check.arguments).Count -ne $argsList.Count) { throw 'Falha na validacao JSON.' }
    # Um backup anterior nunca e sobrescrito. Mantemos backups historicos intactos.
    $backup = "$profile.backup-antes-ptbr.json"
    if (!(Test-Path -LiteralPath $backup)) {
        Copy-Item -LiteralPath $profile -Destination $backup -ErrorAction Stop
        Write-Host "Backup do perfil criado: $backup"
    } else {
        Write-Host "Backup existente preservado: $backup"
    }
    $tmp = "$profile.$([guid]::NewGuid().ToString('N')).tmp"
    $transaction = "$profile.$([guid]::NewGuid().ToString('N')).transaction.bak"
    try {
        [System.IO.File]::WriteAllText($tmp, $json, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Replace($tmp, $profile, $transaction)
    } finally {
        Remove-Item -LiteralPath $tmp,$transaction -Force -ErrorAction SilentlyContinue
    }
    Write-Host 'Traducao PT-BR ativada com sucesso.' -ForegroundColor Green
    Write-Host 'O executavel, a RomFS e os packs de texturas nao foram alterados.'
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

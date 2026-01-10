# LibOrbisPkg Build Troubleshooting

## Common Build Errors and Solutions

### Error 1: "Could not find project or directory"
**Symptoms**: Can't find PkgTool.csproj

**Solution**: Make sure you're in the LibOrbisPkg directory
```powershell
cd C:\Path\To\LibOrbisPkg
dir PkgTool\PkgTool.csproj  # Verify file exists
```

### Error 2: "The project file may be invalid"
**Symptoms**: Project file errors, missing targets

**Solution**: Try building the Core solution instead
```powershell
dotnet build LibOrbisPkg.Core.sln --configuration Release
```

### Error 3: "Unable to load service index for nuget.org"
**Symptoms**: Network/NuGet errors

**Solution**: Check internet connection and NuGet access
```powershell
# Test NuGet access
curl https://api.nuget.org/v3/index.json

# Clear NuGet cache if needed
dotnet nuget locals all --clear

# Retry build
dotnet restore
dotnet build PkgTool\PkgTool.csproj --configuration Release
```

### Error 4: "Could not find Windows Desktop SDK"
**Symptoms**: Missing SDK for PkgEditor

**Solution**: Build only PkgTool.Core (command-line only)
```powershell
dotnet build PkgTool.Core\PkgTool.Core.csproj --configuration Release
```

### Error 5: "Target framework not supported"
**Symptoms**: netcoreapp3.0 or other framework errors

**Solution**: Update to newer framework or install .NET Core 3.1
```powershell
# Install .NET Core 3.1 SDK if needed
winget install Microsoft.DotNet.SDK.3_1

# Or try with newer .NET
dotnet build PkgTool\PkgTool.csproj --configuration Release --framework net6.0
```

## Get More Information

Please provide:
1. **Full error message** from the build output
2. **Your .NET version**: `dotnet --version`
3. **Operating System**: Windows 10/11 version

## Alternative: Try PkgTool.Core

If PkgTool fails, try the Core library directly:

```powershell
cd LibOrbisPkg
dotnet build PkgTool.Core\PkgTool.Core.csproj --configuration Release
```

Then use it with:
```powershell
dotnet run --project PkgTool.Core -- pkg_build path\to\file.gp4 output\dir
```

## Quick Test

Try this simpler build command:
```powershell
cd LibOrbisPkg\PkgTool
dotnet build --configuration Release
```

## Last Resort: Pre-built Binary

Check if there's a pre-built version:
- https://github.com/maxton/LibOrbisPkg/releases
- https://ci.appveyor.com/project/maxton/liborbispkg/build/artifacts

Download and use directly without building.

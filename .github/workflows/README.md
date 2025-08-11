# Hearthlink CI/CD Workflows

This directory contains GitHub Actions workflows for automated building, testing, and deployment of Hearthlink.

## Available Workflows

### 🏗️ Windows Native Build (`tauri-build-windows.yml`)

Builds native Windows installers using Tauri v2.

**Triggers:**
- Manual dispatch with configurable options
- Git tags matching `v*.*.*` pattern
- Pushes to `main` branch (for relevant files)
- Pull requests to `main` branch (validation only)

**Artifacts Produced:**
- Windows MSI installer (`.msi`)
- Windows NSIS EXE installer (`.exe`)
- Build information JSON file
- Build logs (on failure)

**Manual Trigger Options:**
- **Release Type:** `development`, `alpha`, `release`
- **Build Target:** `msi`, `nsis`, `both`

## Build Requirements

### Environment
- **OS:** Windows (windows-latest runner)
- **Node.js:** v18 LTS
- **Python:** 3.11
- **Rust:** Stable toolchain
- **Tauri CLI:** v2.0+

### Dependencies
- All NPM packages from `package.json`
- Python packages from `requirements.txt` and `requirements_full.txt`
- Rust dependencies from `src-tauri/Cargo.toml`

## Build Process

### 1. Environment Setup
- Installs Node.js, Python, and Rust toolchains
- Caches dependencies for faster builds
- Verifies all tools are properly installed

### 2. Dependency Installation
- Runs `npm ci` for Node.js packages
- Installs Python requirements with pip
- Rust dependencies are handled by Cargo

### 3. Frontend Build
- Builds React application with `npm run build`
- Verifies build output in `build/` directory

### 4. Native Application Build
- Uses Tauri CLI to build native Windows installers
- Supports both MSI and NSIS (EXE) bundle types
- Includes all Python dependencies and resources

### 5. Artifact Preparation
- Renames files with version and timestamp
- Creates build information JSON
- Prepares for upload or release

## Configuration Files

### `tauri.conf.json`
Primary Tauri configuration file with:
- Application metadata and branding
- Window configuration and permissions
- Bundle settings for different platforms
- Security policies and allowed operations

### Required Assets
- Icons in `src-tauri/icons/` directory
- Application resources and Python files
- Configuration files in `config/`

## Using the Workflows

### Manual Build
1. Go to **Actions** tab in GitHub
2. Select **"Windows Native Build - Tauri"**
3. Click **"Run workflow"**
4. Choose release type and build target
5. Monitor build progress

### Automatic Builds
- **Tags:** Create a tag like `v1.3.1` to trigger release build
- **Main Branch:** Pushes automatically trigger development builds
- **Pull Requests:** Validation builds to check for issues

### Downloading Artifacts
1. Go to the completed workflow run
2. Scroll to **Artifacts** section
3. Download `windows-installers-*` zip file
4. Extract to find MSI and EXE installers

## Artifact Naming Convention

```
Hearthlink-{version}-{releaseType}-{timestamp}-{target}.{ext}
```

Example:
```
Hearthlink-1.3.0-alpha-20250109-1200-x86_64-pc-windows-msvc.msi
Hearthlink-1.3.0-alpha-20250109-1200-x86_64-pc-windows-msvc.exe
```

## Security Configuration

### Required Secrets
- `TAURI_PRIVATE_KEY`: For app signing (optional)
- `TAURI_KEY_PASSWORD`: Private key password (optional)
- `GITHUB_TOKEN`: Automatic for releases

### Build Security
- Sandboxed build environment
- Read-only dependency caching
- No external network access during build
- Artifact integrity verification

## Troubleshooting

### Common Build Failures

1. **Missing Icons**
   - Ensure all required icon files exist in `src-tauri/icons/`
   - Verify icon formats and sizes are correct

2. **Python Dependencies**
   - Check `requirements.txt` syntax
   - Ensure all packages are available on Windows

3. **Tauri Configuration**
   - Validate `tauri.conf.json` schema
   - Check bundle settings and permissions

4. **Resource Bundling**
   - Verify resource paths in `tauri.conf.json`
   - Ensure Python files are included correctly

### Debug Information
- Build logs are automatically uploaded on failure
- Check the **Artifacts** section for detailed logs
- Review the build summary for quick issue identification

## Local Testing

Before pushing changes, test locally:

```bash
# Install Tauri CLI
cargo install tauri-cli --version "^2.0"

# Build React frontend
npm run build

# Test Tauri build
tauri build --debug

# Test specific bundle types
tauri build --bundles msi
tauri build --bundles nsis
```

## Development Workflow Integration

### Branch Protection
- Require CI checks to pass before merging
- Validate build on all pull requests
- Automatic artifact generation for releases

### Version Management
- Version defined in `src-tauri/tauri.conf.json`
- Must match `package.json` version
- Semantic versioning recommended

### Release Process
1. Update version in configuration files
2. Create and push git tag
3. Workflow automatically creates draft release
4. Review and publish release with artifacts

## Performance Optimizations

### Build Speed
- Dependency caching for all package managers
- Parallel job execution where possible
- Incremental Rust compilation
- Efficient artifact compression

### Resource Usage
- Optimized build runners
- Memory-efficient compilation
- Minimal artifact retention

## Monitoring and Notifications

The workflow provides:
- Detailed build summaries
- Step-by-step progress tracking
- Automatic failure notifications
- Artifact download instructions

For additional help or issues, check the workflow logs or contact the development team.
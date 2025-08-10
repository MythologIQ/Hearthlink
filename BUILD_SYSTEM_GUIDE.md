# Hearthlink Build System Guide

## 🚀 GitHub Actions Windows Native Build

This project now includes a comprehensive CI/CD pipeline for building Windows native applications using Tauri v2.

### Quick Start

#### 1. Manual Build (GitHub Actions)
1. Go to **Actions** tab in GitHub repository
2. Select **"Windows Native Build - Tauri"**
3. Click **"Run workflow"**
4. Configure options:
   - **Release Type**: `development`, `alpha`, `release`
   - **Build Target**: `msi`, `nsis`, `both`
5. Download artifacts when complete

#### 2. Local Testing
```bash
# Test configuration
npm run test:tauri-config

# Test full build process
npm run test:build-local

# Test specific installers
npm run test:build-msi
npm run test:build-nsis

# Quick CI validation
npm run ci:validate
```

### Automatic Triggers

- **Git Tags**: `v1.2.3` → Production release build
- **Main Branch**: Push → Development build  
- **Pull Requests**: → Validation build (no artifacts)

### Build Artifacts

The workflow produces:
- **MSI Installer** (Windows Installer format)
- **NSIS EXE** (Self-extracting executable)
- **Build Information** (JSON with metadata)

Naming convention:
```
Hearthlink-{version}-{releaseType}-{timestamp}-{target}.{ext}
Example: Hearthlink-1.3.0-alpha-20250109-1200-x86_64-pc-windows-msvc.msi
```

### Build Environment

- **OS**: Windows (latest)
- **Node.js**: v18 LTS
- **Python**: 3.11  
- **Rust**: Stable toolchain
- **Tauri**: v2.0+

### Key Features

✅ **Tauri v2 Compatible** - Modern configuration schema  
✅ **Multi-format Support** - Both MSI and NSIS installers  
✅ **Error Handling** - Comprehensive logging and recovery  
✅ **Artifact Management** - Versioned, timestamped outputs  
✅ **Local Testing** - Pre-flight validation scripts  
✅ **Caching** - Optimized for fast builds  
✅ **Security** - Sandboxed builds with audit trails  

### Configuration Files

| File | Purpose |
|------|---------|
| `src-tauri/tauri.conf.json` | Main Tauri configuration |
| `src-tauri/Cargo.toml` | Rust dependencies |
| `requirements.txt` | Python dependencies |
| `.github/workflows/tauri-build-windows.yml` | CI/CD workflow |

### Common Issues & Solutions

#### Build Failures
- **Missing Icons**: Create `src-tauri/icons/` with required files
- **Python Deps**: Check `requirements.txt` syntax
- **Version Mismatch**: Sync `package.json` and `tauri.conf.json`

#### Local Testing
- **Install Tauri CLI**: `cargo install tauri-cli --version "^2.0"`
- **Verify Setup**: `npm run test:tauri-config`
- **Test Build**: `npm run test:build-local`

### Development Workflow

1. **Make Changes** → Edit code/config
2. **Local Test** → `npm run ci:validate`  
3. **Commit & Push** → Triggers CI build
4. **Create Tag** → `git tag v1.2.3` for releases
5. **Download** → Get installers from Actions artifacts

### Monitoring

The workflow provides:
- ✅ Step-by-step progress tracking
- 📊 Detailed build summaries  
- 📦 Automatic artifact uploads
- ⚠️ Error logs and diagnostics
- 🔔 Email notifications on failure

### Security

- 🔒 Sandboxed build environment
- 🛡️ Read-only dependency caching
- 🔐 Optional code signing support
- 📝 Complete audit trail
- 🚫 No external network access during build

### Performance

- ⚡ Dependency caching (NPM, Cargo, Python)
- 🔄 Parallel job execution
- 📦 Efficient artifact compression
- ⏱️ Typical build time: 15-20 minutes

### Support

For issues:
1. Check workflow logs in GitHub Actions
2. Run local testing scripts
3. Review configuration validation
4. Check the troubleshooting guide in `.github/workflows/README.md`

---

🎯 **Ready to Build**: The CI/CD pipeline is production-ready and will reliably produce Windows installer artifacts for distribution.
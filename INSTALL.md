# Installation Guide for scr

*This file created with AI Coding Assistant*

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

```bash
# Clone or navigate to the project directory
cd /path/to/scr

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

### Method 2: Install from Source Distribution

```bash
# Build source distribution
python setup.py sdist

# Install the generated tarball
pip install dist/scr-1.0.0.tar.gz
```

### Method 3: Build and Install RPM Package

```bash
# Install required tools (on RHEL/CentOS/Fedora)
sudo yum install rpm-build python3-setuptools

# Build the RPM
python setup.py bdist_rpm

# Install the RPM
sudo rpm -ivh dist/scr-1.0.0-1.noarch.rpm
```

## Post-Installation

After installation, the `scr` command will be available system-wide:

```bash
# Run scr
scr

# Run with options
scr --nocolor
scr --default_sessions "web,api,db"
```

## Configuration

Create a configuration file at `~/.scr`:

```ini
[scr]
color = True
default_sessions = dev,dev2,run,log,test
```

## Uninstallation

### If installed via pip:
```bash
pip uninstall scr
```

### If installed via RPM:
```bash
sudo rpm -e scr
```

## Requirements

- Python 3.6 or higher
- GNU Screen
- click library (automatically installed as dependency)

## Troubleshooting

### Command not found after installation

Make sure your Python scripts directory is in your PATH:
```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH="$HOME/.local/bin:$PATH"
```

### Permission denied

If you get permission errors, try:
```bash
pip install --user .
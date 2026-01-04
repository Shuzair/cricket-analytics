# SETUP INSTRUCTIONS
## Setting Up Cricket Analytics on Company Laptop with Personal GitHub

This guide helps you set up the project using your **personal GitHub** while keeping your company GitHub separate.

You already have your personal SSH key (`id_ed25519_personal`) set up, so we'll use the same approach as your other personal project.

---

## STEP 1: Create Repository on Personal GitHub

1. Go to https://github.com (log in with your **personal** account)
2. Click the **+** icon → **New repository**
3. Name it: `cricket-analytics`
4. Keep it **Private** (recommended) or Public
5. **DO NOT** initialize with README (we already have files)
6. Click **Create repository**

---

## STEP 2: Set Up the Project Folder

### 2.1 Create the project directory

```bash
# Go to where you want the project
cd ~
mkdir cricket-analytics
cd cricket-analytics
```

### 2.2 Copy the project files

Extract the downloaded zip contents into this folder.

---

## STEP 3: Initialize Git with Personal Account

### 3.1 Initialize git

```bash
cd ~/cricket-analytics
git init
```

### 3.2 Configure this repo to use your personal SSH key

```bash
# Tell this repo to use your personal SSH key
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_personal -F /dev/null"
```

### 3.3 Set your personal identity for this repo

```bash
git config user.name "Your Name"
git config user.email "your.personal.email@gmail.com"
```

### 3.4 Verify the config

```bash
git config --list --local
```

You should see:
```
core.sshcommand=ssh -i ~/.ssh/id_ed25519_personal -F /dev/null
user.name=Your Name
user.email=your.personal.email@gmail.com
```

---

## STEP 4: Connect to Personal GitHub and Push

### 4.1 Add remote

```bash
# Replace YOUR_USERNAME with your personal GitHub username
git remote add origin git@github.com:YOUR_USERNAME/cricket-analytics.git
```

### 4.2 Add all files and commit

```bash
git add .
git commit -m "Initial commit: project scaffold"
```

### 4.3 Push to personal GitHub

```bash
git branch -M main
git push -u origin main
```

---

## STEP 5: Set Up the Development Environment

### 5.1 Create your .env file

```bash
cp .env.example .env
```

Edit `.env` if you want to change default passwords:

```bash
nano .env
```

### 5.2 Install Docker Desktop

If not already installed:
- Download from: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop

### 5.3 Start PostgreSQL

```bash
docker-compose up -d
```

Verify it's running:

```bash
docker ps
```

You should see `cricket_postgres` running.

### 5.4 Set up Python virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5.5 Test everything

```bash
# Test database connection
python src/db/connection.py

# Load sample data
python src/pipelines/load_data.py
```

---

## STEP 6: Open in VS Code

```bash
code .
```

### Recommended VS Code Extensions:
- Python
- PostgreSQL (by Chris Kolkman)
- Docker
- GitLens

---

## Daily Workflow

```bash
# 1. Start Docker (if not running)
docker-compose up -d

# 2. Activate Python environment
source venv/bin/activate

# 3. Do your work...

# 4. Commit and push
git add .
git commit -m "Your message"
git push
```

---

## Cloning on Another Machine

When you clone this project on a different computer:

```bash
# Clone the repo
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics

# Configure to use personal SSH key (if on a machine with multiple keys)
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_personal -F /dev/null"
git config user.name "Your Name"
git config user.email "your.personal.email@gmail.com"

# Set up environment
cp .env.example .env
docker-compose up -d
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Troubleshooting

### "Permission denied (publickey)" when pushing
- Verify the SSH key is configured for this repo:
  ```bash
  git config --local core.sshCommand
  ```
- Test SSH connection:
  ```bash
  ssh -i ~/.ssh/id_ed25519_personal -T git@github.com
  ```

### Docker not starting
- Make sure Docker Desktop is running
- Try: `docker-compose down && docker-compose up -d`

### Can't connect to database
- Check if container is running: `docker ps`
- Check logs: `docker-compose logs postgres`

### Python can't find modules
- Make sure venv is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

---

## Common Commands Reference

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View database logs
docker-compose logs -f

# Connect to database directly
docker exec -it cricket_postgres psql -U postgres -d cricket

# Reset database (delete all data)
docker-compose down -v
docker-compose up -d

# Check git config for this repo
git config --list --local
```

---

## Summary: Key Points

1. **core.sshCommand** tells this repo to use your personal SSH key
2. **Local git config** keeps personal commits separate from company work
3. **Docker** keeps PostgreSQL portable across machines
4. **Virtual environment** keeps Python dependencies isolated
5. **.env file** keeps secrets out of git

This approach is repo-specific and won't affect your other projects!

# 🔐 Set up SSH Access from GitHub Actions to VPS for CI/CD

This guide walks you through securely setting up SSH access between GitHub Actions and your VPS. This enables automatic deployment via CI/CD.

---

## ✅ Goal

Allow GitHub Actions to SSH into your VPS without a password using an SSH key.

---

## 🧱 1. Generate SSH Key Pair (Locally)

Open your terminal and run:

```bash
ssh-keygen -t ed25519 -C "github-deploy" -f deploy_key
```

- This creates:
  - `deploy_key` → private key
  - `deploy_key.pub` → public key

> Leave the passphrase empty (just press Enter when prompted).

---

## 📤 2. Upload Public Key to VPS

### Option A: Manually

```bash
ssh youruser@YOUR_VPS_IP
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
```

Paste the contents of `deploy_key.pub` into `authorized_keys`.

### Option B: Using `ssh-copy-id`
it will not work on windows terminal.
for windows need to use gitbash
```bash
ssh-copy-id -i deploy_key.pub youruser@YOUR_VPS_IP
```

### Set Correct Permissions

On the VPS:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## 🛡️ 3. Add Private Key to GitHub Actions Secrets

In your GitHub repository:

Go to **Settings > Secrets and variables > Actions > Repository secrets**, then add:

| Name             | Value                               |
|------------------|--------------------------------------|
| `VPS_SSH_KEY`    | Paste contents of `deploy_key`       |
| `VPS_HOST`       | Your VPS IP (e.g., `188.165.79.187`) |
| `VPS_USER`       | Your VPS user (e.g., `deploy`)       |

---

## 🧪 4. Test SSH Access (Optional)

Locally, verify the connection:

```bash
ssh -i deploy_key youruser@YOUR_VPS_IP
```

You should connect without being prompted for a password.

---

## ⚙️ 5. Use in GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup SSH agent
      uses: webfactory/ssh-agent@v0.9.0
      with:
        ssh-private-key: ${{ secrets.VPS_SSH_KEY }}

    - name: Run deployment script
      run: |
        ssh -o StrictHostKeyChecking=no ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} 'bash ~/deploy.sh'
```

---

## 🔁 Optional: Copy Files via SCP in GitHub Actions

```yaml
    - name: Upload artifact to VPS
      run: |
        scp -o StrictHostKeyChecking=no ./build.zip ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }}:~/app/
```

---

## 🧼 Security & Best Practices

- Never commit `deploy_key` or `deploy_key.pub` to your repo
- Use a dedicated `deploy` user with limited access
- Disable root login or restrict it via firewall
- Consider adding IP-based SSH restrictions

---

## ✅ You’re Done!

GitHub Actions now has secure SSH access to your VPS and can deploy automatically.
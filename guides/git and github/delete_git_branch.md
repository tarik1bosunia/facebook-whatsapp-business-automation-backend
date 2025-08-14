# How to Delete a Git Branch

You can delete a Git branch **locally** and/or on **GitHub (remote)**.

---

## 1️⃣ Delete branch locally

```bash
# If you're on another branch (not the one you want to delete)
git branch -d branch_name   # Safe delete (won't delete if unmerged)
git branch -D branch_name   # Force delete (even if unmerged)
```

---

## 2️⃣ Delete branch on GitHub (remote)

```bash
git push origin --delete branch_name
```

---

## 3️⃣ Delete from GitHub web interface

1. Go to your repository on GitHub.  
2. Click **Branches** (usually near the top).  
3. Find the branch you want to delete.  
4. Click the **trash bin icon** next to it.

---

**Note:** You **cannot delete the default branch** (usually `main` or `master`) without changing it first in your repo settings.

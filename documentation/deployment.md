# Deployment Guide

Replace `REPOSITORY_URL` with your repo (e.g. `https://github.com/<user>/latticelab.git`).

## 1. GitHub
```bash
git init
git add .
git commit -m "Initial Commit"
git branch -M main
git remote add origin REPOSITORY_URL
git push -u origin main
```
**Releases / versioning (SemVer):**
```bash
git tag -a v1.0.0 -m "First release"
git push origin v1.0.0
```
Then on GitHub: *Releases → Draft a new release → choose tag v1.0.0 → Publish*.

## 2. Streamlit Community Cloud
1. Push the repo to GitHub (public or private).
2. Go to https://share.streamlit.io → **New app**.
3. Select the repository, branch `main`, main file `app.py`.
4. *Advanced settings* → Python 3.11; paste optional secrets (see `streamlit_config/secrets.toml.example`).
5. **Deploy**. Every `git push` to `main` auto-redeploys.

## 3. Hugging Face Spaces
1. https://huggingface.co/new-space → SDK **Docker** (recommended) → blank.
2. Clone the Space, copy the project in, and add this front-matter at the top of `README.md`:
   ```yaml
   ---
   title: LatticeLab
   sdk: docker
   app_port: 8501
   ---
   ```
3. `git add . && git commit -m "Deploy" && git push`. The Space builds from the `Dockerfile`.

## 4. Render
1. New → **Web Service** → connect the repo.
2. Runtime: Docker (uses `Dockerfile`) **or** Python with
   Build `pip install -r requirements.txt`, Start `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
3. Health check path: `/_stcore/health`.

## 5. Railway
1. New Project → **Deploy from GitHub repo**.
2. Railway detects the `Dockerfile` (or `Procfile`). Set variable `PORT=8501` if needed.
3. *Settings → Networking → Generate Domain*.

## 6. Replit
Import from GitHub, then in `.replit` set `run = "streamlit run app.py --server.port 8080 --server.address 0.0.0.0"`.

## 7. Docker
```bash
docker build -t ai-project .
docker run -p 8501:8501 ai-project
```
Open http://localhost:8501.

## Checklist
- [ ] Replace LinkedIn/GitHub URLs in `utils/ui.py`
- [ ] (Optional) add SMTP secrets for the contact form

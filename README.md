# Web CV

This repo is now a plain static site.

## Files

- `index.html`: page structure and content
- `resume.html`: compact resume page
- `styles.css`: visual design and responsive layout
- `Dockerfile`: nginx-based container image on port `1313`
- `compose.yaml`: local container run config

## Local preview

Open `index.html` directly in a browser, or run a simple static server:

```bash
python3 -m http.server 8000
```

## Docker

Build and run manually:

```bash
docker build -t web-cv .
docker run --rm -p 1313:1313 web-cv
```

Or with Compose:

```bash
docker compose up --build
```

Then open `http://localhost:1313`.

## CI/CD

GitHub Actions workflow lives in `.github/workflows/docker.yml`.

- On pull requests: validates required files and builds the Docker image
- On pushes to `main`: builds and pushes the image to `ghcr.io/<owner>/web-cv`

Typical server-side deployment flow:

```bash
docker pull ghcr.io/<owner>/web-cv:latest
docker stop web-cv || true
docker rm web-cv || true
docker run -d --name web-cv --restart unless-stopped -p 1313:1313 ghcr.io/<owner>/web-cv:latest
```

If you want full CD, the next step is adding either:

- a webhook-based deploy on your server after image push
- a self-hosted GitHub Actions runner on the server
- Portainer/Watchtower style pull-based deployment

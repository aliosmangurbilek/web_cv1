# Web CV

This repo is now a plain static site.

## Files

- `index.html`: page structure and content
- `resume.html`: compact resume page
- `styles.css`: visual design and responsive layout
- `DESIGN.md`: machine-readable design tokens and human-readable visual rules
- `Dockerfile`: nginx-based container image on port `1313`
- `compose.yaml`: local container run config
- `scripts/visitor_intel.py`: IP-level bot/human/recruiter log analysis

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

## Design system

The visual language is documented in `DESIGN.md` using Google's DESIGN.md specification. It defines the shared colors, typography, spacing, shapes, components, responsive behavior, and design rationale used by both language versions.

Validate it locally with:

```bash
npx --yes @google/design.md lint DESIGN.md
```

When changing the interface, update `DESIGN.md` and `styles.css` together so the documented system and implementation stay aligned.

Nginx access logs stay inside the container at:

- `/var/log/nginx/access.log`

Inspect them without a host volume:

```bash
docker exec web-cv tail -n 100 /var/log/nginx/access.log
```

Copy a snapshot to the host only when analysis is needed:

```bash
docker cp web-cv:/var/log/nginx/access.log logs/access.log
```

## Visitor Intelligence (IP Analysis)

This project now emits JSON access logs and includes an analyzer script to inspect:

- top IP activity and visited paths
- likely bot traffic
- likely human traffic
- recruiter-likelihood signal (best effort, probabilistic)

Run analysis:

```bash
python3 scripts/visitor_intel.py --log-file logs/access.log --since 24h --top 15
```

Write JSON report:

```bash
python3 scripts/visitor_intel.py \
  --log-file logs/access.log \
  --since 7d \
  --json-output reports/visitor-intel.json
```

`--since` accepts relative values like `90m`, `24h`, `7d`, or an ISO datetime.

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

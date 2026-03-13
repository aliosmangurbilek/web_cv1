FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY index-tr.html /usr/share/nginx/html/index-tr.html
COPY resume.html /usr/share/nginx/html/resume.html
COPY styles.css /usr/share/nginx/html/styles.css

EXPOSE 1313

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:1313/ || exit 1

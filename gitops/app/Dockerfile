# Unprivileged nginx: listens on 8080 and runs as UID 101, which matches the
# securityContext in the Deployment (runAsNonRoot, runAsUser: 101).
FROM nginxinc/nginx-unprivileged:1.27-alpine

LABEL org.opencontainers.image.title="ivolve-gitops" \
      org.opencontainers.image.description="Lab 23 GitOps demo app" \
      org.opencontainers.image.source="https://github.com/whabeba/IvolVe-Tasks"

COPY index.html /usr/share/nginx/html/index.html

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=2s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1

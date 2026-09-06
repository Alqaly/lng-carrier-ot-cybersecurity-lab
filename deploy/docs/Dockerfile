FROM python:3.14-slim AS build
WORKDIR /build
COPY requirements-docs.txt .
RUN python -m pip install --no-cache-dir -r requirements-docs.txt
COPY mkdocs.yml .
COPY docs ./docs
RUN python -m mkdocs build --strict

FROM nginx:1.30.4-alpine
LABEL org.opencontainers.image.title="LNG Carrier Evidence-First Course" \
      org.opencontainers.image.source="https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab" \
      org.opencontainers.image.description="Static course only; no PLC, HMI, lab credentials or live process APIs"
COPY deploy/docs/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /build/site /srv/course
USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

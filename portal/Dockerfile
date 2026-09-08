FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN addgroup --system --gid 10001 portal \
    && adduser --system --uid 10001 --ingroup portal --no-create-home portal
COPY --chown=10001:10001 app.py .
COPY --chown=10001:10001 static ./static
USER 10001:10001
EXPOSE 8500
CMD ["python","app.py"]

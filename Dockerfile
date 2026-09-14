FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY --chown=appuser:appuser . .
RUN mkdir -p runtime && chown appuser:appuser runtime
USER appuser
ENV CLAIMBACK_MODE=demo
EXPOSE 8765
CMD ["python", "-m", "uvicorn", "claimback.api:app", "--host", "0.0.0.0", "--port", "8765"]

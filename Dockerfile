FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/python/app.py ./backend/python/app.py
COPY index.html ./index.html
COPY assets ./assets
COPY manifest.webmanifest ./manifest.webmanifest
COPY service-worker.js ./service-worker.js
RUN useradd --system --uid 10001 pulsenet
USER 10001:10001
EXPOSE 8000
CMD ["python", "backend/python/app.py"]

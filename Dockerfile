FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860 \
    PYTHONPATH=/home/user/app/src

RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

COPY --chown=user . /home/user/app

RUN python -m pip install --upgrade pip && \
    python -m pip install .

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "social_reels_automation.main:app", "--host", "0.0.0.0", "--port", "7860"]

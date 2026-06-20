# Circuit Breaker - (c) 2026 Example Org
FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install -e .

EXPOSE 3000

CMD ["sh", "-c", "python -m app"]

FROM python:3
COPY socks5proxy.py /app/
WORKDIR /app
CMD ["python", "socks5proxy.py"]

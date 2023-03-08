FROM python:3
COPY socks5.py /app/
WORKDIR /app
CMD ["python", "socks5proxy.py"]

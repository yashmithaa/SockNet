# SockNet

SockNet is a multi-user chat room built using raw sockets. It supports secure communication over TLS/SSL and allows clients from multiple devices to connect and chat in real-time.

## Security Setup (TLS/SSL)

To ensure encrypted communication and prevent man-in-the-middle attacks, generate a self-signed certificate:

```bash
openssl genrsa -out server.key 2048
openssl req -new -x509 -key server.key -out server.cert -days 365 -subj "/CN=localhost"
```

Make sure all clients have access to `server.cert` to verify the server's identity.

### How to Run

1. Check IPv4 Address (windows: `ipconfig`, Linux/MacOS: `ifconfig`)
2. Start the server

```bash
python server.py
```

3. Run the client

```bash
python client.py
```

Ensure `server.cert` is present in the client's directory.

# Features

- Multi-user chat support
- Secure TLS/SSL encryption
- Multi-device connectivity
- Protection against man-in-the-middle attacks

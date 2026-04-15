# Far-Side Window Hosting

This folder is a minimal deploy package for the live challenge service.

## Files

- `server.py`: TCP challenge service
- `common.py`: protocol parsing and validation helpers
- `relay_downlink.bin`: challenge state data used by the service
- `Dockerfile`: container build
- `docker-compose.yml`: easy deploy with restart policy

## Run With Docker

```powershell
docker build -t far-side-window .
docker run -d --name far-side-window -p 31337:31337 -e FLAG="NSC{your_flag_here}" far-side-window
```

## Run With Compose

First create a local `.env` file from the example and put your real flag there:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set:

```text
FLAG=NSC{your_real_flag_here}
```

Start the service:

```powershell
docker compose up -d --build
```

## Run Without Docker

```powershell
$env:FLAG="NSC{your_flag_here}"
python .\server.py
```

The service listens on port `31337` by default and stays up automatically when launched with Compose because it uses `restart: unless-stopped`.

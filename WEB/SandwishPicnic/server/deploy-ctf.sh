#!/bin/bash
# SandwishPicnic CTF Challenge - Master Deployment Script
# This script sets up the complete CTF environment for organizers

echo "Deploying SandwishPicnic Log4j CTF Challenge..."
echo "=================================================="

chmod +x run-vulnerable.sh

# Set up environment variables
echo "Setting up environment variables..."
source setup-ctf-env.sh

# Compile the application
echo "Compiling Spring Boot application..."
mvn clean compile

# Package the application
echo "Creating JAR package..."
mvn package -DskipTests

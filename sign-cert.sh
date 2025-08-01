#!/bin/bash

# Configuration
CSR_FILE="maintenancelogs.seancohmer.com.csr"
CERT_FILE="maintenancelogs.seancohmer.com.crt"
CA_URL="https://dc01.seancohmer.com/certsrv"
TEMPLATE="WebServer"
DOMAIN="SEANCOHMER.COM"

# Prompt for username and password
read -p "Enter your username: " USER_INPUT
read -sp "Enter your password: " PASSWORD
echo

USERNAME="${DOMAIN}\\${USER_INPUT}"

# Submit the CSR to the CA
echo "[*] Submitting CSR to CA..."
REQ_ID=$(curl -s -k --ntlm -u "${USERNAME}:${PASSWORD}" \
 -F "Mode=newreq" \
 -F "CertRequest=$(< "$CSR_FILE")" \
 -F "CertAttrib=CertificateTemplate:${TEMPLATE}" \
 -F "TargetStoreFlags=0" \
 -F "SaveCert=yes" \
 "${CA_URL}/certfnsh.asp" | grep -oP 'certnew.cer\?ReqID=\K[0-9]+')

if [ -z "$REQ_ID" ]; then
  echo "[-] Failed to submit CSR. Please check your credentials and try again."
  exit 1
fi

echo "[*] CSR submitted successfully. Request ID: $REQ_ID"

# Download the issued certificate in base64 format
echo "[*] Downloading issued certificate..."
curl -s -k --ntlm --output "$CERT_FILE" -u "${USERNAME}:${PASSWORD}" "$CA_URL/certnew.cer?ReqID=$REQ_ID&Enc=b64"

if [ -s "$CERT_FILE" ]; then
    echo "[*] Certificate downloaded successfully: $CERT_FILE"
else    
  echo "[!] Failed to download the certificate. Please check your credentials and try again."
  exit 1
fi
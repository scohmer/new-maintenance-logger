#!/bin/bash

# Configuration
CSR_FILE="maintenancelogs.seancohmer.com.csr"
CERT_FILE="maintenancelogs.seancohmer.com.crt"
CA_URL="https://dc01.seancohmer.com/certsrv"
TEMPLATE="WebServer"
DOMAIN="SEANCOHMER.COM"

# prompt for username and password
read -p "Enter your username: " USER_INPUT
read -s -p "Enter your password: " PASSWORD
echo

USERNAME="${DOMAIN}\\${USER_INPUT}"

# Submit the CSR
echo "[*] Submitting CSR to CA..."
REQ_ID=$(curl -s -k --ntlm -u "$USERNAME:$PASSWORD" \
  --data-urlencode "Mode=newreq" \
  --data-urlencode "CertRequest=$(< "$CSR_FILE")" \
  --data-urlencode "CertAttrib=CertificateTemplate:$TEMPLATE" \
  --data-urlencode "TargetStoreFlags=0" \
  --data-urlencode "SaveCert=yes" \
  "$CA_URL/certfnsh.asp" | grep -oP 'certnew.cer\?ReqID=\K[0-9]+')

if [ -z "$REQ_ID" ]; then
  echo "[!] Failed to retrieve Request ID from CA response."
  exit 1
fi

echo "[+] Request submitted successfully. Request ID: $REQ_ID"

# Download the certificate in base64-encoded PEM format
echo "[*] Downloading signed certificate..."
curl -s -k --ntlm --output "$CERT_FILE" -u "$USERNAME:$PASSWORD" \
  "$CA_URL/certnew.cer?ReqID=$REQ_ID&Enc=b64"

if [ -s "$CERT_FILE" ]; then
  echo "[+] Certificate saved to $CERT_FILE"
else
  echo "[!] Failed to retrieve the certificate. Check CA or credentials."
  exit 1
fi


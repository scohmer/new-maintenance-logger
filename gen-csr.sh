#!/bin/bash

echo "[*] Generating CSR for new maintenance logger..."
openssl req -new -newkey rsa:2048 -nodes -keyout maintenancelogs.seancohmer.com.key -out maintenancelogs.seancohmer.com.csr -subj "/CN=maintenancelogs.seancohmer.com" -config ./openssl.cnf
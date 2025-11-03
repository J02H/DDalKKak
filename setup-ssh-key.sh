#!/bin/bash

SERVER_IP="52.79.102.92"
SERVER_USER="ubuntu"

echo "🔑 SSH 키를 서버에 등록합니다..."

# 공개키를 서버의 authorized_keys에 추가
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD0jdcvt6uie5r86Fo5dOouUwRWNJ2Lluo8q9TlpX/fE2duShoMwRXtJByAT8xe6haI3RfwoVPN6iVoSJeeSyLJnDIVmW0hh8YLYh2Ne8VQV81lk2wWmjaEWtli+9CNJSv3i/e7iNskho24vVfl8vLYmbBkfRjEQLEaud3zohLhCOZOwOTWijUVGl0g0D+FInkEMPmvO8i7LbE1GwVZizpXBs6kqm9AuMh9BoZAy31OuBbvN12vMpcyMNHGJpYsc8x8bKiDwLTRDiPm92Rn6J20Bbtgs0JjSKB8A2xlrT/1067QD/2RO1gB7JJzf3kbaIX27Tnrzz7VLhg6BY1qduJ j02h@johyeonhoui-MacBookPro.local" | ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"

echo "✅ SSH 키 등록 완료!"
#!/bin/bash

# Configuration
# Replace with your actual server details or set via environment variables
SERVER_USER="${DEPLOY_USER:-ubuntu}"
SERVER_IP="${DEPLOY_HOST:-147.224.205.129}"
REMOTE_DIR="/home/ubuntu/mahakaal"

echo "🚀 Deploying Mahakaal to $SERVER_USER@$SERVER_IP..."

# 1. Sync files to the server
# Excluding venv, node_modules, .git, etc. to save bandwidth
echo "📦 Syncing code..."
rsync -avz --exclude 'venv' --exclude 'node_modules' --exclude '.git' --exclude '__pycache__' \
    --exclude '.DS_Store' --exclude 'mahakaal_chats.db' \
    ./ "$SERVER_USER@$SERVER_IP:$REMOTE_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Rsync failed. Check your SSH keys and connection."
    exit 1
fi

# 2. Rebuild and restart on remote
echo "🔄 Rebuilding and restarting containers..."
ssh "$SERVER_USER@$SERVER_IP" "cd $REMOTE_DIR && docker compose down && docker compose up --build -d"

if [ $? -eq 0 ]; then
    echo "✅ Deployment complete! Mahakaal is live."
else
    echo "❌ Remote docker command failed."
    exit 1
fi

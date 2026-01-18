#!/bin/bash

# Availability Domains to cycle through
ADS=("KLzk:US-CHICAGO-1-AD-1" "KLzk:US-CHICAGO-1-AD-2" "KLzk:US-CHICAGO-1-AD-3")
TFVARS="terraform.tfvars"

echo "🚀 Starting OCI ARM Capacity Sniper..."
echo "Press [CTRL+C] to stop."

while true; do
    for AD in "${ADS[@]}"; do
        echo "-------------------------------------------"
        echo "🕒 $(date): Trying $AD..."
        
        # Update the AD in terraform.tfvars (macOS compatible sed)
        sed -i '' "s/availability_domain = .*/availability_domain = \"$AD\"/" "$TFVARS"
        
        # Run terraform apply
        if terraform apply -auto-approve; then
            echo "✅ SUCCESS! Your OCI ARM Instance is UP!"
            # Play a sound if possible (macOS)
            afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
            exit 0
        else
            echo "❌ Still out of capacity for $AD."
        fi
    done
    
    echo "-------------------------------------------"
    echo "😴 All ADs full. Sleeping for 2 minutes before retrying..."
    sleep 120
done

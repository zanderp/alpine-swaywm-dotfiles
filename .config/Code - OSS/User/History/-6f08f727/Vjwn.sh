#!/bin/bash

# Check if notifications are muted
if swaync-client -D == true; then
    echo "[M]"  # Muted
else
    echo "[N]"  # Active
fi
#!/bin/bash

# Check if notifications are muted
if swaync-client -D; then
    echo "[M]"  # Muted
else
    echo "[N]"  # Active
fi
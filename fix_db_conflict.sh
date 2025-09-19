#!/bin/bash
# Quick database conflict resolver

echo "🔧 Resolving database conflict..."

# Backup current database
if [ -f "instance/database.db" ]; then
    cp instance/database.db "instance/database_backup_$(date +%Y%m%d_%H%M%S).db"
    echo "✅ Current database backed up"
fi

# Use main branch version
git checkout --theirs instance/database.db
git add instance/database.db

echo "✅ Database conflict resolved - using main branch version"
echo "⚠️  Note: You may need to recreate some data"

# Optional: Reset database completely
read -p "🤔 Reset database completely? (y/N): " reset_db
if [[ $reset_db =~ ^[Yy]$ ]]; then
    rm -f instance/database.db
    echo "🗑️  Database deleted - will be recreated on next app start"
fi

echo "🚀 Ready to continue with merge/PR!"
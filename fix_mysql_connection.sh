#!/bin/bash

echo "🔧 MySQL Connection Fix for Docker"
echo "===================================="
echo ""

# Check if MySQL is running
echo "1. Checking MySQL status..."
if ps aux | grep -v grep | grep mysqld > /dev/null; then
    echo "   ✅ MySQL is running"
else
    echo "   ❌ MySQL is not running"
    echo "   Run: sudo systemctl start mysql"
    exit 1
fi

# Check current bind address
echo ""
echo "2. Checking MySQL bind address..."
BIND_ADDRESS=$(netstat -tlnp 2>/dev/null | grep 3306 || ss -tlnp 2>/dev/null | grep 3306)
echo "   Current: $BIND_ADDRESS"

if echo "$BIND_ADDRESS" | grep -q "127.0.0.1:3306"; then
    echo "   ⚠️  MySQL is only listening on localhost (127.0.0.1)"
    echo "   ⚠️  Docker containers cannot connect!"
    echo ""
    echo "   You need to change MySQL configuration:"
    echo ""
    echo "   Option 1: Edit MySQL config file"
    echo "   ================================"
    echo "   sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf"
    echo ""
    echo "   Find the line:"
    echo "   bind-address = 127.0.0.1"
    echo ""
    echo "   Change it to:"
    echo "   bind-address = 0.0.0.0"
    echo ""
    echo "   Save and restart MySQL:"
    echo "   sudo systemctl restart mysql"
    echo ""
    echo "   Option 2: Quick fix (temporary)"
    echo "   ==============================="
    echo "   Run these commands:"
    echo ""
    echo "   sudo sed -i 's/bind-address.*=.*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf"
    echo "   sudo systemctl restart mysql"
    echo ""
elif echo "$BIND_ADDRESS" | grep -q "0.0.0.0:3306"; then
    echo "   ✅ MySQL is listening on all interfaces (0.0.0.0)"
fi

echo ""
echo "3. Checking MySQL permissions..."
echo "   You need to grant access to root from any host"
echo ""
echo "   Run these commands in MySQL:"
echo "   ============================"
echo "   mysql -u root -p"
echo ""
echo "   Then in MySQL prompt:"
echo "   CREATE DATABASE IF NOT EXISTS tour_management_db;"
echo "   GRANT ALL PRIVILEGES ON tour_management_db.* TO 'root'@'%' IDENTIFIED BY 'root';"
echo "   FLUSH PRIVILEGES;"
echo "   EXIT;"
echo ""

echo "4. After fixing MySQL, deploy Docker:"
echo "   ==================================="
echo "   docker-compose down"
echo "   docker-compose up -d --build"
echo "   docker-compose logs tour_management"
echo ""

echo "📚 For detailed instructions, see: MYSQL_CONNECTION_GUIDE.md"


# 🔌 Connect Docker to Localhost MySQL

## ✅ Changes Made

I've updated your configuration to connect Docker containers to your localhost MySQL database.

### Files Modified:
1. **`tour_management_project/settings.py`** - Updated database HOST
2. **`docker-compose.yml`** - Added extra_hosts configuration

---

## 🚀 How It Works

### Before:
```python
'HOST': 'localhost',  # ❌ This refers to the container's localhost, not your machine
```

### After:
```python
'HOST': os.environ.get('DB_HOST', 'host.docker.internal'),  # ✅ Points to host machine
```

**`host.docker.internal`** is a special DNS name that Docker provides to access the host machine from inside a container.

---

## 📋 Prerequisites

### 1. Ensure MySQL is Running on Your Host Machine

```bash
# Check if MySQL is running
sudo systemctl status mysql

# If not running, start it
sudo systemctl start mysql

# Enable it to start on boot
sudo systemctl enable mysql
```

### 2. Ensure MySQL is Listening on All Interfaces (Not Just localhost)

Check your MySQL configuration:

```bash
# Edit MySQL config
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Find this line:
bind-address = 127.0.0.1

# Change it to:
bind-address = 0.0.0.0

# Save and restart MySQL
sudo systemctl restart mysql
```

### 3. Create Database and Grant Permissions

```bash
# Login to MySQL
mysql -u root -p

# Create database (if not exists)
CREATE DATABASE IF NOT EXISTS tour_management_db;

# Grant permissions to root from any host
GRANT ALL PRIVILEGES ON tour_management_db.* TO 'root'@'%' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;

# Or create a specific user for Docker
CREATE USER 'tour_user'@'%' IDENTIFIED BY 'tour_password';
GRANT ALL PRIVILEGES ON tour_management_db.* TO 'tour_user'@'%';
FLUSH PRIVILEGES;

# Exit
EXIT;
```

---

## 🔧 Deployment Steps

### Step 1: Stop Existing Containers
```bash
docker-compose down
```

### Step 2: Rebuild and Start Containers
```bash
# Rebuild to pick up new settings
docker-compose up -d --build
```

### Step 3: Verify Connection
```bash
# Check Django logs
docker-compose logs tour_management

# You should see successful database connection
# If you see errors, check the troubleshooting section below
```

### Step 4: Run Migrations (if needed)
```bash
docker-compose exec tour_management python manage.py migrate
```

### Step 5: Test the API
```bash
# Test a simple API call
curl -X POST http://localhost:9300/package/get/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1, "package_id": 1}'
```

---

## 🐛 Troubleshooting

### Issue 1: "Can't connect to MySQL server on 'host.docker.internal'"

**Cause:** MySQL not accessible from Docker container

**Solutions:**

1. **Check MySQL is running:**
   ```bash
   sudo systemctl status mysql
   ```

2. **Check MySQL is listening on 0.0.0.0:**
   ```bash
   sudo netstat -tlnp | grep 3306
   # Should show: 0.0.0.0:3306 (not 127.0.0.1:3306)
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   # If active, allow MySQL
   sudo ufw allow 3306
   ```

### Issue 2: "Access denied for user 'root'@'172.x.x.x'"

**Cause:** MySQL user doesn't have permission from Docker network

**Solution:**
```sql
-- Login to MySQL
mysql -u root -p

-- Grant permissions from any host
GRANT ALL PRIVILEGES ON tour_management_db.* TO 'root'@'%' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;
```

### Issue 3: "host.docker.internal" not resolving

**Cause:** Older Docker versions or Linux systems

**Solution 1 - Use extra_hosts (Already added):**
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Solution 2 - Use host network mode:**
```yaml
# In docker-compose.yml
tour_management:
  network_mode: "host"
  # Remove the networks section
```

**Solution 3 - Use host IP directly:**
```bash
# Find your host IP
ip addr show docker0 | grep inet
# Usually 172.17.0.1

# Set environment variable
export DB_HOST=172.17.0.1

# Or update settings.py directly:
'HOST': '172.17.0.1',
```

### Issue 4: Connection works but tables not found

**Cause:** Database not migrated

**Solution:**
```bash
# Run migrations
docker-compose exec tour_management python manage.py migrate

# Check tables
docker-compose exec tour_management python manage.py dbshell
SHOW TABLES;
EXIT;
```

---

## 🔍 Verify Connection

### Method 1: Django Shell
```bash
docker-compose exec tour_management python manage.py shell

# In the shell:
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT DATABASE()")
print(cursor.fetchone())
# Should print: ('tour_management_db',)
```

### Method 2: Check Logs
```bash
docker-compose logs tour_management | grep -i mysql
docker-compose logs tour_management | grep -i database
```

### Method 3: Test Query
```bash
docker-compose exec tour_management python manage.py dbshell

# In MySQL shell:
SHOW TABLES;
SELECT COUNT(*) FROM tour_management_package;
EXIT;
```

---

## 🎯 Alternative Approaches

### Option 1: Use Environment Variables (Current - Recommended)

**Pros:**
- Flexible (can change without code changes)
- Works across environments
- Easy to configure

**Current Setup:**
```python
'HOST': os.environ.get('DB_HOST', 'host.docker.internal'),
```

**Usage:**
```bash
# Default: uses host.docker.internal
docker-compose up -d

# Custom host:
DB_HOST=172.17.0.1 docker-compose up -d

# Or add to docker-compose.yml:
environment:
  - DB_HOST=172.17.0.1
```

### Option 2: Run MySQL in Docker

**Pros:**
- Everything in Docker
- Consistent across environments
- Easy to reset

**Setup:**
```yaml
# Add to docker-compose.yml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: tour_management_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - nginx_network

  tour_management:
    depends_on:
      - mysql
    environment:
      - DB_HOST=mysql  # Use service name

volumes:
  mysql_data:
```

### Option 3: Use Host Network Mode

**Pros:**
- Direct access to host services
- No special DNS needed

**Cons:**
- Less isolation
- Port conflicts possible

**Setup:**
```yaml
tour_management:
  network_mode: "host"
  # Then use 'localhost' in settings.py
```

---

## 📊 Current Configuration Summary

| Setting | Value | Purpose |
|---------|-------|---------|
| **Database Engine** | MySQL | Database type |
| **Database Name** | tour_management_db | Your database |
| **User** | root | MySQL user |
| **Password** | root | MySQL password |
| **Host** | host.docker.internal | Points to host machine |
| **Port** | 3306 | MySQL default port |

---

## ✅ Quick Checklist

Before deploying:
- [ ] MySQL running on host machine
- [ ] MySQL listening on 0.0.0.0:3306 (not just 127.0.0.1)
- [ ] Database `tour_management_db` exists
- [ ] User has permissions from any host (`'root'@'%'`)
- [ ] Firewall allows port 3306 (if enabled)
- [ ] Docker containers stopped
- [ ] Configuration files updated (already done)

Deploy:
- [ ] `docker-compose down`
- [ ] `docker-compose up -d --build`
- [ ] Check logs: `docker-compose logs tour_management`
- [ ] Test connection (see Verify Connection section)
- [ ] Run migrations if needed
- [ ] Test API endpoints

---

## 🆘 Still Having Issues?

### Debug Steps:

1. **Check MySQL from host:**
   ```bash
   mysql -u root -p -h 127.0.0.1 tour_management_db
   ```

2. **Check from inside container:**
   ```bash
   docker-compose exec tour_management bash
   apt-get update && apt-get install -y mysql-client
   mysql -u root -p -h host.docker.internal tour_management_db
   ```

3. **Check network connectivity:**
   ```bash
   docker-compose exec tour_management ping host.docker.internal
   docker-compose exec tour_management telnet host.docker.internal 3306
   ```

4. **Check Django settings:**
   ```bash
   docker-compose exec tour_management python manage.py shell
   from django.conf import settings
   print(settings.DATABASES)
   ```

---

## 📞 Need Help?

If you're still having connection issues, provide:
1. MySQL version: `mysql --version`
2. Docker version: `docker --version`
3. OS: `uname -a`
4. Error logs: `docker-compose logs tour_management`
5. MySQL config: `cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep bind-address`

---

**Your configuration is ready! Just follow the deployment steps above.** 🚀


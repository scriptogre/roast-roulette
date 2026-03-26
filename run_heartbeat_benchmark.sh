#!/bin/bash

# Heartbeat Performance Benchmark Script
# This simulates your heartbeat workload to measure database capacity

DB_NAME="roast_roulette"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# If using Docker, try these settings:
# DB_HOST="127.0.0.1"  # or the docker container IP
# Check your .env file for actual settings

echo "🚀 Starting Heartbeat Performance Benchmark"
echo "Database: $DB_NAME"
echo "=========================================="

# Copy SQL files to container
echo "📁 Copying SQL files to container..."
docker compose cp heartbeat_simple.sql postgres:/tmp/
docker compose cp heartbeat_realistic.sql postgres:/tmp/

# Initialize pgbench tables
echo "📊 Initializing pgbench with 1000 'players' (scaling factor 10)..."
docker compose exec postgres pgbench -i -s 10 -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

echo ""
echo "🔧 Checking database connection limits..."
docker compose exec postgres psql -U $DB_USER -d $DB_NAME -c "SHOW max_connections;"

echo ""
echo "🔥 Test 1: Simple heartbeat updates only"
echo "Simulating 50 concurrent players for 60 seconds..."
docker compose exec postgres pgbench -c 50 -T 60 -f /tmp/heartbeat_simple.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

echo ""
echo "🔥 Test 2: Realistic heartbeat workload"
echo "Simulating 30 concurrent players with disconnection checks..."
docker compose exec postgres pgbench -c 30 -T 60 -f /tmp/heartbeat_realistic.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

echo ""
echo "🔥 Test 3: Gradual stress test"
echo "Testing incremental concurrency..."
for clients in 10 20 30 40 50; do
    echo "  Testing $clients concurrent clients..."
    docker compose exec postgres pgbench -c $clients -T 15 -f /tmp/heartbeat_simple.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME | grep "tps ="
done

echo ""
echo "📈 Benchmark Results Summary:"
echo "- Look for 'tps' (transactions per second) in the output above"
echo "- For 1000 players with 30s heartbeats, you need ~33 TPS"
echo "- For 1000 players with 15s heartbeats, you need ~67 TPS"
echo "- For 1000 players with 5s heartbeats, you need ~200 TPS"
echo ""
echo "✅ Benchmark complete!"
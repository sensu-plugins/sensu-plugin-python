def example_settings():
    settings = '''
{
  "redis": {
    "reconnect_on_error": false,
    "auto_reconnect": true,
    "host": "redis",
    "db": 0,
    "port": 6379
  },
  "api": {
    "bind": "0.0.0.0",
    "host": "api",
    "port": 4567
  },
  "transport": {
    "reconnect_on_error": true,
    "name": "redis"
  },
  "checks": {},
  "handlers": {}
}
'''

    return settings


def example_check_result():
    check_result = '''
{
  "id": "ef6b87d2-1f89-439f-8bea-33881436ab90",
  "action": "create",
  "timestamp": 1460172826,
  "occurrences": 2,
  "check": {
    "type": "standard",
    "total_state_change": 11,
    "history": ["0", "0", "1", "1", "2", "2"],
    "status": 2,
    "output": "No keepalive sent from client for 230 seconds (>=180)",
    "executed": 1460172826,
    "issued": 1460172826,
    "name": "keepalive",
    "thresholds": {
      "critical": 180,
      "warning": 120
    }
  },
  "client": {
    "timestamp": 1460172596,
    "version": "1.1.0",
    "socket": {
      "port": 3030,
      "bind": "127.0.0.1"
    },
    "subscriptions": [
      "production"
    ],
    "environment": "development",
    "address": "127.0.0.1",
    "name": "client-01"
  }
}
'''

    return check_result

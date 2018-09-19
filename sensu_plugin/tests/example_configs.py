#!/usr/bin/env python
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


def example_check_result_v2():
    check_result = '''
{
  "entity": {
    "id": "test_entity",
    "subscriptions": [
      "sub1",
      "sub2",
      "sub3"
    ]
  },
  "check": {
    "name": "test_check",
    "output": "test_output",
    "subscriptions": [
      "sub1",
      "sub2",
      "sub3"
    ],
    "proxy_entity_id": "test_proxy",
    "total_state_change": 4,
    "state":"failing",
    "history": [
      {
        "status": 0,
        "executed": 0
      },
      {
        "status": 1,
        "executed": 1
      },
      {
        "status": 2,
        "executed": 2
      },
      {
        "status": 3,
        "executed": 3
      },
      {
        "status":0,
        "executed":4
      }
    ],
    "status": 0
  },
  "occurrences": 1
}
'''

    return check_result


def example_check_result_v2_mapped():
    check_result = '''
{
  "action": "create",
  "check": {
    "history": [
      "0",
      "1",
      "2",
      "3",
      "0"
    ],
    "history_v2": [
      {
        "executed": 0,
        "status": 0
      },
      {
        "executed": 1,
        "status": 1
      },
      {
        "executed": 2,
        "status": 2
      },
      {
        "executed": 3,
        "status": 3
      },
      {
        "executed": 4,
        "status": 0
      }
    ],
    "name": "test_check",
    "output": "test_output",
    "proxy_entity_id": "test_proxy",
    "source": "test_proxy",
    "state": "failing",
    "status": 0,
    "subscribers": [
      "sub1",
      "sub2",
      "sub3"
    ],
    "subscriptions": [
      "sub1",
      "sub2",
      "sub3"
    ],
    "total_state_change": 4
  },
  "client": {
    "id": "test_entity",
    "name": "test_entity",
    "subscribers": [
      "sub1",
      "sub2",
      "sub3"
    ],
    "subscriptions": [
      "sub1",
      "sub2",
      "sub3"
    ]
  },
  "entity": {
    "id": "test_entity",
    "name": "test_entity",
    "subscribers": [
      "sub1",
      "sub2",
      "sub3"
    ],
    "subscriptions": [
      "sub1",
      "sub2",
      "sub3"
    ]
  },
  "occurrences": 1,
  "v2_event_mapped_into_v1": true
}
'''
    return check_result

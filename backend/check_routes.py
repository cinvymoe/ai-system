#!/usr/bin/env python3
"""检查FastAPI路由"""

import sys
sys.path.insert(0, 'src')

from main import app

print("已注册的路由:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', ['WEBSOCKET'])
        print(f"  {route.path} - {methods}")

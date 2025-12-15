# Vision Security Monitoring System

## Overview

Vision Security Monitor is a comprehensive security monitoring solution that combines real-time camera surveillance with intelligent motion detection and directional control capabilities.

## Core Features

- **Multi-Camera Management**: Support for multiple RTSP cameras with online/offline status monitoring
- **Real-time Streaming**: Live video feeds from multiple cameras with configurable resolution and FPS
- **Motion Detection**: AI-powered motion detection and tracking
- **Directional Control**: Automated camera direction control (forward, backward, left, right)
- **Sensor Integration**: Support for JY901S IMU sensors for motion and angle detection
- **Message Broker**: Real-time WebSocket-based message broker for camera and sensor updates
- **Web-based UI**: Electron-based desktop application with React frontend
- **Admin Management**: User authentication and role-based access control

## Architecture

- **Frontend**: React + TypeScript with Electron for desktop deployment
- **Backend**: Python FastAPI with SQLite database
- **Communication**: REST API + WebSocket for real-time updates
- **Deployment**: Cross-platform (Linux, macOS, Windows)

## Key Domains

1. **Camera Management**: CRUD operations, status monitoring, RTSP stream handling
2. **Sensor Data**: Real-time sensor readings, motion direction calculation
3. **Message Broker**: Event-driven architecture for camera and sensor updates
4. **AI Settings**: Configuration for motion detection and alert thresholds
5. **Angle Ranges**: Directional control ranges for cameras

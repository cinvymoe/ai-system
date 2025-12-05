# Requirements Document

## Introduction

本文档定义了前端9轴传感器实时显示界面的需求。该界面将订阅后端mock_sensor的实时数据流，显示原始传感器数据（加速度、角速度、角度），并展示处理后的运动方向结果（前进、后退、左转、右转、静止）。该功能将集成到现有的传感器设置界面中，为用户提供实时的传感器状态监控和运动分析可视化。

## Glossary

- **SensorSettingsUI**: 传感器设置用户界面组件，位于前端应用中
- **MockSensor**: 后端模拟传感器设备，生成IMU数据
- **MotionCommand**: 运动指令，包括forward（前进）、backward（后退）、turn_left（左转）、turn_right（右转）、stationary（静止）
- **WebSocket**: 用于前后端实时数据通信的协议
- **IMU Data**: 惯性测量单元数据，包括加速度、角速度和角度
- **DataStream**: 实时数据流，持续推送传感器数据到前端

## Requirements

### Requirement 1

**User Story:** 作为用户，我希望在传感器设置界面中看到实时的传感器数据，以便监控传感器的工作状态。

#### Acceptance Criteria

1. WHEN the user opens the sensor settings page THEN the system SHALL display a real-time data panel
2. WHEN the mock sensor is active THEN the system SHALL display acceleration values for X, Y, Z axes with units (g)
3. WHEN the mock sensor is active THEN the system SHALL display angular velocity values for X, Y, Z axes with units (°/s)
4. WHEN the mock sensor is active THEN the system SHALL display angle values for X, Y, Z axes with units (°)
5. WHEN sensor data updates THEN the system SHALL refresh the displayed values within 200ms

### Requirement 2

**User Story:** 作为用户，我希望看到处理后的运动方向结果，以便直观了解当前的运动状态。

#### Acceptance Criteria

1. WHEN the system receives motion command data THEN the system SHALL display the current motion direction (前进/后退/左转/右转/静止)
2. WHEN the motion direction is "forward" THEN the system SHALL display "前进" with a distinctive visual indicator
3. WHEN the motion direction is "backward" THEN the system SHALL display "后退" with a distinctive visual indicator
4. WHEN the motion direction is "turn_left" THEN the system SHALL display "左转" with a distinctive visual indicator
5. WHEN the motion direction is "turn_right" THEN the system SHALL display "右转" with a distinctive visual indicator
6. WHEN the motion direction is "stationary" THEN the system SHALL display "静止" with a distinctive visual indicator

### Requirement 3

**User Story:** 作为用户，我希望进入传感器设置页面时自动开始监控数据，离开时自动停止，以便获得流畅的使用体验。

#### Acceptance Criteria

1. WHEN the user enters the sensor settings page THEN the system SHALL automatically establish a connection to the mock sensor data stream
2. WHEN the user leaves the sensor settings page THEN the system SHALL automatically disconnect from the data stream and clean up resources
3. WHEN the data stream is active THEN the system SHALL display a "连接中" status indicator
4. WHEN the data stream is disconnected THEN the system SHALL display a "已断开" status indicator
5. WHEN connection fails THEN the system SHALL display an error message and attempt automatic reconnection

### Requirement 4

**User Story:** 作为用户，我希望界面能够显示运动强度信息，以便了解运动的幅度。

#### Acceptance Criteria

1. WHEN the system receives motion command data THEN the system SHALL display the linear motion intensity value
2. WHEN the system receives motion command data THEN the system SHALL display the angular motion intensity value
3. WHEN motion intensity exceeds a threshold THEN the system SHALL highlight the intensity value
4. WHEN motion is stationary THEN the system SHALL display intensity values near zero

### Requirement 5

**User Story:** 作为用户，我希望看到数据更新的时间戳，以便确认数据的实时性。

#### Acceptance Criteria

1. WHEN sensor data is received THEN the system SHALL display the timestamp of the latest data point
2. WHEN no data is received for 2 seconds THEN the system SHALL display a "数据延迟" warning
3. WHEN data stream resumes THEN the system SHALL clear the delay warning

### Requirement 6

**User Story:** 作为开发人员，我希望前端能够通过WebSocket或HTTP轮询订阅后端数据，以便实现实时数据传输。

#### Acceptance Criteria

1. WHEN the frontend establishes connection THEN the system SHALL use WebSocket for real-time data streaming
2. WHEN WebSocket is unavailable THEN the system SHALL fall back to HTTP polling with 100ms interval
3. WHEN data is received THEN the system SHALL parse the JSON payload containing sensor data and motion commands
4. WHEN connection is lost THEN the system SHALL attempt automatic reconnection with exponential backoff
5. WHEN reconnection succeeds THEN the system SHALL resume data display without user intervention

### Requirement 7

**User Story:** 作为用户，我希望界面设计清晰美观，以便轻松阅读和理解传感器数据。

#### Acceptance Criteria

1. WHEN displaying sensor data THEN the system SHALL group related values (acceleration, angular velocity, angles) in separate sections
2. WHEN displaying numeric values THEN the system SHALL format numbers to 2 decimal places
3. WHEN displaying motion direction THEN the system SHALL use color coding (green for forward, red for backward, blue for turns, gray for stationary)
4. WHEN the interface is rendered THEN the system SHALL maintain responsive layout on different screen sizes
5. WHEN data updates THEN the system SHALL use smooth transitions without flickering

### Requirement 8

**User Story:** 作为用户，我希望能够选择不同的运动模式进行测试，以便验证各种运动场景。

#### Acceptance Criteria

1. WHEN the user views the interface THEN the system SHALL display a motion pattern selector with options (forward, backward, turn_left, turn_right, stationary)
2. WHEN the user selects a motion pattern THEN the system SHALL send a command to the backend to change the mock sensor pattern
3. WHEN the pattern changes THEN the system SHALL display the new pattern name
4. WHEN pattern change fails THEN the system SHALL display an error message and retain the previous pattern

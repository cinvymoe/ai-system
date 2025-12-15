# Requirements Document

## Introduction

本文档定义了传感器-摄像头消息代理系统的需求。该系统作为全局消息处理模块，负责订阅传感器数据（方向处理结果和角度值），并将这些数据映射到对应的摄像头地址列表。系统设计为可扩展架构，支持未来添加 AI 报警等新的消息类型。

## Glossary

- **Message Broker（消息代理）**: 负责接收、处理和分发消息的中央处理模块
- **Sensor Data（传感器数据）**: 来自传感器设备的数据，包括方向和角度信息
- **Direction Result（方向处理结果）**: 经过处理后的传感器方向数据
- **Angle Value（角度值）**: 传感器测量的角度数值
- **Camera Mapping（摄像头映射）**: 将传感器数据与对应的摄像头地址关联的过程
- **Subscriber（订阅者）**: 订阅特定消息类型的组件或模块
- **Publisher（发布者）**: 发布消息到消息代理的组件或模块
- **AI Alert（AI 报警）**: 由 AI 系统生成的报警消息

## Requirements

### Requirement 1

**User Story:** 作为系统架构师，我希望有一个全局消息代理模块，以便集中管理系统中的消息流转和处理。

#### Acceptance Criteria

1. THE Message Broker SHALL provide a singleton instance accessible throughout the backend application
2. WHEN the backend application starts THEN the Message Broker SHALL initialize automatically
3. THE Message Broker SHALL support registration of multiple message types
4. THE Message Broker SHALL maintain separate subscription lists for each message type
5. WHEN a component requests the Message Broker instance THEN the system SHALL return the same instance

### Requirement 2

**User Story:** 作为传感器数据处理模块，我希望能够发布方向处理结果，以便其他模块可以订阅和使用这些数据。

#### Acceptance Criteria

1. WHEN a direction result is published THEN the Message Broker SHALL accept the direction data with timestamp
2. THE Message Broker SHALL validate that direction data contains required fields before accepting
3. WHEN direction data is published THEN the Message Broker SHALL notify all registered direction subscribers
4. THE Message Broker SHALL handle publishing failures gracefully without crashing
5. WHEN multiple direction results are published rapidly THEN the Message Broker SHALL process them in order

### Requirement 3

**User Story:** 作为传感器数据处理模块，我希望能够发布角度值数据，以便其他模块可以订阅和使用这些数据。

#### Acceptance Criteria

1. WHEN an angle value is published THEN the Message Broker SHALL accept the angle data with timestamp
2. THE Message Broker SHALL validate that angle data is within valid range before accepting
3. WHEN angle data is published THEN the Message Broker SHALL notify all registered angle subscribers
4. THE Message Broker SHALL support publishing multiple angle values simultaneously
5. WHEN invalid angle data is published THEN the Message Broker SHALL reject it and log the error

### Requirement 4

**User Story:** 作为摄像头管理模块，我希望订阅方向处理结果，以便获取与该方向关联的摄像头地址列表。

#### Acceptance Criteria

1. WHEN a module subscribes to direction results THEN the Message Broker SHALL register the subscriber callback
2. WHEN a direction result is published THEN the Message Broker SHALL invoke all direction subscriber callbacks with the direction data
3. THE Message Broker SHALL query the camera database to retrieve cameras matching the direction
4. WHEN cameras are found for a direction THEN the Message Broker SHALL return a list of camera URLs
5. WHEN no cameras match a direction THEN the Message Broker SHALL return an empty list

### Requirement 5

**User Story:** 作为摄像头管理模块，我希望订阅角度值数据，以便获取与该角度范围关联的摄像头地址列表。

#### Acceptance Criteria

1. WHEN a module subscribes to angle values THEN the Message Broker SHALL register the subscriber callback
2. WHEN an angle value is published THEN the Message Broker SHALL invoke all angle subscriber callbacks with the angle data
3. THE Message Broker SHALL query the angle range database to find matching camera associations
4. WHEN cameras are found for an angle range THEN the Message Broker SHALL return a list of camera URLs
5. WHEN an angle falls outside all defined ranges THEN the Message Broker SHALL return an empty list

### Requirement 6

**User Story:** 作为系统开发者，我希望消息代理系统具有可扩展的架构，以便未来可以轻松添加新的消息类型（如 AI 报警）。

#### Acceptance Criteria

1. THE Message Broker SHALL provide a generic interface for registering new message types
2. WHEN a new message type is registered THEN the Message Broker SHALL create a dedicated subscription channel
3. THE Message Broker SHALL support dynamic addition of message types without code modification to the core broker
4. THE Message Broker SHALL allow each message type to define its own data validation rules
5. WHEN extending with new message types THEN existing message type handlers SHALL continue functioning unchanged

### Requirement 7

**User Story:** 作为系统开发者，我希望预留 AI 报警消息的接口，以便未来可以集成 AI 报警功能。

#### Acceptance Criteria

1. THE Message Broker SHALL define an interface for AI alert message types
2. THE Message Broker SHALL support registration of AI alert subscribers
3. WHEN an AI alert is published THEN the Message Broker SHALL retrieve associated camera URLs
4. THE Message Broker SHALL allow AI alert messages to include severity levels and metadata
5. THE Message Broker SHALL provide placeholder implementation that can be activated when AI system is ready

### Requirement 8

**User Story:** 作为系统管理员，我希望消息代理系统能够记录日志，以便监控系统运行状态和排查问题。

#### Acceptance Criteria

1. WHEN a message is published THEN the Message Broker SHALL log the message type and timestamp
2. WHEN a subscriber is registered THEN the Message Broker SHALL log the subscription details
3. WHEN an error occurs during message processing THEN the Message Broker SHALL log the error with context
4. THE Message Broker SHALL support configurable log levels
5. WHEN processing high-frequency messages THEN the Message Broker SHALL use efficient logging to avoid performance degradation

### Requirement 9

**User Story:** 作为系统开发者，我希望消息代理系统是线程安全的，以便在并发环境中可靠运行。

#### Acceptance Criteria

1. WHEN multiple threads publish messages simultaneously THEN the Message Broker SHALL handle them safely
2. WHEN subscribers are registered from different threads THEN the Message Broker SHALL maintain consistent state
3. THE Message Broker SHALL use appropriate locking mechanisms to prevent race conditions
4. WHEN a subscriber callback is executing THEN the Message Broker SHALL not block other message processing
5. THE Message Broker SHALL handle subscriber callback failures without affecting other subscribers

### Requirement 10

**User Story:** 作为 API 开发者，我希望通过 WebSocket 或 HTTP 接口访问消息代理的输出，以便前端可以实时接收摄像头列表更新。

#### Acceptance Criteria

1. THE system SHALL provide a WebSocket endpoint for streaming camera list updates
2. WHEN a direction or angle message is processed THEN the system SHALL broadcast the resulting camera list via WebSocket
3. THE system SHALL provide an HTTP endpoint to query current camera mappings
4. WHEN a client connects to the WebSocket THEN the system SHALL send the current state immediately
5. THE system SHALL handle client disconnections gracefully without affecting message processing

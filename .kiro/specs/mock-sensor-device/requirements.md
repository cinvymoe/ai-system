# Requirements Document

## Introduction

本文档定义了一个模拟传感器设备系统的需求。该系统能够生成模拟的IMU传感器数据（加速度、角速度、角度），并通过数据处理层分析这些数据，输出运动方向指令（左转、右转、前进、后退）。该系统主要用于开发和测试，无需实际硬件即可验证数据采集和处理流程。

## Glossary

- **MockSensorDevice**: 模拟传感器设备，能够生成符合JY901传感器格式的模拟数据
- **IMU**: 惯性测量单元（Inertial Measurement Unit），包含加速度计、陀螺仪和磁力计
- **DataProcessor**: 数据处理器，负责分析传感器数据并计算运动方向
- **MotionDirectionCalculator**: 运动方向计算器，将传感器数据转换为运动指令
- **CollectedData**: 采集数据模型，符合现有数据采集接口的数据结构
- **MotionCommand**: 运动指令，包括前进、后退、左转、右转等

## Requirements

### Requirement 1

**User Story:** 作为开发人员，我希望能够创建一个模拟传感器设备，以便在没有实际硬件的情况下测试数据采集流程。

#### Acceptance Criteria

1. WHEN the system initializes a MockSensorDevice THEN the MockSensorDevice SHALL generate configurable sensor data patterns
2. WHEN the MockSensorDevice generates data THEN the system SHALL produce acceleration data in the range of -16g to 16g for each axis
3. WHEN the MockSensorDevice generates data THEN the system SHALL produce angular velocity data in the range of -2000°/s to 2000°/s for each axis
4. WHEN the MockSensorDevice generates data THEN the system SHALL produce angle data in the range of -180° to 180° for each axis
5. WHEN the MockSensorDevice is configured with a data generation interval THEN the system SHALL emit data at the specified interval

### Requirement 2

**User Story:** 作为开发人员，我希望模拟设备能够生成预定义的运动模式数据，以便测试特定的运动场景。

#### Acceptance Criteria

1. WHEN a user configures the MockSensorDevice with a "forward" motion pattern THEN the system SHALL generate acceleration data indicating forward movement
2. WHEN a user configures the MockSensorDevice with a "backward" motion pattern THEN the system SHALL generate acceleration data indicating backward movement
3. WHEN a user configures the MockSensorDevice with a "turn_left" motion pattern THEN the system SHALL generate angular velocity data indicating left rotation
4. WHEN a user configures the MockSensorDevice with a "turn_right" motion pattern THEN the system SHALL generate angular velocity data indicating right rotation
5. WHEN a user configures the MockSensorDevice with a "stationary" motion pattern THEN the system SHALL generate data indicating no significant movement

### Requirement 3

**User Story:** 作为开发人员，我希望模拟设备生成的数据符合现有的数据采集接口，以便无缝集成到现有系统中。

#### Acceptance Criteria

1. WHEN the MockSensorDevice generates data THEN the system SHALL format the data as CollectedData objects
2. WHEN the MockSensorDevice implements the IDataSource interface THEN the system SHALL provide a collect_stream method that yields CollectedData
3. WHEN the MockSensorDevice is queried for source_id THEN the system SHALL return a unique identifier for the mock device
4. WHEN the MockSensorDevice generates data THEN the system SHALL include metadata with sensor_type, sensor_id, and collection_time
5. WHEN the MockSensorDevice encounters an error THEN the system SHALL yield CollectedData with status FAILED and error information

### Requirement 4

**User Story:** 作为开发人员，我希望数据处理层能够接收模拟传感器数据并计算运动方向，以便验证运动分析算法。

#### Acceptance Criteria

1. WHEN the DataProcessor receives sensor data with forward acceleration THEN the system SHALL output a "forward" motion command
2. WHEN the DataProcessor receives sensor data with backward acceleration THEN the system SHALL output a "backward" motion command
3. WHEN the DataProcessor receives sensor data with left rotation angular velocity THEN the system SHALL output a "turn_left" motion command
4. WHEN the DataProcessor receives sensor data with right rotation angular velocity THEN the system SHALL output a "turn_right" motion command
5. WHEN the DataProcessor receives sensor data below motion thresholds THEN the system SHALL output a "stationary" motion command

### Requirement 5

**User Story:** 作为开发人员，我希望能够实时观察模拟设备生成的数据和处理结果，以便调试和验证系统行为。

#### Acceptance Criteria

1. WHEN the system processes mock sensor data THEN the system SHALL log the raw sensor values including acceleration, angular velocity, and angles
2. WHEN the system calculates motion direction THEN the system SHALL log the calculated motion command and intensity
3. WHEN the system runs in demo mode THEN the system SHALL display sensor data and motion commands in a readable format
4. WHEN the system processes data THEN the system SHALL include timestamps for each data point and calculation result
5. WHEN the system encounters processing errors THEN the system SHALL log error messages with context information

### Requirement 6

**User Story:** 作为开发人员，我希望模拟设备能够支持连续数据流模式，以便模拟真实传感器的持续数据输出。

#### Acceptance Criteria

1. WHEN the MockSensorDevice is started THEN the system SHALL continuously generate data until stopped
2. WHEN the MockSensorDevice is running THEN the system SHALL allow stopping data generation
3. WHEN the MockSensorDevice is stopped THEN the system SHALL clean up resources and reset internal state
4. WHEN the MockSensorDevice generates data in stream mode THEN the system SHALL emit data at the configured interval
5. WHEN the MockSensorDevice is restarted THEN the system SHALL resume data generation from the configured initial state

### Requirement 7

**User Story:** 作为开发人员，我希望数据处理层能够使用现有的MotionDirectionCalculator，以便保持与实际传感器处理逻辑的一致性。

#### Acceptance Criteria

1. WHEN the DataProcessor is initialized THEN the system SHALL create an instance of MotionDirectionCalculator
2. WHEN the DataProcessor receives sensor data THEN the system SHALL invoke MotionDirectionCalculator.calculate_motion_direction
3. WHEN MotionDirectionCalculator returns direction information THEN the system SHALL extract the primary motion direction
4. WHEN the DataProcessor outputs motion commands THEN the system SHALL map direction strings to standardized motion command enums
5. WHEN MotionDirectionCalculator detects motion start THEN the system SHALL flag the motion command as a new motion event

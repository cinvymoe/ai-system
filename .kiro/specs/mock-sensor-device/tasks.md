# Implementation Plan

- [x] 1. Create MotionCommand data model
  - Add MotionCommand dataclass to backend/src/collectors/models.py
  - Include fields: command, intensity, angular_intensity, timestamp, is_motion_start, raw_direction, metadata
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 2. Implement MockSensorDevice class
  - Create backend/src/collectors/sensors/mock_sensor.py
  - Extend BaseSensorCollector
  - Implement IDataSource interface methods (connect, disconnect, read_sensor_data, collect_stream, get_source_id)
  - _Requirements: 1.1, 3.1, 3.2, 3.3_

- [x] 2.1 Implement motion pattern data generation
  - Create _generate_forward_data() method for forward motion pattern
  - Create _generate_backward_data() method for backward motion pattern
  - Create _generate_turn_left_data() method for left turn pattern
  - Create _generate_turn_right_data() method for right turn pattern
  - Create _generate_stationary_data() method for stationary pattern
  - Add noise generation using numpy.random.normal
  - Ensure all generated values stay within valid sensor ranges
  - _Requirements: 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2.2 Implement continuous data streaming
  - Create background thread for data generation
  - Implement timing control to emit data at configured interval
  - Add thread-safe state management with threading.Lock
  - Implement start/stop/cleanup methods
  - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 2.3 Implement data formatting and metadata
  - Format generated data as CollectedData objects
  - Include required metadata: sensor_type, sensor_id, collection_time
  - Add timestamp to each data point
  - Handle error cases with FAILED status
  - _Requirements: 3.1, 3.4, 3.5, 5.4_

- [x] 3. Create MotionDirectionProcessor class
  - Create backend/src/collectors/processors/motion_processor.py
  - Initialize MotionDirectionCalculator in __init__
  - Implement process() method to analyze sensor data
  - _Requirements: 7.1, 7.2_

- [x] 3.1 Implement motion direction analysis
  - Extract acceleration, angular_velocity, and angles from sensor data
  - Call MotionDirectionCalculator.calculate_motion_direction
  - Extract primary motion direction from calculator result
  - Map direction strings to standardized motion commands
  - Create MotionCommand object with all required fields
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 7.3, 7.4_

- [x] 3.2 Implement motion event detection
  - Check motion_start flag from MotionDirectionCalculator
  - Set is_motion_start in MotionCommand accordingly
  - Track motion state changes
  - _Requirements: 7.5_

- [x] 3.3 Add logging and error handling
  - Log raw sensor values (acceleration, angular velocity, angles)
  - Log calculated motion command and intensity
  - Handle missing or invalid sensor data fields
  - Catch and log MotionDirectionCalculator exceptions
  - Return stationary command on errors with error metadata
  - _Requirements: 5.1, 5.2, 5.5_

- [ ] 4. Create demo script
  - Create backend/src/collectors/sensors/example_mock_sensor.py
  - Demonstrate all motion patterns (forward, backward, turn_left, turn_right, stationary)
  - Display real-time sensor data and motion commands in readable format
  - Allow interactive pattern switching or sequential pattern demonstration
  - Show timing and performance metrics
  - _Requirements: 5.3_

- [ ] 5. Integration and validation
  - Verify MockSensorDevice works with existing IDataSource interface
  - Test data flow from MockSensorDevice through MotionDirectionProcessor
  - Validate all motion patterns produce expected motion commands
  - Test start/stop/restart sequences
  - Verify error handling and recovery
  - _Requirements: All_

# Design Document - Data Collector Interfaces

## Overview

本设计文档定义了数据采集模块的接口规范，该模块采用三层架构设计：数据采集层（Data Collection Layer）、数据处理层（Data Processing Layer）和数据存储层（Data Storage Layer）。

设计遵循以下核心原则：
- **依赖倒置原则**：各层依赖抽象接口而非具体实现
- **单一职责原则**：每层专注于特定功能
- **开闭原则**：通过接口扩展功能，无需修改现有代码
- **异步优先**：所有 I/O 操作支持异步执行
- **可观测性**：内置监控、日志和事件机制

## Architecture

系统采用分层架构，数据流向如下：

```
Data Source → Collection Layer → Processing Layer → Storage Layer → Storage Backend
                    ↓                    ↓                  ↓
                Metadata           Processing          Storage
                Parsing            Pipeline            Confirmation
```

### 层次职责

1. **Data Collection Layer**
   - 管理数据源注册和生命周期
   - 执行数据采集操作
   - 解析和验证元数据
   - 提供采集统计信息

2. **Data Processing Layer**
   - 管理处理函数注册
   - 构建和执行处理管道
   - 处理错误和重试逻辑
   - 提供处理统计信息

3. **Data Storage Layer**
   - 管理存储后端注册
   - 执行数据持久化操作
   - 提供数据查询接口
   - 提供存储统计信息

## Components and Interfaces


### 1. Data Collection Layer Interfaces

#### 1.1 IDataSource

数据源的抽象接口，所有具体数据源必须实现此接口。

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CollectedData:
    """采集到的原始数据及其元数据"""
    source_id: str
    timestamp: datetime
    data_format: str
    collection_method: str
    raw_data: bytes
    metadata: Dict[str, Any]

class IDataSource(ABC):
    """数据源接口"""
    
    @abstractmethod
    async def connect(self) -> None:
        """建立与数据源的连接"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开与数据源的连接"""
        pass
    
    @abstractmethod
    async def collect(self) -> CollectedData:
        """采集单次数据"""
        pass
    
    @abstractmethod
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """采集数据流"""
        pass
    
    @abstractmethod
    def get_source_id(self) -> str:
        """获取数据源唯一标识"""
        pass
```

#### 1.2 IMetadataParser

元数据解析接口，用于从采集数据中提取和验证元数据。

```python
@dataclass
class ParsedMetadata:
    """解析后的元数据"""
    schema: Dict[str, Any]
    quality_indicators: Dict[str, float]
    source_attributes: Dict[str, Any]
    is_valid: bool
    validation_errors: list[str]

class IMetadataParser(ABC):
    """元数据解析器接口"""
    
    @abstractmethod
    async def parse(self, collected_data: CollectedData) -> ParsedMetadata:
        """解析元数据"""
        pass
    
    @abstractmethod
    async def validate(self, metadata: ParsedMetadata) -> bool:
        """验证元数据完整性和正确性"""
        pass
```


#### 1.3 ICollectionManager

采集管理器接口，负责管理数据源的注册和采集任务。

```python
from enum import Enum
from typing import Optional

class CollectionStatus(Enum):
    """采集状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class CollectionTask:
    """采集任务"""
    task_id: str
    source_id: str
    status: CollectionStatus
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]

@dataclass
class CollectionStatistics:
    """采集统计信息"""
    success_count: int
    failure_count: int
    average_processing_time: float
    last_collection_time: Optional[datetime]

class ICollectionManager(ABC):
    """采集管理器接口"""
    
    @abstractmethod
    async def register_source(self, source: IDataSource, config: Dict[str, Any]) -> str:
        """注册数据源，返回源ID"""
        pass
    
    @abstractmethod
    async def unregister_source(self, source_id: str) -> None:
        """注销数据源"""
        pass
    
    @abstractmethod
    async def start_collection(self, source_id: str) -> str:
        """启动采集任务，返回任务ID"""
        pass
    
    @abstractmethod
    async def stop_collection(self, task_id: str) -> None:
        """停止采集任务"""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> CollectionStatus:
        """获取任务状态"""
        pass
    
    @abstractmethod
    async def get_statistics(self, source_id: str) -> CollectionStatistics:
        """获取采集统计信息"""
        pass
```


### 2. Data Processing Layer Interfaces

#### 2.1 IProcessor

数据处理器接口，定义单个处理步骤。

```python
@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    processed_data: Optional[Any]
    error: Optional[str]
    processing_time: float

class IProcessor(ABC):
    """数据处理器接口"""
    
    @abstractmethod
    async def process(self, data: Any) -> ProcessingResult:
        """处理数据"""
        pass
    
    @abstractmethod
    def get_processor_name(self) -> str:
        """获取处理器名称"""
        pass
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """验证输入数据"""
        pass
```

#### 2.2 IPipeline

处理管道接口，定义多个处理步骤的组合。

```python
@dataclass
class PipelineStep:
    """管道步骤"""
    step_id: str
    processor: IProcessor
    order: int

@dataclass
class PipelineResult:
    """管道执行结果"""
    success: bool
    final_data: Optional[Any]
    step_results: list[ProcessingResult]
    failed_step: Optional[str]
    total_time: float

class IPipeline(ABC):
    """处理管道接口"""
    
    @abstractmethod
    async def add_step(self, processor: IProcessor, order: int) -> str:
        """添加处理步骤，返回步骤ID"""
        pass
    
    @abstractmethod
    async def remove_step(self, step_id: str) -> None:
        """移除处理步骤"""
        pass
    
    @abstractmethod
    async def execute(self, input_data: Any) -> PipelineResult:
        """执行管道"""
        pass
    
    @abstractmethod
    def get_steps(self) -> list[PipelineStep]:
        """获取所有步骤"""
        pass
```


#### 2.3 IProcessingManager

处理管理器接口，负责管理处理器和管道。

```python
@dataclass
class ProcessingStatistics:
    """处理统计信息"""
    step_name: str
    execution_count: int
    success_count: int
    failure_count: int
    average_time: float

class IProcessingManager(ABC):
    """处理管理器接口"""
    
    @abstractmethod
    async def register_processor(self, processor: IProcessor) -> str:
        """注册处理器，返回处理器ID"""
        pass
    
    @abstractmethod
    async def unregister_processor(self, processor_id: str) -> None:
        """注销处理器"""
        pass
    
    @abstractmethod
    async def create_pipeline(self, pipeline_id: str) -> IPipeline:
        """创建处理管道"""
        pass
    
    @abstractmethod
    async def get_pipeline(self, pipeline_id: str) -> IPipeline:
        """获取处理管道"""
        pass
    
    @abstractmethod
    async def delete_pipeline(self, pipeline_id: str) -> None:
        """删除处理管道"""
        pass
    
    @abstractmethod
    async def get_statistics(self, pipeline_id: str) -> list[ProcessingStatistics]:
        """获取处理统计信息"""
        pass
```

### 3. Data Storage Layer Interfaces

#### 3.1 IStorageBackend

存储后端接口，定义数据持久化操作。

```python
@dataclass
class StorageLocation:
    """存储位置"""
    backend_id: str
    location_id: str
    path: str
    created_at: datetime

@dataclass
class QueryCriteria:
    """查询条件"""
    filters: Dict[str, Any]
    sort_by: Optional[str]
    limit: Optional[int]
    offset: Optional[int]

class IStorageBackend(ABC):
    """存储后端接口"""
    
    @abstractmethod
    async def connect(self) -> None:
        """连接到存储后端"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开存储后端连接"""
        pass
    
    @abstractmethod
    async def store(self, data: Any) -> StorageLocation:
        """存储数据，返回存储位置"""
        pass
    
    @abstractmethod
    async def query(self, criteria: QueryCriteria) -> list[Any]:
        """查询数据"""
        pass
    
    @abstractmethod
    async def delete(self, location_id: str) -> None:
        """删除数据"""
        pass
    
    @abstractmethod
    def get_backend_id(self) -> str:
        """获取后端ID"""
        pass
```


#### 3.2 IStorageManager

存储管理器接口，负责管理存储后端和存储操作。

```python
@dataclass
class StorageStatistics:
    """存储统计信息"""
    backend_id: str
    stored_count: int
    storage_usage_bytes: int
    last_storage_time: Optional[datetime]

class IStorageManager(ABC):
    """存储管理器接口"""
    
    @abstractmethod
    async def register_backend(self, backend: IStorageBackend, config: Dict[str, Any]) -> str:
        """注册存储后端，返回后端ID"""
        pass
    
    @abstractmethod
    async def unregister_backend(self, backend_id: str) -> None:
        """注销存储后端"""
        pass
    
    @abstractmethod
    async def store_data(self, backend_id: str, data: Any) -> StorageLocation:
        """存储数据到指定后端"""
        pass
    
    @abstractmethod
    async def query_data(self, backend_id: str, criteria: QueryCriteria) -> list[Any]:
        """从指定后端查询数据"""
        pass
    
    @abstractmethod
    async def get_statistics(self, backend_id: str) -> StorageStatistics:
        """获取存储统计信息"""
        pass
```

### 4. Cross-Cutting Interfaces

#### 4.1 IErrorHandler

错误处理器接口，用于处理系统错误。

```python
class ErrorType(Enum):
    """错误类型"""
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"

@dataclass
class ErrorInfo:
    """错误信息"""
    error_type: ErrorType
    timestamp: datetime
    layer_name: str
    operation: str
    message: str
    details: Dict[str, Any]
    is_critical: bool

class IErrorHandler(ABC):
    """错误处理器接口"""
    
    @abstractmethod
    async def handle_error(self, error: ErrorInfo) -> None:
        """处理错误"""
        pass
    
    @abstractmethod
    def can_handle(self, error_type: ErrorType) -> bool:
        """判断是否可以处理该类型错误"""
        pass
```


#### 4.2 IEventEmitter

事件发射器接口，用于发布系统事件。

```python
class EventType(Enum):
    """事件类型"""
    COLLECTION_START = "collection_start"
    COLLECTION_COMPLETE = "collection_complete"
    PROCESSING_START = "processing_start"
    PROCESSING_COMPLETE = "processing_complete"
    STORAGE_START = "storage_start"
    STORAGE_COMPLETE = "storage_complete"
    ERROR_OCCURRED = "error_occurred"

@dataclass
class SystemEvent:
    """系统事件"""
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]

class IEventEmitter(ABC):
    """事件发射器接口"""
    
    @abstractmethod
    async def emit(self, event: SystemEvent) -> None:
        """发射事件"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: callable) -> str:
        """订阅事件，返回订阅ID"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """取消订阅"""
        pass
```

#### 4.3 ITaskTracker

任务跟踪器接口，用于跟踪异步操作。

```python
class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: float
    result: Optional[Any]
    error: Optional[str]

class ITaskTracker(ABC):
    """任务跟踪器接口"""
    
    @abstractmethod
    async def create_task(self, task_type: str) -> str:
        """创建任务，返回任务ID"""
        pass
    
    @abstractmethod
    async def update_status(self, task_id: str, status: TaskStatus) -> None:
        """更新任务状态"""
        pass
    
    @abstractmethod
    async def update_progress(self, task_id: str, progress: float) -> None:
        """更新任务进度"""
        pass
    
    @abstractmethod
    async def get_task_info(self, task_id: str) -> TaskInfo:
        """获取任务信息"""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> None:
        """取消任务"""
        pass
```


#### 4.4 Factory Interfaces

工厂接口，用于创建各层实例。

```python
class ICollectionLayerFactory(ABC):
    """采集层工厂接口"""
    
    @abstractmethod
    def create_collection_manager(self) -> ICollectionManager:
        """创建采集管理器"""
        pass
    
    @abstractmethod
    def create_metadata_parser(self) -> IMetadataParser:
        """创建元数据解析器"""
        pass

class IProcessingLayerFactory(ABC):
    """处理层工厂接口"""
    
    @abstractmethod
    def create_processing_manager(self) -> IProcessingManager:
        """创建处理管理器"""
        pass
    
    @abstractmethod
    def create_pipeline(self) -> IPipeline:
        """创建处理管道"""
        pass

class IStorageLayerFactory(ABC):
    """存储层工厂接口"""
    
    @abstractmethod
    def create_storage_manager(self) -> IStorageManager:
        """创建存储管理器"""
        pass
```

## Data Models

### Core Data Structures

系统中的核心数据结构已在接口定义中通过 `@dataclass` 定义：

1. **CollectedData**: 采集的原始数据及元数据
2. **ParsedMetadata**: 解析后的元数据
3. **CollectionTask**: 采集任务信息
4. **CollectionStatistics**: 采集统计信息
5. **ProcessingResult**: 处理结果
6. **PipelineStep**: 管道步骤
7. **PipelineResult**: 管道执行结果
8. **ProcessingStatistics**: 处理统计信息
9. **StorageLocation**: 存储位置
10. **QueryCriteria**: 查询条件
11. **StorageStatistics**: 存储统计信息
12. **ErrorInfo**: 错误信息
13. **SystemEvent**: 系统事件
14. **TaskInfo**: 任务信息

### Data Flow

```
1. 数据采集流程:
   DataSource → collect() → CollectedData → parse() → ParsedMetadata

2. 数据处理流程:
   CollectedData → Pipeline.execute() → ProcessingResult → PipelineResult

3. 数据存储流程:
   ProcessedData → StorageBackend.store() → StorageLocation

4. 完整流程:
   DataSource → Collection → Processing → Storage → Backend
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration validation consistency

*For any* data source configuration (valid or invalid), when registering a data source, the validation result should correctly reflect whether the configuration meets all required criteria.
**Validates: Requirements 1.2**

### Property 2: Collected data completeness

*For any* data source, when data is collected, the returned CollectedData object should contain all required metadata fields: source_id, timestamp, data_format, and collection_method.
**Validates: Requirements 1.5**

### Property 3: Metadata parsing completeness

*For any* collected data, when metadata is parsed, the resulting ParsedMetadata should contain all required structured information: schema, quality_indicators, and source_attributes.
**Validates: Requirements 1.7**

### Property 4: Processing function signature validation

*For any* processing function (with valid or invalid signature), when registering the function, the validation should correctly identify whether the signature matches the required interface.
**Validates: Requirements 2.2**

### Property 5: Pipeline execution produces result

*For any* valid processing pipeline and input data, when the pipeline is executed, it should return a PipelineResult containing either processed data or error information.
**Validates: Requirements 2.4**

### Property 6: Processing error information completeness

*For any* processing pipeline with a failing step, when execution fails, the error information should include both the failed step identifier and error details.
**Validates: Requirements 2.5**

### Property 7: Storage backend configuration validation

*For any* storage backend configuration (valid or invalid), when registering a backend, the validation should correctly determine configuration validity.
**Validates: Requirements 3.2**

### Property 8: Storage confirmation contains location

*For any* data stored to a registered backend, the storage operation should return a StorageLocation containing a valid location_id.
**Validates: Requirements 3.5**

### Property 9: Async operations return task identifiers

*For any* asynchronous operation (collection, processing, or storage), when initiated, the operation should return a unique task identifier for tracking.
**Validates: Requirements 4.4**

### Property 10: Error information structure

*For any* error occurring in any layer, the returned ErrorInfo should be structured with all required fields: error_type, timestamp, layer_name, operation, message, and details.
**Validates: Requirements 5.1**

### Property 11: Error type categorization

*For any* error, the error_type field should be one of the defined categories: CONFIGURATION, CONNECTION, VALIDATION, PROCESSING, or STORAGE.
**Validates: Requirements 5.2**

### Property 12: Error context completeness

*For any* error, the ErrorInfo should include complete context information: timestamp, layer_name, and operation details.
**Validates: Requirements 5.3**

### Property 13: Critical error handler invocation

*For any* critical error, when it occurs, all registered error handlers that can handle that error type should be invoked.
**Validates: Requirements 5.5**

### Property 14: Collection statistics completeness

*For any* data source with collection history, the retrieved CollectionStatistics should contain success_count, failure_count, and average_processing_time.
**Validates: Requirements 6.1**

### Property 15: Processing statistics per step

*For any* pipeline with execution history, the retrieved processing statistics should include separate statistics for each pipeline step.
**Validates: Requirements 6.2**

### Property 16: Storage statistics completeness

*For any* storage backend with stored data, the retrieved StorageStatistics should contain stored_count and storage_usage_bytes.
**Validates: Requirements 6.3**

### Property 17: Event emission for operations

*For any* significant operation (collection start/complete, processing complete, storage complete), when the operation occurs, a corresponding SystemEvent should be emitted.
**Validates: Requirements 6.4**


## Error Handling

### Error Categories

系统定义了五种错误类型，每种类型对应特定的错误场景：

1. **CONFIGURATION**: 配置错误
   - 无效的数据源配置
   - 无效的存储后端配置
   - 无效的处理器配置

2. **CONNECTION**: 连接错误
   - 数据源连接失败
   - 存储后端连接失败
   - 网络超时

3. **VALIDATION**: 验证错误
   - 数据格式验证失败
   - 元数据验证失败
   - 处理器签名验证失败

4. **PROCESSING**: 处理错误
   - 处理步骤执行失败
   - 数据转换错误
   - 管道执行错误

5. **STORAGE**: 存储错误
   - 数据存储失败
   - 查询执行失败
   - 存储空间不足

### Error Handling Strategy

1. **错误捕获**: 每层在接口边界捕获异常并转换为 ErrorInfo
2. **错误传播**: 错误通过返回值传播，不使用异常
3. **错误处理**: 通过注册的 IErrorHandler 处理错误
4. **错误记录**: 所有错误通过 IEventEmitter 发射事件
5. **错误恢复**: 关键错误触发错误处理器进行恢复尝试

### Error Flow

```
Operation → Error Occurs → Create ErrorInfo → 
  ↓
Check if Critical → Yes → Invoke Error Handlers
  ↓                 ↓
  No              Emit Error Event
  ↓                 ↓
Return ErrorInfo ← ←
```

## Testing Strategy

### Unit Testing

单元测试将验证各个接口实现的正确性：

1. **接口实现测试**
   - 测试每个接口方法的基本功能
   - 测试边界条件和异常情况
   - 测试接口方法的返回值类型

2. **数据模型测试**
   - 测试数据类的创建和序列化
   - 测试枚举类型的有效性
   - 测试数据验证逻辑

3. **工厂模式测试**
   - 测试工厂创建的实例类型正确
   - 测试工厂创建的实例可用

### Property-Based Testing

属性测试将使用 **Hypothesis** 库验证系统的通用属性。每个属性测试将运行至少 100 次迭代。

1. **配置验证属性**
   - 生成随机配置（有效和无效）
   - 验证配置验证逻辑的一致性

2. **数据完整性属性**
   - 生成随机数据源和采集数据
   - 验证元数据字段的完整性

3. **管道执行属性**
   - 生成随机处理管道
   - 验证管道执行结果的正确性

4. **错误处理属性**
   - 触发各种错误场景
   - 验证错误信息的结构和完整性

5. **异步操作属性**
   - 生成随机异步操作
   - 验证任务跟踪的正确性

### Integration Testing

集成测试将验证各层之间的交互：

1. **端到端流程测试**
   - 测试从数据采集到存储的完整流程
   - 测试多个数据源并发采集
   - 测试复杂处理管道

2. **错误传播测试**
   - 测试错误在各层之间的传播
   - 测试错误处理器的调用链

3. **事件系统测试**
   - 测试事件的发射和订阅
   - 测试多个订阅者的通知

### Mock Strategy

为支持独立测试，系统将提供 Mock 实现：

1. **MockDataSource**: 模拟数据源，返回预定义数据
2. **MockProcessor**: 模拟处理器，执行简单转换
3. **MockStorageBackend**: 模拟存储后端，使用内存存储
4. **MockErrorHandler**: 模拟错误处理器，记录错误
5. **MockEventEmitter**: 模拟事件发射器，记录事件

每个 Mock 实现将实现对应的接口，并提供额外的测试辅助方法。

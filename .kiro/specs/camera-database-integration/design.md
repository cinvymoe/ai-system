# 设计文档

## 概述

本设计文档描述了如何为视觉安全监控系统的摄像头列表界面添加 Python 后端数据库交互功能，采用 MVVM（Model-View-ViewModel）架构模式。设计重点在于实现数据持久化、前后端通信和状态同步。

### 设计目标

1. 实现摄像头数据的持久化存储（SQLite 数据库）
2. 采用 MVVM 架构模式分离关注点
3. 建立高效的前后端 IPC 通信机制
4. 确保数据一致性和完整性
5. 支持实时状态更新和同步
6. 提供完整的 CRUD 操作接口

### 技术栈

**后端：**
- Python 3.10+
- FastAPI（Web 框架）
- SQLAlchemy（ORM）
- SQLite（数据库）
- Pydantic（数据验证）

**前端：**
- React + TypeScript
- Zustand（状态管理）
- React Query（数据获取和缓存）

**通信：**
- Electron IPC（进程间通信）
- HTTP/REST（备用方案）

## 架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Electron 应用                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    渲染进程 (React)                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │ │
│  │  │   View 层     │  │  ViewModel   │  │  Service 层     │  │ │
│  │  │  (React 组件) │◄─┤  (Zustand)   │◄─┤  (API Client)   │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              │ IPC                               │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    主进程 (Node.js)                         │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │           IPC Handler (IPC 消息路由)                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Python 后端 (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  API 路由层   │  │  Service 层   │  │   Repository 层     │  │
│  │  (FastAPI)   │─►│  (业务逻辑)   │─►│  (数据库操作)       │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                  │               │
│                                                  ▼               │
│                                       ┌─────────────────────┐   │
│                                       │   Model 层          │   │
│                                       │  (SQLAlchemy ORM)   │   │
│                                       └─────────────────────┘   │
│                                                  │               │
│                                                  ▼               │
│                                       ┌─────────────────────┐   │
│                                       │   SQLite 数据库     │   │
│                                       └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```


### MVVM 架构详解

#### Model 层（Python 后端）

**职责：**
- 定义数据结构和数据库模型
- 执行数据库 CRUD 操作
- 实现业务逻辑和数据验证
- 管理数据持久化

**组件：**
- `models/camera.py`: SQLAlchemy ORM 模型
- `repositories/camera_repository.py`: 数据访问层
- `services/camera_service.py`: 业务逻辑层
- `schemas/camera.py`: Pydantic 数据验证模型

#### ViewModel 层（React 前端）

**职责：**
- 管理 UI 状态
- 处理用户交互
- 调用后端 API
- 数据转换和格式化
- 错误处理和加载状态管理

**组件：**
- `stores/cameraStore.ts`: Zustand 状态管理
- `hooks/useCameraData.ts`: React Query 数据钩子
- `services/cameraService.ts`: API 客户端

#### View 层（React 组件）

**职责：**
- UI 渲染
- 用户交互事件绑定
- 从 ViewModel 获取数据
- 显示加载和错误状态

**组件：**
- `CameraListSettings.tsx`: 摄像头列表视图
- `AddCameraSettings.tsx`: 添加摄像头视图
- `EditCameraSettings.tsx`: 编辑摄像头视图

### 目录结构

```
project-root/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 应用入口
│   │   ├── database.py                # 数据库连接配置
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── camera.py              # SQLAlchemy 模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── camera.py              # Pydantic 模式
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── camera_repository.py   # 数据访问层
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── camera_service.py      # 业务逻辑层
│   │   └── api/
│   │       ├── __init__.py
│   │       └── cameras.py             # API 路由
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_camera_repository.py
│   │   └── test_camera_service.py
│   └── pyproject.toml
├── electron/
│   ├── main.ts                        # 主进程（添加 IPC 处理）
│   └── preload.ts                     # 预加载脚本（暴露 API）
└── src/
    ├── stores/
    │   └── cameraStore.ts             # Zustand 状态管理
    ├── services/
    │   └── cameraService.ts           # API 客户端
    ├── hooks/
    │   └── useCameraData.ts           # React Query 钩子
    └── components/
        └── settings/
            ├── CameraListSettings.tsx  # 更新为使用 ViewModel
            ├── AddCameraSettings.tsx   # 更新为使用 ViewModel
            └── EditCameraSettings.tsx  # 更新为使用 ViewModel
```


## 组件和接口

### 1. 数据库模型（Model 层）

#### SQLAlchemy ORM 模型

```python
# backend/src/models/camera.py
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    resolution = Column(String, default="1920x1080")
    fps = Column(Integer, default=30)
    brightness = Column(Integer, default=50)
    contrast = Column(Integer, default=50)
    status = Column(String, default="offline")  # 'online' | 'offline'
    direction = Column(String, nullable=False)  # 'forward' | 'backward' | 'left' | 'right' | 'idle'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Pydantic 验证模式

```python
# backend/src/schemas/camera.py
from pydantic import BaseModel, Field, validator
from typing import Literal
from datetime import datetime

class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., regex=r'^rtsp://.*')
    enabled: bool = True
    resolution: str = "1920x1080"
    fps: int = Field(default=30, ge=1, le=60)
    brightness: int = Field(default=50, ge=0, le=100)
    contrast: int = Field(default=50, ge=0, le=100)
    status: Literal["online", "offline"] = "offline"
    direction: Literal["forward", "backward", "left", "right", "idle"]
    
    @validator('resolution')
    def validate_resolution(cls, v):
        if not v or 'x' not in v:
            raise ValueError('Invalid resolution format')
        return v

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    enabled: bool | None = None
    resolution: str | None = None
    fps: int | None = Field(None, ge=1, le=60)
    brightness: int | None = Field(None, ge=0, le=100)
    contrast: int | None = Field(None, ge=0, le=100)
    status: Literal["online", "offline"] | None = None
    direction: Literal["forward", "backward", "left", "right", "idle"] | None = None

class CameraResponse(CameraBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 2. Repository 层（数据访问）

```python
# backend/src/repositories/camera_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from models.camera import Camera
from schemas.camera import CameraCreate, CameraUpdate
import uuid

class CameraRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Camera]:
        return self.db.query(Camera).all()
    
    def get_by_id(self, camera_id: str) -> Optional[Camera]:
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    def get_by_direction(self, direction: str) -> List[Camera]:
        return self.db.query(Camera).filter(Camera.direction == direction).all()
    
    def create(self, camera_data: CameraCreate) -> Camera:
        camera = Camera(
            id=str(uuid.uuid4()),
            **camera_data.dict()
        )
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def update(self, camera_id: str, camera_data: CameraUpdate) -> Optional[Camera]:
        camera = self.get_by_id(camera_id)
        if not camera:
            return None
        
        update_data = camera_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)
        
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def delete(self, camera_id: str) -> bool:
        camera = self.get_by_id(camera_id)
        if not camera:
            return False
        
        self.db.delete(camera)
        self.db.commit()
        return True
    
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        query = self.db.query(Camera).filter(Camera.name == name)
        if exclude_id:
            query = query.filter(Camera.id != exclude_id)
        return query.first() is not None
```


### 3. Service 层（业务逻辑）

```python
# backend/src/services/camera_service.py
from repositories.camera_repository import CameraRepository
from schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from typing import List
from fastapi import HTTPException

class CameraService:
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def get_all_cameras(self) -> List[CameraResponse]:
        cameras = self.repository.get_all()
        return [CameraResponse.from_orm(cam) for cam in cameras]
    
    def get_camera_by_id(self, camera_id: str) -> CameraResponse:
        camera = self.repository.get_by_id(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        return CameraResponse.from_orm(camera)
    
    def get_cameras_by_direction(self, direction: str) -> List[CameraResponse]:
        cameras = self.repository.get_by_direction(direction)
        return [CameraResponse.from_orm(cam) for cam in cameras]
    
    def create_camera(self, camera_data: CameraCreate) -> CameraResponse:
        # 检查名称是否重复
        if self.repository.exists_by_name(camera_data.name):
            raise HTTPException(status_code=400, detail="Camera name already exists")
        
        camera = self.repository.create(camera_data)
        return CameraResponse.from_orm(camera)
    
    def update_camera(self, camera_id: str, camera_data: CameraUpdate) -> CameraResponse:
        # 如果更新名称，检查是否重复
        if camera_data.name and self.repository.exists_by_name(camera_data.name, exclude_id=camera_id):
            raise HTTPException(status_code=400, detail="Camera name already exists")
        
        camera = self.repository.update(camera_id, camera_data)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return CameraResponse.from_orm(camera)
    
    def delete_camera(self, camera_id: str) -> dict:
        success = self.repository.delete(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return {"message": "Camera deleted successfully"}
    
    def update_camera_status(self, camera_id: str, status: str) -> CameraResponse:
        camera_data = CameraUpdate(status=status)
        return self.update_camera(camera_id, camera_data)
```

### 4. API 路由层

```python
# backend/src/api/cameras.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from repositories.camera_repository import CameraRepository
from services.camera_service import CameraService
from schemas.camera import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

def get_camera_service(db: Session = Depends(get_db)) -> CameraService:
    repository = CameraRepository(db)
    return CameraService(repository)

@router.get("/", response_model=List[CameraResponse])
async def get_all_cameras(service: CameraService = Depends(get_camera_service)):
    return service.get_all_cameras()

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: str, service: CameraService = Depends(get_camera_service)):
    return service.get_camera_by_id(camera_id)

@router.get("/direction/{direction}", response_model=List[CameraResponse])
async def get_cameras_by_direction(direction: str, service: CameraService = Depends(get_camera_service)):
    return service.get_cameras_by_direction(direction)

@router.post("/", response_model=CameraResponse, status_code=201)
async def create_camera(camera: CameraCreate, service: CameraService = Depends(get_camera_service)):
    return service.create_camera(camera)

@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(camera_id: str, camera: CameraUpdate, service: CameraService = Depends(get_camera_service)):
    return service.update_camera(camera_id, camera)

@router.delete("/{camera_id}")
async def delete_camera(camera_id: str, service: CameraService = Depends(get_camera_service)):
    return service.delete_camera(camera_id)

@router.patch("/{camera_id}/status")
async def update_camera_status(camera_id: str, status: str, service: CameraService = Depends(get_camera_service)):
    return service.update_camera_status(camera_id, status)
```

### 5. 数据库配置

```python
# backend/src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.camera import Base
import os

# 数据库文件路径
DATABASE_URL = "sqlite:///./vision_security.db"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


### 6. Electron IPC 通信层

#### 主进程 IPC 处理器

```typescript
// electron/main.ts (添加部分)
import { ipcMain } from 'electron';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

// 通用 API 调用函数
async function callBackendAPI(method: string, endpoint: string, data?: any) {
  try {
    const response = await axios({
      method,
      url: `${BACKEND_URL}${endpoint}`,
      data,
      timeout: 5000,
    });
    return { success: true, data: response.data };
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message,
    };
  }
}

// 摄像头相关 IPC 处理器
ipcMain.handle('camera:getAll', async () => {
  return await callBackendAPI('GET', '/api/cameras');
});

ipcMain.handle('camera:getById', async (event, cameraId: string) => {
  return await callBackendAPI('GET', `/api/cameras/${cameraId}`);
});

ipcMain.handle('camera:getByDirection', async (event, direction: string) => {
  return await callBackendAPI('GET', `/api/cameras/direction/${direction}`);
});

ipcMain.handle('camera:create', async (event, cameraData: any) => {
  return await callBackendAPI('POST', '/api/cameras', cameraData);
});

ipcMain.handle('camera:update', async (event, cameraId: string, updates: any) => {
  return await callBackendAPI('PATCH', `/api/cameras/${cameraId}`, updates);
});

ipcMain.handle('camera:delete', async (event, cameraId: string) => {
  return await callBackendAPI('DELETE', `/api/cameras/${cameraId}`);
});

ipcMain.handle('camera:updateStatus', async (event, cameraId: string, status: string) => {
  return await callBackendAPI('PATCH', `/api/cameras/${cameraId}/status`, { status });
});
```

#### 预加载脚本 API 暴露

```typescript
// electron/preload.ts (添加部分)
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('cameraAPI', {
  getAll: () => ipcRenderer.invoke('camera:getAll'),
  getById: (cameraId: string) => ipcRenderer.invoke('camera:getById', cameraId),
  getByDirection: (direction: string) => ipcRenderer.invoke('camera:getByDirection', direction),
  create: (cameraData: any) => ipcRenderer.invoke('camera:create', cameraData),
  update: (cameraId: string, updates: any) => ipcRenderer.invoke('camera:update', cameraId, updates),
  delete: (cameraId: string) => ipcRenderer.invoke('camera:delete', cameraId),
  updateStatus: (cameraId: string, status: string) => ipcRenderer.invoke('camera:updateStatus', cameraId, status),
});

// 类型定义
declare global {
  interface Window {
    cameraAPI: {
      getAll: () => Promise<any>;
      getById: (cameraId: string) => Promise<any>;
      getByDirection: (direction: string) => Promise<any>;
      create: (cameraData: any) => Promise<any>;
      update: (cameraId: string, updates: any) => Promise<any>;
      delete: (cameraId: string) => Promise<any>;
      updateStatus: (cameraId: string, status: string) => Promise<any>;
    };
  }
}
```

### 7. 前端 Service 层（API 客户端）

```typescript
// src/services/cameraService.ts
export interface Camera {
  id: string;
  name: string;
  url: string;
  enabled: boolean;
  resolution: string;
  fps: number;
  brightness: number;
  contrast: number;
  status: 'online' | 'offline';
  direction: 'forward' | 'backward' | 'left' | 'right' | 'idle';
  created_at: string;
  updated_at: string;
}

export interface CameraCreate {
  name: string;
  url: string;
  enabled?: boolean;
  resolution?: string;
  fps?: number;
  brightness?: number;
  contrast?: number;
  status?: 'online' | 'offline';
  direction: 'forward' | 'backward' | 'left' | 'right' | 'idle';
}

export interface CameraUpdate {
  name?: string;
  url?: string;
  enabled?: boolean;
  resolution?: string;
  fps?: number;
  brightness?: number;
  contrast?: number;
  status?: 'online' | 'offline';
  direction?: 'forward' | 'backward' | 'left' | 'right' | 'idle';
}

export class CameraService {
  async getAllCameras(): Promise<Camera[]> {
    const result = await window.cameraAPI.getAll();
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }

  async getCameraById(cameraId: string): Promise<Camera> {
    const result = await window.cameraAPI.getById(cameraId);
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }

  async getCamerasByDirection(direction: string): Promise<Camera[]> {
    const result = await window.cameraAPI.getByDirection(direction);
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }

  async createCamera(cameraData: CameraCreate): Promise<Camera> {
    const result = await window.cameraAPI.create(cameraData);
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }

  async updateCamera(cameraId: string, updates: CameraUpdate): Promise<Camera> {
    const result = await window.cameraAPI.update(cameraId, updates);
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }

  async deleteCamera(cameraId: string): Promise<void> {
    const result = await window.cameraAPI.delete(cameraId);
    if (!result.success) {
      throw new Error(result.error);
    }
  }

  async updateCameraStatus(cameraId: string, status: 'online' | 'offline'): Promise<Camera> {
    const result = await window.cameraAPI.updateStatus(cameraId, status);
    if (!result.success) {
      throw new Error(result.error);
    }
    return result.data;
  }
}

export const cameraService = new CameraService();
```


### 8. ViewModel 层（状态管理）

```typescript
// src/stores/cameraStore.ts
import { create } from 'zustand';
import { cameraService, Camera, CameraCreate, CameraUpdate } from '../services/cameraService';

interface CameraState {
  cameras: Camera[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchCameras: () => Promise<void>;
  fetchCamerasByDirection: (direction: string) => Promise<void>;
  addCamera: (cameraData: CameraCreate) => Promise<void>;
  updateCamera: (cameraId: string, updates: CameraUpdate) => Promise<void>;
  deleteCamera: (cameraId: string) => Promise<void>;
  toggleCameraEnabled: (cameraId: string) => Promise<void>;
  updateCameraStatus: (cameraId: string, status: 'online' | 'offline') => Promise<void>;
  clearError: () => void;
}

export const useCameraStore = create<CameraState>((set, get) => ({
  cameras: [],
  loading: false,
  error: null,

  fetchCameras: async () => {
    set({ loading: true, error: null });
    try {
      const cameras = await cameraService.getAllCameras();
      set({ cameras, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  fetchCamerasByDirection: async (direction: string) => {
    set({ loading: true, error: null });
    try {
      const cameras = await cameraService.getCamerasByDirection(direction);
      set({ cameras, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  addCamera: async (cameraData: CameraCreate) => {
    set({ loading: true, error: null });
    try {
      const newCamera = await cameraService.createCamera(cameraData);
      set(state => ({
        cameras: [...state.cameras, newCamera],
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateCamera: async (cameraId: string, updates: CameraUpdate) => {
    set({ loading: true, error: null });
    try {
      const updatedCamera = await cameraService.updateCamera(cameraId, updates);
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? updatedCamera : cam
        ),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deleteCamera: async (cameraId: string) => {
    set({ loading: true, error: null });
    try {
      await cameraService.deleteCamera(cameraId);
      set(state => ({
        cameras: state.cameras.filter(cam => cam.id !== cameraId),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  toggleCameraEnabled: async (cameraId: string) => {
    const camera = get().cameras.find(cam => cam.id === cameraId);
    if (!camera) return;
    
    await get().updateCamera(cameraId, { enabled: !camera.enabled });
  },

  updateCameraStatus: async (cameraId: string, status: 'online' | 'offline') => {
    set({ loading: true, error: null });
    try {
      const updatedCamera = await cameraService.updateCameraStatus(cameraId, status);
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? updatedCamera : cam
        ),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
```

## 数据模型

### 摄像头实体

```typescript
interface Camera {
  id: string;                    // UUID
  name: string;                  // 摄像头名称（唯一）
  url: string;                   // RTSP URL
  enabled: boolean;              // 是否启用
  resolution: string;            // 分辨率（如 "1920x1080"）
  fps: number;                   // 帧率（1-60）
  brightness: number;            // 亮度（0-100）
  contrast: number;              // 对比度（0-100）
  status: 'online' | 'offline';  // 在线状态
  direction: Direction;          // 方向
  created_at: string;            // 创建时间（ISO 8601）
  updated_at: string;            // 更新时间（ISO 8601）
}

type Direction = 'forward' | 'backward' | 'left' | 'right' | 'idle';
```

### API 响应格式

```typescript
// 成功响应
interface SuccessResponse<T> {
  success: true;
  data: T;
}

// 错误响应
interface ErrorResponse {
  success: false;
  error: string;
}

type APIResponse<T> = SuccessResponse<T> | ErrorResponse;
```

### 数据库表结构

```sql
CREATE TABLE cameras (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    resolution TEXT DEFAULT '1920x1080',
    fps INTEGER DEFAULT 30,
    brightness INTEGER DEFAULT 50,
    contrast INTEGER DEFAULT 50,
    status TEXT DEFAULT 'offline',
    direction TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cameras_direction ON cameras(direction);
CREATE INDEX idx_cameras_status ON cameras(status);
```


## 正确性属性

*属性是指在系统的所有有效执行中都应该成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在分析所有验收标准后，我们识别出以下可以合并或简化的属性：

**合并的属性：**
- 多个关于"数据验证"的标准（3.1, 4.1, 10.1-10.5）可以合并为一个综合的数据验证属性
- 多个关于"UI 同步"的标准（4.3, 5.2, 6.2）可以合并为一个 UI 状态同步属性
- 多个关于"往返一致性"的标准（3.2, 4.2）可以合并为一个 CRUD 往返属性
- 多个关于"IPC 通信"的标准（8.1, 8.2, 8.3）可以合并为一个端到端通信属性

**排除的标准：**
- 性能相关标准（2.5, 6.5, 9.2, 9.3）不适合属性测试
- 架构约束标准（7.1-7.4）无法通过自动化测试验证
- 具体配置验证（1.4, 9.5）更适合示例测试

以下是精简后的核心属性：

### 属性 1：数据验证完整性

*对于任何* 摄像头数据输入（创建或更新），系统应该验证所有必填字段存在、URL 格式正确、数值在有效范围内（brightness 和 contrast 在 0-100，fps 在 1-60），并在验证失败时返回详细的错误信息。

**验证：需求 3.1, 4.1, 10.1, 10.2, 10.3, 10.4, 10.5**

### 属性 2：创建往返一致性

*对于任何* 有效的摄像头数据，创建后立即查询应该返回相同的数据（除了系统生成的 id 和时间戳字段）。

**验证：需求 3.2, 3.3**

### 属性 3：更新往返一致性

*对于任何* 存在的摄像头和有效的更新数据，更新后立即查询应该返回更新后的数据。

**验证：需求 4.2**

### 属性 4：删除幂等性

*对于任何* 存在的摄像头，删除后查询应该返回"未找到"错误，再次删除同一摄像头也应该返回"未找到"错误。

**验证：需求 5.1**

### 属性 5：名称唯一性约束

*对于任何* 已存在的摄像头名称，尝试创建或更新另一个摄像头使用相同名称应该被拒绝并返回错误。

**验证：需求 3.5**

### 属性 6：状态切换往返

*对于任何* 摄像头，切换 enabled 状态后查询应该返回新状态，再次切换应该返回原状态。

**验证：需求 6.1**

### 属性 7：批量操作原子性

*对于任何* 摄像头集合，批量更新操作应该要么全部成功（所有摄像头都更新），要么全部失败（所有摄像头保持原状态）。

**验证：需求 6.4**

### 属性 8：错误处理一致性

*对于任何* 数据库操作失败（如连接失败、约束违反），系统应该记录错误日志并返回包含错误详情的响应，而不是崩溃或返回空响应。

**验证：需求 1.3, 3.4**

### 属性 9：数据加载完整性

*对于任何* 数据库中的摄像头集合，加载所有摄像头应该返回完整的数据，且按方向分组后每个摄像头都应该在正确的组中。

**验证：需求 2.1, 2.4**

### 属性 10：更新失败回滚

*对于任何* 摄像头更新操作，如果更新失败（如验证失败、网络错误），数据库中的数据应该保持不变，UI 状态也应该恢复到原始状态。

**验证：需求 4.4, 6.3**

### 属性 11：IPC 端到端通信

*对于任何* 前端发起的摄像头操作请求（获取、创建、更新、删除），请求应该通过 IPC 正确传递到后端，后端处理后应该通过 IPC 返回结果给前端。

**验证：需求 8.1, 8.2, 8.3**

### 属性 12：状态变化通知

*对于任何* 摄像头状态变化（status 字段从 online 变为 offline 或反之），数据库应该正确更新，且 ViewModel 应该通知 View 层更新显示。

**验证：需求 7.5, 9.1, 9.4**

### 属性 13：操作日志记录

*对于任何* 摄像头删除操作，系统应该记录包含操作时间、操作类型和目标摄像头信息的日志条目。

**验证：需求 5.5**


## 错误处理

### 1. 数据库错误

**连接失败：**
```python
try:
    db = SessionLocal()
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise HTTPException(status_code=503, detail="Database unavailable")
```

**约束违反：**
```python
try:
    db.add(camera)
    db.commit()
except IntegrityError as e:
    db.rollback()
    logger.error(f"Integrity constraint violated: {e}")
    raise HTTPException(status_code=400, detail="Camera name already exists")
```

**查询失败：**
```python
try:
    cameras = db.query(Camera).all()
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise HTTPException(status_code=500, detail="Failed to fetch cameras")
```

### 2. 数据验证错误

**Pydantic 验证：**
```python
try:
    camera_data = CameraCreate(**request_data)
except ValidationError as e:
    return {
        "success": False,
        "error": "Validation failed",
        "details": e.errors()
    }
```

**业务规则验证：**
```python
if repository.exists_by_name(camera_data.name):
    raise HTTPException(
        status_code=400,
        detail=f"Camera with name '{camera_data.name}' already exists"
    )
```

### 3. IPC 通信错误

**超时处理：**
```typescript
async function callBackendAPI(method: string, endpoint: string, data?: any) {
  try {
    const response = await axios({
      method,
      url: `${BACKEND_URL}${endpoint}`,
      data,
      timeout: 5000,
    });
    return { success: true, data: response.data };
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      return { success: false, error: 'Request timeout' };
    }
    return { success: false, error: error.message };
  }
}
```

**重试机制：**
```typescript
async function callBackendAPIWithRetry(
  method: string,
  endpoint: string,
  data?: any,
  maxRetries: number = 3
) {
  for (let i = 0; i < maxRetries; i++) {
    const result = await callBackendAPI(method, endpoint, data);
    if (result.success) {
      return result;
    }
    if (i < maxRetries - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  return { success: false, error: 'Max retries exceeded' };
}
```

### 4. 前端错误处理

**加载状态管理：**
```typescript
try {
  set({ loading: true, error: null });
  const cameras = await cameraService.getAllCameras();
  set({ cameras, loading: false });
} catch (error: any) {
  set({ error: error.message, loading: false });
}
```

**乐观更新回滚：**
```typescript
const toggleCameraEnabled = async (cameraId: string) => {
  const camera = get().cameras.find(cam => cam.id === cameraId);
  if (!camera) return;
  
  // 乐观更新
  const newEnabled = !camera.enabled;
  set(state => ({
    cameras: state.cameras.map(cam =>
      cam.id === cameraId ? { ...cam, enabled: newEnabled } : cam
    ),
  }));
  
  try {
    await cameraService.updateCamera(cameraId, { enabled: newEnabled });
  } catch (error) {
    // 回滚
    set(state => ({
      cameras: state.cameras.map(cam =>
        cam.id === cameraId ? { ...cam, enabled: camera.enabled } : cam
      ),
      error: error.message,
    }));
  }
};
```

## 测试策略

本项目采用以手动测试为主的测试策略，确保功能的实际可用性和用户体验。

### 手动测试（主要测试方式）

**测试清单：**

1. **数据库初始化测试**
   - 首次启动应用，验证数据库文件创建
   - 检查数据库表结构是否正确
   - 验证默认数据是否加载

2. **摄像头 CRUD 操作测试**
   - 添加新摄像头，验证保存成功
   - 编辑摄像头配置，验证更新生效
   - 删除摄像头，验证从列表移除
   - 查看摄像头列表，验证数据显示正确

3. **数据验证测试**
   - 尝试添加空名称的摄像头，验证被拒绝
   - 尝试添加重复名称的摄像头，验证提示错误
   - 输入无效的 URL 格式，验证提示错误
   - 输入超出范围的亮度/对比度值，验证被拒绝

4. **状态切换测试**
   - 切换摄像头启用/禁用状态，验证立即生效
   - 验证状态在重启后保持
   - 测试多个摄像头同时切换状态

5. **数据持久化测试**
   - 添加摄像头后关闭应用
   - 重新打开应用，验证数据仍然存在
   - 修改配置后重启，验证修改已保存

6. **错误处理测试**
   - 关闭后端服务，验证前端显示错误提示
   - 模拟网络延迟，验证加载状态显示
   - 尝试删除不存在的摄像头，验证错误处理

7. **UI 交互测试**
   - 验证按钮点击响应
   - 验证表单输入和验证提示
   - 验证列表滚动和筛选功能
   - 验证加载状态和错误提示显示

8. **方向分组测试**
   - 添加不同方向的摄像头
   - 验证列表按方向正确分组
   - 验证每个方向的摄像头数量统计

9. **并发操作测试**
   - 快速连续添加多个摄像头
   - 同时编辑和删除不同摄像头
   - 验证数据一致性

10. **边界条件测试**
    - 测试空数据库状态
    - 测试大量摄像头（50+）的性能
    - 测试特殊字符在名称中的处理

**测试记录：**
- 为每个测试场景记录测试结果
- 记录发现的问题和修复情况
- 维护测试通过/失败的统计

### 基础单元测试（可选）

如果需要基础的代码验证，可以添加少量单元测试：

**后端基础测试：**
- 数据库连接测试
- 模型创建和查询测试
- API 端点基本功能测试

**前端基础测试：**
- Service 层 API 调用测试
- Store 状态管理基本逻辑测试

**测试工具：**
- 后端：pytest（可选）
- 前端：Vitest（可选）

### 测试优先级

1. **高优先级：** 手动测试所有核心 CRUD 功能
2. **中优先级：** 手动测试错误处理和边界条件
3. **低优先级：** 可选的自动化单元测试


## 开发工作流

### 后端开发流程

1. **环境设置：**
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # Linux/Mac
   uv pip install -e ".[dev]"
   ```

2. **数据库初始化：**
   ```bash
   python -c "from src.database import init_db; init_db()"
   ```

3. **运行开发服务器：**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

4. **运行测试：**
   ```bash
   pytest tests/ -v
   pytest tests/ -v --hypothesis-show-statistics  # 属性测试统计
   ```

### 前端开发流程

1. **安装依赖：**
   ```bash
   npm install zustand @tanstack/react-query axios
   ```

2. **运行开发服务器：**
   ```bash
   npm run dev
   ```

3. **运行测试：**
   ```bash
   npm run test
   npm run test:ui  # Vitest UI
   ```

### 完整开发流程

1. **启动后端：**
   ```bash
   cd backend && uvicorn src.main:app --reload
   ```

2. **启动 Electron：**
   ```bash
   npm run dev
   ```

3. **测试流程：**
   - 后端单元测试 → 前端单元测试 → 集成测试 → 端到端测试

## 性能考虑

### 1. 数据库优化

**索引策略：**
```sql
CREATE INDEX idx_cameras_direction ON cameras(direction);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_enabled ON cameras(enabled);
```

**查询优化：**
- 使用 SQLAlchemy 的 lazy loading 避免 N+1 查询
- 对频繁查询的字段添加索引
- 使用数据库连接池

### 2. 前端优化

**状态管理优化：**
- 使用 Zustand 的 selector 避免不必要的重渲染
- 实现虚拟滚动处理大量摄像头列表
- 使用 React.memo 优化组件渲染

**数据获取优化：**
- 使用 React Query 的缓存机制
- 实现乐观更新提升用户体验
- 批量请求减少网络往返

### 3. 通信优化

**IPC 优化：**
- 批量操作合并为单个请求
- 使用消息队列处理高频更新
- 实现请求去抖和节流

**缓存策略：**
- 前端缓存摄像头列表数据
- 设置合理的缓存过期时间
- 实现增量更新机制

## 安全考虑

### 1. 数据验证

- 所有输入数据必须经过 Pydantic 验证
- URL 格式验证防止注入攻击
- 数值范围验证防止异常值

### 2. SQL 注入防护

- 使用 SQLAlchemy ORM 参数化查询
- 避免字符串拼接构建 SQL
- 对用户输入进行转义

### 3. IPC 安全

- 验证 IPC 消息来源
- 限制可调用的 API 端点
- 实现请求频率限制

### 4. 数据库安全

- 数据库文件权限控制
- 敏感数据加密存储
- 定期备份数据库

## 部署考虑

### 1. 数据库迁移

**初始化脚本：**
```python
# backend/src/init_db.py
from database import init_db, engine
from models.camera import Base

def initialize_database():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

if __name__ == "__main__":
    initialize_database()
```

**迁移策略：**
- 使用 Alembic 管理数据库版本
- 提供升级和回滚脚本
- 在应用启动时自动检查数据库版本

### 2. 配置管理

**环境变量：**
```python
# backend/src/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./vision_security.db"
    log_level: str = "INFO"
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 日志配置

```python
# backend/src/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("vision_security")
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### 4. 打包配置

**electron-builder 配置更新：**
```yaml
# electron-builder.yml
extraResources:
  - backend/**/*
  - "!backend/.venv"
  - "!backend/**/__pycache__"
  - "!backend/tests"
  - backend/vision_security.db  # 包含初始数据库
```

## 未来扩展

### 1. 实时视频流

- 集成 WebRTC 或 HLS 流媒体
- 实现视频流的缓冲和优化
- 支持多路视频同时播放

### 2. 高级查询

- 实现全文搜索功能
- 支持复杂的过滤条件
- 添加排序和分页

### 3. 数据同步

- 实现多客户端数据同步
- 使用 WebSocket 推送实时更新
- 处理冲突解决

### 4. 数据分析

- 摄像头使用统计
- 故障率分析
- 性能监控仪表板

### 5. 备份和恢复

- 自动备份数据库
- 导出/导入配置
- 灾难恢复方案

## 技术债务和改进

### 当前限制

1. **SQLite 限制：**
   - 不支持真正的并发写入
   - 适合单用户场景
   - 未来可迁移到 PostgreSQL

2. **轮询机制：**
   - 当前使用轮询获取状态更新
   - 未来可改为 WebSocket 推送

3. **缓存策略：**
   - 当前缓存策略较简单
   - 未来可实现更智能的缓存失效

### 改进计划

1. **短期（1-2 周）：**
   - 完善错误处理
   - 添加更多单元测试
   - 优化 UI 响应速度

2. **中期（1-2 月）：**
   - 实现 WebSocket 推送
   - 添加数据导出功能
   - 性能优化和监控

3. **长期（3-6 月）：**
   - 迁移到 PostgreSQL
   - 实现多用户支持
   - 添加高级分析功能

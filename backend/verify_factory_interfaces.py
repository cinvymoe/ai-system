#!/usr/bin/env python
"""Verification script for factory interfaces."""

import sys
import inspect
from abc import ABC

sys.path.insert(0, 'src')

from collectors.interfaces import (
    ICollectionLayerFactory,
    IProcessingLayerFactory,
    IStorageLayerFactory,
    ICollectionManager,
    IMetadataParser,
    IProcessingManager,
    IPipeline,
    IStorageManager,
)


def verify_factory_interface(factory_class, expected_methods):
    """Verify that a factory interface has the expected methods."""
    print(f"\n验证 {factory_class.__name__}...")
    
    # Check if it's an ABC
    if not issubclass(factory_class, ABC):
        print(f"  ✗ {factory_class.__name__} 不是抽象基类")
        return False
    
    print(f"  ✓ 是抽象基类")
    
    # Check methods
    for method_name, return_type in expected_methods.items():
        if not hasattr(factory_class, method_name):
            print(f"  ✗ 缺少方法: {method_name}")
            return False
        
        method = getattr(factory_class, method_name)
        if not callable(method):
            print(f"  ✗ {method_name} 不是可调用的")
            return False
        
        # Check if it's abstract
        if not hasattr(method, '__isabstractmethod__') or not method.__isabstractmethod__:
            print(f"  ✗ {method_name} 不是抽象方法")
            return False
        
        print(f"  ✓ 方法 {method_name} 存在且为抽象方法")
    
    return True


def main():
    """Main verification function."""
    print("=" * 60)
    print("工厂接口验证")
    print("=" * 60)
    
    all_passed = True
    
    # Verify ICollectionLayerFactory
    all_passed &= verify_factory_interface(
        ICollectionLayerFactory,
        {
            'create_collection_manager': ICollectionManager,
            'create_metadata_parser': IMetadataParser,
        }
    )
    
    # Verify IProcessingLayerFactory
    all_passed &= verify_factory_interface(
        IProcessingLayerFactory,
        {
            'create_processing_manager': IProcessingManager,
            'create_pipeline': IPipeline,
        }
    )
    
    # Verify IStorageLayerFactory
    all_passed &= verify_factory_interface(
        IStorageLayerFactory,
        {
            'create_storage_manager': IStorageManager,
        }
    )
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有工厂接口验证通过！")
        return 0
    else:
        print("❌ 部分工厂接口验证失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

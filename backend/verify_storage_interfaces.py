"""Verification script for storage layer interfaces implementation."""

import inspect
from src.collectors import (
    IStorageBackend,
    IStorageManager,
    StorageLocation,
    QueryCriteria,
    StorageStatistics,
)


def verify_interface_methods(interface_class, expected_methods):
    """Verify that an interface has all expected methods."""
    actual_methods = {
        name: method
        for name, method in inspect.getmembers(interface_class, predicate=inspect.isfunction)
        if not name.startswith('_')
    }
    
    missing_methods = set(expected_methods.keys()) - set(actual_methods.keys())
    extra_methods = set(actual_methods.keys()) - set(expected_methods.keys())
    
    return missing_methods, extra_methods, actual_methods


def verify_dataclass_fields(dataclass, expected_fields):
    """Verify that a dataclass has all expected fields."""
    actual_fields = {field.name: field.type for field in dataclass.__dataclass_fields__.values()}
    
    missing_fields = set(expected_fields.keys()) - set(actual_fields.keys())
    extra_fields = set(actual_fields.keys()) - set(expected_fields.keys())
    
    return missing_fields, extra_fields, actual_fields


def main():
    print("=" * 70)
    print("Storage Layer Interfaces Verification")
    print("=" * 70)
    
    # Verify IStorageBackend
    print("\n1. Verifying IStorageBackend interface...")
    expected_backend_methods = {
        'connect': 'async',
        'disconnect': 'async',
        'store': 'async',
        'query': 'async',
        'delete': 'async',
        'get_backend_id': 'sync',
    }
    
    missing, extra, actual = verify_interface_methods(IStorageBackend, expected_backend_methods)
    
    if not missing and not extra:
        print("   ✓ IStorageBackend has all required methods")
    else:
        if missing:
            print(f"   ✗ Missing methods: {missing}")
        if extra:
            print(f"   ✗ Extra methods: {extra}")
    
    # Verify IStorageManager
    print("\n2. Verifying IStorageManager interface...")
    expected_manager_methods = {
        'register_backend': 'async',
        'unregister_backend': 'async',
        'store_data': 'async',
        'query_data': 'async',
        'get_statistics': 'async',
    }
    
    missing, extra, actual = verify_interface_methods(IStorageManager, expected_manager_methods)
    
    if not missing and not extra:
        print("   ✓ IStorageManager has all required methods")
    else:
        if missing:
            print(f"   ✗ Missing methods: {missing}")
        if extra:
            print(f"   ✗ Extra methods: {extra}")
    
    # Verify StorageLocation dataclass
    print("\n3. Verifying StorageLocation dataclass...")
    expected_location_fields = {
        'backend_id': str,
        'location_id': str,
        'path': str,
        'created_at': 'datetime',
    }
    
    missing, extra, actual = verify_dataclass_fields(StorageLocation, expected_location_fields)
    
    if not missing and not extra:
        print("   ✓ StorageLocation has all required fields")
    else:
        if missing:
            print(f"   ✗ Missing fields: {missing}")
        if extra:
            print(f"   ✗ Extra fields: {extra}")
    
    # Verify QueryCriteria dataclass
    print("\n4. Verifying QueryCriteria dataclass...")
    expected_criteria_fields = {
        'filters': dict,
        'sort_by': 'Optional[str]',
        'limit': 'Optional[int]',
        'offset': 'Optional[int]',
    }
    
    missing, extra, actual = verify_dataclass_fields(QueryCriteria, expected_criteria_fields)
    
    if not missing and not extra:
        print("   ✓ QueryCriteria has all required fields")
    else:
        if missing:
            print(f"   ✗ Missing fields: {missing}")
        if extra:
            print(f"   ✗ Extra fields: {extra}")
    
    # Verify StorageStatistics dataclass
    print("\n5. Verifying StorageStatistics dataclass...")
    expected_stats_fields = {
        'backend_id': str,
        'stored_count': int,
        'storage_usage_bytes': int,
        'last_storage_time': 'Optional[datetime]',
    }
    
    missing, extra, actual = verify_dataclass_fields(StorageStatistics, expected_stats_fields)
    
    if not missing and not extra:
        print("   ✓ StorageStatistics has all required fields")
    else:
        if missing:
            print(f"   ✗ Missing fields: {missing}")
        if extra:
            print(f"   ✗ Extra fields: {extra}")
    
    print("\n" + "=" * 70)
    print("Verification Complete!")
    print("=" * 70)
    
    # Verify that interfaces are abstract
    print("\n6. Verifying interfaces are abstract...")
    try:
        IStorageBackend()
        print("   ✗ IStorageBackend should not be instantiable")
    except TypeError:
        print("   ✓ IStorageBackend is properly abstract")
    
    try:
        IStorageManager()
        print("   ✗ IStorageManager should not be instantiable")
    except TypeError:
        print("   ✓ IStorageManager is properly abstract")
    
    print("\n" + "=" * 70)
    print("All verifications passed! ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()

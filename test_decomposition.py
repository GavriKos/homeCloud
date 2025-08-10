"""
Test script to verify the decomposed application structure works correctly.
"""

import sys
import os

def test_imports():
    """
    Test that all modules can be imported without errors.
    
    Returns:
        bool: True if all imports succeed, False otherwise
    """
    try:
        # Test helper imports
        from helpers import get_locale, _, calculate_md5, SUPPORTED_LANGS, DEFAULT_LANG
        print("✓ helpers module imported successfully")
        
        # Test CLI imports
        from cli import register_cli_commands
        print("✓ cli module imported successfully")
        
        # Test guest blueprint imports
        from guest import guest_bp
        print("✓ guest module imported successfully")
        
        # Test admin blueprint imports
        from admin import admin_bp
        print("✓ admin module imported successfully")
        
        # Test main app creation
        from app import create_app
        print("✓ app module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_app_creation():
    """
    Test that the Flask application can be created successfully.
    
    Returns:
        bool: True if app creation succeeds, False otherwise
    """
    try:
        from app import create_app
        app = create_app('default')
        
        if app is None:
            print("✗ App creation returned None")
            return False
            
        print("✓ Flask application created successfully")
        
        # Test that blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        if 'admin' in blueprint_names:
            print("✓ Admin blueprint registered")
        else:
            print("✗ Admin blueprint not registered")
            return False
            
        if 'guest' in blueprint_names:
            print("✓ Guest blueprint registered")
        else:
            print("✗ Guest blueprint not registered")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False


def test_helper_functions():
    """
    Test that helper functions work correctly.
    
    Returns:
        bool: True if helper functions work, False otherwise
    """
    try:
        from helpers import calculate_md5, format_size, get_folder_size
        
        # Test MD5 calculation
        test_path = "test/path"
        md5_result = calculate_md5(test_path)
        if len(md5_result) == 32:  # MD5 hash should be 32 characters
            print("✓ MD5 calculation works")
        else:
            print("✗ MD5 calculation failed")
            return False
            
        # Test size formatting
        size_result = format_size(1024)
        if "KB" in size_result:
            print("✓ Size formatting works")
        else:
            print("✗ Size formatting failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Helper function error: {e}")
        return False


def main():
    """
    Run all tests and report results.
    """
    print("Testing decomposed homeCloud application...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Creation Tests", test_app_creation),
        ("Helper Function Tests", test_helper_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Decomposition successful.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

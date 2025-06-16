#!/usr/bin/env python3
"""
Test Runner for Orientor School Programs Integration
Runs comprehensive tests and provides detailed feedback
"""

import subprocess
import sys
import os
from pathlib import Path

def install_test_dependencies():
    """Install required test dependencies"""
    dependencies = [
        "pytest",
        "pytest-asyncio", 
        "httpx",
        "fastapi[all]",
        "sqlalchemy",
        "pydantic"
    ]
    
    print("📦 Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")

def run_unit_tests():
    """Run unit tests with detailed output"""
    print("\n🧪 Running Unit Tests...")
    
    test_command = [
        sys.executable, "-m", "pytest", 
        "test_orientor_integration.py",
        "-v",
        "--tb=short",
        "--color=yes",
        "-x"  # Stop on first failure
    ]
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ Tests failed with return code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest first.")
        return False

def check_code_quality():
    """Run basic code quality checks"""
    print("\n🔍 Running Code Quality Checks...")
    
    # Check if files exist
    files_to_check = [
        "orientor_backend_integration.py",
        "test_orientor_integration.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Basic syntax check
    for file in files_to_check:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"✅ {file} syntax OK")
        except SyntaxError as e:
            print(f"❌ Syntax error in {file}: {e}")
            return False
    
    return True

def run_integration_validation():
    """Run integration validation checks"""
    print("\n🔗 Running Integration Validation...")
    
    try:
        # Import and validate the integration module
        sys.path.append(os.getcwd())
        
        # Test basic imports
        from orientor_backend_integration import (
            OrientorEducationService,
            PersonalizedProgramResponse, 
            CareerEducationPathway,
            EducationDashboardResponse
        )
        print("✅ Core imports successful")
        
        # Test model validation
        test_response = PersonalizedProgramResponse(
            id="test-123",
            title="Test Program",
            institution_name="Test Institution", 
            institution_city="Test City",
            program_type="technical",
            level="diploma"
        )
        print("✅ Pydantic model validation works")
        
        # Test database integration types
        from orientor_backend_integration import INTEGRATION_MIGRATION_SQL
        assert len(INTEGRATION_MIGRATION_SQL) > 0
        print("✅ Database migration SQL prepared")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration validation error: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Orientor School Programs Integration - Test Suite")
    print("=" * 60)
    
    # Step 1: Install dependencies
    install_test_dependencies()
    
    # Step 2: Check code quality
    if not check_code_quality():
        print("\n❌ Code quality checks failed. Please fix issues before proceeding.")
        return False
    
    # Step 3: Run integration validation
    if not run_integration_validation():
        print("\n❌ Integration validation failed. Please check integration code.")
        return False
    
    # Step 4: Run unit tests
    tests_passed = run_unit_tests()
    
    # Summary
    print("\n" + "=" * 60)
    if tests_passed:
        print("🎉 All tests passed! Integration is ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Review test coverage")
        print("2. Run integration with actual Orientor database")
        print("3. Test with real user data")
        print("4. Deploy to staging environment")
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        print("\n🔧 Debugging Tips:")
        print("1. Check error messages above")
        print("2. Verify all dependencies are installed")
        print("3. Ensure database models match expectations")
        print("4. Test individual components in isolation")
    
    return tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import pytest as pt
import os
import glob

@pt.hookimpl
def pytest_sessionstart() -> None:
    files = glob.glob("tests/components/*.test")
    for file in files:
        os.remove(file)
@pt.hookimpl
def pytest_sessionfinish() -> None:
    files = glob.glob("tests/components/*.test")
    for file in files:
        os.remove(file)

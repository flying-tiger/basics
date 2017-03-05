import sys
import os

# Define some useful constants
test_root    = os.path.dirname(__file__)
package_root = os.path.dirname(test_root)

# Make sure package is on sys.path
sys.path.append(package_root)

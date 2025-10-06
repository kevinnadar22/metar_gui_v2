import os

# --- Auto-detect environment ---
RUNNING_IN_DOCKER = os.path.exists('/.dockerenv')

# --- Base Data Directory ---
if RUNNING_IN_DOCKER:
    # Inside Docker container
    DOCKER_VOLUME_MOUNT_POINT = '/app/data'
else:
    # Local "Docker-like" test environment
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCKER_VOLUME_MOUNT_POINT = os.path.join(PROJECT_ROOT, 'data')

# Normalize path for cross-platform (Windows/Linux)
DOCKER_VOLUME_MOUNT_POINT = os.path.normpath(DOCKER_VOLUME_MOUNT_POINT)

# --- Application-specific directories ---
METAR_DATA_DIR = os.path.join(DOCKER_VOLUME_MOUNT_POINT, 'metar_data')
UPPER_AIR_DATA_DIR = os.path.join(DOCKER_VOLUME_MOUNT_POINT, 'upper_air_data')
AD_WARN_DIR = os.path.join(DOCKER_VOLUME_MOUNT_POINT, 'ad_warn_data')

def initialize_data_directories():
    """Creates persistent directories under /data or local ./data."""
    print(f"📁 Initializing data directories at: {DOCKER_VOLUME_MOUNT_POINT}")
    os.makedirs(METAR_DATA_DIR, exist_ok=True)
    os.makedirs(UPPER_AIR_DATA_DIR, exist_ok=True)
    os.makedirs(AD_WARN_DIR, exist_ok=True)

    print("✅ Data directories created or verified.")

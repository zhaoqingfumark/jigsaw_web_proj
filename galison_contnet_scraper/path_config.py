#!/usr/bin/env python
"""
Path Configuration Module
Centralized management of all project paths to avoid duplication
"""

import os

# Project root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Base directories
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')

# Crawler output directories
IMAGES_DIR = os.path.join(OUTPUTS_DIR, 'images')
INFOS_DIR = os.path.join(OUTPUTS_DIR, 'infos')

# Relative paths for Scrapy settings
RELATIVE_IMAGES_PATH = '../outputs/images'
RELATIVE_INFOS_PATH = '../outputs/infos'

# Ensure necessary directories exist
def ensure_dirs_exist():
    """Ensure all necessary directories exist"""
    for directory in [LOGS_DIR, OUTPUTS_DIR, IMAGES_DIR, INFOS_DIR]:
        os.makedirs(directory, exist_ok=True)

# Initialize directories automatically
ensure_dirs_exist()

# Path getter functions
def get_root_dir():
    """Get project root directory path"""
    return ROOT_DIR

def get_logs_dir():
    """Get logs directory path"""
    return LOGS_DIR

def get_outputs_dir():
    """Get outputs directory path"""
    return OUTPUTS_DIR

def get_scripts_dir():
    """Get scripts directory path"""
    return SCRIPTS_DIR

def get_images_dir():
    """Get images directory path"""
    return IMAGES_DIR

def get_infos_dir():
    """Get product info directory path"""
    return INFOS_DIR

# Relative path getters
def get_relative_images_path():
    """Get relative path to images directory (for Scrapy settings)"""
    return RELATIVE_IMAGES_PATH

def get_relative_infos_path():
    """Get relative path to product info directory (for Scrapy settings)"""
    return RELATIVE_INFOS_PATH
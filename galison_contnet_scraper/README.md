# Galison Web Scraper

A web crawler tool for scraping puzzle product information from the Galison website. This project uses the Scrapy framework and supports both single URL crawling and batch URL crawling from CSV files.

## Features

- Single product page crawling
- Batch URL crawling from CSV files
- Automatic product image downloading and saving
- Optimized path management with automatic directory creation
- Detailed logging
- Unified command line interface

## Directory Structure

```
galison_web_scraper/
├── galison_scraper/         # Scrapy crawler project
│   ├── spiders/             # Spider definitions
│   ├── items.py             # Item definitions
│   ├── pipelines.py         # Data processing pipelines
│   ├── settings.py          # Scrapy settings
│   └── utils.py             # Utility functions
├── scripts/                 # Command line scripts
│   ├── batch_crawl.py       # Batch crawling script
│   ├── crawl.py             # Single URL crawling script
│   └── crawler_utils.py     # Shared utility functions
├── logs/                    # Log output directory
├── outputs/                 # Data output directory
│   ├── images/              # Product image storage directory
│   └── infos/               # Product info storage directory
├── path_config.py           # Path configuration module
├── run.py                   # Unified execution entry point
└── scrapy.cfg               # Scrapy configuration file
```

## Usage

### Installation

```bash
pip install scrapy
```

### Single URL Crawling

```bash
# Using the unified entry point
python run.py crawl [URL]

# Or directly using the script
python scripts/crawl.py [URL]
```

### Batch Crawling from CSV

The CSV file should have product URLs in the second column:

```bash
# Using the unified entry point
python run.py batch products.csv [--delay 0]

# Or directly using the script
python scripts/batch_crawl.py products.csv [--delay 0]
```

Parameters:
- `--delay`: Delay time between requests (seconds), default is 0

## Optimization Details

1. **Path Management Optimization**
   - Created a centralized path configuration module
   - Unified management of all paths to avoid hardcoding
   - Automatic creation of necessary directories

2. **Code Structure Optimization**
   - Fixed module import methods to avoid circular imports
   - Unified use of relative paths for better portability
   - Streamlined redundant code

3. **Batch Processing Improvements**
   - Changed default delay time to 0 for better efficiency
   - Only add delay when needed (when delay > 0)
   - Failed URL saving uses absolute paths to avoid errors

## Output Description

1. **Product Information**
   - Output to `outputs/infos/` directory
   - File naming format: `{product_number}_{product_name}.json`

2. **Product Images**
   - Output to `outputs/images/{product_number}_{product_name}/` directory
   - Each product's images are stored in a separate subdirectory

3. **Log Files**
   - Output to `logs/crawler.log`
   - Also displayed on the console

4. **Failure Records**
   - Failed URLs from batch crawling are saved to `failed_urls.txt` in the root directory

## Notes

1. Please respect the website's robots.txt rules
2. Set appropriate delay if needed to avoid putting too much pressure on the target website
3. Ensure correct directory structure to avoid path errors
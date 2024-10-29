#!/bin/bash

# Set the base directory for the Gutenberg collection
BASE_DIR="/home/ubuntu/Desktop/gutenberg"

# Subdirectories for plain text and HTML files
TXT_DIR="${BASE_DIR}/plain_text"
HTML_DIR="${BASE_DIR}/html"

# Create the directory structure if it doesn't already exist, with error handling
echo "Creating directory structure for eBooks..."
if mkdir -p "${BASE_DIR}" "${TXT_DIR}" "${HTML_DIR}"; then
    echo "Directories created successfully."
else
    echo "Failed to create directories. Check permissions." >&2
    exit 1
fi

# Verify directories were created
if [[ -d "${TXT_DIR}" && -d "${HTML_DIR}" ]]; then
    echo "Directories confirmed created."
else
    echo "Directory creation failed." >&2
    exit 1
fi

echo "Starting Project Gutenberg download with rsync (only eBooks in plain text and HTML)..."

# Run rsync to download only .txt and .html files
rsync -avz --info=progress2 --delete \
    --include="*/" --include="*.txt" --include="*.html" --exclude="*" \
    ftp@ftp.ibiblio.org::gutenberg "${BASE_DIR}" || { 
        echo "rsync failed. Check connection or permissions."; 
        exit 1; 
    }

echo "Download complete. Organizing files by format..."

# Check if any .txt or .html files were downloaded
if [[ -z "$(find "${BASE_DIR}" -type f -name "*.txt" -o -name "*.html")" ]]; then
    echo "No .txt or .html files downloaded. Please check the rsync source or network connection." >&2
    exit 1
fi

# Move plain text files to the text directory
if find "${BASE_DIR}" -type f -name "*.txt" -exec mv {} "${TXT_DIR}" \;; then
    echo "Text files moved to ${TXT_DIR}"
else
    echo "No text files found to move." >&2
fi

# Move HTML files to the HTML directory
if find "${BASE_DIR}" -type f -name "*.html" -exec mv {} "${HTML_DIR}" \;; then
    echo "HTML files moved to ${HTML_DIR}"
else
    echo "No HTML files found to move." >&2
fi

echo "Organization complete. Project Gutenberg files are organized in:"
echo "  - Text files: ${TXT_DIR}"
echo "  - HTML files: ${HTML_DIR}"

echo "Data acquisition and organization complete!"

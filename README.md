# Vortex

A lightning-fast, zero-cloud CLI utility that cleans your Windows directories by parsing file contents and visual data, automatically destroying clones and auto-generating intelligently named folder structures.

## Overview

Vortex uses state-of-the-art embedding models to intelligently group your files. Whether you have text documents, code, PDFs, or images, it semantically analyzes their content entirely locally. Your data never leaves your machine.

## Features

### 1. Intelligent Deduplication
- **Directory Traversal**: Recursively scans and resolves target directories.
- **SHA-256 Hashing**: Efficiently identifies exact clones, even for extremely large files, using chunked reading.
- **Statistics Gathering**: Analyzes storage before acting.

### 2. Semantic Clustering
- **Multi-format Extraction**:
  - Text-based (`.txt`, `.md`, `.csv`, `.json`, `.py`, `.js`, `.html`)
  - Documents (`.pdf` via PyMuPDF)
  - Visual (`.png`, `.jpg`, `.jpeg` via Tesseract OCR)
- **Local Embeddings Generation**:
  - Text embeddings via `BAAI/bge-small-en-v1.5` (`fastembed`).
  - Image embeddings via `Qdrant/clip-ViT-B-32-vision` (`fastembed`).
- **Vector Database**: Automatically manages semantic indexes in a local Qdrant database.
- **DBSCAN Clustering**: Groups files based on semantic proximity (Implementation in progress).

### 3. Human in the Loop (HITL)
Vortex will provide a safety mechanism to verify the clustered structures and directory names before finalizing changes to your filesystem (Implementation in progress).

## Requirements

- **Python**: `>=3.12`
- **Dependencies**:
  - `fastembed`
  - `pymupdf`
  - `qdrant-client`
  - `scikit-learn`
  - `pytesseract`
  - `pillow`
- **External Tools**:
  - **Tesseract OCR**: Required for image text extraction. Must be installed and accessible via your system's PATH.

## Installation

1. Clone the repository.
2. Install dependencies using `uv` (recommended) or `pip`:
   ```bash
   uv sync
   ```
   *(Ensure Tesseract is installed separately on your Windows machine).*

## Usage

*Command-line interface instructions coming soon as the main entry point is finalized.*

## Architecture / Pipeline

1. **Phase 1: Deduplication (`src/1dedup`)** - Scan the target directory and remove exact binary copies.
2. **Phase 2: Clustering (`src/2clustering`)** - Generate vector embeddings for remaining files and group them into logical folders using density-based clustering.
3. **Phase 3: HITL (`src/3hitl`)** - Provide an interactive review phase before auto-generating intelligently named directory structures.

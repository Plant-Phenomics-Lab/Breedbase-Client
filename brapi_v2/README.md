# BrAPI v2 Pydantic Models Generation Guide

Note: This is for regenerating the json schemas and pydnatic models. In normal operations, this should not be required. 

This guide explains how to generate Pydantic v2 models from the official BrAPI specification.

## Prerequisites

### 1. Install Java 21 (required for Gradle)

```bash
# Ubuntu/Debian/WSL
sudo apt update
sudo apt install -y openjdk-21-jdk

# Verify installation
java -version
```

### 2. Install Python Dependencies

Create a `requirements.txt`:

```txt
# requirements.txt
pydantic>=2.0
datamodel-code-generator[http]>=0.25.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Generation Steps

### Step 1: Clone the BrAPI Repository

```bash
cd /path/to/your/workspace
git clone https://github.com/plantbreeding/BrAPI.git
cd BrAPI
```

### Step 2: Clean the Generated Folder

Remove any previously generated files to ensure a fresh build:

```bash
rm -rf Specification/Generated/*
```

### Step 3: Generate OpenAPI Specification

Use Gradle to generate the OpenAPI JSON from BrAPI JSON schemas:

```bash
cd generator
./gradlew generateOpenAPI
```

This creates `Specification/Generated/brapi_openapi.json` or `brapi_generated.json`.

### Step 4: Generate Pydantic v2 Models

Use `datamodel-codegen` to convert the OpenAPI spec to Pydantic models:

```bash
# Navigate back to project root
cd ..

# Generate models
datamodel-codegen \
  --input Specification/Generated/brapi_generated.json \
  --output model.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.11 \
  --use-annotated \
  --use-standard-collections \
  --collapse-root-models
```

### Step 5: Copy Generated Models to Your Project

```bash
# Copy the generated model file to your project
cp Specification/Generated/brapi_generated.json /path/to/your/project/client/brapi_v2_dev/
cp model.py /path/to/your/project/client/brapi_v2_dev/
```

## Verification

Test that the models import correctly:

```python
from client.brapi_v2_dev.model import Trial, Germplasm, Study

# Should print successfully
print("✓ Models imported successfully!")
```

## Troubleshooting

### Issue: `datamodel-codegen: command not found`

Make sure you've installed the package:
```bash
pip install 'datamodel-code-generator[http]'
```

### Issue: `Java version X required, but Y found`

The BrAPI schema generator requires Java 21 or newer. Upgrade Java:
```bash
sudo apt install -y openjdk-21-jdk
```

### Issue: Pydantic v1 models generated instead of v2

Ensure you're using the `--output-model-type pydantic_v2.BaseModel` flag explicitly.

## Generated Files

- `brapi_generated.json` - The OpenAPI 3.0 specification (522KB)
- `model.py` - Pydantic v2 models (~65KB, 379 schemas)

## Notes

- The models are auto-generated from the official BrAPI specification
- All 379 BrAPI schemas are included (Core, Phenotyping, Genotyping, Germplasm)
- Models use Pydantic v2's `RootModel` instead of deprecated `__root__`
- Field descriptions from the BrAPI spec are preserved in the models
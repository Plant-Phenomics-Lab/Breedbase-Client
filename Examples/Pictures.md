# BrAPI Picture Operations Examples

## Getting Image Search Parameters

Before searching or downloading images, check what search filters are available:

**Tool Call:**

```json
get_image_search_parameters()
```

**Response:**

```json
{
  "service": "search/images",
  "valid_parameters": {
    "imageDbIds": {
      "type": "array",
      "description": "A list of image Ids to search for",
      "example": ["564b64a6", "0d122d1d"]
    } // Other Services
  },
  "description": "Use these parameters with download_images()"
}
```

**Key Search Capabilities:**
- Filter by observation units or observations
- Search by descriptive tags/ontology terms
- Filter by timestamp range
- Filter by file size, dimensions, or format
- Search by file name or image ID

---

## Downloading Images

### Example 1: Download First 10 Images

**Tool Call:**

```json
{
  "max_images": 10
}
```

**Response:**

```json
{
  "success": true,
  "output_directory": "C:\\Users\\yujer\\L_Documents\\Current_Classes\\Breedbase-Client-refactor\\cache\\sweetpotatobase\\downloads\\20260105_090834",
  "images_downloaded": 10,
  "images_failed": 0,
  "total_found": 10,
  "metadata_csv": "C:\\Users\\yujer\\L_Documents\\Current_Classes\\Breedbase-Client-refactor\\cache\\sweetpotatobase\\downloads\\20260105_090834\\images_metadata.csv",
  "downloaded_images": [
    {
      "image_id": "2425",
      "image_name": "Apom-raw image.jpg",
      "local_path": "C:\\Users\\yujer\\...\\Apom-raw image.jpg",
      "url": "https://sweetpotatobase.org//data/images/image_files/61/39/2a/05/d1721215b176e531195a94d8/medium.jpg"
    },
    {
      "image_id": "2426",
      "image_name": "purple.JPG",
      "local_path": "C:\\Users\\yujer\\...\\purple.JPG",
      "url": "https://sweetpotatobase.org//data/images/image_files/71/9e/1e/00/d5a455017631ad657d5e2a79/medium.jpg"
    } // Other Images
  ]
}
```
**Downloaded Images:**
- 10 images successfully downloaded
- Saved to timestamped directory
- Metadata CSV generated with all image details
- Mix of variety photos (Apom, purple, kuffuor, nane) and reference images (RTSHP.png, LeafLobeNumber.png)

---

### Example 2: Download Images with Search Filter (Height ≥ 300px)

**Tool Call:**

```json
{
  "max_images": 10,
  "search_params": {
    "imageHeightMin": 300
  }
}
```

**Response:**

```json
{
  "success": true,
  "output_directory": "C:\\Users\\yujer\\...\\cache\\sweetpotatobase\\downloads\\20260105_094708",
  "images_downloaded": 4,
  "images_failed": 0,
  "total_found": 4,
  "metadata_csv": "C:\\Users\\yujer\\...\\20260105_094708\\images_metadata.csv",
  "downloaded_images": [
    {
      "image_id": "2430",
      "image_name": "2430.jpg",
      "local_path": "C:\\Users\\yujer\\...\\2430.jpg",
      "url": "https://sweetpotatobase.org//data/images/image_files/.../medium.jpg"
    },
    {
      "image_id": "2431",
      "image_name": "2431.jpg",
      "local_path": "C:\\Users\\yujer\\...\\2431.jpg",
      "url": "https://sweetpotatobase.org//data/images/image_files/.../medium.jpg"
    },
    {
      "image_id": "2432",
      "image_name": "2432.jpg",
      "local_path": "C:\\Users\\yujer\\...\\2432.jpg",
      "url": "https://sweetpotatobase.org//data/images/image_files/.../medium.jpg"
    },
    {
      "image_id": "2433",
      "image_name": "RTSHP.png",
      "local_path": "C:\\Users\\yujer\\...\\RTSHP.png",
      "url": "https://sweetpotatobase.org//data/images/image_files/.../medium.jpg"
    }
  ]
}
```

---
# Notes
- For now, only local mode is supported, with images being stored in ./cache/{name}/{session}/downloads/{timestamp} directory by default, or the DOWNLOAD_DIR_OVERRIDE/{timestamp} directory. 
  - So the `RTSHP.png` image would be in `./cache/sweetpotatobase/downloads/20260105_094708/RTSHP.png` or `DOWNLOAD_DIR_OVERRIDE/images/20260105_094708/RTSHP.png`
  - .zip file support is coming very soon!
- Images should be named with their original file name, or their DbID if they don't have one. 

# Mesh Simplification with MDD and LME

This repository implements a mesh simplification algorithm based on the concepts of **MDD (Minimal Simplification Domain)** and **LME (Local Minimal Edges)** from the paper on out-of-core mesh simplification.

## Overview

The implementation provides a modular approach to mesh simplification that:

1. **Partitions** large meshes into smaller sub-meshes (MDD - Minimal Simplification Domain)
2. **Simplifies** each sub-mesh independently using QEM with border preservation (LME - Local Minimal Edges)
3. **Merges** the simplified sub-meshes back into a single coherent output mesh

This approach is particularly useful for:
- Processing very large meshes that don't fit in memory
- Parallel simplification of mesh partitions
- Preserving geometric details at partition boundaries

## Files

- **`QEM.py`**: Base implementation of Quadric Error Metric (QEM) mesh simplification
  - `PLYReader`: Read PLY mesh files (ASCII and binary formats)
  - `PLYWriter`: Write PLY mesh files (ASCII format)
  - `QEMSimplifier`: Core QEM simplification algorithm

- **`mesh_simplification_mdd_lme.py`**: Main implementation of MDD/LME simplification
  - `MeshPartitioner`: Partitions meshes using octree spatial subdivision
  - `LMESimplifier`: Extends QEM to preserve border vertices
  - `MeshMerger`: Merges simplified sub-meshes with deduplication
  - Command-line interface for processing PLY files

- **`create_test_mesh.py`**: Utility to generate test meshes (simple and subdivided cubes)

## Installation

### Requirements

- Python 3.7+
- NumPy

```bash
pip install numpy
```

## Usage

### Basic Usage

Process all PLY files in a directory:

```bash
python mesh_simplification_mdd_lme.py
```

By default, the script:
- Reads PLY files from `./demo/data`
- Writes simplified meshes to `./demo/output`
- Uses simplification ratio of 0.5 (keeps 50% of vertices)
- Creates 8 partitions using octree subdivision

### Customizing Paths

Edit the `main()` function in `mesh_simplification_mdd_lme.py` to change:

```python
# Input/output directories
input_folder = "./demo/data"
output_folder = "./demo/output"

# Simplification parameters
simplification_ratio = 0.5  # Keep 50% of vertices
num_partitions = 8          # Octree partitioning (2x2x2)
```

### Using as a Library

```python
from mesh_simplification_mdd_lme import simplify_mesh_with_partitioning
from QEM import PLYReader, PLYWriter

# Read input mesh
vertices, faces = PLYReader.read_ply("input.ply")

# Simplify with partitioning
simplified_vertices, simplified_faces = simplify_mesh_with_partitioning(
    vertices, 
    faces,
    target_ratio=0.5,      # Keep 50% of vertices
    num_partitions=8       # Use 8 partitions
)

# Write output mesh
PLYWriter.write_ply("output.ply", simplified_vertices, simplified_faces)
```

## Algorithm Details

### 1. Mesh Partitioning (MDD)

The mesh is partitioned using **octree spatial subdivision**:

- The bounding box of the mesh is divided into 8 octants
- Each vertex is assigned to an octant based on its position
- Faces are assigned to all octants they touch
- Vertices on partition boundaries are marked as **border vertices**

This creates smaller, independent sub-meshes that can be simplified separately.

### 2. Local Simplification (LME)

Each sub-mesh is simplified using the **QEM (Quadric Error Metric)** method with border preservation:

- **Border vertices** (shared between partitions) are preserved
- Only **interior vertices** are simplified through edge collapse
- This ensures that partition boundaries remain compatible for merging

The QEM method:
- Computes a quadric error matrix for each vertex
- Iteratively collapses edges with minimal error
- Finds optimal vertex positions that minimize geometric distortion

### 3. Sub-mesh Merging

The simplified sub-meshes are merged back together:

- Vertices are deduplicated based on:
  - Original vertex indices (for border vertices)
  - Position-based matching (with tolerance)
- Faces are deduplicated to remove duplicates from overlapping partitions
- The result is a single, coherent simplified mesh

## Testing

Generate test meshes:

```bash
python create_test_mesh.py
```

This creates:
- `cube_simple.ply`: A basic cube (8 vertices, 12 faces)
- `cube_subdivided.ply`: A subdivided cube (152 vertices, 300 faces)

Run simplification on test meshes:

```bash
python mesh_simplification_mdd_lme.py
```

Check the output in `./demo/output/`

## Configuration for Windows Paths

The script is designed to work with the paths specified in the requirements:

- Input: `D:\sxl08\rand1\neural-mesh-simplification\neural-mesh-simplification\demo\data`
- Output: `D:\sxl08\rand1\neural-mesh-simplification\neural-mesh-simplification\demo\output`

If these paths exist, the script will use them automatically. Otherwise, it falls back to relative paths (`./demo/data` and `./demo/output`).

To force specific paths, modify the `main()` function:

```python
input_folder = r"D:\sxl08\rand1\neural-mesh-simplification\neural-mesh-simplification\demo\data"
output_folder = r"D:\sxl08\rand1\neural-mesh-simplification\neural-mesh-simplification\demo\output"
```

## Performance Considerations

- **Partitioning overhead**: For small meshes, partitioning may add overhead. Consider using fewer partitions or the original QEM method.
- **Border vertices**: A high ratio of border vertices to interior vertices limits simplification effectiveness.
- **Memory usage**: Each partition is processed independently, reducing peak memory usage for large meshes.

## References

This implementation is based on concepts from:
- "Out-of-Core Framework for QEM-based Mesh Simplification" (included PDF)
- Quadric Error Metrics for surface simplification (Garland & Heckbert, 1997)

## License

This code is provided for educational and research purposes.

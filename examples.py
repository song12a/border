"""
Example usage of the mesh simplification algorithm with MDD and LME.

This script demonstrates various ways to use the mesh simplification functionality.
"""

from mesh_simplification_mdd_lme import (
    simplify_mesh_with_partitioning,
    process_ply_file,
    MeshPartitioner,
    LMESimplifier,
    MeshMerger
)
from QEM import PLYReader, PLYWriter, simplify_ply_file
import numpy as np
import os


def example_1_basic_usage():
    """
    Example 1: Basic usage - simplify a single PLY file.
    """
    print("=" * 70)
    print("Example 1: Basic Usage - Single File Simplification")
    print("=" * 70)
    
    input_file = "demo/data/cube_subdivided.ply"
    output_file = "demo/output/example1_output.ply"
    
    # Simple one-line processing
    success = process_ply_file(
        input_file, 
        output_file,
        target_ratio=0.5,
        num_partitions=8
    )
    
    if success:
        print(f"\n✓ Successfully simplified {input_file} to {output_file}")
    else:
        print(f"\n✗ Failed to simplify {input_file}")


def example_2_programmatic_usage():
    """
    Example 2: Programmatic usage - load, simplify, and save manually.
    """
    print("\n" + "=" * 70)
    print("Example 2: Programmatic Usage")
    print("=" * 70)
    
    # Load mesh
    input_file = "demo/data/cube_subdivided.ply"
    vertices, faces = PLYReader.read_ply(input_file)
    print(f"\nLoaded mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # Simplify with custom parameters
    simplified_vertices, simplified_faces = simplify_mesh_with_partitioning(
        vertices,
        faces,
        target_ratio=0.4,      # Keep 40% of vertices
        num_partitions=8       # Use octree (2x2x2)
    )
    
    # Save result
    output_file = "demo/output/example2_output.ply"
    PLYWriter.write_ply(output_file, simplified_vertices, simplified_faces)
    print(f"\n✓ Saved to {output_file}")


def example_3_comparison_with_standard_qem():
    """
    Example 3: Compare MDD/LME approach with standard QEM.
    """
    print("\n" + "=" * 70)
    print("Example 3: Comparison with Standard QEM")
    print("=" * 70)
    
    input_file = "demo/data/cube_subdivided.ply"
    vertices, faces = PLYReader.read_ply(input_file)
    
    print(f"\nOriginal mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # Method 1: Standard QEM (from QEM.py)
    print("\n--- Method 1: Standard QEM ---")
    output_qem = "demo/output/example3_standard_qem.ply"
    simplify_ply_file(input_file, output_qem, simplification_ratio=0.5)
    
    # Method 2: MDD/LME approach
    print("\n--- Method 2: MDD/LME with Partitioning ---")
    simplified_vertices, simplified_faces = simplify_mesh_with_partitioning(
        vertices, faces, target_ratio=0.5, num_partitions=8
    )
    output_mdd = "demo/output/example3_mdd_lme.ply"
    PLYWriter.write_ply(output_mdd, simplified_vertices, simplified_faces)
    
    print(f"\n✓ Standard QEM output: {output_qem}")
    print(f"✓ MDD/LME output: {output_mdd}")


def example_4_different_partition_counts():
    """
    Example 4: Test different numbers of partitions.
    """
    print("\n" + "=" * 70)
    print("Example 4: Different Partition Counts")
    print("=" * 70)
    
    input_file = "demo/data/cube_subdivided.ply"
    vertices, faces = PLYReader.read_ply(input_file)
    
    print(f"\nOriginal mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # Try different partition counts
    for num_parts in [8]:  # Could also try [1, 4, 8, 16, 27] for larger meshes
        print(f"\n--- Using {num_parts} partitions ---")
        simplified_vertices, simplified_faces = simplify_mesh_with_partitioning(
            vertices, faces, target_ratio=0.5, num_partitions=num_parts
        )
        output_file = f"demo/output/example4_parts_{num_parts}.ply"
        PLYWriter.write_ply(output_file, simplified_vertices, simplified_faces)


def example_5_batch_processing():
    """
    Example 5: Batch process multiple files.
    """
    print("\n" + "=" * 70)
    print("Example 5: Batch Processing")
    print("=" * 70)
    
    input_dir = "demo/data"
    output_dir = "demo/output/batch"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all PLY files
    ply_files = [f for f in os.listdir(input_dir) if f.endswith('.ply')]
    print(f"\nFound {len(ply_files)} PLY files in {input_dir}")
    
    # Process each file
    for filename in ply_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"batch_{filename}")
        
        print(f"\nProcessing {filename}...")
        process_ply_file(input_path, output_path, target_ratio=0.5, num_partitions=8)


def example_6_step_by_step():
    """
    Example 6: Step-by-step usage showing each component.
    """
    print("\n" + "=" * 70)
    print("Example 6: Step-by-Step Component Usage")
    print("=" * 70)
    
    # Load mesh
    input_file = "demo/data/cube_subdivided.ply"
    vertices, faces = PLYReader.read_ply(input_file)
    print(f"\n1. Loaded mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # Step 1: Partition
    print("\n2. Partitioning mesh...")
    partitioner = MeshPartitioner(vertices, faces, num_partitions=8)
    partitions = partitioner.partition_octree()
    print(f"   Created {len(partitions)} partitions")
    print(f"   Border vertices: {len(partitioner.border_vertices)}")
    
    # Step 2: Simplify each partition
    print("\n3. Simplifying partitions...")
    simplified_submeshes = []
    
    for idx, partition in enumerate(partitions[:2]):  # Just process first 2 for demo
        print(f"\n   Partition {idx + 1}:")
        
        # Extract submesh
        submesh_vertices, submesh_faces, vertex_map = partitioner.extract_submesh(partition)
        print(f"   - Submesh: {len(submesh_vertices)} vertices, {len(submesh_faces)} faces")
        
        # Create reverse mapping
        reverse_map = {local: global_idx for global_idx, local in vertex_map.items()}
        
        # Get border vertices in local indices
        local_border = {vertex_map[v] for v in partition['is_border'] if v in vertex_map}
        
        # Simplify
        simplifier = LMESimplifier(submesh_vertices, submesh_faces, local_border)
        simp_verts, simp_faces = simplifier.simplify(target_ratio=0.5)
        print(f"   - Simplified: {len(simp_verts)} vertices, {len(simp_faces)} faces")
        
        # Create reverse map for simplified vertices (position-based matching)
        simp_reverse_map = {}
        for local_idx, simp_vert in enumerate(simp_verts):
            min_dist = float('inf')
            best_orig_idx = None
            for orig_local_idx, orig_global_idx in reverse_map.items():
                if orig_local_idx < len(submesh_vertices):
                    dist = np.linalg.norm(simp_vert - submesh_vertices[orig_local_idx])
                    if dist < min_dist:
                        min_dist = dist
                        best_orig_idx = orig_global_idx
            if min_dist < 1e-5:
                simp_reverse_map[local_idx] = best_orig_idx
        
        simplified_submeshes.append({
            'vertices': simp_verts,
            'faces': simp_faces,
            'vertex_map': vertex_map,
            'reverse_map': simp_reverse_map
        })
    
    # Step 3: Merge (only if we processed all partitions)
    print("\n4. Note: Full merge would happen after processing all partitions")
    print("   (Skipped in this demo to keep output concise)")


def main():
    """Run all examples."""
    
    print("=" * 70)
    print("Mesh Simplification Examples")
    print("MDD (Minimal Simplification Domain) + LME (Local Minimal Edges)")
    print("=" * 70)
    
    # Make sure output directory exists
    os.makedirs("demo/output", exist_ok=True)
    os.makedirs("demo/output/batch", exist_ok=True)
    
    # Run examples
    example_1_basic_usage()
    example_2_programmatic_usage()
    example_3_comparison_with_standard_qem()
    example_4_different_partition_counts()
    example_5_batch_processing()
    example_6_step_by_step()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nCheck the 'demo/output' directory for results.")


if __name__ == "__main__":
    main()

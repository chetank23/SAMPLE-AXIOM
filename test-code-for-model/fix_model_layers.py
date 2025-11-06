import h5py
import os
import shutil

def fix_model_layer_names(input_path, output_path):
    """
    Fix model layer names by replacing forward slashes with underscores
    """
    try:
        with h5py.File(input_path, 'r') as src_file:
            with h5py.File(output_path, 'w') as dst_file:
                def copy_group(src, dst, path=''):
                    for key in src.keys():
                        if isinstance(src[key], h5py.Group):
                            # Create new group with sanitized name
                            new_key = key.replace('/', '_')
                            new_group = dst.create_group(new_key)
                            copy_group(src[key], new_group, path + '/' + new_key)
                        else:
                            # Copy dataset
                            dst.create_dataset(key, data=src[key][:])
                
                copy_group(src_file, dst_file)
        
        print(f"✓ Model fixed and saved to: {output_path}")
        return True
    except Exception as e:
        print(f"✗ Error fixing model: {e}")
        return False

def backup_and_fix_model(model_path):
    """
    Create a backup and fix the model
    """
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        return False
    
    # Create backup
    backup_path = model_path + '.backup'
    shutil.copy2(model_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Create fixed version
    fixed_path = model_path.replace('.h5', '_fixed.h5')
    success = fix_model_layer_names(model_path, fixed_path)
    
    if success:
        # Replace original with fixed version
        shutil.move(fixed_path, model_path)
        print(f"✓ Original model replaced with fixed version")
        return True
    else:
        print(f"✗ Failed to fix model, keeping original")
        return False

if __name__ == "__main__":
    # Fix the problematic models
    models_to_fix = [
        'model/DenseNet121v2_95.h5',
        'model/SoilNet_93_86.h5'
    ]

    existing_models = [p for p in models_to_fix if os.path.exists(p)]

    if not existing_models:
        # Auto-discover .h5 files anywhere under the project root
        project_root = os.path.dirname(os.path.dirname(__file__))
        discovered = []
        for root, _dirs, files in os.walk(project_root):
            for fname in files:
                if fname.lower().endswith('.h5'):
                    discovered.append(os.path.join(root, fname))

        if not discovered:
            print("No .h5 model files were found in the project. Place your .h5 files in the 'model' folder next to this script or anywhere under the project, then run again.")
        else:
            print(f"Found {len(discovered)} .h5 file(s). Processing all discovered models.")
            existing_models = discovered

    for model_path in existing_models:
        print(f"\nProcessing: {model_path}")
        backup_and_fix_model(model_path)

    print("\nModel fixing completed!")

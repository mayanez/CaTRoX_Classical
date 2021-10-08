#!/usr/bin/env python3

import argparse
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
from zipfile import ZipFile

import call_wrapper

def path_basename_tuple(path):
    return (path, path.name)

def zipdir(zip_file, path, arc_path=None):
    if (path.exists() and path.is_dir()):
        for file in path.rglob('*'):
            if (file.name.startswith('.')):
                # skip `hidden` files
                continue
            if (arc_path):
                file_arc_path = f'{arc_path}/{file.relative_to(path)}'
            else:
                file_arc_path = file.relative_to(path)
            zip_file.write(file, file_arc_path)

def pack():
    cur_dir = Path(__file__).parent.absolute()
    root_dir = cur_dir.parent
    
    output_dir = root_dir/'_result'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_zip = output_dir/'catrox_classical_edition.zip'
    try:
        os.remove(output_zip)
    except:
        pass
    
    output_packages_dir = output_dir/'packages'
    if output_packages_dir.exists():
        shutil.rmtree(output_packages_dir)
    output_packages_dir.mkdir(parents=True)
    
    external_packages = {'ArtistBioAlternate': 'https://github.com/mayanez/WilB-Biography-Mod/releases/latest/download/SMP-Biography-Mod.zip', 
                         'ComposerBio': 'https://github.com/mayanez/WilB-Biography-Mod/releases/latest/download/SMP-Biography-Mod.zip'}

    for d in (root_dir/'packages').glob('*'):
        d_name = os.path.basename(d)
        if d_name not in external_packages.keys():
            for f in d.glob('*'):
                package_zip = output_packages_dir/f'{d_name}.zip'
                with ZipFile(package_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                    zipdir(z, f)   
                    print(f'Generated package: {package_zip}')
                
                # there should be only one package per dir anyway
                break
        else:
            urllib.request.urlretrieve(external_packages[d_name], output_packages_dir/f'{d_name}.zip')
            print(f'Downloaded package: {d_name}')

    with ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        zipdir(z, output_packages_dir, 'packages')
        zipdir(z, root_dir/'fonts', 'fonts')
        z.write(root_dir/'layout'/'classical.fcl', 'layout/classical.fcl')
        z.write(root_dir/'layout'/'theme.fcl', 'layout/theme.fcl')

    print(f'Generated file: {output_zip}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pack')

    call_wrapper.final_call_decorator(
        'Packing',
        'Packing: success',
        'Packing: failure!'
    )(
    pack
    )(
    )

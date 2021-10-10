#!/usr/bin/env python3

import argparse
import os
import requests
import shutil
import yaml
import zipfile
from pathlib import Path
from zipfile import ZipFile

import call_wrapper

PACK_YML = 'pack.yml'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0' ,
}

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

def handle_package(package_path, output_packages_dir):
    package_name = os.path.basename(package_path)
    package_zip = output_packages_dir/f'{package_name}.zip'
    
    for f in package_path.glob('*'):
        if os.path.basename(f) == PACK_YML:
            with open(f, "r") as ymlfile:
                data = yaml.load(ymlfile, Loader=yaml.FullLoader)
                r = requests.get(data[package_name]['url'])
                with open(package_zip, 'wb') as out:
                    out.write(r.content)
                    print(f'Downloaded package: {package_zip}')
        elif f.is_dir():
            with ZipFile(package_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                zipdir(z, f)   
                print(f'Generated package: {package_zip}')
        
def handle_additional_files(root_dir, zip_file):
    for d in (root_dir/'packages').glob('*'):
        package_name = os.path.basename(d)
        for f in d.glob('*'):
            if os.path.basename(f) == PACK_YML:
                with open(f, "r") as ymlfile:
                    data = yaml.load(ymlfile, Loader=yaml.FullLoader)
                    # TODO: Handle arbitrary nesting?
                    for output_dir, additional_files in data[package_name]['additional_files'].items():
                        for output_file in additional_files:
                            zip_file.write(f'{d}/{output_file}', f'{output_dir}/{output_file}')

def handle_user_components(component_path, output_components_dir):
    component_name = os.path.basename(component_path)

    for f in component_path.glob('*'):
        if os.path.basename(f) == PACK_YML:
            with open(f, "r") as ymlfile:
                data = yaml.load(ymlfile, Loader=yaml.FullLoader)
                r = requests.get(data[component_name]['url'])
                with open(f'{output_components_dir}/{component_name}.fb2k-component', 'wb') as out:
                    out.write(r.content)
                    print(f'Downloaded Component: {component_name}')

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

    output_components_dir = output_dir/'user-components'
    if output_components_dir.exists():
        shutil.rmtree(output_components_dir)
    output_components_dir.mkdir(parents=True)

    for d in (root_dir/'packages').glob('*'):
        handle_package(d, output_packages_dir)

    for d in (root_dir/'user-components').glob('*'):
        handle_user_components(d, output_components_dir)

    with ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        zipdir(z, output_packages_dir, 'packages')
        zipdir(z, output_components_dir, 'user-components')
        zipdir(z, root_dir/'fonts', 'fonts')
        z.write(root_dir/'layout'/'classical.fcl', 'layout/classical.fcl')
        z.write(root_dir/'layout'/'theme.fcl', 'layout/theme.fcl')
        handle_additional_files(root_dir, z)

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

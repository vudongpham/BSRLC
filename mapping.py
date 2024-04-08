import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y','--year', required=True, type=str)
    parser.add_argument('-t','--tile', required=True, type=str)
    args = vars(parser.parse_args())
    year = args['year']
    tile = args['tile']
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mapping_script = os.path.join(dir_path, "Scripts/process.py")
    os.system('{} {} --dir {} --year {} --tile {}'.format('python', mapping_script, dir_path, year, tile))

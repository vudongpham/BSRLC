import numpy as np
from osgeo import gdal
import rasterio
from tqdm import tqdm
import tensorflow as tf
import os
import argparse




def predict(main_dir, tile, year, model_lc, model_crop, nodata_in=-9999, nodata_out=255):
    def toRaster(arr_in):
        path = main_dir + '/FORCE_datacube_fbm/' + tile + '/' + year + '-' + year + '_001-365_HL_TSA_LNDLG_BLU_FBW.tif'
        ds = gdal.Open(path)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        [cols, rows] = arr.shape
        arr_out = arr_in
        driver = gdal.GetDriverByName("GTiff")
        if not os.path.isdir(main_dir + '/Maps/' + tile):
            os.makedirs(main_dir + '/Maps/' + tile)
        path_out = main_dir + '/Maps/' + tile + '/map_' + year + '.tif'
        outdata = driver.Create(path_out, rows, cols, 1, gdal.GDT_Byte)
        outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).SetNoDataValue(255)
        outdata.GetRasterBand(1).WriteArray(arr_out)
        # outdata.GetRasterBand(1).SetDescription()
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band=None
        ds=None

    
    def get_stack(tile, year):
        def get_band(b):
            with rasterio.open(main_dir + '/FORCE_datacube_fbm/' + tile + '/' + year + '-' + year + '_001-365_HL_TSA_LNDLG_' + b + '_FBW.tif') as src:
                arr = src.read()
            arr = np.moveaxis(arr, 0, -1)
            return arr
        band_list = ['BLU', 'GRN', 'RED', 'NIR', 'SW1', 'SW2', 'NDV', 'NDW', 'SAV']
        fbm = np.array([get_band(b) for b in band_list])
        fbm = np.moveaxis(fbm, 0, -1)
        fbm[fbm == nodata_in] = 0
        return  fbm
    
    def pred(model, x_in):
        y_pred = model(x_in, training=False)
        y_pred = tf.nn.softmax(y_pred)
        y_pred = tf.math.argmax(y_pred, axis=-1)
        y_pred = y_pred.numpy()
        return y_pred

    
    # LC mapping
    x_stack = get_stack(tile, year)
    no_data_mask = np.all(x_stack[:, :, :, 0] == 0, axis = -1)
    x_stack = x_stack.astype(np.float32)
    x_stack = x_stack / 10000.
    x_out_lc = np.zeros([x_stack.shape[0], x_stack.shape[1]], dtype=np.int16)
    print('Step 1/2 Mapping general LC')
    for i in tqdm(range(x_stack.shape[0])):
        x_in = x_stack[i, ...]
        y_pred = pred(model_lc, x_in)
        x_out_lc[i, :] = y_pred
    x_out_lc[no_data_mask] = nodata_out
    
    # Crop mapping on top of LC map
    cropland = 9
    mask_lc = x_out_lc != cropland
    x_out_crop = np.zeros([x_stack.shape[0], x_stack.shape[1]], dtype=np.int16)
    print('Step 2/2 Mapping crop types on top of LC map')
    for i in tqdm(range(x_stack.shape[0])):
        x_in = x_stack[i, ...]
        y_pred = pred(model_crop, x_in)
        x_out_crop[i, :] = y_pred
        
    # Shift the results + 9 classes
    x_out_crop = x_out_crop + 9
    
    # Insert LC classes from previous result and shift LC code to start at 1
    x_out_crop[mask_lc] = x_out_lc[mask_lc]
    x_out_crop = x_out_crop + 1
    x_out_crop[no_data_mask] = nodata_out
    
    
    #Export map
    toRaster(x_out_crop)
    print('Done', tile, year, sep = ' ')
    
    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir', required=True, type=str)
    parser.add_argument('-y','--year', required=True, type=str)
    parser.add_argument('-t','--tile', required=True, type=str)
    
    args = vars(parser.parse_args())
    year = args['year']
    tile = args['tile']
    main_dir = args['dir']
    model_lc = tf.keras.models.load_model(main_dir + '/pre_trained_models/model_lc', compile=False)
    model_crop = tf.keras.models.load_model(main_dir + '/pre_trained_models/model_crop', compile=False)
    predict(main_dir=main_dir,
            tile = tile,
            year = year, 
            model_lc = model_lc, 
            model_crop = model_crop)



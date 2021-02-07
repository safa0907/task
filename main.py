import os
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from osmxtract import overpass, location
import overpy
import overpass
import osmnx
import numpy as np
from osgeo import ogr
import rasterio
import pandas
import geopandas
import fiona
from rasterio.mask import mask
from rasterio import Affine as A
from rasterio.warp import reproject, Resampling
import json
import geojson
import tempfile
from osgeo import gdal
import subprocess

user = 'safa09' 
password = 'Safa09071993+' 

api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
SAVE_FOLDER='sat_images'
#SHAPE='shapefiles'
def main():
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
        download()
    #if not os.path.exists(SHAPE):
        #os.mkdir(SHAPE)
        #buildings()
 
def download():
    # search by polygon
    footprint = geojson_to_wkt(read_geojson(r"C:\Users\Ridene Safa\Desktop\task\task2\map.geojson"))
    print (footprint)
    print("Searching")
    products = api.query(footprint,
                     date = ('20200204','20210206'),
                     platformname = 'Sentinel-2',
                     cloudcoverpercentage = (0, 30),
                     #filename="*TCI_10m*",
                     limit=1)
    print (len(products))
    print("Start downloading...")
    #for i in products:
        #api.get_product_odata(i)
        #api.download(i,SAVE_FOLDER)
print('Finished downloading satellite image')
#Retrieve buildings with height data from OSM
def buildings():
    #tags={'building':True,'height':True},
    api=overpass.API()
    res=api.get('way["building"]["height"](47.003436,15.370560,47.109626,15.506172);',responseformat="geojson", verbosity="geom")
    #print geojson file
    print(res) 
    #Export Geojson file
    res = geojson.Feature(geometry= (), properties={})
    tmp_file = tempfile.mkstemp(suffix='.geojson')
    with open(tmp_file[1], 'w') as f:
        geojson.dump(res, f)
    #Save to shp
    args=['ogr2ogr','-f','esri shapefile','destination_data.shp', 'res.geojson']
    subprocess.Popen(args)
    print ('Finished downloading buildings with height')
#Mask raster with polygons
#inRaster=r'C:\Users\Ridene Safa\Desktop\task\task2\S2B_MSIL2A_20210204T100119_N0214_R122_T33TWN_20210204T121352.SAFE\GRANULE\L2A_T33TWN_A020454_20210204T100116\IMG_DATA\R10m\T33TWN_20210204T100119_TCI_10m.jp2'
#inshape=r'C:\Users\Ridene Safa\Desktop\task\task2\buildings\buildings.shp'
with fiona.open(r'buildings\buildings_project.shp') as shapefile:
    shapes=[feature["geometry"]for feature in shapefile]
with rasterio.open(r'sat_images\T33TWN_20210204T100119_TCI_10m.jp2') as src:
    out_image, out_transform=rasterio.mask.mask(src, shapes, crop=True)
    out_meta=src.meta
out_meta.update({"driver": "Gtiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

with rasterio.open("RGB.masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)
print("Mask completed")
#reproject to EPSG 3857
input_raster = gdal.Open("RGB.masked.tif")
output_raster = "RGB.masked.proj.tif"
warp = gdal.Warp(output_raster,input_raster,dstSRS='EPSG:3857')
warp = None # Closes the files




if __name__=='__main__':
    main()
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 11:52:49 2021

@author: AazadPatle
 
Contents

1. Description
2. Modules
3. Code Sequence
4. User defined function Desription 
5. Script Content
    a. Imports
    b. User Defined Functions
    c. Function tests

1. Descritption 
                Scripts automates the inclusion of metadata from a json file to a tiff file
                it writes a new GeoTiff files forming correct tiftags
2. Module Requirements
                a. os, glob - for paths setup
                b. json - to read mtadata json file
                c. numpy  - for array operation
                d. rasterio - raster processing / reading /writing
                e. shapely - to create polygon data
                f. geopandas - to create geodataframe of polygon data
3. User defined function 
                a. create_vector_GDF 
                    Creates polygon geodataframe using corner Coordinates
                    Inputs -i. coordinates: numpy array =>  containing x ,y cooordinates of polygon size Nx2 
                                        where N is number of corners of polygon e.g.,[(x1,y1),(x2,y2),(x3,y3)]
                            ii. epsg_code: int  =>epsg code for CRS  default 4326 as metadata is in degree decimal
                    Returns: Geodataframe
                
                b. Meta_write 
                    writes new GeoTiff file with correct  metadata and tags with proper geocoding information
                    Input: 1 - SR_path: str  surface reflectance tiff file path
                            meta_path: str  metadata json file path 
                    * Once transforms are applied properly while writing geotiff file, geocoding tiff tags gets automatically applied
                    Output: 1- writes a new tiff file in same directory as of tiff with name ending "_tagged"
        
                    
"""

'''1. Imports '''

import os
import glob
import json
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

'''1. Imports '''

def create_vector_GDF(coordinates,epsg_code=4326):
    '''Creates polygon geodataframe from Coordinates
    
    coordinates: array containing x ,y cooordinates of polygon size Nx2 where N is number of corners of plygon
    epsg_code: int
    '''
    polygon_geom = Polygon(coordinates)
    crs = {'init': 'epsg:'+str(epsg_code)}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    print('Polygon dataframe generated')
    return polygon
    

def Meta_write(SR_path,meta_path):
    
    ''' Create new TIFF dataset based on Metadata filejup
    SR_path: str (tiff file path)
    meta_path: str (metadata path)'''
    
    metadata = json.load(open(meta_path,'rb')) # reding metadata json
    coords = np.array(metadata['geometry']['coordinates'])[0] # reading coordinates
    polygon = create_vector_GDF(coords,4326)
    bounds = polygon.bounds.values[0]  ## getting bounds from metadata coordinates
    
    tiff_data = rasterio.open(SR_path) # reading tiff data

    count=tiff_data.read().shape[0]
    height=tiff_data.read().shape[1]
    width=tiff_data.read().shape[2]
    
    # defining transform from bounds and CRS
    transform = rasterio.transform.from_bounds(bounds[0],bounds[1],bounds[2],bounds[3], width,height)
    crs = rasterio.crs.CRS.from_epsg(4326)  

    # defining  output file name and path  to the same directory as of TIff file
    fname = SR_path.split('\\')[-1][:-4] +'_tagged.TIF'
    fdirpath = '\\'.join(SR_path.split('\\')[:-1])
    Out_fpath = '\\'.join((fdirpath,fname))    
    
    
    
    #Writing GeoTiff
    with rasterio.open(Out_fpath,'w+',driver='GTiff',height=height,width=width,count=count,
                       compress = 'lzw',dtype=np.uint16,transform = transform,crs =crs,nodata= 0.0,
                       blockxsize= 512, blockysize=512,interleave= 'pixel',tiled=True) as dst:
            dst.update_tags(AREA_OR_POINT= tiff_data.tags()['AREA_OR_POINT'],
                            TIFFTAG_DATETIME= tiff_data.tags()['TIFFTAG_DATETIME'],
                            TIFFTAG_IMAGEDESCRIPTION = str(metadata['properties']))
                            
            dst.write(tiff_data.read())
            print('Tiff ',Out_fpath,'-- writing Complete')
            
    tiff_data.close()

# Driver Code
if __name__ == '__main__':
    
    # SR_path = 'D:\\Skysat\\SkySat-Co-Registration\\files\\SkySatScene\\20210813_125720_ssc15d2_0016\\analytic_sr_udm2\\20210813_125720_ssc15d2_0016_analytic_SR.TIF'
    # meta_path = 'D:\\Skysat\\SkySat-Co-Registration\\files\\SkySatScene\\20210813_125720_ssc15d2_0016\\20210813_125720_ssc15d2_0016_metadata.json'
     
    os.chdir('.\\20210813_125720_ssc15d2_0016\\analytic_sr_udm2')   # setting working directory where tiff file exist
    
    #defining paths 
    SR_path = sorted(glob.glob(os.path.join(os.getcwd() ,'*SR.TIF')))[0] 
    meta_path = sorted(glob.glob(os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir),'*.json')))[0]
    
    Meta_write(SR_path,meta_path)
                

        
        
    
    
    
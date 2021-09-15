# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 11:52:49 2021

@author: AazadPatle
"""

import json
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

SR_path = '.\\20210813_125720_ssc15d2_0016\\analytic_sr_udm2\\20210813_125720_ssc15d2_0016_analytic_SR.TIF'
meta_path = '.\\20210813_125720_ssc15d2_0016\\20210813_125720_ssc15d2_0016_metadata.json'

def create_vector_GDF(coordinates,epsg_code):
    '''Creates polygon geodataframe from Coordinates
    
    coordinates: array containing x ,y cooordinates of polygon size Nx2 where N is number of corners of plygon
    epsg_code: int
    '''
    polygon_geom = Polygon(coordinates)
    crs = {'init': 'epsg:'+str(epsg_code)}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    return polygon
    

def Meta_write(SR_path,meta_path):
    
    ''' Create new TIFF dataset based on Metadata file
    SR_path: str (tiff file path)
    meta_path: str (metadata path)'''
    
    metadata = json.load(open(meta_path,'rb'))
    
    coords = np.array(metadata['geometry']['coordinates'])[0]
    polygon = create_vector_GDF(coords,4326)
    bounds = polygon.bounds.values[0]  ## getting bounds from metadata coordinates
    
    tiff_data = rasterio.open(SR_path)
    count=tiff_data.read().shape[0]
    height=tiff_data.read().shape[1]
    width=tiff_data.read().shape[2]
    transform = rasterio.transform.from_bounds(bounds[0],bounds[1],bounds[2],bounds[3], width,height)
    crs = rasterio.crs.CRS.from_epsg(4326)

    fname = SR_path.split('\\')[-1][:-4] +'_tagged1.TIF'
    fdirpath = '\\'.join(SR_path.split('\\')[:-1])
    Out_fpath = '\\'.join((fdirpath,fname))    

    with rasterio.open(Out_fpath,'w+',driver='GTiff',height=height,width=width,count=count,
                       compress = 'lzw',dtype=np.uint16,transform = transform,crs =crs,nodata= 0.0,
                       blockxsize= 512, blockysize=512,interleave= 'pixel',tiled=True) as dst:
            dst.update_tags(AREA_OR_POINT= tiff_data.tags()['AREA_OR_POINT'],
                            TIFFTAG_DATETIME= tiff_data.tags()['TIFFTAG_DATETIME'],
                            TIFFTAG_IMAGEDESCRIPTION = str(metadata['properties']))
                            
            dst.write(tiff_data.read())
            
    tiff_data.close()
    
Meta_write(SR_path,meta_path)
            

        
        
    
    
    
    
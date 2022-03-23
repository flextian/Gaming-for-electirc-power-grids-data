# osgeo - https://www.lfd.uci.edu/~gohlke/pythonlibs/
# https://firedanger.cr.usgs.gov/apps/staticmaps - Bulk downloader
# https://firedanger.cr.usgs.gov/viewer/index.html
# Ugly WIP

from csv import reader
from osgeo import gdal, osr
import pandas as pd
import csv
import numpy as np
import os
import matplotlib.pyplot as plt

'''
Upper Left  (-1964218.710,  -93668.323) (124d 0'53.32"W, 41d32'26.70"N)
Lower Left  (-1964218.710, -275668.323) (123d25'15.64"W, 39d59'13.69"N)
Upper Right (-1826218.710,  -93668.323) (122d23'58.61"W, 41d53'21.02"N)
Lower Right (-1826218.710, -275668.323) (121d50'23.60"W, 40d19'29.86"N)
Center      (-1895218.710, -184668.323) (122d54'56.02"W, 40d56'20.96"N)
'''


def main():
    # Import the corresponding geoTIFF
    dataset = gdal.Open("../raw_data/wildfire_data/emodis-wfpi-forecast-7_data_20220320_20220320.tiff")
    print(dataset)

    metadata = os.popen('gdalinfo ../raw_data/wildfire_data/emodis-wfpi-forecast-7_data_20220320_20220320.tiff').read()
    print(metadata)

    old_cs = osr.SpatialReference()
    old_cs.ImportFromWkt(dataset.GetProjectionRef())

    print(dataset.GetProjectionRef())

    '''
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.01745329251994328,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]]
    '''

    new_cs = osr.SpatialReference()
    new_cs.ImportFromEPSG(4326)

    transformer = osr.CoordinateTransformation(old_cs, new_cs)

    width = dataset.RasterXSize
    height = dataset.RasterYSize
    gt = dataset.GetGeoTransform()

    print(gt)

    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    print(minx, maxy)
    print(transformer.TransformPoint(minx, maxy))
    print(maxx, miny)
    print(transformer.TransformPoint(maxx, miny))

    convert(dataset, transformer)


def convert(dataset, transformer):
    xyz = gdal.Translate("output.xyz", dataset)

    dataframe = pd.read_csv("output.xyz", sep=" ", header=None)
    dataframe.columns = ["x", "y", "risk"]
    dataframe.to_csv("output2.csv", index=False)
    translate(transformer)


def translate(transformer):
    # open file
    with open('output2.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader)

        f = open('output3.csv', 'w', newline='')
        writer = csv.writer(f)
        writer.writerow(["x", "y", "value"])

        for row in csv_reader:
            # row variable is a list that represents a row in csv
            print(row[0], row[1])
            a = transformer.TransformPoint(float(row[0]), float(row[1]))
            row[0], row[1] = str(a[0]), str(a[1])
            writer.writerow(row)


if __name__ == "__main__":
    main()

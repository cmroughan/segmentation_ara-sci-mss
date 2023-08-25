#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_svg-to-alto.py

Takes SVG files exported from InkScape and converts them into ALTO XML
to be used by eScriptorium, Kraken, and other layout analysis training tools.

The SVG files must link to a relevant page image and contain vector polygons
indicating the annotated regions.

This script expects to be used from the main project directory.

See documentation on the 'd' property of the <path> element for SVG files:
https://www.w3.org/TR/SVG2/paths.html#TheDProperty

See documentation on ALTO XML:
https://www.loc.gov/standards/alto/

DISCLAIMER - this is a prototype.
"""

import re
import os
import sys
from PIL import Image
from lxml import etree
from pathlib import Path

# The same function can handle M, L, and (L) commands
# Get two rounded integer coordinates from the svgCoord string
def extractTwoCoords(svgCoord):
    global toMultiply
    x, y = svgCoord.split(',')
    x = float(x)
    y = float(y)
    xRound = round(x*toMultiply)
    yRound = round(y*toMultiply)

    return xRound, yRound
    
# Get a bounding box by its min X, Y and its height and width
def bounding_box(points):
    bboxDict = {}
    x_coordinates, y_coordinates = zip(*points)
    bboxDict['HPOS'] = min(x_coordinates)
    bboxDict['VPOS'] = min(y_coordinates)
    bboxDict['WIDTH'] = max(x_coordinates) - bboxDict['HPOS']
    bboxDict['HEIGHT'] = max(y_coordinates) - bboxDict['VPOS']

    return bboxDict

# Construct paths from command line input.
# The manuscript directory should be the first argument
# and the filetype subdirectory the second argument.
if len(sys.argv) != 3:
    print(f'ERROR: {len(sys.argv) - 1} arguments detected. This script takes exactly two arguments. Arguments detected:')
    for a in sys.argv:
        print(f'- {a}')
    exit()

xmlDirPath = Path('data/xml/')
imgDirPath = Path('data/imgs-to-upload/')
msDir = sys.argv[1]
typeDir = sys.argv[2]
fullDirPath = imgDirPath / msDir / typeDir
fullXmlDirPath = xmlDirPath / msDir

# Create XML directory path if none exists:
if fullXmlDirPath.is_dir():
    pass
else:
    fullXmlDirPath.mkdir()

# Find all svg files in the directory to iterate over.
svg_list = [f for f in os.listdir(fullDirPath) if '.svg' in f]
svg_list.sort()

for svgFile in svg_list:
    relativeCoordFlag = False # The script doesn't handle relative coordinates yet.

    svgPath = fullDirPath / svgFile
    altoFile = f"{svgFile.split('.')[0]}.xml"
    altoPath = fullXmlDirPath / altoFile
    
    regionDict = {'mz': ['BT5', 'MainZone', 'block type MainZone'],
                  'mtz': ['BT6', 'MarginTextZone', 'block type MarginTextZone'],
                  'gz': ['BT7', 'GraphicZone', 'block type GraphicZone'],
                  'nz': ['BT8', 'NumberingZone', 'block type NumberingZone'],
                  'tz': ['BT9', 'TableZone', 'block type TableZone']}
    
    altoXML = etree.fromstring(b"""<?xml version="1.0" encoding="UTF-8"?>
    <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns="http://www.loc.gov/standards/alto/ns-v4#"
          xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-2.xsd">
      <Description>
        <MeasurementUnit>pixel</MeasurementUnit>
        <sourceImageInformation>
          <fileName>#####</fileName>
        </sourceImageInformation>
      </Description>
      
      <Tags>
        <OtherTag ID="BT5" LABEL="MainZone" DESCRIPTION="block type MainZone"/><OtherTag ID="BT6" LABEL="MarginTextZone" DESCRIPTION="block type MarginTextZone"/><OtherTag ID="BT7" LABEL="GraphicZone" DESCRIPTION="block type GraphicZone"/><OtherTag ID="BT8" LABEL="NumberingZone" DESCRIPTION="block type NumberingZone"/><OtherTag ID="BT9" LABEL="TableZone" DESCRIPTION="block type TableZone"/>
        
      </Tags>
      
      <Layout>
        <Page WIDTH="#####"
              HEIGHT="#####"
              PHYSICAL_IMG_NR="#####"
              ID="InSc_dummypage_">
          <PrintSpace HPOS="0"
                      VPOS="0"
                      WIDTH="#####"
                      HEIGHT="#####">
                      
          </PrintSpace>
        </Page>
      </Layout>
    </alto>""")
    
    ALTO_NS = "{http://www.loc.gov/standards/alto/ns-v4#}"
    
    # Extracting preliminary data from SVG file
    tree = etree.parse(svgPath)
    g = tree.find('{http://www.w3.org/2000/svg}g')
    imgTag = g.find('{http://www.w3.org/2000/svg}image')
    
    svgWidth = float(imgTag.attrib['width'])
    svgHeight = float(imgTag.attrib['height'])
    imgFile = imgTag.attrib['{http://www.w3.org/1999/xlink}href']
    imgNum = str(int(imgFile.split('.')[0]))
    
    # Getting image dimensions from the image file
    imgPath = fullDirPath / imgFile
    with Image.open(imgPath) as img:
        imgWidth = img.width
        imgHeight = img.height
    
    # Finding difference between SVG dimensions and image dimensions
    toMultiply = imgWidth / svgWidth
    
    # Inputting data into the ALTO template
    # <fileName>
    el_fileName = altoXML.find(f'.//{ALTO_NS}sourceImageInformation/{ALTO_NS}fileName' )
    el_fileName.text = imgFile
    
    # <Page WIDTH, HEIGHT, PHYSICAL_IMG_NR>
    el_Page = altoXML.find(f'.//{ALTO_NS}Layout/{ALTO_NS}Page')
    el_Page.attrib['WIDTH'] = str(imgWidth)
    el_Page.attrib['HEIGHT'] = str(imgHeight)
    el_Page.attrib['PHYSICAL_IMG_NR'] = imgNum
    
    # <PrintSpace WIDTH, HEIGHT>
    el_PrintSpace = altoXML.find(f'.//{ALTO_NS}PrintSpace')
    el_PrintSpace.attrib['WIDTH'] = str(imgWidth)
    el_PrintSpace.attrib['HEIGHT'] = str(imgHeight)
    
    # Iterate through <path>s in SVG file
    paths = g.findall('{http://www.w3.org/2000/svg}path')
    for path in paths:
        d = path.attrib['d']
        label = path.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        path_id = path.attrib['id']

        print(f"\rConverting: {svgFile}\t{path_id}", end="")
        
        # Create empty list to be filled with tuples of coordinates:
        coords = []
        segments = re.findall(r' ?[MmVvLlHh]? [\d\.,]+', d)
        for i, svgCoord in enumerate(segments):
            svgCoord = svgCoord.strip()
            if svgCoord[0] in ['M','L']:
                # Get numerical values
                svgCoord = svgCoord.split()[1]
                x, y = extractTwoCoords(svgCoord)
                coords.append([x, y])
            elif svgCoord[0].isdigit():
                try:
                    x, y = extractTwoCoords(svgCoord)
                except:
                    if segments[i-1][0] == 'V':
                        y = float(svgCoord.split()[1])
                        y = round(y*toMultiply)
                        x = coords[-1][0]
                    elif segments[i-1][0] == 'H':  
                        x = float(svgCoord.split()[1])
                        x = round(x*toMultiply)
                        y = coords[-1][1] 
                coords.append([x, y])
            elif svgCoord[0] == 'V':
                y = float(svgCoord.split()[1])
                y = round(y*toMultiply)
                x = coords[-1][0]
                coords.append([x, y])
            elif svgCoord[0] == 'H':
                x = float(svgCoord.split()[1])
                x = round(x*toMultiply)
                y = coords[-1][1]
                coords.append([x, y])
            else:
                print("WARNING: relative coordinates")
                print(svgCoord)
                relativeCoordFlag = True
                break

        if relativeCoordFlag == True:
            break
            
        bbox = bounding_box(coords)
    
        # <TextBlock HPOS, VPOS, WIDTH, HEIGHT, ID, TAGREGS>
        el_TextBlock = etree.SubElement(el_PrintSpace, "TextBlock")
        el_TextBlock.attrib['HPOS'] = str(bbox['HPOS'])
        el_TextBlock.attrib['VPOS'] = str(bbox['VPOS'])
        el_TextBlock.attrib['WIDTH'] = str(bbox['WIDTH'])
        el_TextBlock.attrib['HEIGHT'] = str(bbox['HEIGHT'])
        el_TextBlock.attrib['ID'] = path_id
        el_TextBlock.attrib['TAGREFS'] = regionDict[label][0]
        
        # <Polygon POINTS>
        el_Shape = etree.SubElement(el_TextBlock, "Shape")
        el_Polygon = etree.SubElement(el_Shape, "Polygon")
        el_Polygon.attrib['POINTS'] = " ".join([" ".join([str(i), str(j)]) for i, j in coords])

    if relativeCoordFlag == True:
        continue

    # Save file to XML directory
    xmlData = etree.tostring(altoXML, encoding='utf-8', pretty_print=True, xml_declaration=True)
    with open(altoPath, "wb") as file:
        file.write(xmlData)
print('\rDone.                            ')
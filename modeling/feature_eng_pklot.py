import sys
from fastapi import FastAPI
from sklearn.metrics import mean_squared_error
import warnings
import mlflow
from mlflow.sklearn import load_model
import xml.etree.ElementTree as ET
import cv2
import numpy as np
import os
from torch.utils.data import DataLoader
from torchvision import models, transforms
from torch import nn
import torch
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

warnings.filterwarnings("ignore")


def preprocessor_test(image):
    pass

def show_images_with_boxes(image, xml_path):
    '''
    Reads in an XML with predefined structure.
    The XML contains the coordinates of the boxes.
    OUTPUT:
    Image with not classified boxes on top.
    '''

    # XML-Datei analysieren
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Kopiere das Originalbild für die Anzeige der Boxen
    image_with_boxes = image.copy()

    # Iteriere durch jede Box im XML
    for space in root.iter('space'):
        space_id = int(space.attrib['id'])

        # Extrahiere Koordinaten und Winkel aus XML (Konturkoordinaten)
        contour_points = []
        for point in space.iter('point'):
            x = int(point.attrib['x'])
            y = int(point.attrib['y'])
            contour_points.append((x, y))

        # Konvertiere die Konturpunkte in ein NumPy-Array
        contour_np = np.array(contour_points, dtype=np.int32)
        contour_np = contour_np.reshape((-1, 1, 2))

        # Zeichne ein Rechteck um die Konturpunkte auf dem Bild mit Boxen
        cv2.polylines(image_with_boxes, [contour_np], isClosed=True, color=(255, 0, 0), thickness=2)

        # Extrahiere Winkel aus XML
        try:
            angle = float(space.find('./rotatedRect/angle').attrib['d'])
        except (AttributeError, ValueError):
            # Falls angle nicht extrahiert werden kann oder ein ValueError auftritt, setze angle auf 0
            angle = 0.0

        # Extrahiere Zentrum aus XML
        center_x = float(space.find('./rotatedRect/center').attrib['x'])
        center_y = float(space.find('./rotatedRect/center').attrib['y'])
        center = (center_x, center_y)

        # Beschrifte das Bild mit der Box-ID
        cv2.putText(image_with_boxes, str(space_id), (int(center_x), int(center_y) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

    # Anzeigen des Bildes mit den eingezeichneten Boxen im Output
    plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def crop_images(image, xml_path):
    '''
    Reads the attributes of detected bounding boxes from the xml.
    Cuts the bounding boxes from the image.
    OUTPUT:
    to_classify - list with coordinates of the boxes
    image_with_boxes - original image with boxes on top. 
    
    '''

    # XML-Datei analysieren
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Leeres Array für die ausgeschnittenen Boxen
    to_classify = []

    # Kopiere das Originalbild für die Anzeige der Boxen
    image_with_boxes = image.copy()

    # Iteriere durch jede Box im XML
    for space in root.iter('space'):
        space_id = int(space.attrib['id'])

        # Extrahiere Koordinaten und Winkel aus XML (Konturkoordinaten)
        contour_points = []
        for point in space.iter('point'):
            x = int(point.attrib['x'])
            y = int(point.attrib['y'])
            contour_points.append((x, y))

        # Konvertiere die Konturpunkte in ein NumPy-Array
        contour_np = np.array(contour_points, dtype=np.int32)
        contour_np = contour_np.reshape((-1, 1, 2))

        # Zeichne ein Rechteck um die Konturpunkte auf dem Bild mit Boxen
        cv2.polylines(image_with_boxes, [contour_np], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Extrahiere Winkel aus XML
        try:
            angle = float(space.find('./rotatedRect/angle').attrib['d'])
        except (AttributeError, ValueError):
            # Falls angle nicht extrahiert werden kann oder ein ValueError auftritt, setze angle auf 0
            angle = 0.0
        
        # Extrahiere Zentrum aus XML
        center_x = float(space.find('./rotatedRect/center').attrib['x'])
        center_y = float(space.find('./rotatedRect/center').attrib['y'])
        center = (center_x, center_y)

        # Berechne die Rotationsmatrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Rotiere das Bild
        rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

        # Schneide die Box aus dem rotierten Bild aus
        rect = cv2.boundingRect(contour_np)
        box_image = rotated_image[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]

        # Füge die ausgeschnittene Box zur Liste hinzu
        to_classify.append({'image': box_image, 'id': space_id, 'contour': contour_np})
        
        # Beschrifte das Bild mit der Box-ID
        cv2.putText(image_with_boxes, str(space_id), (rect[0], rect[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

    # # Anzeigen des Bildes mit den eingezeichneten Boxen im Output
    # plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()

    return to_classify, image_with_boxes

# Helper functions
def create_xml(image):
    ''' 
    Creates an XML file with recognized boxes.
    '''
    pass

import os
import xml.etree.ElementTree as ET
from crop import crop
import numpy as np

vocPath = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'dataset'))

class objInfo():
    """
    objInfo saves the information of an object, including its class num, its cords
    """
    def __init__(self,x,y,h,w,class_num):
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.class_num = class_num

class Cell():
    """
    A cell is a grid cell of an image, it has a boolean variable indicating whether there are any objects in this cell,
    and a list of objInfo objects indicating the information of objects if there are any
    """
    def __init__(self):
        self.has_obj = False
        self.objs = []

class image():
    """
    Args:
       side: An image is divided into side*side grids
    Each image class has two variables:
       imgPath: the path of an image on my computer
       bboxes: a side*side matrix, each element in the matrix is cell
    """
    def __init__(self,side,imgPath):
        self.imgPath = imgPath
        self.boxes = []
        for i in range(side):
            rows = []
            for j in range(side):
                rows.append(Cell())
            self.boxes.append(rows)

    def parseXML(self,xmlPath,labels,side):
        """
        Args:
          xmlPath: The path of the xml file of this image
          labels: label names of pascal voc dataset
          side: an image is divided into side*side grid
        """
        tree = ET.parse(xmlPath)
        root = tree.getroot()

        width = int(root.find('size').find('width').text)
        height = int(root.find('size').find('height').text)

        for obj in root.iter('object'):
            class_num = labels.index(obj.find('name').text)
            bndbox = obj.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)
            objif = objInfo(xmin/448.0,ymin/448.0,np.sqrt(ymax-ymin)/448.0,np.sqrt(xmax-xmin).448.0,class_num)

            #which cell this obj falls into
            centerx = (xmax+xmin)/2
            centery = (ymax+ymin)/2
            newx = (448.0/width)*centerx
            newy = (448.0/height)*centery


            cell_size = 448.0/side
            row = int(newx / cell_size)
            col = int(newy / cell_size)

            self.boxes[row][col].has_obj = True
            self.boxes[row][col].objs.append(objif)

def prepareBatch(start,end,imageNameFile,vocPath):
    """
    Args:
      start: the number of image to start
      end: the number of image to end
      imageNameFile: the path of the file that contains image names
      vocPath: the path of pascal voc dataset
    Funs:
      generate a batch of images from start~end
    Returns:
      A list of end-start+1 image objects
    """
    imageList = []
    labels = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train","tvmonitor"]
    file = open(imageNameFile)
    imageNames = file.readlines()
    for i in range(start,end):
        imgName = imageNames[i].strip('\n')
        imgPath = os.path.join(vocPath,'JPEGImages',imgName)+'.jpg'
        xmlPath = os.path.join(vocPath,'Annotations',imgName)+'.xml'
        img = image(side=7,imgPath=imgPath)
        img.parseXML(xmlPath,labels,7)
        imageList.append(img)

    return imageList

#Prepare training data
def generate_batch_data(vocPath,imageNameFile):
    """
    Args:
      vocPath: the path of pascal voc data
      imageNameFile: the path of the file of image names
      batchsize: batch size, sample_number should be divided by batchsize
    Funcs:
      A data generator generates training batch indefinitely
    """
    sample_number = 5000 #use only 5000 images so we have more batchsize choices
    class_num = 20

    while 1:
        for i in range(0,sample_number):
            imageList = prepareBatch(i,i+1,imageNameFile,vocPath)
            image_list = []
            box_list = []

            image_array = crop(imageList[0].imgPath,resize_width=512,resize_height=512,new_width=448,new_height=448)

            y = []
            for i in range(7):
                for j in range(7):
                    box = imageList[0].boxes[i][j]
                    if(box.has_obj):
                        obj = box.objs[0]

                        y.append(obj.x)
                        y.append(obj.y)
                        y.append(obj.h)
                        y.append(obj.w)

                        labels = [0]*20
                        labels[obj.class_num] = 1
                        y.extend(labels)
                    else:
                        y.extend([0]*24)
            y = np.asarray(y)
            #yield images,y

if __name__ == '__main__':
    imageNameFile='/Users/lixueting/Documents/researches/Darknet.keras/dataset/train_val/imageNames.txt'
    vocPath='/Users/lixueting/Documents/researches/Darknet.keras/dataset/train_val'
    '''
    imageList = prepareBatch(0,2,imageNameFile,vocPath)
    for i in range(0,2):
        img = imageList[i]
        print img.imgPath
        boxes = img.boxes
        for i in range(7):
            for j in range(7):
                if(boxes[i][j].has_obj):
                    print i,j
                    objs = boxes[i][j].objs
                    for obj in objs:
                        print obj.class_num
                        print obj.x
                        print obj.y
                        print
    '''
    generate_batch_data(vocPath,imageNameFile)
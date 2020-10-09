# created on Fri 9 Oct 2020
# @author Zubair Khaliq (CS UoK)

from pytesseract import Output
import pytesseract
import json
import cv2
import sys
import os
#for arg in sys.argv:
JSON_FILE = sys.argv[1] #Contains path to json file
INPUT_IMAGE_FILE = sys.argv[2] #A file that contains input image directory path


# This function creates directories to hold intermediate components and complete components
def make_dir(input_path,caption):
    current_dir = os.getcwd()
    #print("Current Directory is " + str(current_dir))
    path = os.path.splitext(os.path.basename(input_path))[0]
    path += caption
    path = os.path.join(current_dir, path)
    #print("path is " + str(path))
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)
    #print("This path is " + str(path))
    return path
#-------------------------------------------------------

#This function extracts file paths from the input text file and returns a list
def extract_path(dir_path):
    lines =[]
    with open(dir_path) as f:
        for line in f:
            line = line.strip()
            lines.append(line)
    #print(lines[0])
    return lines

#-------------------------------------------------------
#This function uses tesseract to extract text from intermediate components
def tesse(tesse_path,dest_path):
    # construct the argument parser and parse the arguments

    # load the input image, convert it from BGR to RGB channel ordering,
    # and use Tesseract to localize each area of text in the input image
    for filename in os.listdir(tesse_path):
        #print("------" + tesse_path + "---------")
        image = cv2.imread(tesse_path + filename)
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(image, output_type=Output.DICT)



        # loop over each of the individual text localizations
        for i in range(0, len(results["text"])):
            # extract the bounding box coordinates of the text region from
            # the current result
            x = results["left"][i]
            y = results["top"][i]
            w = results["width"][i]
            h = results["height"][i]

            # extract the OCR text itself along with the confidence of the
            # text localization
            text = results["text"][i]
            conf = int(results["conf"][i])

            # filter out weak confidence text localizations
            if conf > 0:
                # display the confidence and text to our terminal
                #print("Confidence: {}".format(conf))
                #print("Text: {}".format(text))
                #print("")

                # strip out non-ASCII text so we can draw the text on the image
                # using OpenCV, then draw a bounding box around the text along
                # with the text itself
                text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 0, 0), 3)

        # show the output
        #print("------" + dest_path + "---------")
        cv2.imwrite(dest_path +"/"+ filename, image)
        # cv2.imshow('image',image)
        # cv2.waitKey(0)

#------------------------------------------------------------------------------

#This function crops the components from the input images
def cropping(FILE, INPUT): #Funtion to crop image and return multiple cropped images
    with open(FILE) as json_file:
        data = json.load(json_file)


    # Output will be stored in a folder named with the Naive_filename and each output component is number named

    for filename in sorted(INPUT):
        z=int(os.path.splitext(os.path.basename(filename))[0])-1
        #print("Value of z is = "+str(z))
        path = make_dir(str(data[z]["filename"]), "_Naive") #Directory to hold intermediate components
        path1 = make_dir(str(data[z]["filename"]), "_Complete")#Directory to hold final captioned components
        #print(INPUT,filename)
        img = cv2.imread(filename)
        dimensions = img.shape
        HEIGHT = str(dimensions[0])  # height of image
        WIDTH = str(dimensions[1])  # width of image
        for i in range(0,len(data[z]["objects"])):
            name = data[z]["objects"][i]["name"]
            width = int(abs(data[z]["objects"][i]["relative_coordinates"]["width"]*int(WIDTH)))
            height = int(abs(data[z]["objects"][i]["relative_coordinates"]["height"]*int(HEIGHT)))
            center_x = int(abs((data[z]["objects"][i]["relative_coordinates"]["center_x"]*int(WIDTH))-(width/2)))
            center_y = int(abs((data[z]["objects"][i]["relative_coordinates"]["center_y"]*int(HEIGHT))-(height/2)))

            #print(center_x,center_y,width, height)
            crop_img = img[center_y:center_y + height, center_x:center_x + width]
            cv2.imwrite(path + "/" + str(i) + '.jpg', crop_img)
        tesse(path + "/",path1)



if __name__ == "__main__":
    INPUT_DIR = extract_path(INPUT_IMAGE_FILE)
    cropping(JSON_FILE, INPUT_DIR)
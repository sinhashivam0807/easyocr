from flask import Flask, jsonify,request
from flask_cors import CORS
import json
import easyocr
import PIL
import cv2
import re
import datetime
import cv2
import base64
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("API_KEY")

def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
    ]
    return roi_cropped

def extractnumber(date):
    data=""
    date_out=""
    for i in range(len(date)):
        data+=date[i]
    for s in range(len(data)):
        if(data[s].isnumeric()):
            date_out+=data[s]
    return date_out

def dateformatter(date):
    s=""
    for i in range(len(date)):
        s+=date[i]
        if(i==3 or i==5):
            s+="-"
    return s

def ocr_output():
    # Load Image
    img=cv2.imread("testimage.png")
    img=cv2.resize(img,(1170,733))
    #ROI Selection
    roi_bdate=(427,447,297,108)
    bdate_img=cropImageRoi(img, roi_bdate)
    
    roi_idate=(426,567,262,103)
    idate_img=cropImageRoi(img, roi_idate)
    
    roi_edate=(691,564,257,107)
    edate_img=cropImageRoi(img, roi_edate)
    
    roi_name=(398,201,724,245)
    name_img=cropImageRoi(img, roi_name)

    roi_sex=(742, 489, 100,70)
    sex_img=cropImageRoi(img, roi_sex)

    roi_sign= (82,607,323,123)
    sign_img=cropImageRoi(img, roi_sign)
    #OCR Reader
    reader= easyocr.Reader(['en'],gpu=False)

    birth_date = reader.readtext(bdate_img, detail=0) 
    expiry_date = reader.readtext(edate_img, detail=0)
    issue_date = reader.readtext(idate_img, detail=0)
    name = reader.readtext(name_img, detail=0)
    sex_data= reader.readtext(sex_img, detail=0)

    birth_date=extractnumber(birth_date)
    birth_date=dateformatter(birth_date)

    issue_date=extractnumber(issue_date)
    issue_date=dateformatter(issue_date)

    expiry_date=extractnumber(expiry_date)
    expiry_date=dateformatter(expiry_date)

    name_list=[]
    for i in range(len(name)):
        if(name[i].isupper()):
            name_list.append(name[i])

    healthid_string=""
    if(len(name)==4):
        healthid_string+=name[3]
    elif(len(name)==3):
        healthid_string+=name[2]
    else:
        for i in range(len(name)):
            if(name[i].isnumeric()):
                for s in range(i,len(name)):
                    healthid_string+=name[s]
                    if(s<(len(name)-1)):
                        healthid_string+="-"
                break

    cv2.imwrite("sign.png", sign_img);
    with open("sign.png", "rb") as image_file:
        sign = base64.b64encode(image_file.read()).decode('utf-8')

    sex=""
    for i in range(len(sex_data)):
        if(sex_data[i]=="M" or sex_data=="F"):
            sex+=sex_data[i]
            break

    json_data={}
    json_data["name"]=name_list[0]
    json_data["healthcard-id"]=healthid_string
    json_data["birth_date"]=birth_date
    json_data["issue_date"]=issue_date
    json_data["expiry_date"]=expiry_date
    json_data["sex"]=sex
    json_data["signature"]=sign
    
    json_obj=jsonify(json_data)
    return(json_obj)


app= Flask(__name__)
CORS(app)

@app.route('/autofillform', methods = ['POST'])
def ReturnJSON():
    try:
        if request.method == "POST":
            img2get=(request.json.get('image'))
            with open("testimage.png", "wb") as fh:
                fh.write(base64.b64decode(img2get))
        if(request.headers.get('API_KEY')==API_KEY):
            try:
                return (ocr_output())
            except:
                error={"error":"Unable to extract data"}
                return jsonify(error)
        else:
            error={"error":"authorization error"}
            return jsonify(error)
    except:
        error={"error":"Bad request"}
        return jsonify(error)


if __name__ == '__main__':
    app.run(debug=True,ssl_context="adhoc")

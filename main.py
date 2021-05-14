import streamlit as st
import io
#import json
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

st.title('顔認識アプリ試作（MS-Azure版）')

#ローカル環境用のサブスクリプションキー取得
#with open('secrets.toml') as f:
#    test_toml = toml.load(f)
#    subscription_key = test_toml['secrets']['SUBSCRIPTION_KEY']
#assert subscription_key
#with open('secret.json') as f:
#    test_json = json.load(f)
#    subscription_key = test_json['SUBSCRIPTION_KEY']
#assert subscription_key

#公開環境用のサブスクリプションキー取得（streamlit公開サイトの環境変数として設定したものを取得する）
subscription_key = st.secrets['SUBSCRIPTION_KEY']
assert subscription_key

face_api_url = 'https://abe20210512.cognitiveservices.azure.com/face/v1.0/detect'
upload_file = st.file_uploader("顔の写真をアップロードしてみ")
if upload_file is not None:
	img = Image.open(upload_file)
	with io.BytesIO() as output:
		img.save(output,format="PNG")
		binary_img = output.getvalue()
	headers = {
		'Content-Type' : 'application/octet-stream',
		'Ocp-Apim-subscription-Key'  : subscription_key   
	}
	params = {
		'returnFaceId': 'true',
		'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion'     
	}
	res = requests.post(face_api_url, params=params,headers=headers, data=binary_img)
	results = res.json()
	for result in results:
		rect = result['faceRectangle']
		attr = result['faceAttributes']
		age = int(attr['age'])
		if attr['gender'] == "male":
			gender = "男"
		else:
			gender = "女"
		anger  = int(attr['emotion']['anger']*100)
		happiness  = int(attr['emotion']['happiness']*100)
		sadness  = int(attr['emotion']['sadness']*100)
		surprise  = int(attr['emotion']['surprise']*100)
		fear  = int(attr['emotion']['fear']*100)
		neutral  = int(attr['emotion']['neutral']*100)   
		if attr['makeup']['eyeMakeup']:
			eyeMakeup = "化粧"
		else:
			eyeMakeup = "スッピン"
		if attr['makeup']['lipMakeup']:
			lipMakeup = "化粧"
		else:
			lipMakeup = "スッピン"  
		text = "[性]"+str(gender)+" "+"[齢]"+str(age)+"才"+"\n"+"[怒]"+str(anger)+"%"+" "+"[楽]"+str(happiness)+"%"+"\n"+"[悲]"+str(sadness)+"%"+" "+"[驚]"+str(surprise)+"%"+"\n"+"[恐]"+str(fear)+"%"+" "+"[平]"+str(neutral)+"%"+"\n"+"[目]"+str(eyeMakeup)+" "+"[口]"+str(lipMakeup)+"\n"
		#フォントサイズを動的に変える
		ttfontname = "./font/HannariMincho-Regular.otf"
		fontsize=int(rect['width']/6)
		if fontsize >= 9:
			fontsize = 9       
		fnt = ImageFont.truetype(ttfontname, fontsize)
		draw = ImageDraw.Draw(img)
		draw.text((rect['left'],rect['top']-fontsize*7.3),text, font=fnt, fill='yellow')
		draw.rectangle([(rect['left'],rect['top']),(rect['left']+rect['width'],rect['top']+rect['height'])],fill=None,outline='green',width=3)

	st.image(img,caption='Uploaded Image', use_column_width=True)
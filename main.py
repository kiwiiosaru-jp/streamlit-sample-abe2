import streamlit as st
import io
#import json
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account

st.title('AI画像分析アプリ(byしげる)')

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
#画像縮小率を設定
df = pd.DataFrame({
  #'fst_column': ["PCからアップロード(1倍)", "スマホからアップロード(1/2倍)","1/3倍","1/4倍","1/5倍","1/6倍","1/7倍","1/8倍","1/9倍","1/10倍"],
  #'snd_column': [1,2,3,4,5,6,7,8,9,10]
  #'fst_column': ["PCからアップロード(100%)", "スマホからアップロード(75%)", "スマホからアップロード(60%)", "スマホからアップロード(50%)"],
  'fst_column': ["スマホからアップロード(画像サイズ50%縮小)","PCからアップロード(画像サイズ100%)"],
  #'snd_column': [3,4,5,6]
  'snd_column': [6,3]
})
option = st.selectbox(
    '写真の縮小倍率を選択',
     df['fst_column'])
#'You selected: ', option
if option == df['fst_column'][0]:
	trn_num = df['snd_column'][0]
elif option == df['fst_column'][1]:
	trn_num = df['snd_column'][1]
#elif option == df['fst_column'][2]:
#	trn_num = df['snd_column'][2]
#elif option == df['fst_column'][3]:
#	trn_num = df['snd_column'][3]
#elif option == df['fst_column'][4]:
#	trn_num = df['snd_column'][4]
#elif option == df['fst_column'][5]:
#	trn_num = df['snd_column'][5]
#elif option == df['fst_column'][6]:
#	trn_num = df['snd_column'][6]
#elif option == df['fst_column'][7]:
#	trn_num = df['snd_column'][7]
#elif option == df['fst_column'][8]:
#	trn_num = df['snd_column'][8]
#elif option == df['fst_column'][9]:
#	trn_num = df['snd_column'][9]
else :
	trn_num = 3

upload_file = st.file_uploader("スマホで写真撮ってアップロードしてみ")
if upload_file is not None:
	img = Image.open(upload_file)
	
	#画像縮小処理
	img_resize = img.resize((img.width * 3, img.height * 3))
	img_resize = img_resize.resize((img_resize.width // trn_num, img_resize.height // trn_num))
	img = img_resize

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
		if option == df['fst_column'][0]:
			fontsize = 32
				
		fnt = ImageFont.truetype(ttfontname, fontsize)
		draw = ImageDraw.Draw(img)
		draw.text((rect['left'],rect['top']-fontsize*7.3),text, font=fnt, fill='white')
		draw.rectangle([(rect['left'],rect['top']),(rect['left']+rect['width'],rect['top']+rect['height'])],fill=None,outline='green',width=3)

	st.image(img,caption='Uploaded Image', use_column_width=True)
	#st.write(fontsize)
	#st.write(option)
	#st.write(df['fst_column'][1])

#グーグルのAIで画像の認識結果を取得する
#from google.cloud import vision
#with open('./img/nuts.jpg','rb') as image_file:
#	content = image_file.read()
	#グーグル認証情報セット
	service_account_key = {
	  "type": st.secrets['google_vision_api_type'],
	  "project_id": st.secrets['google_vision_api_project_id'],
	  "private_key_id": st.secrets['google_vision_api_private_key_id'],
	  "private_key": st.secrets['google_vision_api_private_key'],
	  "client_email": st.secrets['google_vision_api_client_email'],
	  "client_id": st.secrets['google_vision_api_client_id'],
	  "auth_uri": st.secrets['google_vision_api_auth_uri'],
	  "token_uri": st.secrets['google_vision_api_token_uri'],
	  "auth_provider_x509_cert_url": st.secrets['google_vision_api_auth_provider_x509_cert_url'],
	  "client_x509_cert_url": st.secrets['google_vision_api_client_x509_cert_url'],
	  }
	credentials = service_account.Credentials.from_service_account_info(service_account_key)
	scoped_credentials = credentials.with_scopes(
	  [
	    'https://www.googleapis.com/auth/cloud-platform',
	    'https://www.googleapis.com/auth/analytics.readonly'
	  ])

	content = binary_img
	image = vision.Image(content = content)
	#ImageAnnotatorClientのインスタンスを生成
	annotator_client = vision.ImageAnnotatorClient(credentials=scoped_credentials)
	response_data = annotator_client.label_detection(image=image)
	labels = response_data.label_annotations
	st.write("----画像分析結果----")
	for label in labels:
		#print(label.description, ':', round(label.score * 100, 2), '%')
		#st.write(label)
		st.write(label.description, ':', round(label.score * 100, 2), '%')
	st.write("----でした！----")
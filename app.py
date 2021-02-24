import numpy as np

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)

#from keras.models import load_model
#from keras.preprocessing import image

# TensorFlow cpu == 2.3.1
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
#model = load_model("resnet50_imagenet.h5")
model = load_model('ResNet_32.h5')

import pandas as pd
import os

app = Flask(__name__)

ACCESS_TOKEN = "VzJxMa7DiVPzf3Z1y9+4OOIDBmRzhCdE3DHy/rkjGoSjoYhujyNxYLPOlji+uBgPZlcoGGv6RoTlZJ/IcJKGg2dAQV9AKIBAOM4RfGFxFHFq7g/IgS3WbMUCZz+/gv1IiZNhOTIHuJMpVquPWEv6NQdB04t89/1O/w1cDnyilFU="
SECRET = "4b4400f6e9a2fe31bb19fb5525b73d58"

#FQDN = "https://cats-vs-dogs-line-bot-naoya.herokuapp.com/callback"
FQDN = "https://udon-ai-bot.herokuapp.com/callback"

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Requestbody: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)

    # 取得した画像ファイル
    with open("data/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)
        

        test_url = "./data/"+event.message.id+".jpg"

        #img = image.load_img(test_url, target_size=(224, 224)) # read image as PIL data
        img = image.load_img(test_url, target_size=(160, 160)) # read image as PIL data
        x = image.img_to_array(img) # convert PIL data to Numpy Array
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        # モデルのロード
        try:

            predict = model.predict(x).flatten()

            classnames = ["000_suzaki-shokuryohinten_mitoyo", "001_gamou_sakaide",
                          "002_nagata-in-kanoka_zentsuji","003_hinode-seimenjo_sakaide",
                          "004_tamura_ayagawa","005_setobare_takamatsu",
                          "006_hayuka_ayagawa","007_ippuku_takamatsu","008_tanigawa-beikokuten_mannou",
                          "009_mugizou_takamatsu","010_miyoshi-udon_mitoyo","011_ookura_takamatsu",
                          "012_yamagoe_ayagawa","013_okasen_utazu",
                          "014_nakamura-udon_marugame","015_yoshiya_marugame",
                          "016_kamakiri_kanonji","017_joto_kanonji",
                          "018_nekko_tadotsu","019_yamadaya_takamatsu"]
            index = np.argmax(predict)
            label = classnames[index]

            #text = f"cat = {cat_score}\ndog = {dog_score}"

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=label))

        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="failed"))


        #line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=FQDN+"/static/"+event.message.id+".jpg",preview_image_url=FQDN+"/static/"+event.message.id+".jpg"))
        

if __name__ == "__main__":
    app.run()    

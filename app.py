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
model = load_model("resnet50_imagenet.h5")

import pandas as pd


import json
json_open = open("imagenet_class_index.json", 'r')
imagenet_classnames = json.load(json_open)



app = Flask(__name__)

ACCESS_TOKEN = "funnwkyG6dVjtWrCBlEJNd8vzh4I2L/35FthW4SI1Fpc+ocLRl+h8/xu9MyzjlpdEGDNjnZGJ5O/BYZUeGTmioKLjnL5K/pIadduCoThujr3ORGqtgMM0J7pfpA6MV5FrUntqHVY/tsXKyeJu5YZ2wdB04t89/1O/w1cDnyilFU="
SECRET = "115282a59614943423975ca52779a2a6"

FQDN = "https://cats-vs-dogs-line-bot-naoya.herokuapp.com/callback"


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
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)
        

        test_url = "./static/"+event.message.id+".jpg"

        img = image.load_img(test_url, target_size=(224, 224)) # read image as PIL data
        x = image.img_to_array(img) # convert PIL data to Numpy Array
        x = np.expand_dims(x, axis=0)
        #x = x / 255.0
        # モデルのロード
        try:
            #model = load_model('dog_cat.h5')
            #model = load_model('dogs_vs_cats_model_combo.h5')

            predict = model.predict(x).flatten()
            #text = str(float(predict[0]))

            #cat_score = str(round(float(predict[0]), 3)*100)
            #dog_score = str(round(float(predict[1]), 3)*100)

            #classnames = ["ねこ", "いぬ"]
            #index = np.argmax(predict)
            #label = classnames[index]

            #text = f"cat = {cat_score}\ndog = {dog_score}"
            #text = f"これは{label}です。\nねこ確率{cat_score}%\nいぬ確率{dog_score}%"
            
            df = pd.DataFrame()
            df["index"] = np.arange(1000)
            df["predict"] = predict
            df = df.sort_values("predict", ascending=False)

            text = "これは\n"
            for i in range(5):
                label = imagenet_classnames[df.index[i]]
                label_ja = label["ja"]
                conf = df.iloc[i, 1]*100
                text += f"  {label_ja} {conf:.1f}%\n"
            text += "です。"

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="failed"))


        #line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=FQDN+"/static/"+event.message.id+".jpg",preview_image_url=FQDN+"/static/"+event.message.id+".jpg"))
        

if __name__ == "__main__":
    app.run()

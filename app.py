from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
#from keras_applications.imagenet_utils import _obtain_input_shape
import numpy as np
from PIL import Image
#import matplotlib.pyplot as plt
#import argparse
from PIL.ImagePalette import load
from keras.models import Model, load_model
from pickle import dump, load
#import string
#import os
#from tqdm import tqdm
from keras.applications.xception import Xception, preprocess_input
#from keras.preprocessing.image import load_img, img_to_array
#from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
#from keras.utils import to_categorical
#from keras.layers.merge import add
#from keras.layers import Input, Dense, LSTM, Embedding, Dropout


def extract_features(filename, model):
    try:
        image = Image.open(filename)

    except:
        print(
            "ERROR: Couldn't open image! Make sure the image path and extension is correct")
    image = image.resize((299, 299))
    image = np.array(image)
    # for images that has 4 channels, we convert them into 3 channels
    if image.shape[2] == 4:
        image = image[..., :3]
    image = np.expand_dims(image, axis=0)
    image = image/127.5
    image = image - 1.0
    feature = model.predict(image)
    return feature


def word_for_id(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None


def generate_desc(model, tokenizer, photo, max_length):
    in_text = ''
    for _ in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_length)
        pred = model.predict([photo, sequence], verbose=0)
        pred = np.argmax(pred)
        word = word_for_id(pred, tokenizer)
        if word is None:
            break
        in_text += ' ' + word
        if word == 'end':
            break
    return in_text


max_length = 32


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Skg@123!@localhost/flask_learning'
db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), unique=False, nullable=False)
    lname = db.Column(db.String(50), unique=False, nullable=False)
    contact = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    msg = db.Column(db.String(100), unique=False, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/contactus', methods=['GET', 'POST'])
def contactus():

    if(request.method == 'POST'):
        f_name = request.form.get('firstname')
        l_name = request.form.get('lastname')
        contactus = request.form.get('telnum')
        emailid = request.form.get('emailid')
        feedback = request.form.get('feedback')

        entry = Contact(fname=f_name, lname=l_name,
                        contact=contactus, email=emailid, msg=feedback)
        db.session.add(entry)
        db.session.commit()

    return render_template('contactus.html')


@app.route('/', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        file = request.files['file1']
        img_path = "./static/files.jpg"
        file.save(img_path)
        tokenizer = load(open("tokenizer.p", "rb"))
        model = load_model('models/model_9.h5')
        xception_model = Xception(include_top=False, pooling="avg")
        photo = extract_features(img_path, xception_model)
        img = Image.open(img_path)

        description = generate_desc(model, tokenizer, photo, max_length)

        '''result_dic = {
            'img_path': img_path,
            'caption': description
        }'''

    return render_template('index.html', desc=description)


app.run(debug=True)

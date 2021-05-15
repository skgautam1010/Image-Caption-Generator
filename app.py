from flask import Flask,render_template,request,redirect


app=Flask(__name__)


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/prediction',methods=['GET','POST'])
def prediction():
    file=request.files['file1']
    file.save('static/file.jpg')

    return render_template('predict.html')



if __name__=="__main__":
    app.run(debug=True)
from flask import Flask, render_template


app = Flask(__name__)




#definition du route principale 
@app.route("/")


#appelle de la appelle page html pour son affichage 

@app.route("/App")
def home1():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)

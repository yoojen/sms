import os
from flask import (Flask, flash, request, redirect, url_for,
                   send_from_directory, render_template)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'E:/MY STUFFS/PROJECTS/sms/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'E:/MY STUFFS/PROJECTS/sms/uploads'
app.secret_key = 'eugene'
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url = request.url
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and not allowed_file(file.filename):
            print("not allowed extension")
            flash("not allowed extension")
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                return redirect(url_for('/'))
                # return redirect(url_for('download_file', name=filename))
    return render_template('index.html')


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    app.run(debug=True)

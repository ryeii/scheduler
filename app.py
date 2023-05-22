from flask import Flask, request, send_file, redirect, url_for, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename
from scheduler import Scheduler

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route('/')
def home():
    # if no upload or download folder, create them
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    with open('log.txt', 'r') as f:
        log_content = f.read()
    
    # if there is no file in the upload folder
    if not os.listdir(UPLOAD_FOLDER):
        message = 'No file uploaded yet. Please upload a file to start.'
    else:
        message = 'Scheduling Succeeded! 1. check the log below for its schedule result. 2. upload a new file to start a new schedule (erase the existing file).'

    return render_template('index.html', log_content=log_content, message=message)

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ok = process_file(filename)
        if ok:
            # if there are more than one file in the upload folder, delete the other one (the previous one)
            for file in os.listdir(UPLOAD_FOLDER):
                if file != filename:
                    os.remove(UPLOAD_FOLDER+file)
            return redirect(url_for('home'))
        else:
            # if the file is not accepted, delete it
            os.remove(UPLOAD_FOLDER+filename)
            return render_template('error.html', error_message='The file you provided was not accepted. Please check the input file format and try again.')

def process_file(filename):
    # Read the file using pandas
    scheduler = Scheduler(UPLOAD_FOLDER+filename)
    ret = scheduler.schedule(DOWNLOAD_FOLDER+'result.xlsx')
    return ret

@app.route('/download_result')
def download_result():
    # if no downloads/result.xlsx, return no file
    if not os.path.exists(DOWNLOAD_FOLDER+'result.xlsx'):
        return 'No file'
    return send_file(DOWNLOAD_FOLDER+'result.xlsx', as_attachment=True)

@app.route('/download_input_file')
def download_input():
    # if no downloads/result.xlsx, return no file
    if not os.path.exists(UPLOAD_FOLDER+'course_scheduling.xlsx'):
        return 'No file'
    return send_file(UPLOAD_FOLDER+'course_scheduling.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

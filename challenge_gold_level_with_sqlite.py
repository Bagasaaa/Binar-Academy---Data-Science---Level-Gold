##### FROM LINE 5 UNTIL 316 IS JUST A FLASK #####

##### FROM LINE 323 UNTIL 586 IS FLASK + SWAGGER UI. The URL : http://127.0.0.1:5000/docs/ #####

# Importing Library
import sqlite3
import os
from flask import Flask, flash, request, redirect, url_for, render_template, Markup, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
import pandas as pd
import re

# Remove Stopwords
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.corpus.stopwords.words('indonesian')

# Swagger
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__, template_folder='templates')
app.secret_key = 'bagas_data_science'

# Function to cleaning the data
def cleansing(text):
    # Make sentence being lowercase
    text = text.lower()

    # Remove user, rt, \n, retweet, \t, url, xd
    pattern_1 = r'(user|retweet|\\t|\\r|url|xd|orang|kalo)'
    text = re.sub(pattern_1, '', text)

    # Remove mention
    pattern_2 = r'@[^\s]+'
    text = re.sub(pattern_2, '', text)

    # Remove hashtag
    pattern_3 = r'#([^\s]+)'
    text = re.sub(pattern_3, '', text)

    # Remove general punctuation, math operation char, etc.
    pattern_4 = r'[\,\@\*\_\-\!\:\;\?\'\.\"\)\(\{\}\<\>\+\%\$\^\#\/\`\~\|\&\|]'
    text = re.sub(pattern_4, ' ', text)

    # Remove single character
    pattern_5 = r'\b\w{1,3}\b'
    text = re.sub(pattern_5, '', text)

    # Remove emoji
    pattern_6 = r'\\[a-z0-9]{1,5}'
    text = re.sub(pattern_6, '', text)

    # Remove digit character
    pattern_7 = r'\d+'
    text = re.sub(pattern_7, '', text)

    # Remove url start with http or https
    pattern_8 = r'(https|https:)'
    text = re.sub(pattern_8, '', text)

    # Remove (\); ([); (])
    pattern_9 = r'[\\\]\[]'
    text = re.sub(pattern_9, '', text)

    # Remove character non ASCII
    pattern_10 = r'[^\x00-\x7f]'
    text = re.sub(pattern_10, '', text)

    # Remove character non ASCII
    pattern_11 = r'(\\u[0-9A-Fa-f]+)'
    text = re.sub(pattern_11, '', text)

    # Remove multiple whitespace
    pattern_12 = r'(\s+|\\n)'
    text = re.sub(pattern_12, ' ', text)

    # Remove "wkwkwk"
    pattern_13 = r'\bwk\w+'
    text = re.sub(pattern_13, '', text)
    
    # Remove whitespace at the first and end sentences
    text = text.rstrip()
    text = text.lstrip()
    return text

def replaceThreeOrMore(text):
    # Pattern to look for three or more repetitions of any character, including newlines.
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", text)

indo_stop_words = stopwords.words("indonesian")

def remove_stopwords(text):
    return ' '.join([word for word in word_tokenize(text) if word not in indo_stop_words])

##### FROM LINE 98 UNTIL 309 IS JUST A FLASK

##### FROM LINE 318 UNTIL 586 IS FLASK + SWAGGER UI

@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')

##### READING FILE, SHOW DATFRAME .HTML #####
@app.route("/data_before_cleansing", methods=["GET", "POST"])
def read_file_to_html():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        csv_file = request.files.get("file")
        if not csv_file or not csv_file.filename.endswith('.csv'):
            return 'Invalid file'

    # Read the .csv file into a Pandas dataframe
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()
        conn.close()

        df = df.to_html(index=False, justify='left')

        return Markup(df)

    # If the request method is "GET", render the form template
    return render_template("file.html")


##### UPLOAD FILE #####

@app.route("/data_after_cleansing", methods=["GET", "POST"])
def upload_file():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == "POST":
        csv_file = request.files.get("file")
        if not csv_file or not csv_file.filename.endswith('.csv'):
            return 'Invalid file'

    # Read the .csv file into a Pandas dataframe
        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()

    # Apply the cleansing function to each cell in the dataframe
        df = df.select_dtypes(include=['object']).applymap(cleansing)

    # Replace three or more repetitions of any character with two repetitions
        df_clean = df.applymap(replaceThreeOrMore)

    # define stopwords in Indonesian
        indo_stop_words = stopwords.words("indonesian")

    # Apply the function to all string columns in the dataframe
        table = df_clean.applymap(remove_stopwords)

    # Convert the dataframe to an HTML table
        # Replace the existing table with the cleaned data
        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        table = table.to_sql('challenge_cleaned', conn, if_exists='replace') # to prove that this code is running well, drop the "challenge_cleaned" table from the database via the app_sqlite.py file
        conn.close()

    # Return the HTML table as the response to the form submission
        table_2 = df_clean.select_dtypes(include=['object']).applymap(remove_stopwords)
        table_2 = table_2.to_html()
        return Markup(table_2)

  # If the request method is "GET", render the form template
    return render_template("file.html")


##### UPLOAD FILE CSV, CLEAN IT AUTOMATICALLY, AND DOWNLOAD IT #####
UPLOAD_FOLDER = "C:/Users/Acer/Downloads" # PATH DIRECTORY FOR DOWNLOADED CLEAN .CSV FILE
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/upload_download_file', methods=['GET', 'POST'])
def upload_download_file():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # Read the .csv file into a Pandas dataframe
        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()

        # Apply the cleansing function to each cell in the dataframe
        df = df.select_dtypes(include=['object']).applymap(cleansing)

        # Replace three or more repetitions of any character with two repetitions
        df_clean = df.applymap(replaceThreeOrMore)

        # Function to remove stopwords
        def remove_stopwords(text):
            return ' '.join([word for word in word_tokenize(text) if word not in indo_stop_words])

        # Apply the function to all string columns in the dataframe
        table = df_clean.select_dtypes(include=['object']).applymap(remove_stopwords)

        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        table = table.to_sql('upload_and_download_csv_file', conn, if_exists='replace') # to prove that this code is running well, drop the "upload_and_download_csv_file" table first from the database via the app_sqlite.py file
        conn.commit()

        df_cleaned = df_clean.to_csv("nama_file.csv", index=False, encoding='latin-1')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            df_clean.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], "data_clean.csv"), index=False, encoding='latin-1')
            conn.close()
            flash('The file has been downloaded to the "C-Users-Acer-Downloads" directory as data_clean.csv')
            return redirect(url_for('upload_download_file', name=df_cleaned))
    return render_template('download_file.html')

##### CLEANSING DATA BY INDEX NUMBER OF 'TWEET' COLUMN ##### 
@app.route("/cleansing_tweet_column", methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        # get the value of the 'row' field from the form data
        before = request.form.get('before')

        # convert the 'row' value to an integer
        before = int(before)

        # select the row using the 'before' value, then apply cleansing function
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()
        values_data = df[['tweet']].iloc[before].apply(cleansing)

        # apply replaceThreeOrMore function to variable values_data
        values_data = values_data.apply(replaceThreeOrMore)

        # define stopwords in Indonesian
        indo_stop_words = stopwords.words("indonesian")

        # Function to remove stopwords
        def remove_stopwords(text):
            return ' '.join([word for word in word_tokenize(text) if word not in indo_stop_words])

        # Apply the function to all string columns in the dataframe
        table = values_data.apply(remove_stopwords)

        # format the values_data to list
        values_str = table.to_list()

        # select the row using the 'row' value
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()
        before_data = df[['tweet']].iloc[before]

        # format the values to list
        before_pre = before_data.to_list()
        conn.close()

        return redirect(url_for("by_index", clean=values_str, before=before_pre))

    return render_template("index_2.html")


@app.route("/by_index", methods=['GET'])
def by_index():
    clean = request.args.get('clean')
    before = request.args.get('before')
    return f'''
    TWEET BEFORE PREPROCESSING (CLEANSING): <br> <br> {before} <br> <br> <br> <br> <br>
    TWEET AFTER PREPROCESSING (CLEANSING): <br> <br> {clean}
    '''

##### PREPROCESSING TEXT (INPUT TEXT) #####
@app.route("/text_cleansing", methods=['GET', 'POST'])
def clean():
    if request.method == 'POST':
        tweet = request.form['tweet']
        clean_text = cleansing(tweet)
        result = replaceThreeOrMore(clean_text)
            
        return redirect(url_for("cleansing", text=result))

    return render_template("input_text.html")

@app.route("/<text>", methods=['GET'])
def cleansing(text):
    return f'Cleansing result: {text}'



##### -------------------------------------SWAGGER---------------------------------------- #####


app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flagger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

def cleansing(text):
    # Make sentence being lowercase
    text = text.lower()

    # Remove user, rt, \n, retweet, \t, url, xd
    pattern_1 = r'(user|retweet|\\t|\\r|url|xd|orang|kalo)'
    text = re.sub(pattern_1, '', text)

    # Remove mention
    pattern_2 = r'@[^\s]+'
    text = re.sub(pattern_2, '', text)

    # Remove hashtag
    pattern_3 = r'#([^\s]+)'
    text = re.sub(pattern_3, '', text)

    # Remove general punctuation, math operation char, etc.
    pattern_4 = r'[\,\@\*\_\-\!\:\;\?\'\.\"\)\(\{\}\<\>\+\%\$\^\#\/\`\~\|\&\|]'
    text = re.sub(pattern_4, ' ', text)

    # Remove single character
    pattern_5 = r'\b\w{1,3}\b'
    text = re.sub(pattern_5, '', text)

    # Remove emoji
    pattern_6 = r'\\[a-z0-9]{1,5}'
    text = re.sub(pattern_6, '', text)

    # Remove digit character
    pattern_7 = r'\d+'
    text = re.sub(pattern_7, '', text)

    # Remove url start with http or https
    pattern_8 = r'(https|https:)'
    text = re.sub(pattern_8, '', text)

    # Remove (\); ([); (])
    pattern_9 = r'[\\\]\[]'
    text = re.sub(pattern_9, '', text)

    # Remove character non ASCII
    pattern_10 = r'[^\x00-\x7f]'
    text = re.sub(pattern_10, '', text)

    # Remove character non ASCII
    pattern_11 = r'(\\u[0-9A-Fa-f]+)'
    text = re.sub(pattern_11, '', text)

    # Remove multiple whitespace
    pattern_12 = r'(\s+|\\n)'
    text = re.sub(pattern_12, ' ', text)

    # Remove "wkwkwk"
    pattern_13 = r'\bwk\w+'
    text = re.sub(pattern_13, '', text)
    
    # Remove whitespace at the first and end sentences
    text = text.rstrip()
    text = text.lstrip()
    return text

def replaceThreeOrMore(text):
    # Pattern to look for three or more repetitions of any character, including newlines.
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", text)

indo_stop_words = stopwords.words("indonesian")

def remove_stopwords(text):
    return ' '.join([word for word in word_tokenize(text) if word not in indo_stop_words]) 


##################################################################################################################


##### UPLOADING FILE TO CLEAN THE DATA, THEN SEE THE RESULTS AS JSON ON SWAGGER, AND STORE THE FILE TO DATABASE #####
@swag_from("./templates/swag_clean.yaml", methods=['POST'])
@app.route('/upload_file_to_clean_see_as_json_and_store_to_database', methods=['POST'])
def upload_file_swgr():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == "POST":
        csv_file = request.files.get("file")
        if not csv_file or not csv_file.filename.endswith('.csv'):
            return 'Invalid file'

    # Read the .csv file into a Pandas dataframe
        df = pd.read_csv(csv_file, encoding='latin-1')

    # Apply the cleansing function to each cell in the dataframe
        df = df.select_dtypes(include=['object']).applymap(cleansing)

    # Replace three or more repetitions of any character with two repetitions
        df_clean = df.applymap(replaceThreeOrMore)

    # Apply the function to all string columns in the dataframe
        table = df_clean.applymap(remove_stopwords)

    # Convert the dataframe to an HTML table
        # Replace the existing table with the cleaned data
        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        table = table.to_sql('challenge_cleaned_flask_swagger', conn, if_exists='replace') # to prove that this code is running well, drop the "challenge_cleaned_flask_swagger" table from the database via the app_sqlite.py file
        conn.close()

    # Return the HTML table as the response to the form submission
        table_2 = df_clean.select_dtypes(include=['object']).applymap(remove_stopwords)

    # Convert the dataframe to an HTML table
        table = table_2.to_json()

    return table


###################################################################################################


##### UPLOADING FILE TO CLEAN THE DATA, THEN DOWNLOAD IT, AND STORE IT TO DATABASE #####
UPLOAD_FOLDER = "C:/Users/Acer/Downloads" # PATH DIRECTORY FOR DOWNLOADED CLEAN .CSV FILE
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@swag_from("./templates/swag_clean.yaml", methods=['POST'])
@app.route('/upload_file_to_clean_download_and_store_to_database', methods=['POST'])
def upload_file_swgr_download():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

    # Read the .csv file into a Pandas dataframe
        df = pd.read_csv(file, encoding='latin-1')

    # Apply the cleansing function to each cell in the dataframe
        df = df.select_dtypes(include=['object']).applymap(cleansing)

    # Replace three or more repetitions of any character with two repetitions
        df_clean = df.applymap(replaceThreeOrMore)

    # Apply the function to all string columns in the dataframe
        table = df_clean.applymap(remove_stopwords)

    # Convert the dataframe to an HTML table
        # Replace the existing table with the cleaned data
        conn = sqlite3.connect('database/challenge_level_3.db')
        cursor = conn.cursor()
        table = table.to_sql('challenge_cleaned_flask_swagger_download_file', conn, if_exists='replace') # to prove that this code is running well, drop the "challenge_cleaned_flask_swagger" table from the database via the app_sqlite.py file
        conn.close()

    # Return the HTML table as the response to the form submission
        table_2 = df_clean.select_dtypes(include=['object']).applymap(remove_stopwords)

        df_cleaned = df_clean.to_csv("nama_file.csv", index=False, encoding='latin-1')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            df_clean.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], "data_clean.csv"), index=False, encoding='latin-1')
            flash('The file has been downloaded to the C-Users-Acer-Downloads directory as data_clean.csv')
            return redirect(url_for('upload_download_file', name=df_cleaned))

    # Convert the dataframe to json
        table = table_2.to_json()
        return table

@swag_from("./templates/text_clean.yaml", methods=['POST'])
@app.route('/cleansing_text', methods=['POST'])
def text_cleansing_swgr():
    if request.method == 'POST':
        text = request.form.get('text')

    # Apply the cleansing function to each cell in the dataframe
        process_text = cleansing(text)

    # Replace three or more repetitions of any character with two repetitions
        cleaned_text = replaceThreeOrMore(process_text)
    
    return cleaned_text


################################################################################################


# Clean dataframe by index, then show the results as a JSON
@swag_from("./templates/swagger_index.yaml", methods=['POST'])
@app.route("/Clean dataframe by index. Choose 0 - 13168", methods=['GET','POST'])
def index_swgr():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        # get the value of the 'row' field from the form data
        index = int(request.form.get('index'))

        # select the row using the 'before' value, then apply cleansing function
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()
        values_data = df[['tweet']].iloc[index].apply(cleansing)

        # apply replaceThreeOrMore function to variable values_data
        values_data = values_data.apply(replaceThreeOrMore)

        # define stopwords in Indonesian
        indo_stop_words = stopwords.words("indonesian")

        # Function to remove stopwords
        def remove_stopwords(text):
            return ' '.join([word for word in word_tokenize(text) if word not in indo_stop_words])

        # Apply the function to all string columns in the dataframe
        table = values_data.apply(remove_stopwords)

        # format the values_data to list
        values_str = table.to_list()

        # select the row using the 'row' value
        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()
        before_data = df[['tweet']].iloc[index]

        # format the values to list
        before_pre = before_data.to_list()
        conn.close()

    return jsonify(clean=values_str, before=before_pre)

##### UPLOAD FILE TO CLEAN IT, AND SHOW IT AS JSON #####
@swag_from("./templates/swag_clean.yaml", methods=['POST'])
@app.route("/data_before_cleansing_swagger", methods=["GET", "POST"])
def read_file_to_json():
    conn = sqlite3.connect('database/challenge_level_3.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        csv_file = request.files.get("file")
        if not csv_file or not csv_file.filename.endswith('.csv'):
            return 'Invalid file'

        cursor.execute('''SELECT * FROM challenge''')
        df = pd.read_sql_query('''SELECT * FROM challenge''', conn)
        conn.commit()

    # Convert the dataframe to an HTML table
        table = df.to_json()
        conn.close()
        return table

if __name__ == '__main__':
    app.run(debug=True)
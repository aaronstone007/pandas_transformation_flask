import os
import pandas as pd
from flask import *
from flask import send_file
UPLOAD_FOLDER = 'uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'akakak123'
@app.route('/')
def upload():
    return render_template("form.html")

@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        loc = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        f.save(loc)
        session['loc'] = str(loc)
        return redirect(url_for('head'))

@app.route('/head')
def head():
    loc = session.get('loc', None)
    df = pd.read_csv(loc,header='infer',encoding = "ISO-8859-1")
    df.astype(str)
    # head
    sample_df = df.head(10)
    return render_template('simple.html', sample_tables=[sample_df.to_html(classes='data')], sample_titles=sample_df.columns.values)

@app.route('/agg')
def agg():
    """
    Get Params for making aggregation transformation
    """
    loc = session.get('loc', None)
    df = pd.read_csv(loc,header='infer',encoding = "ISO-8859-1")
    df.astype(str)
    agg_titles=df.columns.values
    return render_template('agg.html', agg_titles=agg_titles)


@app.route('/split')
def split():
    loc = session.get('loc', None)
    df = pd.read_csv(loc,header='infer',encoding = "ISO-8859-1")
    df.astype(str)
    split_titles=df.columns.values
    return render_template('split.html',split_titles=split_titles)


@app.route('/get_agg_val', methods=['GET', 'POST'])
def get_agg_val():
    groupby_column = str(request.form.get('groupby'))
    cols = request.form.getlist('agg')
    loc = session.get('loc', None)
    df = pd.read_csv(loc,header='infer',encoding = "ISO-8859-1")
    df.astype(str)
    inter_agg_df = df.groupby(groupby_column)[cols].agg(",".join).reset_index()
    merge_cols=[groupby_column]
    for i in range(len(cols)):
        merge_cols.append(cols[i])
    diff_array=list(set(df.columns.values)-set(cols))
    agg_df = pd.merge(df[diff_array],inter_agg_df[merge_cols],how='left',on=['User ID']).drop_duplicates()
    sample_agg_df = agg_df.head(10)
    agg_df.to_csv('./download/agg.csv')
    return render_template('agg_view.html', agg_tables=[sample_agg_df.to_html(classes='data')], agg_titles=sample_agg_df.columns.values)

@app.route('/get_split_val', methods=['GET', 'POST'])
def get_split_val():
    split_columns_input = request.form.getlist('split')
    loc = session.get('loc', None)
    df = pd.read_csv(loc,header='infer',encoding = "ISO-8859-1")
    df.astype(str)
    split_df=df

    # Empty list to append the results
    l=[]
    # For each data on the column list split and create a dataframe
    for i in split_columns_input:
        x=split_df[i].str.split(',', expand=True).stack().str.strip().reset_index(level=1,drop=True)
        l.append(x)
    # Concatenate all the individual dataframe in the list to intermediate df
    split_intermediate_df = pd.concat(l, axis=1, keys=split_columns_input)
    # Join the dataframe
    split_df = split_df.drop(split_columns_input, axis=1).join(split_intermediate_df).reset_index(drop=True)

    sample_split_df = split_df.head(10)
    split_df.to_csv('./download/split.csv')
    return render_template('split_view.html', split_tables=[sample_split_df.to_html(classes='data')], split_titles=sample_split_df.columns.values)



@app.route('/getAggregated')
def getAggregated():
    return send_file('download/agg.csv',
                     mimetype='text/csv',
                     attachment_filename='Aggregated.csv',
                     as_attachment=True)

@app.route('/getSplit')
def getSplit():
    return send_file('download/split.csv',
                     mimetype='text/csv',
                     attachment_filename='Split.csv',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug = True)

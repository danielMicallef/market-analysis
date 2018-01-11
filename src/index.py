from flask import Flask, render_template

from tip_ranks import get_data_list

app = Flask(__name__)


@app.route('/get/company_data', methods=['GET'])
def list_of_company_details():
    return get_data_list()


@app.route('/index')
def index():
    return render_template('index.html', stock_index_data=get_data_list())

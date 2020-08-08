from flask import Flask, Markup, render_template
import os
from google.cloud import bigquery
from flask import request


app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/shatadaldey/Desktop/pandas/my_key.json"

# 2. Establish BQ client
client = bigquery.Client()

sql_query1 = """
        SELECT 
            *
            
        FROM 
            `deft-effect-282902.population.population_by_country` as A
        WHERE 
            A.country = "World"
    """
df = client.query(sql_query1).to_dataframe()

df.drop(['country', 'country_code'], axis = 1,inplace = True) 

df1 = df.transpose() 

df1.reset_index(inplace = True)
df1.rename(columns={0: "Population", "index" : "Year"},inplace = True)

df1['Population'] = df1['Population']/1000000

df1['Year'] = df1['Year'].astype(str)
df1['Year'] = df1['Year'].str.replace("year_","")

# print(df1.head())

labels = df1['Year'].values.tolist()
values = df1['Population'].values.tolist()




@app.route('/')
def bar():
    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='World Population Trend', max = 10000, labels=bar_labels, values=bar_values)


@app.route("/year")
def fetch_population_details(methods=['GET']):

    bar_labels=labels
    bar_values=values

    # Fetch query parameter
    query_params = request.args
    year = query_params["year"]

    # Fetch details from DB
    # 1. Establish credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/shatadaldey/Desktop/pandas/my_key.json"

    # 2. Establish BQ client
    client = bigquery.Client()

    # 3. Query
    sql_query = """
        SELECT 
            {year} as year,
            A.year_{year}/1000000 as population,
            ((A.year_{year}/year_1960)-1)*100 as perc_inc
            
        FROM 
            `deft-effect-282902.population.population_by_country` as A
        WHERE 
            A.country = "World"
    """

    # 4. Fetch results
    result = list(client.query(sql_query.format(year = year)))
    print("result" ,result)


    # Return response to 
    
    return render_template('bar_chart.html',perc_inc = result[0]['perc_inc'], year = result[0]['year'],population = result[0]['population'], title='World Population Trend', max = 10000, labels=bar_labels, values=bar_values)



app.run(host='0.0.0.0', port=8003)
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta

app = Flask(__name__)

def plot_to_img(plot_fn):
    """Genera un gráfico y lo convierte en una cadena de imagen base64."""
    buf = io.BytesIO()
    plot_fn()  # Llama a la función que genera el gráfico
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf8')

def descriptive_create_plot_function(df, days):
    def plot_fn():
        plt.figure()
        plt.grid(True, alpha=0.3)
        title = f'New subs by day - Last {days} days'
        plt.title(title)
        plt.legend([f"New subs"])
        df.plot(figsize=(15, 3))
    return plot_fn

def profiling_create_plot_function(df, df_feat_mean,c):
    def plot_fn():
        plt.figure()
        plt.grid(True, alpha=0.3)
        title = f'Feature {c}'
        plt.title(title)
        plt.legend([f"New subs"])
        df_feat_mean.plot(kind='barh',figsize=(4,2))
    return plot_fn

@app.route("/")
def hello_world():
    
    df = pd.read_csv("df_prepared.csv")

    ####### DESCRIPTIVE
    descriptive_plot_urls = []
    for i in [30, 90]:
        now = datetime.now() - timedelta(days=i)
        df_gr = df.tail(i).groupby("num_subs").subscription_id.count().sort_index()
        plot_function = descriptive_create_plot_function(df_gr, i)
        descriptive_plot_urls.append(plot_to_img(plot_function))


    ####### PROFILING 

    ## PREPARING DATA
    df['age_cut'] = pd.cut(df['age_subcriptionmean'],[18,25,30,35,40,45,99])
    df['salary_cut'] = pd.cut(df['salary'],[1000,1500,2000,3000,4000,6000,99999])
    df['workplace_time_cut'] = pd.cut(df['workplace_time'],[0,50,100,200,500])


    profiling_plot_urls = []
    cols = ["age_cut","salary_cut","workplace_time_cut"]
    for c in cols:
        print("===== "+c)
        feat = c
        df_feat = df.groupby(f"{feat}").aging_30plus_subcriptionmean.agg(['count','mean']).sort_index()
        df_feat_mean = df_feat['mean'].sort_index(ascending=False)
        dt_temp = df.groupby(feat).aging_30plus_subcriptionmean.agg(['count','mean']).sort_index()
        plot_function = profiling_create_plot_function(dt_temp,df_feat_mean, c)
        profiling_plot_urls.append(plot_to_img(plot_function))

    return render_template('index.html', 
                            descriptive_plot_urls=descriptive_plot_urls,
                            profiling_plot_urls=profiling_plot_urls)

if __name__ == '__main__':
    app.run(debug=True)

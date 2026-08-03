import yfinance as yf
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, round as spark_round
from pyspark.sql.window import Window
import json

def run_oil_pipeline():
    print("🚀 [1/4] Fetching Crude Oil Market Data...")
    oil = yf.Ticker("CL=F")
    df_raw = oil.history(period="1mo")
    df_raw = df_raw.reset_index()

    df_pd = df_raw[['Date', 'Close']].rename(columns={'Date': 'date', 'Close': 'price'})
    df_pd['date'] = df_pd['date'].dt.strftime('%Y-%m-%d')
    df_pd['price'] = df_pd['price'].round(2)

    print("⚡ [2/4] Starting PySpark Session Engine...")
    spark = SparkSession.builder \
        .appName("DatenlensOilPipeline") \
        .master("local[*]") \
        .getOrCreate()

    spark_df = spark.createDataFrame(df_pd)

    print("📊 [3/4] Running PySpark Window Functions for Aggregations...")
    window_7d = Window.orderBy("date").rowsBetween(-6, 0)
    
    processed_df = spark_df.withColumn(
        "sma_7", 
        spark_round(avg(col("price")).over(window_7d), 2)
    )

    processed_df.show(5)

    print("💾 [4/4] Exporting Processed Data to JSON...")
    results = processed_df.toPandas().to_dict(orient="records")
    
    with open("oil_processed_data.json", "w") as f:
        json.dump(results, f, indent=4)

    print("✅ Pipeline Completed Successfully! Output saved to oil_processed_data.json")
    spark.stop()

if __name__ == "__main__":
    run_oil_pipeline()

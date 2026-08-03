import json
import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, round as spark_round
from pyspark.sql.window import Window
import yfinance as yf


def run_oil_pipeline() -> dict:
  """Fetches Crude Oil data, processes 7-day moving averages via PySpark,

  saves output to JSON, and returns the results dictionary.
  """
  spark = None
  try:
    print("🚀 [1/4] Fetching Crude Oil Market Data...")
    oil = yf.Ticker("CL=F")
    df_raw = oil.history(period="1mo")

    if df_raw.empty:
      raise ValueError("No market data fetched from yfinance.")

    df_raw = df_raw.reset_index()

    df_pd = df_raw[["Date", "Close"]].rename(
        columns={"Date": "date", "Close": "price"}
    )
    df_pd["date"] = df_pd["date"].dt.strftime("%Y-%m-%d")
    df_pd["price"] = df_pd["price"].round(2)

    print("⚡ [2/4] Starting PySpark Session Engine...")
    spark = (
        SparkSession.builder.appName("DatenlensOilPipeline")
        .master("local[1]")  # Restricted workers for light cloud containers
        .config("spark.driver.memory", "512m")
        .getOrCreate()
    )

    spark_df = spark.createDataFrame(df_pd)

    print("📊 [3/4] Running PySpark Window Functions for Aggregations...")
    window_7d = Window.orderBy("date").rowsBetween(-6, 0)

    processed_df = spark_df.withColumn(
        "sma_7", spark_round(avg(col("price")).over(window_7d), 2)
    )

    print("💾 [4/4] Converting Processed Data...")
    results = processed_df.toPandas().to_dict(orient="records")

    # Save locally to JSON as a backup/export
    output_filename = "oil_processed_data.json"
    with open(output_filename, "w") as f:
      json.dump(results, f, indent=4)

    print(
        f"✅ Pipeline Completed Successfully! Saved to {output_filename}"
    )

    return {
        "status": "success",
        "total_records": len(results),
        "data": results,
    }

  except Exception as e:
    print(f"❌ Pipeline failed with error: {str(e)}")
    return {"status": "error", "message": str(e)}

  finally:
    if spark:
      spark.stop()
      print("🔌 PySpark session closed.")


if __name__ == "__main__":
  run_oil_pipeline()

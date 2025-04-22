from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load CSVs
swimmers_df = pd.read_csv("swimmers_data_.csv")
best_times_df = pd.read_csv("best_times_data.csv")
rankings_df = pd.read_csv("rankings_data.csv")
countries_df = pd.read_csv("countries_data.csv")
strokes_df = pd.read_csv("strokes_data.csv")

# Add country names and codes to swimmers
swimmers_df = swimmers_df.merge(countries_df, on="country_id")

# Add stroke names to best_times
best_times_df = best_times_df.merge(strokes_df, on="stroke_id")

# Group event info by swimmer
swimmer_events = best_times_df.groupby("swimmer_id").apply(
    lambda df: [
        {
            "distance": int(row["distance"]),
            "stroke": row["stroke_name"],
            "best_time": row["best_time"],
        }
        for _, row in df.iterrows()
    ]
).to_dict()

@app.route("/")
def home():
    import pandas as pd

    swimmers_df = pd.read_csv("swimmers_data_.csv")
    best_times_df = pd.read_csv("best_times_data.csv")
    rankings_df = pd.read_csv("rankings_data.csv")
    countries_df = pd.read_csv("countries_data.csv")
    strokes_df = pd.read_csv("strokes_data.csv")

    swimmers_df = swimmers_df.merge(countries_df, on="country_id")
    strokes_dict = strokes_df.set_index("stroke_id")["stroke_name"].to_dict()

    swimmer_events = best_times_df.merge(strokes_df, on="stroke_id")
    swimmer_events["event"] = swimmer_events["distance"].astype(str) + " " + swimmer_events["stroke_name"]

    event_dict = swimmer_events.groupby("swimmer_id").apply(
        lambda df: df[["distance", "stroke_name", "best_time"]].to_dict(orient="records")
    ).to_dict()

    rankings_dict = {
        (row["first_name"], row["last_name"]): int(row["ranking"])
        for _, row in rankings_df.iterrows()
    }

    swimmers = []
    for _, swimmer in swimmers_df.iterrows():
        swimmers.append({
            "first_name": swimmer["first_name"],
            "last_name": swimmer["last_name"],
            "country": swimmer["country_name"],
            "country_code": swimmer["country_code"].lower(),
            "ranking": rankings_dict.get((swimmer["first_name"], swimmer["last_name"]), "—"),
            "events": event_dict.get(swimmer["swimmer_id"], [])
        })

    return render_template("index.html", swimmers=swimmers)

@app.route("/swimmers")
def get_swimmers():
    import pandas as pd

    swimmers_df = pd.read_csv("swimmers_data_.csv")
    best_times_df = pd.read_csv("best_times_data.csv")
    rankings_df = pd.read_csv("rankings_data.csv")
    countries_df = pd.read_csv("countries_data.csv")
    strokes_df = pd.read_csv("strokes_data.csv")

    swimmers_df = swimmers_df.merge(countries_df, on="country_id")
    strokes_dict = strokes_df.set_index("stroke_id")["stroke_name"].to_dict()

    swimmer_events = best_times_df.merge(strokes_df, on="stroke_id")
    swimmer_events["event"] = swimmer_events["distance"].astype(str) + " " + swimmer_events["stroke_name"]

    event_dict = swimmer_events.groupby("swimmer_id").apply(
        lambda df: df[["distance", "stroke_name", "best_time"]].to_dict(orient="records")
    ).to_dict()

    # Rankings lookup dictionary
    rankings_dict = {
        (row["first_name"], row["last_name"]): int(row["ranking"])
        for _, row in rankings_df.iterrows()
    }

    swimmers = []
    for _, swimmer in swimmers_df.iterrows():
        swimmers.append({
            "first_name": swimmer["first_name"],
            "last_name": swimmer["last_name"],
            "country": swimmer["country_name"],
            "country_code": swimmer["country_code"].lower(),
            "ranking": rankings_dict.get((swimmer["first_name"], swimmer["last_name"]), "—"),
            "events": event_dict.get(swimmer["swimmer_id"], [])
        })
    return jsonify(swimmers)

@app.route("/rankings-data")
def get_rankings_data():
    sorted_rankings = rankings_df.sort_values(by="ranking")
    return jsonify(sorted_rankings.to_dict(orient="records"))

@app.route("/rankings")
def rankings_page():
    return render_template("rankings.html")

@app.route("/countries-data")
def get_countries_data():
    merged = swimmers_df[["first_name", "last_name", "country_name", "country_code"]].merge(
        rankings_df[["first_name", "last_name", "ranking"]],
        on=["first_name", "last_name"],
        how="inner"
    )
    country_avg = merged.groupby(["country_name", "country_code"]).agg({"ranking": "mean"}).reset_index()
    country_avg["average_ranking"] = country_avg["ranking"].round(2)
    country_avg = country_avg.drop(columns=["ranking"])
    country_avg = country_avg.sort_values(by="average_ranking").reset_index(drop=True)
    country_avg["rank"] = country_avg.index + 1
    return jsonify(country_avg.to_dict(orient="records"))

@app.route("/countries")
def countries_page():
    return render_template("countries.html")

@app.route("/top-swims")
def top_swims():
    return render_template("top_swims.html")

@app.route("/top-swims-data")
def top_swims_data():
    import pandas as pd
    swimmers_df = pd.read_csv("swimmers_data_.csv")
    best_times_df = pd.read_csv("best_times_data.csv")
    countries_df = pd.read_csv("countries_data.csv")
    strokes_df = pd.read_csv("strokes_data.csv")

    swimmers_df = swimmers_df.merge(countries_df, on="country_id")
    best_times_df = best_times_df.merge(swimmers_df, on="swimmer_id")
    best_times_df = best_times_df.merge(strokes_df, on="stroke_id")

    best_times_df["event_name"] = best_times_df["distance"].astype(str) + " " + best_times_df["stroke_name"]
    best_times_df["rank"] = best_times_df.groupby("event_name")["best_time"].rank(method="min")

    ranked = best_times_df.sort_values(by=["event_name", "rank"])[
        ["event_name", "rank", "country_name", "first_name", "last_name", "best_time"]
    ]

    from flask import jsonify
    return jsonify(ranked.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)

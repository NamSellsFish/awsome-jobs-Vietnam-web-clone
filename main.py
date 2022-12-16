import sqlite3
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template

# Get Data
ses = requests.session()
ses = requests.get(
    f"https://github.com/awesome-jobs/vietnam/issues?page=2&q=is%3Aissue+is%3Aopen")
soup = BeautifulSoup(ses.content, "html.parser")
titles = [title.text for title in
          soup.find_all("a", class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title")]
details = [f"https://github.com{detail.attrs.get('href')}" for detail in
           soup.find_all("a", class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title")]
openedDates = [date.text for date in soup.find_all(
    "relative-time", class_="no-wrap")]
jobs = []
for i in range(len(titles)):
    jobs.append((titles[i], openedDates[i], details[i]))

# Work with database
con = sqlite3.connect("awesomeJobs.db", check_same_thread=False)
cur = con.cursor()
res = cur.execute("SELECT name FROM sqlite_master  WHERE name='jobs'")
cur.execute("CREATE TABLE IF NOT EXISTS jobs(titles, opened, details)")
for job in jobs:
    cur.execute(f"""
        INSERT INTO jobs   VALUES
                {job}
        """)
    con.commit()

# Work with website
app = Flask("myapp")


@app.route("/")
def showTheJobs():
    jobsJSON = []
    for top, row in enumerate(cur.execute("SELECT titles,opened,details FROM jobs ORDER BY titles"), 1):
        jobsJSON.append(
            {"No": top, "title": row[0], "opened": row[1], "detail": row[2]})

    return render_template("index.html", jobs=jobsJSON)


if __name__ == "__main__":
    app.run(debug=True)

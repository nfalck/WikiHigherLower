from article import Article
from flask import Flask, request, render_template, session
from flask_bootstrap import Bootstrap5
from flask_session import Session
import os

#
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Bootstrap5(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


def generate_first_articles():
    """ Generate the first two articles with Article class with its title, image and views when user starts playing.
    Make a JSON of the results of each article.  """
    # Generate the first article and retrieve its title, image and views
    article_1 = Article()
    article_1.generate_article()
    article_1.high_res_url = article_1.get_image()
    article_1.get_views()

    # Convert title, image and views to JSON
    article_1 = {
        "title": article_1.title,
        "high_res_url": article_1.high_res_url,
        "total": article_1.total
    }

    # Generate the second article and retrieve its title, image and views
    article_2 = Article()
    article_2.generate_article()
    article_2.high_res_url = article_2.get_image()
    article_2.get_views()

    # Convert title, image and views to JSON
    article_2 = {
        "title": article_2.title,
        "high_res_url": article_2.high_res_url,
        "total": article_2.total
    }

    return [article_1, article_2]


def generate_next_articles(article_2):
    """ """
    # The first article gets replaced by the second article
    article_1 = article_2

    # A new second article is generated
    article_2 = Article()
    article_2.generate_article()
    article_2.high_res_url = article_2.get_image()
    article_2.get_views()

    # Convert title, image and views to JSON
    article_2 = {
        "title": article_2.title,
        "high_res_url": article_2.high_res_url,
        "total": article_2.total
    }

    return [article_1, article_2]


#
@app.route("/", methods=["GET", "POST"])
def home():
    """ Render the webpage containing the articles, score and options for the user to guess higher or lower """
    # If player does not have a session, a score with 0 is initialized
    if "score" not in session:
        session["score"] = 0

    # If player does not have a session, the first articles are initialized
    if "articles" not in session:
        # Generate the first two articles
        session["articles"] = generate_first_articles()

    # Retrieve the articles from the session
    article_1 = session["articles"][0]
    article_2 = session["articles"][1]

    # Process the user's guess
    if request.method == "POST":
        guess = request.form.get("guess")
        if article_1["total"] > article_2["total"]:
            correct = "lower"
        else:
            correct = "higher"

        if guess == correct:
            session["score"] += 1
        else:
            session["score"] = 0  # Reset score on incorrect guess

        # Replace article_1 with article_2 and generate a new article_2
        session["articles"] = generate_next_articles(article_2)
    return render_template("index.html", articles=session["articles"], score=session["score"])


if __name__ == '__main__':
    app.run(debug=False, port=5002)

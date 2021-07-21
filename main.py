from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

# Create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api_key = 'f336d60ecacd88fbcfd3899a9e1753dd'

# Add Bootstrap
Bootstrap(app)

# Initiate SQL Database
db = SQLAlchemy(app)

class Movie(db.Model):
    # Class to store info and create Movie model 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000))
    rating = db.Column(db.Float(), nullable=False)
    ranking = db.Column(db.Integer(), nullable=True)
    review = db.Column(db.String(), nullable=False)
    img_url = db.Column(db.String, nullable=False)

    def __init__(self, title, year, description, rating, ranking, review, img_url):
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.review = review
        self.img_url = img_url

        if self.year == '':
            self.year = 'Data not available'

db.create_all()
class UpdateMovie(FlaskForm):
    # Class to update rating and review fields
    rating = FloatField('Your Rating Out of 10')
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovie(FlaskForm):
    # Class to add a movie to the list.
    title = StringField('Movie Title')
    submit = SubmitField('Add Movie')


# Create tables if not yet created
db.create_all()

# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    # Get a list of all the movies in the database
    movies=db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()
    return render_template("index.html", movies=movies)



@app.route('/search', methods=['GET', 'POST'])
def search():
    # Create a quick form to add a new movie
    form = AddMovie()
    if request.method == 'POST':
        # Search for the api based on user request title
        title = request.form['title']
        search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}'
        response = requests.get(search_url).json()['results']
        # Redirect user to specify which movie based on list
        return render_template('select.html', movies=response)

    # Send user to add a movie
    return render_template('add.html', form=form)

@app.route('/add/<int:movie_id>', methods=['GET', 'POST'])
def add(movie_id):
    # Request apiu using the movie id key from the user selection.
    request_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    # Create variable names of the SQL Database information
    response = requests.get(request_url).json()
    title = response['title']
    year = response['release_date']
    description = response['overview']
    rating = response['vote_average']
    review = response['tagline']
    img_url = f'https://image.tmdb.org/t/p/w500/{response["poster_path"]}'

    # Add the movie to the database
    new_movie = Movie(title=title,year=year,description=description,rating=rating,ranking='',review=review,img_url=img_url)
    db.session.add(new_movie)
    db.session.commit()

    # Return user to updated home screen
    return redirect(url_for('home'))
    

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    # Create a QuickForm wiht the UpdateMovie fields
    form = UpdateMovie()
    form.validate_on_submit()

    # Grab the movie that matches with the given id(Primary Key)
    movie = Movie.query.get(movie_id)

    if request.method == 'POST':
        # User submitted rating
        rating = request.form['rating']
        # User submitted review
        review = request.form['review']

        # Update the SQL Database with information
        movie.rating = rating
        movie.review = review
        # Save the database
        db.session.commit()
        # Return the user to the home page
        return redirect(url_for('home'))

    # Load up the edit page 
    return render_template('edit.html', form=form, movie=movie)

@app.route('/delete/<int:movie_id>')
def delete(movie_id):
    # Find movie in Database based on the movie's id. 

    movie = Movie.query.get(movie_id)  
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
 
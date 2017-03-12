# LisaPisaBot

## Intro

## Datasets Used
First, we created a database of the top 150 movies from [IMDB](http://www.imdb.com/). For that, we used the API provided through [Open Movie Database](http://www.omdbapi.com/) to get a short and a long plot version. Those are then saved into a csv file with the movie title in the first column, followed by the long plot description, and the short plot description in the last column.

Furthermore, we hand-crafted a chit chat database containing appropriate answers for certain questions/statements by the user. The questions/statements are labeled with a meaningful string followed by `_Bot` so that the user is less likely to type in one of the labels by accident. The chit chat is also saved into a csv file with the first column being the label, followed by a response and possibly another response in the last column. If there is only one response, the last column is filled with another string followed by `_bot` so that it can be recognized by the program later on.

## Program Structure

### doc2vec model
When the bot starts, it loads the movie data into the Gensim doc2vec format ('load_movies_gensim()' and 'load_names_gensim()') and trains a model on the 150 long movie descriptions, using the same parameters as in the Lee dataset jupyter tutorial from Gensim (https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb)

### Regex
We have several regex' which are used for recognizing what the user intended. They are compiled once and loaded in the function responsible for responses. In our program, the performance of the regex matching is limited to the amount of possible questions we thought of, so far there is no query expansion implemented.

### Databases
The databases described above are loaded by reading the csv files into a python dictionary.

### Response function
In the function `echo_all` the responses from the bot are generated. First, the message from the user is checked for stickers, because they do not have a text field in the json, which will make the following procedure crash otherwise. Then, the text of the message is retrieved and checked against the regex'. If one of the chit chat situations is recognized, the related label is saved and if the user mentioned his or her name, this will also be extracted. If the user asked for the description of the movie, the movie name is saved and a flag is set, so that the user can be informed if the movie is not found in the database.
In the following, the saved label/movie name is searched for in both databases. If a movie is found, the short plot description is returned and sent by the bot. If the label is found, the belonging answer is returned and sent by the bot.

### Movie Suggestion
The boolean flag 'asked_to_find_movie' is added to track whether the person answered YES to the 'START_BOT' question ("Do you want me to help you with deciding on a movie?"); any response after the user's YES is passed to a Gensim doc2vec model (https://radimrehurek.com/gensim/models/doc2vec.html) trained on the 150 long movie descriptions in the database.

The model infers a new vector for the user text, and returns the titles of the top 5 most similar movie-text-vectors.

<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot01.png" width="250 alt="Small Conversation Example"> 
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot02.png" width="250" alt="Small Conversation Example">


# LisaPisaBot
## NOTE:
In order to run this bot, please first run the 'train-model.py' script, which trains the model that the bot later uses.

## Datasets Used

# TODO describe the new dataset!

First, we created a database of the top 150 movies from [IMDB](http://www.imdb.com/). For that, we used the API provided through [Open Movie Database](http://www.omdbapi.com/) to get a short and a long plot version. Those are then saved into a csv file with the movie title in the first column, followed by the long plot description, and the short plot description in the last column.

The movie dataset was also uploaded to [Algolia](www.algolia.com), a service providing fast results for fuzzy search. Uploaded data is indexed and search can be conducted via an API. A ranked list of search results is then given back and can be integrated into the bot.

Furthermore, we hand-crafted a chit chat database containing appropriate answers for certain questions/statements by the user. The questions/statements are labeled with a meaningful string followed by `_Bot` so that the user is less likely to type in one of the labels by accident. The chit chat is also saved into a csv file with the first column being the label, followed by a response and possibly another response in the last column. If there is only one response, the last column is filled with another string followed by `_bot` so that it can be recognized by the program later on.

## Program Structure
### doc2vec model
The bot uses a pretrained doc2vec model (trained using train-model.py). The model is trained on the larger movie dataset described above, using the same parameters as in the [Lee dataset jupyter tutorial](https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb) from Gensim. When the bot starts, it loads the pretrained model, as well as the plots/titles of the movies in the database ('load_gensim_data()'). 

### Regex
We have several regex' which are used for recognizing what the user intended. They are compiled once and loaded in the function responsible for responses. In our program, the performance of the regex matching is limited to the amount of possible questions we thought of, so far there is no query expansion implemented.

### Databases
The databases described above are loaded by reading the csv files into a python dictionary.

### Response function
In the function `echo_all` the responses from the bot are generated. First, the message from the user is checked for stickers, because they do not have a text field in the json, which will make the following procedure crash otherwise. Then, the text of the message is retrieved and checked against the regex'. If one of the chit chat situations is recognized, the related label is saved and if the user mentioned his or her name, this will also be extracted.
In the following, the saved label is searched for in the chitchat database. If the label is found, the belonging answer is returned and sent by the bot. Otherwise, the user's input will be echoed.

### Movie Description
If the user asked for the description of a movie, the movie name is saved and a flag is set, so that the user can be informed if the movie is not found in the database. The movie name is then combined to an API call to Algolia and sent to the server. From the resulting ranked list of movies, the first one is chosen and the plot is extracted and shown in the answer message.

### Movie Suggestion
If the user asks for a movie about certain keywords, those keywords will be feed into a [Gensim doc2vec model](https://radimrehurek.com/gensim/models/doc2vec.html) trained on the 150 long movie descriptions in the database.
The model infers a new vector for the user text, and returns the titles of the top 5 most similar movie-text-vectors.

## Examples
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot01.png" width="270" alt="Small Conversation Example"> 
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot02.png" width="270" alt="Small Conversation Example">
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot42.png" width="270" alt="Small Conversation Example">

## Future Outlook
While the bot is insensitive to misspellings of movie names, the user must enter fairly specific keywords in order to trigger a particular bot behavior. A future implementation might elevate this by using some combination of look-up and word embeddings; by comparing an embedding of user input to several predefined response-embeddings, the closest behavior might be identified and triggered.
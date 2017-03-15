# LisaPisaBot
## Datasets Used
In order to teach our bot about movies (to feed into the doc2vec model for movie recommendation, and to populate the bots mental library of movie synopsi), we provided it with a dataset of movie titles and plots, obtained from IMDB's [Alternative Interfaces](http://www.imdb.com/interfaces) collection. After discarding all the movies with a rating <5 (to make the number of movies manageable, and the quality of movies at least passable), we are left with 110855 movies with which to educate our bot. These are stored in a .csv file which is read at model-train time, as well as at run-time in order to match recommended movies to their titles. The CSV file consists of 5 columns: | Index | Title | Year | Plot | Rating |. Currently, our bot only makes use of Title and Plot.

The movie dataset was also uploaded to [Algolia](www.algolia.com), a service providing fast results for fuzzy search. Uploaded data is indexed and search can be conducted via an API. A ranked list of search results is then given back and can be integrated into the bot.

Furthermore, we hand-crafted a chit chat database containing appropriate answers for certain questions/statements by the user. The questions/statements are labeled with a meaningful string followed by `_Bot` so that the user is less likely to type in one of the labels by accident. The chit chat is also saved into a csv file with the first column being the label, followed by a response and possibly another response in the last column. If there is only one response, the last column is filled with another string followed by `_bot` so that it can be recognized by the program later on.

## Program Structure
### doc2vec model
The bot uses a pretrained doc2vec model (trained using train-model.py). The model is trained on the larger movie dataset described above, using the same parameters as in the [Lee dataset jupyter tutorial](https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb) from Gensim. When the bot starts, it loads the pretrained model, as well as the plots/titles of the movies in the database ('load_gensim_data()'). 

### Regex
We have several regex' which are used for recognizing what the user intended. They are compiled once and loaded in the function responsible for responses. In our program, the performance of the regex matching is limited to the amount of possible questions we thought of, so far there is no query expansion implemented.

### Databases
The chitchat database described above is loaded by reading the csv files into a python dictionary. The movie database will be accessed via the Algolia API.

### Response function
In the function `echo_all` the responses from the bot are generated. First, the message from the user is checked for stickers, because they do not have a text field in the json, which will make the following procedure crash otherwise. Then, the text of the message is retrieved and checked against the regex'. If one of the chit chat situations is recognized, the related label is saved and if the user mentioned his or her name, this will also be extracted.
In the following, the saved label is searched for in the chitchat database. If the label is found, the belonging answer is returned and sent by the bot. Otherwise, the user's input will be echoed.

### Movie Description
If the user asked for the description of a movie, the movie name is saved and a flag is set, so that the user can be informed if the movie is not found in the database. The movie name is then combined to an API call to Algolia and sent to the server. From the resulting ranked list of movies, the user is asked to confirm if he or she meant the found movie. When the user confirms his or her selection, the plot is displayed.

### Movie Suggestion
If the user asks for a movie about certain keywords, those keywords are fed into a [Gensim doc2vec model](https://radimrehurek.com/gensim/models/doc2vec.html) trained on the 110855 movie plots in the database.

With a couple steps of gradient descent (more on that during the doc2vec presentation), the model infers a new vector for the user text, calculates the cosine between this vector and those learned by the model, and finally returns the titles and synopsi of the movies corresponding to the top 5 most similar movie-text-vectors.

## Examples
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot01.png" width="270" alt="Small Conversation Example"> 
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot02.png" width="270" alt="Small Conversation Example">
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot42.png" width="270" alt="Small Conversation Example">
<img src="https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot23.png" width="270" alt="Small Conversation Example">

## Future Outlook
While the bot is insensitive to misspellings of movie names, the user must enter fairly specific keywords in order to trigger a particular bot behavior. A future implementation might alleviate this by using some combination of look-up and word embeddings; by comparing an embedding of user input to several predefined response-embeddings, the closest behavior might be identified and triggered.
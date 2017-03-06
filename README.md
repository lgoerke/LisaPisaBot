# LisaPisaBot

## Intro

## Datasets Used
First, we created a database of the top 150 movies from [IMDB](http://www.imdb.com/). For that, we used the API provided through [Open Movie Database](http://www.omdbapi.com/) to get a short and a long plot version. Those are then saved into a csv file with the movie title in the first column, followed by the long plot description, and the short plot description in the last column.

Furthermore, we hand-crafted a chit chat database containing appropriate answers for certain questions/statements by the user. The questions/statements are labeled with a meaningful string followed by `_Bot` so that the user is less likely to type in one of the labels by accident. The chit chat is also saved into a csv file with the first column being the label, followed by a response and possibly another response in the last column. If there is only one response, the last column is filled with another string followed by `_bot` so that it can be recognized by the program later on.

## Program Structure

### Regex
We have several regex' which are used for recognizing what the user intended. They are compiled once and loaded in the function responsible for responses. In our program, the performance of the regex matching is limited to the amount of possible questions we thought of, so far there is no query expansion implemented.

### Databases
The databases described above are loaded by reading the csv files into a python dictionary.

### Response function
In the function `echo_all` the responses from the bot are generated. First, the message from the user is checked for stickers, because they do not have a text field in the json, which will make the following procedure crash otherwise. Then, the text of the message is retrieved and checked against the regex'. If one of the chit chat situations is recognized, the related label is saved and if the user mentioned his or her name, this will also be extracted. If the user asked for the description of the movie, the movie name is saved and a flag is set, so that the user can be informed if the movie is not found in the database.
In the following, the saved label/movie name is searched for in both databases. If a movie is found, the short plot description is returned and sent by the bot. If the label is found, the belonging answer is returned and sent by the bot.
 
![Small Conversation Example](https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot01.png =250x250)

![Small Conversation Example](https://github.com/lgoerke/LisaPisaBot/blob/master/figures/screenshot02.png =250x250)


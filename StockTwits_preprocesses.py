from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import word_tokenize, pos_tag
from nltk.corpus import sentiwordnet as swn
from nltk.wsd import lesk
from nltk.stem.wordnet import WordNetLemmatizer
import re
import html







def clean(text):
    text = re.sub("[0-9]+", "number", text)
    text = re.sub("#", "", text)
    text = re.sub("\n", "", text)
    text = re.sub("$[^\s]+", "", text)
    text = re.sub("@[^\s]+", "", text)
    text = re.sub("(http|https)://[^\s]*", "", text)
    text = re.sub("[^\s]+@[^\s]+", "", text)
    text = re.sub('[^a-z A-Z]+', '', text)
    return text




def Vader_score(text):
    return SentimentIntensityAnalyzer().polarity_scores(text)["compound"]

def get_sentiword_score(message):

        """
            takes a message and performs following operations:
            1) tokenize
            2) POS tagging
            3) reduce text to nouns, verbs, adjectives, adverbs
            4) lemmatize the words

            for each selected tag, if more than one sense exists, performs word sense disambiguation
            using lesk algorithm and finally returns positivity score, negativity score from
            sentiwordnet lexicon
        """

        tokens = word_tokenize(message)
        pos = pos_tag(tokens)
        lemmatizer = WordNetLemmatizer()
        selected_tags = list()
        scores = list()

        for i in range(len(pos)):
            if pos[i][1].startswith('J'):
                selected_tags.append((lemmatizer.lemmatize(pos[i][0], 'a'), 'a'))
            elif pos[i][1].startswith('V'):
                selected_tags.append((lemmatizer.lemmatize(pos[i][0], 'v'), 'v'))
            elif pos[i][1].startswith('N'):
                selected_tags.append((lemmatizer.lemmatize(pos[i][0], 'n'), 'n'))
            elif pos[i][1].startswith('R'):
                selected_tags.append((lemmatizer.lemmatize(pos[i][0], 'r'), 'r'))

        # score list: [(sense name, pos score, neg score)]
        for i in range(len(selected_tags)):
            senses = list(swn.senti_synsets(selected_tags[i][0], selected_tags[i][1]))
            if len(senses) == 1:
                scores.append((senses[0].synset.name(), senses[0].pos_score(), senses[0].neg_score()))
            elif len(senses) > 1:
                sense = lesk(tokens, selected_tags[i][0], selected_tags[i][1])
                if sense is None:
                    # take average score of all original senses
                    pos_score = 0
                    neg_score = 0
                    for i in senses:
                        pos_score += i.pos_score()
                        neg_score += i.neg_score()
                    scores.append((senses[0].synset.name(), pos_score/len(senses), neg_score/len(senses)))
                else:
                    sense = swn.senti_synset(sense.name())
                    scores.append((sense.synset.name(), sense.pos_score(), sense.neg_score()))

        """
            there are a number of ways for aggregating sentiment scores
            1) sum up all scores
            2) average all scores (or only for non zero scores)
            3) (1) or (2) but only for adjectives
            4) if pos score greater than neg score +1 vote else -1 vote
            here we are summing up the positive and negative scores to be used by classifier.
            whenever we encounter a negative word, we reverse the positive and negative score.
        """

        # collected from word stat financial dictionary
        negation_words = list(open('C:/Users/56979/PycharmProjects/Bots/Fundamental_Analisis/data_extractor/lexicon_negation_words.txt').read().split())

        counter = 1
        pos_score = 0
        neg_score = 0
        for score in scores:
            if any(score[0].startswith(x) for x in negation_words):
                counter *= -1
            else:
                if counter == 1:
                    pos_score += score[1]
                    neg_score += score[2]
                elif counter == -1:
                    pos_score += score[2]
                    neg_score += score[1]

        final_score = [pos_score, neg_score]
        return final_score

def clean2(message):
    ##Limpieza del mensaje
    message = html.unescape(message)
    message = re.sub(r'(www\.|https?://).*?(\s|$)|@.*?(\s|$)|\$.*?(\s|$)|\d|\%|\\|/|-|_', ' ', message)
    message = re.sub(r'\.+', '. ', message)
    message = re.sub(r'\,+', ', ', message)
    message = re.sub(r'\?+', '? ', message)
    message = re.sub(r'\s+', ' ', message)
    message = message.lower()
    return message


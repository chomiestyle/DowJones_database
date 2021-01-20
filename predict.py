from Fundamental_Analisis.FinBERT.finbert.finbert import predict
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
import argparse
from pathlib import Path
import datetime
import os
import pandas as pd

# text_path='C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Fundamental_Analisis/FinBERT/test.txt'
# with open(text_path,'r') as f:
#     text = f.read()

def finbert_prediction(text,summary,title):
    #args = parser.parse_args()
    # output_dir='C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Fundamental_Analisis/FinBERT/Sentence_data/{}'.format(stock_name)
    # if not os.path.exists(output_dir):
    #     os.mkdir(output_dir)
    # print(text)
    model_path_complete= 'C:/Users/56979/PycharmProjects/DOW_JONES_BOTS/Fundamental_Analisis/FinBERT/models/classifier_model/finbert_sentiment'
    model = BertForSequenceClassification.from_pretrained(model_path_complete,num_labels=3,cache_dir=None)
    result_title = predict(title, model, write_to_csv=False)
    pred_summary = predict(summary, model, write_to_csv=False)
    summary_result = pd.DataFrame(columns=['sentence', 'positive', 'negative', 'neutral', 'global_sentiment', 'avg_sentiment'])
    summary_sentence, summary_positive, summary_negative, summary_neutral, summary_global_sentiment, summary_avg_sentiment = [], [], [], [], [], []
    for s in pred_summary.values:
        summary_sentence.append(s[0])
        summary_scores = s[1]
        summary_positive.append(summary_scores[0])
        summary_negative.append(summary_scores[1])
        summary_neutral.append(summary_scores[2])
        summary_global_sentiment.append(s[2])
        summary_avg_sentiment.append(s[3])
        # time.append(time_new)
    summary_result['sentence'] = summary_sentence
    summary_result['positive'] = summary_positive
    summary_result['negative'] = summary_negative
    summary_result['neutral'] = summary_neutral
    summary_result['global_sentiment'] = summary_global_sentiment
    summary_result['avg_sentiment'] = summary_avg_sentiment
    #output ='{}_prediction.csv'.format(new_id)
    pred_text=predict(text,model,write_to_csv=False)
    result=pd.DataFrame(columns=['sentence','positive','negative','neutral','global_sentiment','avg_sentiment'])
    text_sentence, text_positive, text_negative, text_neutral, text_global_sentiment, text_avg_sentiment=[], [], [], [], [] ,[]
    for s in pred_text.values:
        text_sentence.append(s[0])
        text_scores=s[1]
        text_positive.append(text_scores[0])
        text_negative.append(text_scores[1])
        text_neutral.append(text_scores[2])
        text_global_sentiment.append(s[2])
        text_avg_sentiment.append(s[3])
        #time.append(time_new)
    result['sentence']=text_sentence
    result['positive']=text_positive
    result['negative']=text_negative
    result['neutral']=text_neutral
    result['global_sentiment']=text_global_sentiment
    result['avg_sentiment']=text_avg_sentiment
    #result['datetime']=time
    #save_dir='C:/Users/56979/PycharmProjects/TimeGAN/Data/DOWJONES/{}'.format(stock_name)
    #if not os.path.exists(save_dir):
    #    os.mkdir(save_dir)
    #save_path=os.path.join(save_dir,output)
    #result.to_csv(save_path)
    return result,summary_result,result_title
# data=finbert_prediction(text=text,stock_name='AAPL',title='CACAPOTO',new_id=32)
# for i in data.index:
#     print(data.iloc[i])
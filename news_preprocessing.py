import pandas as pd


def get_dataframe(lista):
    features=lista[0]
    separeted_features=features.strip().split(',')[1:]
    list=[]
    for i in range(len(separeted_features)):
        list.append([])
    #print(separeted_features)
    dataframe=pd.DataFrame()
    #lista_1,lista_2,lista_3,lista_4=[],[],[],[]
    for content in lista[1:]:
        #content=list[1]
        content=content.strip().split(',')[1:]
        #print(content)
        #print(len(list))
        if len(content)<len(list):
            continue
        for j in range(len(list)):
            if j==0:
                list[j].append(content[0:len(content)-(len(list)-1)])
            else:
                list[j].append(content[-len(list)+j])

    for i in range(len(separeted_features)):
        dataframe[separeted_features[i]] = list[i]
    #dataframe[separeted_features[1]] = lista_2
    #dataframe[separeted_features[2]] = lista_3
    #dataframe[separeted_features[3]] = lista_4



    return dataframe

def get_score(title_list,summary_list,text_list):
    title_dataframe=get_dataframe(title_list)
    summary_dataframe = get_dataframe(summary_list)
    text_dataframe = get_dataframe(text_list)
    delete_index=[]
    for i in text_dataframe.index:
        avg=text_dataframe.iloc[i]['avg_sentiment']
        try:
            #print(avg)
            text_dataframe.iloc[i]['avg_sentiment']=float(avg)
        except:
            #print(avg)
            delete_index.append(i)
    for j in delete_index:
        text_dataframe=text_dataframe.drop(index=j)
        #print(text_dataframe.iloc[i]['avg_sentiment'])
    #print(text_dataframe['avg_sentiment'].values)
    text_dataframe['avg_sentiment']=text_dataframe['avg_sentiment'].apply(lambda x:float(x))
    summary_dataframe['avg_sentiment'] = summary_dataframe['avg_sentiment'].apply(lambda x: float(x))
    title_dataframe['sentiment_score'] = title_dataframe['sentiment_score'].apply(lambda x: float(x))
    text_score=text_dataframe['avg_sentiment'].mean()

    #text_score=0
    #print(summary_dataframe['avg_sentiment'].values)
    summary_score = summary_dataframe['avg_sentiment'].mean()
    title_score = title_dataframe['sentiment_score'].values[0]
    print('text score: {}'.format(text_score))
    print('summary score: {}'.format(summary_score))
    print('title score: {}'.format(title_score))
    return title_score,summary_score,text_score


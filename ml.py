# Python program to generate WordCloud 

# importing all necessery modules 
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd

# Reads 'Youtube04-Eminem.csv' file
# df = pd.read_json(, encoding ="latin-1")
# print(df)

abc = pd.read_json("https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json", orient='records')
# print(abc)

comment_words = ' '
stopwords = set(STOPWORDS)
cloud_words = ' '

def create_cloud(max):
    global cloud_words
    global comment_words
    cloud_words = ' '
    comment_words = ' '
    result = pd.read_json("https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json", orient='records')
    dataList = result.dataList
    dataList = dataList[:max]
    for data in dataList:
        # print(data)
        keywords = data['keywords']
        for keyword in keywords:
            # print(str(keyword['name']) + ':' + str(keyword['count']))
            # wordCount = int(keyword['count'])
            # print("wordCount: " + str(wordCount))
            # while wordCount > 0:
            #     cloud_words = cloud_words + ' ' + str(keyword['name'])
            #     wordCount = wordCount - 1

            cloud_words = cloud_words + ' ' + str(keyword['name'])
            tokens = cloud_words.split()
            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()

            for words in tokens:
                comment_words = comment_words + words + ' '


# call function to generate word list
create_cloud(10)

# generate cloud
wordcloud = WordCloud(width = 600, height = 400,
                      background_color ='white',
                      stopwords = stopwords,
                      min_font_size = 10).generate(comment_words)

# plot the WordCloud image
plt.figure(figsize = (5, 5), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)

plt.show()

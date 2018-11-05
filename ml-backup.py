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
# keyword_string = ' '

# iterate through the csv file
for val in abc.dataList[0]['keywords']:
        # for items in abc.columns:
            # print(abc.columns)


    # typecaste each val to string
    val = str(val['name'])

    # split the value
    tokens = val.split()

    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()

    for words in tokens:
        comment_words = comment_words + words + ' '

# def create_cloud(max):
#     # global keyword_string
#     # keyword_string = ' '
#     result = pd.read_json("https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json", orient='records')
#     dataList = result.dataList
#     dataList = dataList[:max]
#     for data in dataList:
#         print(data)
#
# create_cloud(0)
#
# wordcloud = WordCloud(width = 800, height = 800,
#                       background_color ='white',
#                       stopwords = stopwords,
#                       min_font_size = 10).generate(comment_words)
#
# # plot the WordCloud image
# plt.figure(figsize = (8, 8), facecolor = None)
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.tight_layout(pad = 0)
#
# plt.show()

# # iterate through the csv file
# for val in abc.dataList[1]['keywords']:
#     # for items in abc.columns:
#     #     print(abc.columns)
#
#     # print(val)
#     # typecaste each val to string
#     val = str(val['name'])
#
#     # # split the value
#     tokens = val.split()
#
#     # Converts each token into lowercase
#     for i in range(len(tokens)):
#         tokens[i] = tokens[i].lower()
#
#     for words in tokens:
#         comment_words = comment_words + words + ' '
#
#
#
# # plt.show()
#
#
# def create_cloud(max):
#     # global keyword_string
#     # keyword_string = ' '
#     result = pd.read_json("https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json", orient='records')
#     dataList = result.dataList
#     dataList = dataList[:max]
#     # for data in dataList:
#         # print(data)
#         # keywords = data['keywords']
#         # for keyword in keywords:
#         #     print(str(keyword['name']))
#         #     keyword_string = keyword_string + ' ' + str(keyword['name'])
#
# wordcloud = WordCloud(width = 800, height = 800,
#                       background_color ='white',
#                       stopwords = stopwords,
#                       min_font_size = 10).generate(comment_words)
#
#
#
# # call function to generate word list
# # comment_words = ' '
# # keyword_string = ' '
# create_cloud(1)
#
# # print(keyword_string)
#
# # # split the value
# # tokens = keyword_string.split()
#
# # # Converts each token into lowercase
# # for i in range(len(tokens)):
# #     tokens[i] = tokens[i].lower()
# #
# # for words in tokens:
# #     comment_words = comment_words + words + ' '
# #
# # print(comment_words)
#
# # generate cloud
#
# # plot the WordCloud image
# plt.figure(figsize = (5, 5), facecolor = None)
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.tight_layout(pad = 0)
#
# plt.show()

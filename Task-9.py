from textblob import TextBlob

text = input("Enter a sentence: ")
analysis = TextBlob(text)
polarity = analysis.sentiment.polarity
print("Polarity:", polarity)
if polarity > 0:
    print("Positive Sentiment")
elif polarity < 0:
    print("Negative Sentiment")
else:
    print("Neutral Sentiment")
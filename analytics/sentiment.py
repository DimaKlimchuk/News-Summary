from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch


def load_sentiment_model():
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    return sentiment_analyzer


def analyze_sentiment(df, text_column='Text'):
    print("Аналіз тональності...")

    sentiment_analyzer = load_sentiment_model()
    texts = df[text_column].astype(str).tolist()

    results = sentiment_analyzer(texts, truncation=True)

    def map_result(res):
        label = res['label']
        if "1" in label or "2" in label:
            return "negative"
        elif "3" in label:
            return "neutral"
        else:
            return "positive"

    df['Sentiment'] = [map_result(r) for r in results]
    return df

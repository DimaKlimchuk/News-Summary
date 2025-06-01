def summarize_dataset(df, text_column="Text", summary_column="Summary"):
    from transformers import pipeline
    from tqdm import tqdm

    summarizer = pipeline(
        "summarization",
        model="ukr-models/uk-summarizer",
        tokenizer="ukr-models/uk-summarizer",
        framework="pt",
        device=0,
        max_length=128,
        num_beams=4,
        no_repeat_ngram_size=2,
        clean_up_tokenization_spaces=True
    )

    if text_column not in df.columns:
        raise ValueError(f"Колонка '{text_column}' відсутня в датафреймі!")

    df = df.dropna(subset=[text_column])
    df[text_column] = df[text_column].astype(str).str.slice(0, 2000)

    summaries = []
    for i, text in tqdm(enumerate(df[text_column]), total=len(df), desc="Генеруємо резюме"):
        try:
            summary = summarizer(text, max_length=60, min_length=20, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            print(f"Помилка в рядку {i}: {e}")
            summaries.append("Анотацію не згенеровано.")

    df[summary_column] = summaries
    return df
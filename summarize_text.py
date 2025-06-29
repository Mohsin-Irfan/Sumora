from transformers import pipeline


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")




def summarize_text(text, lang='en'):
    max_chunk_size = 1000
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    summaries = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]
    summary_text = "\n\n".join(summaries)
    return f"{summary_text}"

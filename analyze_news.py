import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai


# Function to scrape news articles from a given URL
def get_news_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')  # Adjust based on the website's structure
    news_data = []
    for article in articles:
        title = article.find('h1').text if article.find('h1') else article.find('h2').text if article.find(
            'h2') else 'No title'
        content = ''

        # Check different possible tags for content
        for tag in ['div', 'p', 'span']:
            elements = article.find_all(tag)
            if elements:
                content = ' '.join(element.text for element in elements)
                break

        if content:
            news_data.append({'title': title, 'content': content})
    return news_data


# Function to clean the scraped data
def clean_data(news_data):
    df = pd.DataFrame(news_data)
    df.dropna(inplace=True)  # Drop rows with missing values
    df['content'] = df['content'].str.replace('\n', ' ')  # Remove newline characters
    return df


# Function to split text into chunks within token limits
def split_into_chunks(text, max_tokens=2048):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # Adding 1 for the space
        if current_length + word_length <= max_tokens:
            current_chunk.append(word)
            current_length += word_length
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


# Function to generate a summary for a chunk of text
def summarize_chunk(content_chunk):
    openai.api_key = 'openai-api-key'  # Replace with your actual OpenAI API key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize the following Chinese political news article."},
            {"role": "user", "content": content_chunk}
        ]
    )
    return response.choices[0].message['content']


# Function to generate summaries for all content chunks
def generate_summaries(contents):
    all_summaries = []
    for content in contents:
        chunks = split_into_chunks(content)
        for chunk in chunks:
            print(f"Chunk length: {len(chunk)} tokens")  # Debugging line
            summary = summarize_chunk(chunk)
            all_summaries.append(summary)
    return all_summaries


# Function to generate a report
def generate_report(news_df):
    contents = news_df['content'].tolist()
    summaries = generate_summaries(contents)

    # Generate final summary and prediction
    final_summary = ' '.join(summaries)
    prediction = summarize_chunk(final_summary + "\nPredict future trends based on the summary above.")

    with open('news_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write("Summary of Recent Chinese Political News and Future Trends\n")
        f.write("=" * 60 + "\n\n")
        f.write(final_summary)
        f.write("\n\nFuture Trend Prediction\n")
        f.write("=" * 60 + "\n\n")
        f.write(prediction)
        f.write("\n\nDetailed Article Analysis\n")
        f.write("=" * 60 + "\n\n")
        for index, row in news_df.iterrows():
            f.write(f"Title: {row['title']}\n")
            f.write(f"Content: {row['content']}\n")
            f.write("\n" + "-" * 60 + "\n\n")

    print("Report generated and saved to 'news_analysis_report.txt'")


# Main function to run the entire analysis
def main():
    url = 'www.example.com'  # Replace with the actual URL
    news_data = get_news_articles(url)
    news_df = clean_data(news_data)
    generate_report(news_df)


if __name__ == "__main__":
    main()

# Veeva Live Summarizer

## Overview
Veeva Live Summarizer is a Python application designed to summarize live call notes using natural language processing. It leverages the OpenAI API to generate concise summaries, extract keywords, and determine sentiment from call notes.

## Features
- Upload CSV files containing call notes.
- Summarize notes into brief summaries.
- Extract relevant keywords.
- Determine the sentiment of the notes (Positive, Neutral, Negative).
- Download the summarized output as a CSV file.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd veeva-live-summarizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in the Streamlit secrets.

## Usage

1. Run the application:
   ```
   streamlit run src/app.py
   ```

2. Upload your call notes in CSV format.

3. Click on the "Summarize Call Notes" button to process the notes.

4. Download the summarized output as a CSV file.

## Requirements
- Python 3.x
- Streamlit
- Pandas
- OpenAI

## License
This project is licensed under the MIT License.
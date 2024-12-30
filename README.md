# Job Search Application

A **Streamlit-based web application** that helps users find jobs tailored to their preferences. The application filters jobs by title, location, salary, and keywords, and uses machine learning to cluster and refine search results for more accurate matching.

## APP Link: https://huggingface.co/spaces/burcuonel/Find_Proper_Job

## Features

- **Salary Parsing**: Cleans and normalizes salary data, converting hourly rates into annual salaries.
- **Filtering Options**:
  - Job title
  - Location
  - Minimum salary
  - Keywords in job titles and descriptions
- **Clustering**: Uses TF-IDF vectorization and K-means clustering to improve search results.
- **Interactive UI**:
  - Expand/collapse job descriptions
  - Highlight keywords in descriptions
  - Debug mode for detailed filtering insights

## How It Works

1. **Data Preprocessing**: Cleans the dataset to normalize salary information and combine job titles with descriptions for better clustering.
2. **Search & Filtering**:
   - Filters jobs based on user-defined parameters.
   - Performs clustering to group similar jobs together.
3. **Result Display**: Presents filtered job listings with highlighted keywords and additional details.

### Detailed Explanation: Clustering with TF-IDF and K-means

- **TF-IDF Vectorization**: Converts job titles and descriptions into numerical representations by calculating the importance of each word. This helps in understanding the context and relevance of each job listing.
  - **Term Frequency (TF)**: Measures how often a word appears in a document.
  - **Inverse Document Frequency (IDF)**: Gives less weight to common words that appear in many documents (e.g., "the," "and").

- **K-means Clustering**: Groups similar job listings together based on their TF-IDF vectors. This algorithm helps identify patterns in job descriptions and titles, ensuring that the search results are more accurate and relevant.
  - **Why it’s used**: It helps refine search results by grouping similar jobs, making it easier to match user queries to appropriate clusters.
  - **How it works**: 
    1. Initializes `K` centroids and assigns each job to the nearest centroid.
    2. Updates centroids based on the average position of jobs in each cluster.
    3. Repeats the process until clusters stabilize.

This combination ensures that users receive tailored job recommendations, even for vague or broad queries.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/job-search-application.git
   cd job-search-application
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open the application in your browser at `http://localhost:8501`.

## Data

This application uses the job dataset hosted at [Hugging Face](https://huggingface.co/datasets/burcuonel/datajob_indeed_usa) containing job listings from the USA.

## Libraries Used

- **Streamlit**: For building the interactive web application
- **Pandas**: For data manipulation
- **NumPy**: For numerical operations
- **Scikit-learn**: For TF-IDF vectorization and K-means clustering
- **Regular Expressions (re)**: For salary data extraction and cleaning

## Contribution

Contributions are welcome! Feel free to submit issues or pull requests to improve the application.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

# Job Search Application

A **Streamlit-based web application** that helps users find jobs tailored to their preferences. The application filters jobs by title, location, salary, and keywords, and uses machine learning to cluster and refine search results for more accurate matching.

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
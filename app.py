import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import streamlit as st
import re

def clean_salary(salary_str):
    """Extract and clean salary information, including ranges and hourly rates."""
    if pd.isna(salary_str):
        return 0
    
    salary_str = str(salary_str).lower().replace(',', '')
    
    # Convert hourly rate to annual salary (assuming 40 hours/week, 52 weeks/year)
    HOURS_PER_YEAR = 40 * 52  # 2080 hours per year
    
    # Handle hourly rates with ranges (e.g., "50-54 an hour" or "$50-$54/hr")
    hourly_range_match = re.search(r'(\d+\.?\d*)\s*[-to]+\s*(\d+\.?\d*)\s*(?:an hour|per hour|\/hour|\/hr|\$?\/h|\$?ph|hr)', salary_str)
    if hourly_range_match:
        low, high = map(float, hourly_range_match.groups())
        avg_hourly = (low + high) / 2
        return int(avg_hourly * HOURS_PER_YEAR)
    
    # Handle single hourly rate (e.g., "50 an hour" or "$50/hr")
    hourly_match = re.search(r'(\d+\.?\d*)\s*(?:an hour|per hour|\/hour|\/hr|\$?\/h|\$?ph|hr)', salary_str)
    if hourly_match:
        hourly_rate = float(hourly_match.group(1))
        return int(hourly_rate * HOURS_PER_YEAR)
    
    # Handle annual salary ranges (e.g., "100,440-223,680 a year" or "100,440−100,440−223,680 a year")
    # First, clean up multiple dashes and convert them to a single dash
    cleaned_str = re.sub(r'−+', '-', salary_str)  # Replace multiple em-dashes with hyphen
    cleaned_str = re.sub(r'-+', '-', cleaned_str)  # Replace multiple hyphens with single hyphen
    
    # Look for salary range pattern
    range_match = re.search(r'(\d+\.?\d*)\s*k?\s*-\s*(\d+\.?\d*)\s*k?', cleaned_str)
    if range_match:
        nums = [float(x) for x in range_match.groups()]
        # Convert if 'k' is in the string
        if 'k' in salary_str:
            nums = [x * 1000 for x in nums]
        low = min(nums)
        high = max(nums)
        return int((low + high) // 2)
    
    # Handle single values with 'k' (e.g., "150k" or "150K")
    k_match = re.search(r'(\d+\.?\d*)\s*k', salary_str)
    if k_match:
        return int(float(k_match.group(1)) * 1000)
    
    # Extract plain numbers
    numbers = re.findall(r'\d+\.?\d*', salary_str)
    if numbers:
        nums = [float(x) for x in numbers]
        # If multiple numbers found, assume it's a range
        if len(nums) >= 2:
            low = min(nums)
            high = max(nums)
            # If the numbers are small (likely in thousands), multiply by 1000
            if high < 1000:
                low *= 1000
                high *= 1000
            return int((low + high) // 2)
        else:
            # Single number found
            salary = nums[0]
            # If the number is small (likely in thousands), multiply by 1000
            if salary < 1000:
                salary *= 1000
            return int(salary)
    
    return 0

def load_and_preprocess_data(url):
    """Load and preprocess the dataset."""
    try:
        df = pd.read_csv(url)
        df = df[['Title', 'Location', 'Salary', 'Description']]
        df.dropna(subset=['Title', 'Location', 'Description'], inplace=True)

        # Clean salary column
        df['clean_salary'] = df['Salary'].apply(clean_salary)
        
        # Add debug print for salary cleaning
        st.write("Sample of cleaned salaries:")
        sample_df = df[['Salary', 'clean_salary']].head()
        st.write(sample_df)

        # Combine title and description for better clustering
        df['combined_text'] = df['Title'].str.lower() + ' ' + df['Description'].str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def find_matching_jobs(df, job_title, location, min_salary, keywords, debug=True):
    """Find matching jobs using simple filtering first."""
    matches = df.copy()

    # Debug information
    if debug:
        st.write("### Debug Information")
        st.write(f"Initial number of jobs: {len(matches)}")

    # Apply location filter if provided
    if location:
        matches = matches[matches['Location'].str.contains(location, case=False, na=False)]
        if debug:
            st.write(f"After location filter: {len(matches)} jobs")

    # Apply salary filter
    if min_salary > 0:
        matches = matches[matches['clean_salary'] >= min_salary]
        if debug:
            st.write(f"After salary filter: {len(matches)} jobs")

    # Apply keyword filter if provided
    if keywords:
        for keyword in keywords.split(','):
            keyword = keyword.strip()
            if keyword:
                matches = matches[
                    matches['Description'].str.contains(keyword, case=False, na=False) |
                    matches['Title'].str.contains(keyword, case=False, na=False)
                ]
                if debug:
                    st.write(f"After keyword '{keyword}' filter: {len(matches)} jobs")

    # Check if we have any matches before applying K-means
    if len(matches) == 0:
        if debug:
            st.warning("No jobs match the basic filters. Try relaxing your search criteria.")
        return matches

    # Only apply title and K-means clustering if we have matches
    if job_title:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )

        # Fit vectorizer on the remaining matches
        tfidf_matrix = vectorizer.fit_transform(matches['combined_text'])

        # Create clusters
        num_clusters = min(5, len(matches))  # Adjust number of clusters based on matches
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(tfidf_matrix)

        # Transform search query
        search_query = job_title.lower()
        query_vector = vectorizer.transform([search_query])
        query_cluster = kmeans.predict(query_vector)[0]

        # Assign clusters and filter
        matches['cluster'] = clusters
        matches = matches[matches['cluster'] == query_cluster]

        if debug:
            st.write(f"After clustering filter: {len(matches)} jobs")
            st.write(f"Query assigned to cluster: {query_cluster}")

    return matches

def main():
    st.set_page_config(page_title="Job Search Application", layout="wide")

    st.title("Job Search Application")
    st.write("Find jobs that match your preferences!")

    # Load data
    url = "https://huggingface.co/datasets/burcuonel/datajob_indeed_usa/raw/main/datajob_indeed_usa.csv"
    jobs_df = load_and_preprocess_data(url)

    if jobs_df is None:
        return

    # Initialize session state
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'filtered_jobs' not in st.session_state:
        st.session_state.filtered_jobs = pd.DataFrame()
    if 'expanded_descriptions' not in st.session_state:
        st.session_state.expanded_descriptions = set()

    # Sidebar filters
    with st.sidebar:
        st.header("Search Filters")

        with st.form(key='search_form'):
            job_title = st.text_input("Job Title:", "")
            location = st.text_input("Location:", "")
            min_salary = st.slider("Minimum Salary:", 0, 300000, 50000, step=5000)

            keywords = st.text_area(
                "Keywords (comma-separated):",
                placeholder="e.g., Python, SQL, machine learning",
                help="Enter keywords to find in job descriptions"
            )

            # Add debug mode checkbox
            debug_mode = st.checkbox("Show debug information", value=True)

            search_button = st.form_submit_button(
                "Search Jobs",
                use_container_width=True,
                type="primary"
            )

            if search_button:
                st.session_state.filtered_jobs = find_matching_jobs(
                    jobs_df, job_title, location, min_salary, keywords, debug=debug_mode
                )
                st.session_state.search_performed = True
                # Reset expanded descriptions when new search is performed
                st.session_state.expanded_descriptions = set()

        if st.button("Reset Filters", use_container_width=True):
            st.session_state.search_performed = False
            st.session_state.filtered_jobs = pd.DataFrame()
            st.session_state.expanded_descriptions = set()
            st.rerun()

    # Display results
    if st.session_state.search_performed:
        filtered_jobs = st.session_state.filtered_jobs
        st.subheader(f"Found {len(filtered_jobs)} Matching Jobs")

        if not filtered_jobs.empty:
            for index, row in filtered_jobs.iterrows():
                with st.expander(f"{row['Title']} - {row['Location']}"):
                    st.write(f"**Salary:** {row['Salary']}")
                    st.write(f"**Cleaned Salary:** {row['clean_salary']}")
                    if 'cluster' in row:
                        st.write(f"**Cluster:** {row['cluster']}")
                    st.write("**Description:**")
                    description = row['Description']

                    # Highlight keywords
                    if keywords:
                        keyword_list = [k.strip() for k in keywords.split(',')]
                        for keyword in keyword_list:
                            if keyword:
                                pattern = re.compile(f'({re.escape(keyword)})', re.IGNORECASE)
                                description = pattern.sub(r'**\1**', description)

                    # Check if this description is expanded
                    is_expanded = index in st.session_state.expanded_descriptions
                    
                    # Show full or truncated description based on state
                    if len(description) > 500 and not is_expanded:
                        st.write(description[:500] + "...")
                        if st.button("See more", key=f"expand_{index}"):
                            st.session_state.expanded_descriptions.add(index)
                            st.rerun()
                    else:
                        st.write(description)
                        if len(description) > 500 and st.button("See less", key=f"collapse_{index}"):
                            st.session_state.expanded_descriptions.remove(index)
                            st.rerun()
        else:
            st.warning("""
            No matching jobs found. Try:
            1. Using fewer filters
            2. Using more general keywords
            3. Reducing the minimum salary
            4. Checking different locations
            """)
    else:
        st.info("Use the filters in the sidebar and click 'Search Jobs' to find matching positions.")

if __name__ == "__main__":
    main()

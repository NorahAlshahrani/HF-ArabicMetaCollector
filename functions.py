import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from huggingface_hub import list_datasets, list_models, hf_hub_download

from huggingface_hub.utils import logging
logging.set_verbosity_error()
 

def covert_sizes_to_bytes(size):
    pattern = r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB)'
    matches = re.findall(pattern, size, flags=re.IGNORECASE)

    size_map = {
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }

    for value, unit in matches:
        unit_upper = unit.upper()
        bytes_size = float(value) * size_map[unit_upper]

    return bytes_size



def get_page_source(url):
    CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    try:
        # Go directly to the dataset page
        driver.get(url)
        time.sleep(3)


        return driver.page_source

    finally:
        driver.quit()


def get_readme_score(readme_text):

    text = readme_text.lower()

    # Define feature flags
    has_usage = "usage" in text or "how to use" in text
    has_license = "license" in text
    has_examples = "example" in text or "examples" in text
    has_citation = "citation" in text or "how to cite" in text
    has_description = "description" in text or "overview" in text
    has_authors = "author" in text or "maintainer" in text

    # Count how many indicators are present
    score = sum([has_usage, has_license, has_examples, has_citation, has_description, has_authors])

    return score



def classify_readme_level(readme_text):
    if not isinstance(readme_text, str) or len(readme_text.strip()) < 20:
        return "Low"

    score = get_readme_score(readme_text)
    
    # Classification logic
    if score >= 4:
        return "High"   # Excellent Threshold
    elif score >= 2:
        return "Medium"  # Trusted Threshold
    else:
        return "Low"


def get_dataset_size_info(dataset_name):
    url = f"https://huggingface.co/datasets/{dataset_name}"
   
    
    try:
        page_source = get_page_source(url)        
        soup = BeautifulSoup(page_source, 'html.parser')

        Size_of_downloaded_dataset_files = soup.find_all('a', class_='bg-linear-to-r dark:via-none group mb-1.5 flex max-w-full flex-col overflow-hidden rounded-lg border border-gray-100 from-white via-white to-white px-2 py-1 hover:from-gray-50 dark:from-gray-900 dark:to-gray-925 dark:hover:to-gray-900 md:mr-1.5 pointer-events-none')
        Size_of_downloaded_dataset_files_str = Size_of_downloaded_dataset_files[0].text.strip("Size of downloaded dataset files:").strip("\n")
        Size_of_downloaded_dataset_files_bytes = covert_sizes_to_bytes(Size_of_downloaded_dataset_files_str)
        
        
        Size_of_the_auto_converted_Parquet_files = soup.find_all('div', class_='truncate text-sm group-hover:underline')
        Size_of_the_auto_converted_Parquet_files_str = Size_of_the_auto_converted_Parquet_files[-1].text.strip()
        Size_of_the_auto_converted_Parquet_files_bytes = covert_sizes_to_bytes(Size_of_the_auto_converted_Parquet_files_str)
        

        Number_of_rows = soup.find_all('a', class_='bg-linear-to-r dark:via-none group mb-1.5 flex max-w-full flex-col overflow-hidden rounded-lg border border-gray-100 from-white via-white to-white px-2 py-1 hover:from-gray-50 dark:from-gray-900 dark:to-gray-925 dark:hover:to-gray-900 md:mr-1.5 pointer-events-none')
        Number_of_rows = Number_of_rows[1].text.strip("Number of rows:").strip("\n")
        Number_of_rows = Number_of_rows.strip(",").replace(",", "")    
       

        return Size_of_downloaded_dataset_files_str, Size_of_downloaded_dataset_files_bytes, Size_of_the_auto_converted_Parquet_files_str, Size_of_the_auto_converted_Parquet_files_bytes, Number_of_rows
    
    except IndexError:
        return "unknown", "unknown", "unknown", "unknown", "unknown"
    
    except UnboundLocalError:
        return "unknown", "unknown", "unknown", "unknown", "unknown"

    except Exception as e:
        print(f"Error processing {dataset_name}: {e}")



def get_dataset_readme(dataset_id):
    readme_path = hf_hub_download(repo_id=dataset_id, repo_type="dataset", filename="README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    return readme_content


def extract_acl_links(readme_content):
    acl_pattern = r"https?://aclanthology\.org/\S+"
    return re.findall(acl_pattern, readme_content)



def get_arabic_datasets_by_task_categories(task_mapping):
    all_rows = []
    
    # Loop through each task
    for user_task, hf_task in task_mapping.items():
        # print(f"🔍 Processing task: {user_task} ({hf_task})")
        try:
            datasets_list = list_datasets(task_categories=hf_task, language="ar")
        except Exception as e:
            print(f"Failed to fetch for task {user_task}: {e}")
            continue
    
        for dataset in datasets_list:
            tags = dataset.tags if hasattr(dataset, "tags") else []
    
            try:
                license = [tag for tag in dataset.tags if "license" in tag][0].split(":")[-1]
            except:
                license = "none"
            try:
                models = len(list(list_models(filter=f"dataset:{dataset.id}")))
            except:
                models = "none"
    
            # size = next((tag.split(":")[-1] for tag in tags if tag.startswith("size:")), "unknown")
            Size_of_downloaded_dataset_files_str, Size_of_downloaded_dataset_files_bytes, Size_of_the_auto_converted_Parquet_files_str, Size_of_the_auto_converted_Parquet_files_bytes, Number_of_rows = get_dataset_size_info(dataset.id)
            
            arxiv_link = next((tag.split(":", 1)[-1] for tag in tags if tag.startswith("arxiv:")), "none")
            if arxiv_link != "none":
                arxiv_link = "https://arxiv.org/abs/"+arxiv_link

            try:
                readme = get_dataset_readme(dataset.id)
                if len(readme) == 0:
                    readme = "none" 
                    
                acl_links = extract_acl_links(readme)
                if len(acl_links) == 0:
                    acl_links = "none" 
            except:
                readme = "none"
                acl_links = "none"  

            readme_quality_level = classify_readme_level(readme)
            readme_quality_score = get_readme_score(readme)

            all_rows.append({
                "Task": user_task,
                "Dataset ID": dataset.id,
                "Likes": dataset.likes,
                "Downloads": dataset.downloads,
                "Last Modified": dataset.lastModified,
                "License": license,
                "Models": models,
                "Size of downloaded files": Size_of_downloaded_dataset_files_str.upper(),
                "Size of downloaded files in bytes": Size_of_downloaded_dataset_files_bytes,
                "Size of Parquet files": Size_of_the_auto_converted_Parquet_files_str.upper(),
                "Size of Parquet files in bytes": Size_of_the_auto_converted_Parquet_files_bytes,
                "Number of Rows" : Number_of_rows,
                "ArXiv Paper": arxiv_link,
                "ACL Paper": acl_links,
                "README file": readme,
                "README Quality Level": readme_quality_level,
                "README Quality Score": readme_quality_score
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(all_rows)
    return df



def get_arabic_datasets_by_keywords(search_keywords, required_tags, required_modality):
    # Get only Arabic datasets
    datasets_list = list_datasets(language="ar")

    dataset_rows = []

    for dataset in datasets_list:
        dataset_id = dataset.id.lower()
        dataset_tags = dataset.tags or []

        # Check for match in name 
        name_match = any(keyword.lower() in dataset_id for keyword in search_keywords)
        
        # Make sure it's a text dataset
        has_text_modality = required_modality in dataset_tags

        if has_text_modality and (name_match ):
            try:
                license = [tag for tag in dataset_tags if "license:" in tag][0].split(":")[-1]
            except:
                license = "none"
            try:
                models = len(list(list_models(filter=f"dataset:{dataset.id}")))
            except:
                models = "none"

            # size = next((tag.split(":")[-1] for tag in dataset_tags if tag.startswith("size:")), "unknown")
            Size_of_downloaded_dataset_files_str, Size_of_downloaded_dataset_files_bytes, Size_of_the_auto_converted_Parquet_files_str, Size_of_the_auto_converted_Parquet_files_bytes, Number_of_rows = get_dataset_size_info(dataset.id)

            arxiv_link = next((tag.split(":", 1)[-1] for tag in dataset_tags if tag.startswith("arxiv:")), "none")
            if arxiv_link != "none":
                arxiv_link = "https://arxiv.org/abs/"+arxiv_link

            try:
                readme = get_dataset_readme(dataset.id)
                if len(readme) == 0:
                    readme = "none" 
                    
                acl_links = extract_acl_links(readme)
                if len(acl_links) == 0:
                    acl_links = "none" 
            except:
                readme = "none"
                acl_links = "none"  

            readme_quality_level = classify_readme_level(readme)
            readme_quality_score = get_readme_score(readme)
            
            dataset_rows.append({
                "Dataset ID": dataset.id,
                "Likes": dataset.likes,
                "Downloads": dataset.downloads,
                "Last Modified": dataset.lastModified,
                "License": license,
                "Models": models,
                "Size of downloaded files": Size_of_downloaded_dataset_files_str.upper(),
                "Size of downloaded files in bytes": Size_of_downloaded_dataset_files_bytes,
                "Size of Parquet files": Size_of_the_auto_converted_Parquet_files_str.upper(),
                "Size of Parquet files in bytes": Size_of_the_auto_converted_Parquet_files_bytes,
                "Number of Rows" : Number_of_rows,
                "ArXiv Paper": arxiv_link,
                "ACL Paper": acl_links,
                "README file": readme,
                "README Quality Level": readme_quality_level,
                "README Quality Score": readme_quality_score
            })

    # Create and show DataFrame
    df = pd.DataFrame(dataset_rows)
    return df
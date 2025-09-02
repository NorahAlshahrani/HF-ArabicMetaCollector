## 📄 Overview

This repository contains Python tools that automatically extract and evaluate metadata for Arabic post-training datasets on Hugging Face. The datasets are organized into four key dimensions:  **LLM Capabilities**, **Steerability**, **Alignment**,and **Robustness** —and are evaluated across six metrics: **popularity**, **adoption**, **recency**, **documentation quality**, **licensing**, and **scientific contribution**.

## 📖 Documentation

### Requirements

•	Python: 3.9 or higher
•	Python packages: Install the required libraries using pip:
```bash
pip install pandas selenium beautifulsoup4 huggingface_hub pyyaml
```
•	ChromeDriver: Ensure ChromeDriver is installed and the path is correctly set in the CHROMEDRIVER_PATH variable in the script.
#### Metadata Extraction Tool  
Run the script from the command line:
```bash
python script.py -c <category> [-s] | -l
```
**Options**
•	-c or --category → Specify the task category (e.g., "Summarization")
•	-s or --save → Save the results to a CSV file
•	-l or --list → List all available categories

**Example:**  
List available categories:
```bash
python script.py --list
```
Fetch datasets in a category and save results:
```bash
python script.py --category "Summarization" --save
```

#### Evaluation Tool  
**Example:**  
```bash
python evals.py --file Summarization.csv --eval all --save
python evals.py --file Summarization.csv --eval popularity_level --save
```

## BibTeX Citation:
```bash
@misc{alkhowaiter2025mindgapreviewarabic,
      title={Mind the Gap: A Review of Arabic Post-Training Datasets and Their Limitations}, 
      author={Mohammed Alkhowaiter and Norah Alshahrani and Saied Alshahrani and Reem I. Masoud and Alaa Alzahrani and Deema Alnuhait and Emad A. Alghamdi and Khalid Almubarak},
      year={2025},
      eprint={2507.14688},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.14688}, 
}
```

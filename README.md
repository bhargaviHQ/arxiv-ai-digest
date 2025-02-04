
The application scrapes research papers from [ArXiv](https://arxiv.org/) and generates brief summaries of the research paper abstracts using LLMs.

## Paired t-test Results for Similarity Scores

### Hypotheses:
- **Null Hypothesis (H0)**: There is no significant difference in the similarity scores between the summarization models.
- **Alternate Hypothesis (H1)**: There is a significant difference in the similarity scores between the summarization models.

### Experiment Details:
- Scraped **arXiv** data and stored it in **MongoDB**.
- Used Large Language Models (LLMs) for summarization: **bart-large-cnn, t5-small, google/pegasus-xsum**.
- Applied **SentenceTransformer** for **Semantic Textual Similarity (STS)**.
  - Results: **BART (0.729) outperformed T5 (0.694) and PEGASUS (0.584)**.

### Paired t-test Results:

The results of the paired t-tests indicate whether there is a statistically significant difference between the models. A **p-value below 0.05** suggests a significant difference.

| Model Pair                                  | p-value                     | Significance                     |
|---------------------------------------------|-----------------------------|----------------------------------|
| facebook/bart-large-cnn vs t5-small         | 1.4711e-47                  | Significant (p < 0.05)          |
| facebook/bart-large-cnn vs google/pegasus-xsum | 1.0123e-231                 | Significant (p < 0.05)          |
| t5-small vs google/pegasus-xsum            | 2.1481e-173                 | Significant (p < 0.05)          |

### Conclusion:
Since all **p-values** are much lower than **0.05**, we reject the **null hypothesis (H0)** and conclude that there is a **significant difference** between each pair of models in terms of similarity scores. We can see that **BART performed better than the other two models**, further confirming the findings of the statistical tests.

## Visualizations of Similarity Score Distributions
![image](https://github.com/user-attachments/assets/14c1a4df-bf4c-45bc-ae16-9b8c48fa38f9)


### **1. Distribution of Similarity Scores**  
The above plot shows the **distribution of similarity scores** for each model (**BART, T5, and PEGASUS**). It highlights key differences in how each model performs in terms of semantic similarity.
#### **Observations:**
- **T5 and PEGASUS:**  
  - A **large bar** in the **0.2** and **0.2-0.4** score ranges suggests that a significant portion of their scores are in the **lower range (0.2 to 0.4)**.  
  - This indicates that these models frequently produce **lower similarity scores** which may mean they are **less effective** at the summarization task for this dataset.  
- **BART:**  
  - A **large bar** around **0.5** suggests that **BART consistently produces higher similarity scores** compared to T5 and PEGASUS.  
  - This confirms that **BART is performing better on average**, making it more effective for this specific dataset.

### **2. Similarity Scores Across Rows**  

![image](https://github.com/user-attachments/assets/299834fe-0c53-4170-80aa-4ddd46a94741)

This line graph plots the **similarity scores for each sample in the dataset** across different models.

#### **Observations:**
- **BART maintains consistently higher similarity scores** across most samples.  
- **T5 and PEGASUS show lower scores**, confirming that they are underperforming relative to BART.  


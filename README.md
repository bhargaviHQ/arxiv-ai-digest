# arxiv-ai-digest
The application scrapes research papers from [ArXiv](https://arxiv.org/) and generates brief summaries using LLMs.

## Paired t-test Results for Similarity Scores

| Model Pair                                  | Statistic          | p-value                     | Significance                     |
|---------------------------------------------|--------------------|-----------------------------|----------------------------------|
| facebook/bart-large-cnn vs t5-small        | 14.8592            | 1.4711e-47                  | Significant Difference          |
| facebook/bart-large-cnn vs google/pegasus-xsum | 37.0713        | 1.0123e-231                 | Significant Difference          |
| t5-small vs google/pegasus-xsum            | 30.9367            | 2.1481e-173                 | Significant Difference          |


![image](https://github.com/user-attachments/assets/14c1a4df-bf4c-45bc-ae16-9b8c48fa38f9)

![image](https://github.com/user-attachments/assets/299834fe-0c53-4170-80aa-4ddd46a94741)

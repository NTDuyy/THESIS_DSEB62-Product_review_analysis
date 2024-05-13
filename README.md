# Topic modelling for Vietnamese product reviews
Result summary:
|          Model          | SVM  |      |                   | XGBoost |      |                   |      PhoBert      |
|:-----------------------:|:----:|:----:|:-----------------:|:-------:|:----:|:-----------------:|:-----------------:|
|  Feature representation |  BOW | CBOW | PhoBert Embedding |   BOW   | CBOW | PhoBert Embedding | PhoBert Embedding |
|       Hamming loss      |  0.1 | 0.12 |        0.08       |   0.09  | 0.11 |        0.08       |        0.08       |
|        Precision        | 0.88 | 0.85 |        0.87       |   0.87  | 0.87 |        0.88       |        0.88       |
|          Recall         | 0.83 | 0.79 |        0.90       |   0.87  |  0.8 |        0.89       |        0.89       |
|        F-measure        | 0.85 | 0.82 |        0.88       |   0.87  | 0.83 |        0.88       |        0.88       |

Demo Streamlit app: https://thesis-topic-modelling-ha8fw9vmwmxnpnrr7z6phx.streamlit.app
<br />
App screenshot:
![image](https://github.com/DDKson/THESIS_DSEB62-Product_review_analysis/assets/92723196/7e633598-68b7-46ed-a1ed-64943e6f6207)


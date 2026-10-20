# Student Marks Analysis Project

## Overview
This project analyzes synthetic student performance data consisting of 1,000 students across 5 subjects.

## Data Cleaning
- The dataset originally contained missing marks and duplicate rows.
- **Duplicates**: Removed entirely.
- **Missing Marks**: Imputed using the mean marks for the respective subject over the entire dataset.

## Observations & Analysis
### Overall Performance
- **Overall Average Marks**: 69.47/100
- **Highest Mark**: 100/100
- **Lowest Mark**: 21/100

### Top 5 Students
1. Student_300 (Total: 451)
2. Student_677 (Total: 431)
3. Student_234 (Total: 428)
4. Student_707 (Total: 427)
5. Student_85 (Total: 425)

### Subject-Wise Performance
The average marks for each subject indicate where students are performing the best and where they struggle.

- **Top-Performing Subject**: Computer Science (69.81)
- **Weakest Subject**: Science (69.14)

## Visualizations Built
- `subject_avg_bar_chart.png`: Shows the comparative average performance between different subjects.
- `grade_distribution_pie_chart.png`: Displays the categorical grade distribution across all subjects and students.

## Conclusion
The analysis successfully identifies the high achievers and the subjects that may require more focus. Specifically, Science is the weakest subject and may need instructional intervention, whereas students performed exceptionally well in Computer Science.

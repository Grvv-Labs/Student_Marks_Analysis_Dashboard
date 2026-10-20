import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    print("--- 1. Loading the student marks CSV file ---")
    try:
        df = pd.read_csv('student_marks.csv')
        print(f"Loaded {len(df)} records.")
    except FileNotFoundError:
        print("Error: student_marks.csv not found.")
        return

    print("\n--- 2. Checking for missing marks or duplicate entries ---")
    duplicate_count = df.duplicated().sum()
    print(f"Found {duplicate_count} duplicate rows. Removing duplicates...")
    df.drop_duplicates(inplace=True)
    
    missing_count = df['Marks'].isna().sum()
    print(f"Found {missing_count} rows with missing marks. Filling with subject average...")
    
    # Calculate subject averages excluding NaNs and
    # Made a sepearate column to fill missing values
    subject_avgs = df.groupby('Subject')['Marks'].transform('mean')
    df['Marks'] = df['Marks'].fillna(subject_avgs)
    
    # Ensure marks are integers
    df['Marks'] = df['Marks'].round().astype(int)
    
    print(f"Data cleaned. Proceeding with {len(df)} records.")

    print("\n--- 3. Calculating average marks ---")
    overall_avg = df['Marks'].mean()
    print(f"Overall average marks across all subjects and students: {overall_avg:.2f}")

    print("\n--- 4. Finding highest and lowest marks ---")
    highest_mark = df['Marks'].max()
    lowest_mark = df['Marks'].min()
    
    # Get students who got these marks
    top_scorers = df[df['Marks'] == highest_mark]['Student_Name'].unique()
    bottom_scorers = df[df['Marks'] == lowest_mark]['Student_Name'].unique()
    
    print(f"Highest mark: {highest_mark} (achieved by {len(top_scorers)} students)")
    print(f"Lowest mark: {lowest_mark} (achieved by {len(bottom_scorers)} students)")

    print("\n--- 5. Calculating subject-wise average marks ---")
    subject_avg = df.groupby('Subject')['Marks'].mean().sort_values(ascending=False)
    for subject, avg in subject_avg.items():
        print(f"  {subject}: {avg:.2f}")
        
    top_subject = subject_avg.index[0]
    weakest_subject = subject_avg.index[-1]

    print("\n--- 6. Identifying top 5 students ---")
    student_total_marks = df.groupby('Student_Name')['Marks'].sum().sort_values(ascending=False)
    top_5_students = student_total_marks.head(5)
    print("Top 5 Students by Total Marks:")
    for rank, (student, total) in enumerate(top_5_students.items(), 1):
        print(f"  {rank}. {student} - Total: {total}")

    print("\n--- 7. Creating visualizations ---")
    
    # Chart 1: Bar chart of average marks by subject
    plt.figure(figsize=(10, 6))
    bars = plt.bar(subject_avg.index, subject_avg.values, color=['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#F44336'])
    plt.title('Subject-wise Average Marks', fontsize=14, pad=15)
    plt.xlabel('Subjects', fontsize=12)
    plt.ylabel('Average Marks', fontsize=12)
    plt.ylim(0, 100)
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom')
        
    plt.tight_layout()
    plt.savefig('subject_avg_bar_chart.png', dpi=300)
    print("Saved 'subject_avg_bar_chart.png'")
    
    # Chart 2: Pie chart of grade distribution
    # Define grades
    bins = [-1, 39, 59, 79, 89, 100]
    labels = ['F (<40)', 'C (40-59)', 'B (60-79)', 'A (80-89)', 'A+ (90+)']
    df['Grade'] = pd.cut(df['Marks'], bins=bins, labels=labels)
    
    grade_counts = df['Grade'].value_counts().sort_index()
    
    plt.figure(figsize=(8, 8))
    colors = ['#FF5252', '#FFCA28', '#66BB6A', '#42A5F5', '#AB47BC']
    plt.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title('Overall Grade Distribution', fontsize=14)
    plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig('grade_distribution_pie_chart.png', dpi=300)
    print("Saved 'grade_distribution_pie_chart.png'")

    print("\n--- 8. Writing observations and conclusion to ANALYSIS_REPORT.md ---")
    readme_content = f"""# Student Marks Analysis Project

## Overview
This project analyzes synthetic student performance data consisting of 1,000 students across 5 subjects.

## Data Cleaning
- The dataset originally contained missing marks and duplicate rows.
- **Duplicates**: Removed entirely.
- **Missing Marks**: Imputed using the mean marks for the respective subject over the entire dataset.

## Observations & Analysis
### Overall Performance
- **Overall Average Marks**: {overall_avg:.2f}/100
- **Highest Mark**: {highest_mark}/100
- **Lowest Mark**: {lowest_mark}/100

### Top 5 Students
1. {top_5_students.index[0]} (Total: {top_5_students.iloc[0]})
2. {top_5_students.index[1]} (Total: {top_5_students.iloc[1]})
3. {top_5_students.index[2]} (Total: {top_5_students.iloc[2]})
4. {top_5_students.index[3]} (Total: {top_5_students.iloc[3]})
5. {top_5_students.index[4]} (Total: {top_5_students.iloc[4]})

### Subject-Wise Performance
The average marks for each subject indicate where students are performing the best and where they struggle.

- **Top-Performing Subject**: {top_subject} ({subject_avg[top_subject]:.2f})
- **Weakest Subject**: {weakest_subject} ({subject_avg[weakest_subject]:.2f})

## Visualizations Built
- `subject_avg_bar_chart.png`: Shows the comparative average performance between different subjects.
- `grade_distribution_pie_chart.png`: Displays the categorical grade distribution across all subjects and students.

## Conclusion
The analysis successfully identifies the high achievers and the subjects that may require more focus. Specifically, {weakest_subject} is the weakest subject and may need instructional intervention, whereas students performed exceptionally well in {top_subject}.
"""
    with open('ANALYSIS_REPORT.md', 'w') as f:
        f.write(readme_content)
    
    print("Analysis complete! Wrote 'ANALYSIS_REPORT.md'")

if __name__ == '__main__':
    main()

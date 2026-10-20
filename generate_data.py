import pandas as pd
import numpy as np
import random

def generate_big_dataset(num_students=1000, missing_rate=0.01, duplicate_rate=0.02):
    np.random.seed(42)
    random.seed(42)
    
    subjects = ['Mathematics', 'Science', 'English', 'History', 'Computer Science']
    classes = ['10A', '10B', '10C', '11A', '11B', '12A']
    
    data = []
    
    # Generate base data
    for i in range(1, num_students + 1):
        student_id = f"S{i:04d}"
        student_name = f"Student_{i}"
        student_class = random.choice(classes)
        
        # Each student takes all subjects
        for subject in subjects:
            # Generate marks with a normal distribution
            marks = int(np.clip(np.random.normal(70, 15), 0, 100))
            
            data.append({
                'Student_ID': student_id,
                'Student_Name': student_name,
                'Subject': subject,
                'Marks': marks,
                'Class': student_class
            })
            
    df = pd.DataFrame(data)
    
    # Inject missing values into 'Marks'
    num_missing = int(len(df) * missing_rate)
    missing_indices = np.random.choice(df.index, num_missing, replace=False)
    df.loc[missing_indices, 'Marks'] = np.nan
    
    # Inject duplicate rows
    num_duplicates = int(len(df) * duplicate_rate)
    duplicate_rows = df.sample(n=num_duplicates, replace=True)
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # Shuffle dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv('student_marks.csv', index=False)
    print(f"Dataset generated successfully! Total rows: {len(df)} (including {num_duplicates} duplicates and {num_missing} missing values).")

if __name__ == '__main__':
    generate_big_dataset(num_students=1000)
